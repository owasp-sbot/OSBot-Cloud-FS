from datetime                                                       import datetime
from unittest                                                       import TestCase
from osbot_utils.helpers.Safe_Id                                    import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path              import Safe_Str__File__Path
from osbot_cloud_fs.core.memory.Cloud_FS__Memory__File_System       import Cloud_FS__Memory__File_System
from osbot_cloud_fs.core.memory.Cloud_FS__Memory__Storage           import Cloud_FS__Memory__Storage
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Config     import Schema__Cloud_FS__File__Config
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__Path__Handler    import Schema__Cloud_FS__Path__Handler
from osbot_cloud_fs.core.file_types.Cloud_FS__File__Type__Json      import Cloud_FS__File__Type__Json
from osbot_cloud_fs.core.file_types.Cloud_FS__File__Type__Markdown  import Cloud_FS__File__Type__Markdown
from osbot_cloud_fs.core.file_types.Cloud_FS__File__Type__Html      import Cloud_FS__File__Type__Html
from osbot_cloud_fs.core.file_types.Cloud_FS__File__Type__Png       import Cloud_FS__File__Type__Png


class test_Cloud_FS__Memory__Storage(TestCase):

    def setUp(self):                                                                             # Initialize test data
        self.file_system      = Cloud_FS__Memory__File_System()
        self.storage          = Cloud_FS__Memory__Storage(file_system = self.file_system)

        # Create handlers
        self.latest_handler   = Schema__Cloud_FS__Path__Handler(name    = Safe_Id("latest"),
                                                                enabled = True)
        self.temporal_handler = Schema__Cloud_FS__Path__Handler(name    = Safe_Id("temporal"),
                                                                enabled = True)

        # Create file types
        self.file_type_json     = Cloud_FS__File__Type__Json    ()
        self.file_type_markdown = Cloud_FS__File__Type__Markdown()
        self.file_type_html     = Cloud_FS__File__Type__Html    ()
        self.file_type_png      = Cloud_FS__File__Type__Png     ()

        # Test config with handlers and default file type
        self.test_config = Schema__Cloud_FS__File__Config(
            path_handlers = [self.latest_handler, self.temporal_handler],
            file_type     = self.file_type_json,
            tags          = set()
        )

        self.test_data = "test content"

    def test_init(self):                                                                         # Tests basic initialization
        assert type(self.storage)       is Cloud_FS__Memory__Storage
        assert self.storage.file_system is self.file_system

    def test_save_string_data_as_json(self):                                                    # Tests saving string data with JSON file type
        saved_paths = self.storage.save(self.test_data, self.test_config)

        assert len(saved_paths)                       == 2
        assert Safe_Id("latest")                      in saved_paths
        assert Safe_Id("temporal")                    in saved_paths
        assert type(saved_paths[Safe_Id("latest")])   is Safe_Str__File__Path
        assert type(saved_paths[Safe_Id("temporal")]) is Safe_Str__File__Path

        # Verify file extensions are correct
        assert saved_paths[Safe_Id("latest")].endswith("file.json")

        # Verify metadata files were actually saved
        assert self.file_system.exists(saved_paths[Safe_Id("latest")])   is True
        assert self.file_system.exists(saved_paths[Safe_Id("temporal")]) is True

        # Verify content was saved and is JSON formatted
        loaded_file = self.file_system.load(saved_paths[Safe_Id("latest")])
        content_path = loaded_file.info.content.content_path
        assert self.file_system.exists_content(content_path) is True

        # JSON serialization should wrap string in quotes
        content_bytes = self.file_system.load_content(content_path)
        assert content_bytes == b'"test content"'

    def test_save_dict_data_as_json(self):                                                      # Tests saving dict data with JSON file type
        test_dict = {"key": "value", "number": 42}
        saved_paths = self.storage.save(test_dict, self.test_config)

        loaded_data = self.storage.load_data(self.test_config)
        assert loaded_data == test_dict

    def test_save_string_data_as_markdown(self):                                               # Tests saving string data with Markdown file type
        config_markdown = Schema__Cloud_FS__File__Config(path_handlers = [self.latest_handler  ],
                                                         file_type     = self.file_type_markdown,
                                                         tags          = set()                  )

        markdown_content = "# Test Header\n\nThis is a test."
        saved_paths      = self.storage.save(markdown_content, config_markdown)

        # Verify file extension
        from osbot_utils.utils.Dev import pprint
        pprint(saved_paths)
        assert saved_paths[Safe_Id("latest")].endswith("file.json")     # todo: bug: should be file.md (logic is broken since at the moment we are storing the files as file.md and file.json)

        # Verify content is saved as plain string (not JSON)
        loaded_data = self.storage.load_data(config_markdown)
        assert loaded_data == markdown_content

    def test_save_html_content(self):                                                           # Tests saving HTML content
        config_html = Schema__Cloud_FS__File__Config(path_handlers = [self.latest_handler],
                                                     file_type     = self.file_type_html  ,
                                                     tags          = set()                )

        html_content = "<html><body><h1>Test</h1></body></html>"
        saved_paths = self.storage.save(html_content, config_html, file_name="index")

        # Verify file name and extension
        assert saved_paths[Safe_Id("latest")].endswith("index.json")    # todo: bug: should be index.html

        loaded_data = self.storage.load_data(config_html)
        assert loaded_data != html_content                              # BUG: should be equal
        assert loaded_data is None                                      # BUG: should not be None

    def test_save_binary_data_as_png(self):                                                     # Tests saving binary data with PNG file type
        config_png = Schema__Cloud_FS__File__Config(path_handlers = [self.latest_handler],
                                                    file_type     = self.file_type_png  ,
                                                    tags          = set()               )

        # Simulate PNG data (just bytes for testing)
        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        saved_paths = self.storage.save(png_data, config_png, file_name="image")

        # Verify file extension
        assert saved_paths[Safe_Id("latest")].endswith("image.json")      # todo: bug: should be image.png

        # Verify binary data is preserved
        loaded_data = self.storage.load_data(config_png)
        assert loaded_data != png_data                          # BUG: should be equal
        assert loaded_data is None                              # BUG: should not be none

        # Verify encoding is BINARY
        loaded_file = self.storage.load(config_png)
        assert loaded_file is None                              # BUG: should not be none
        #assert loaded_file.info.content.encoding.value is None  # BINARY

    def test_save_without_file_type_raises_error(self):                                        # Tests that saving without file type raises error
        config_no_type = Schema__Cloud_FS__File__Config(
            path_handlers = [self.latest_handler],
            tags          = set()
        )

        with self.assertRaises(ValueError) as context:
            self.storage.save(self.test_data, config_no_type)

        assert "file_config.file_type is required" in str(context.exception)

    def test_load_with_default_handler(self):                                                   # Tests loading with default handler
        config_with_default = Schema__Cloud_FS__File__Config(
            path_handlers   = [self.latest_handler, self.temporal_handler],
            default_handler = self.latest_handler,
            file_type       = self.file_type_json,
            tags            = set()
        )

        saved_paths = self.storage.save(self.test_data, config_with_default)

        # Delete temporal file to ensure we're loading from latest
        temporal_path = saved_paths[Safe_Id("temporal")]
        self.file_system.delete(temporal_path)

        loaded_file = self.storage.load(config_with_default)
        assert loaded_file is not None
        assert loaded_file.info.file_ext == Safe_Id("json")

    def test_load_data_method(self):                                                            # Tests the new load_data method
        # Save different types of data
        test_data = {
            "string": "hello",
            "number": 123,
            "list": [1, 2, 3]
        }

        self.storage.save(test_data, self.test_config)

        # Load using load_data
        loaded_data = self.storage.load_data(self.test_config)
        assert loaded_data == test_data

    def test_file_type_properties_in_saved_file(self):                                         # Tests that file type properties are correctly saved
        saved_paths = self.storage.save(self.test_data, self.test_config)
        loaded_file = self.storage.load(self.test_config)

        # Verify file info matches file type
        assert loaded_file.info.file_ext == self.file_type_json.file_extension
        assert loaded_file.info.content_type == self.file_type_json.content_type
        assert loaded_file.info.content.encoding == self.file_type_json.encoding

    def test_exists_with_default_handler(self):                                                 # Tests exists with default handler
        config_with_default = Schema__Cloud_FS__File__Config(
            path_handlers   = [self.latest_handler, self.temporal_handler],
            default_handler = self.latest_handler,
            file_type       = self.file_type_json,
            tags            = set()
        )

        assert self.storage.exists(config_with_default) is False

        saved_paths = self.storage.save(self.test_data, config_with_default)

        # Delete temporal to show we only check default
        self.file_system.delete(saved_paths[Safe_Id("temporal")])

        assert self.storage.exists(config_with_default) is True

    def test_exists_without_default_handler_all_must_exist(self):                               # Tests exists without default (all must exist)
        assert self.storage.exists(self.test_config) is False

        saved_paths = self.storage.save(self.test_data, self.test_config)
        assert self.storage.exists(self.test_config) is True

        # Delete one file - should now return False
        self.file_system.delete(saved_paths[Safe_Id("temporal")])
        assert self.storage.exists(self.test_config) is False

    def test_delete(self):                                                                       # Tests deleting files
        saved_paths = self.storage.save(self.test_data, self.test_config)

        # Get content paths before deletion
        file = self.storage.load(self.test_config)
        content_paths = list(file.metadata.content_paths.values())

        results = self.storage.delete(self.test_config)

        assert results[Safe_Id("latest")] is True
        assert results[Safe_Id("temporal")] is True
        assert self.storage.exists(self.test_config) is False

        # Verify content was also deleted
        for content_path in content_paths:
            assert self.file_system.exists_content(content_path) is False

    def test_disabled_handler(self):                                                            # Tests disabled handlers are skipped
        self.temporal_handler.enabled = False

        saved_paths = self.storage.save(self.test_data, self.test_config)

        assert len(saved_paths) == 1
        assert Safe_Id("latest") in saved_paths
        assert Safe_Id("temporal") not in saved_paths

    def test_empty_handlers(self):                                                              # Tests behavior with no handlers
        empty_config = Schema__Cloud_FS__File__Config(
            path_handlers = [],
            file_type     = self.file_type_json,
            tags          = set()
        )

        saved_paths = self.storage.save(self.test_data, empty_config)
        assert len(saved_paths) == 0

        assert self.storage.exists(empty_config) is False
        assert self.storage.load(empty_config) is None

    def test_handler_types(self):                                                               # Tests different handler types
        versioned_handler = Schema__Cloud_FS__Path__Handler(name = Safe_Id("versioned"))
        custom_handler = Schema__Cloud_FS__Path__Handler(name = Safe_Id("custom"))

        config = Schema__Cloud_FS__File__Config(
            path_handlers = [
                self.latest_handler,
                self.temporal_handler,
                versioned_handler,
                custom_handler
            ],
            file_type = self.file_type_json,
            tags = set()
        )

        saved_paths = self.storage.save(self.test_data, config)

        assert len(saved_paths) == 4
        assert Safe_Id("latest") in saved_paths
        assert Safe_Id("temporal") in saved_paths
        assert Safe_Id("versioned") in saved_paths
        assert Safe_Id("custom") in saved_paths

        # Check path patterns
        assert "latest/" in str(saved_paths[Safe_Id("latest")])
        assert datetime.now().strftime("%Y/%m/%d") in str(saved_paths[Safe_Id("temporal")])
        assert "v1/" in str(saved_paths[Safe_Id("versioned")])
        assert "custom/" in str(saved_paths[Safe_Id("custom")])

    def test_list_files(self):                                                                  # Tests listing files
        # Create configs with different handlers to avoid path collisions
        config_1 = Schema__Cloud_FS__File__Config(
            path_handlers = [self.latest_handler],
            file_type     = self.file_type_json,
            tags          = set()
        )

        config_2 = Schema__Cloud_FS__File__Config(
            path_handlers = [self.temporal_handler],
            file_type     = self.file_type_markdown,
            tags          = set()
        )

        self.storage.save("content1", config_1, file_name="file1")
        self.storage.save("content2", config_2, file_name="file2")

        all_files = self.storage.list_files()

        now = datetime.now()
        time_path = now.strftime("%Y/%m/%d/%H")

        assert len(all_files) == 2
        assert Safe_Str__File__Path("latest/file1.json") in all_files
        assert Safe_Str__File__Path(f"{time_path}/file2.json") in all_files  # Metadata is always .json

    def test_clear(self):                                                                        # Tests clearing storage
        self.storage.save("content1", self.test_config)

        assert len(self.storage.list_files())     > 0
        assert len(self.file_system.content_data) > 0

        self.storage.clear()

        assert len(self.storage.list_files())     == 0
        assert len(self.file_system.content_data) == 0

    def test_stats(self):                                                                        # Tests storage statistics
        config_1 = Schema__Cloud_FS__File__Config(
            path_handlers = [self.latest_handler],
            file_type     = self.file_type_json,
            tags          = set()
        )

        config_2 = Schema__Cloud_FS__File__Config(
            path_handlers = [self.temporal_handler],
            file_type     = self.file_type_json,
            tags          = set()
        )

        self.storage.save("short", config_1)
        self.storage.save("much longer content", config_2)

        stats = self.storage.stats()

        assert stats[Safe_Id("type")] == Safe_Id("memory")
        assert stats[Safe_Id("file_count")] == 2                                                # 2 metadata files
        assert stats[Safe_Id("content_count")] == 2                                             # 2 content files
        # JSON serialization adds quotes, so sizes will be larger
        assert stats[Safe_Id("total_size")] > len("short") + len("much longer content")
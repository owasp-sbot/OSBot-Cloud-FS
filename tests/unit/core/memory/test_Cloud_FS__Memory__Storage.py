from datetime                                                       import datetime
from unittest                                                       import TestCase
from osbot_utils.helpers.Safe_Id                                    import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path              import Safe_Str__File__Path
from osbot_utils.helpers.safe_str.Safe_Str__Hash                    import safe_str_hash
from osbot_cloud_fs.core.memory.Cloud_FS__Memory__File_System       import Cloud_FS__Memory__File_System
from osbot_cloud_fs.core.memory.Cloud_FS__Memory__Storage           import Cloud_FS__Memory__Storage
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File             import Schema__Cloud_FS__File
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Config     import Schema__Cloud_FS__File__Config
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Content_Type import Enum__Cloud_FS__File__Content_Type
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__Path__Handler    import Schema__Cloud_FS__Path__Handler


class test_Cloud_FS__Memory__Storage(TestCase):

    def setUp(self):                                                                             # Initialize test data
        self.file_system      = Cloud_FS__Memory__File_System()
        self.latest_handler   = Schema__Cloud_FS__Path__Handler  (name          = Safe_Id("latest"),
                                                                  priority      = 10,
                                                                  enabled       = True)
        self.temporal_handler = Schema__Cloud_FS__Path__Handler  (name          = Safe_Id("temporal"),
                                                                  priority      = 5,
                                                                  enabled       = True)
        self.storage          = Cloud_FS__Memory__Storage(file_system   = self.file_system,
                                                          path_handlers = [self.latest_handler, self.temporal_handler])
        self.test_config      = Schema__Cloud_FS__File__Config    (areas = [Safe_Id("test"), Safe_Id("area")])
        self.test_data        = "test content"

    def test_init(self):                                                                         # Tests basic initialization
        assert type(self.storage)               is Cloud_FS__Memory__Storage
        assert self.storage.file_system         is self.file_system
        assert len(self.storage.path_handlers)  == 2
        assert self.storage.path_handlers[0]    is self.latest_handler
        assert self.storage.path_handlers[1]    is self.temporal_handler

    def test_save_string_data(self):                                                             # Tests saving string data
        saved_paths = self.storage.save(self.test_data, self.test_config)

        assert len(saved_paths)                      == 2
        assert Safe_Id("latest")                      in saved_paths
        assert Safe_Id("temporal")                    in saved_paths
        assert type(saved_paths[Safe_Id("latest")])   is Safe_Str__File__Path
        assert type(saved_paths[Safe_Id("temporal")]) is Safe_Str__File__Path

        # Verify metadata files were actually saved
        assert self.file_system.exists(saved_paths[Safe_Id("latest"  )]) is True
        assert self.file_system.exists(saved_paths[Safe_Id("temporal")]) is True

        # Verify content was saved
        loaded_file = self.file_system.load(saved_paths[Safe_Id("latest")])
        content_path = loaded_file.info.content.content_path
        assert self.file_system.exists_content(content_path) is True

        # Verify content can be loaded
        content_bytes = self.file_system.load_content(content_path)
        assert content_bytes == self.test_data.encode('utf-8')

    def test_save_bytes_data(self):                                                              # Tests saving bytes data
        bytes_data = b"binary content"
        saved_paths = self.storage.save(bytes_data, self.test_config)

        assert len(saved_paths) == 2

        loaded_file = self.file_system.load(saved_paths[Safe_Id("latest")])
        assert loaded_file.info.content.encoding.value is None  # BINARY encoding

        content_path = loaded_file.info.content.content_path
        loaded_content = self.file_system.load_content(content_path)
        assert loaded_content == bytes_data

    def test_save_with_content_type(self):                                                       # Tests saving with specific content type
        saved_paths = self.storage.save(
            self.test_data,
            self.test_config,
            Enum__Cloud_FS__File__Content_Type.MARKDOWN
        )

        loaded_file = self.file_system.load(saved_paths[Safe_Id("latest")])
        assert loaded_file.info.content_type == Enum__Cloud_FS__File__Content_Type.MARKDOWN

    def test_save_with_custom_paths(self):                                                       # Tests saving with custom paths in config
        custom_path = Safe_Str__File__Path("custom/location/file.json")
        config = Schema__Cloud_FS__File__Config(custom_paths = {Safe_Id("custom"): custom_path})

        saved_paths = self.storage.save(self.test_data, config)

        assert Safe_Id("custom") in saved_paths
        assert saved_paths[Safe_Id("custom")] == custom_path
        assert self.file_system.exists(custom_path) is True

    def test_load(self):                                                                         # Tests loading files
        saved_paths = self.storage.save(self.test_data, self.test_config)
        loaded_file = self.storage.load(self.test_config)

        assert type(loaded_file) is Schema__Cloud_FS__File
        assert loaded_file.info.content.size == len(self.test_data)
        assert loaded_file.metadata.content_hash == safe_str_hash(self.test_data)

    def test_load_content(self):                                                                 # Tests loading content
        self.storage.save(self.test_data, self.test_config)
        loaded_content = self.storage.load_content(self.test_config)

        assert loaded_content == self.test_data.encode('utf-8')

    def test_load_priority_order(self):                                                          # Tests loading respects handler priority
        # Disable temporal handler to test priority
        self.temporal_handler.enabled = False
        saved_paths = self.storage.save(self.test_data, self.test_config)

        # Re-enable and test load
        self.temporal_handler.enabled = True

        # Delete the higher priority file
        self.file_system.delete(saved_paths[Safe_Id("latest")])

        loaded_file = self.storage.load(self.test_config)
        assert loaded_file is None                                                               # No latest file exists

        # Now save with temporal enabled
        saved_paths = self.storage.save("new content", self.test_config)
        loaded_file = self.storage.load(self.test_config)

        assert loaded_file.info.content.size == len("new content")                              # Should load from highest priority

    def test_load_from_path(self):                                                              # Tests loading from specific path
        test_path = Safe_Str__File__Path("specific/path/file.json")
        saved_paths = self.storage.save(self.test_data, self.test_config)

        # Get a saved file
        file = self.file_system.load(saved_paths[Safe_Id("latest")])

        # Save it to specific path
        self.file_system.save(test_path, file)
        loaded = self.storage.load_from_path(test_path)

        assert loaded is file
        assert loaded.info.content.size == len(self.test_data)

    def test_exists(self):                                                                       # Tests checking file existence
        assert self.storage.exists(self.test_config) is False

        self.storage.save(self.test_data, self.test_config)

        assert self.storage.exists(self.test_config) is True

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

        # Test deleting non-existent files
        results = self.storage.delete(self.test_config)
        assert results[Safe_Id("latest")] is False
        assert results[Safe_Id("temporal")] is False

    def test_get_paths(self):                                                                    # Tests getting paths without saving
        paths = self.storage.get_paths(self.test_config)

        assert len(paths) == 2
        assert Safe_Id("latest") in paths
        assert Safe_Id("temporal") in paths
        assert type(paths[Safe_Id("latest")]) is Safe_Str__File__Path
        assert type(paths[Safe_Id("temporal")]) is Safe_Str__File__Path

    def test_list_files(self):                                                                   # Tests listing files
        config_1 = Schema__Cloud_FS__File__Config(areas = [Safe_Id("area1")])
        config_2 = Schema__Cloud_FS__File__Config(areas = [Safe_Id("area2")])

        self.storage.save("content1", config_1)
        self.storage.save("content2", config_2)

        all_files = self.storage.list_files()

        now       = datetime.now()
        time_path = now.strftime("%Y/%m/%d/%H")

        assert len(all_files) == 3                                                               # 2 configs x 2 handlers
        assert all_files == [ 'latest/file.json'           ,
                             f'{time_path}/area1/file.json',                                    # todo: review this behaviour since there is a blind spot here
                             f'{time_path}/area2/file.json']                                    #       caused by the fact that the latest value has been overwritten

    def test_add_path_handler(self):                                                            # Tests adding path handlers
        new_handler = Schema__Cloud_FS__Path__Handler(name = Safe_Id("versioned"))

        assert len(self.storage.path_handlers) == 2

        self.storage.add_path_handler(new_handler)

        assert len(self.storage.path_handlers) == 3
        assert self.storage.path_handlers[2] is new_handler

    def test_remove_path_handler(self):                                                         # Tests removing path handlers
        assert len(self.storage.path_handlers) == 2
        assert self.storage.remove_path_handler(Safe_Id("temporal")) is True
        assert len(self.storage.path_handlers) == 1
        assert self.storage.path_handlers[0].name == Safe_Id("latest")
        assert self.storage.remove_path_handler(Safe_Id("temporal")) is False                   # Already removed

    def test_clear(self):                                                                        # Tests clearing storage
        self.storage.save("content1", self.test_config)
        self.storage.save("content2", Schema__Cloud_FS__File__Config())

        assert len(self.storage.list_files()) > 0
        assert len(self.file_system.content_data) > 0

        self.storage.clear()

        assert len(self.storage.list_files()) == 0
        assert len(self.file_system.content_data) == 0

    def test_stats(self):                                                                        # Tests storage statistics
        self.storage.save("short content", self.test_config)
        self.storage.save("much longer content", Schema__Cloud_FS__File__Config())

        stats = self.storage.stats()

        assert stats[Safe_Id("type")] == Safe_Id("memory")
        assert stats[Safe_Id("file_count"       )] == 3                                                # 2 saves x 2 handlers
        assert stats[Safe_Id("content_count"    )] == 3                                            # Same for content
        assert stats[Safe_Id("path_handlers"    )] == 2
        assert stats[Safe_Id("enabled_handlers" )] == 2

    def test_disabled_handler(self):                                                            # Tests disabled handlers are skipped
        self.temporal_handler.enabled = False

        saved_paths = self.storage.save(self.test_data, self.test_config)

        assert len(saved_paths) == 1
        assert Safe_Id("latest") in saved_paths
        assert Safe_Id("temporal") not in saved_paths

    def test_handler_path_generation(self):                                                     # Tests different handler path generation
        versioned_handler = Schema__Cloud_FS__Path__Handler(name = Safe_Id("versioned"))
        self.storage.add_path_handler(versioned_handler)

        config = Schema__Cloud_FS__File__Config(version = 2)
        saved_paths = self.storage.save(self.test_data, config)

        assert Safe_Id("versioned") in saved_paths
        assert "v2" in str(saved_paths[Safe_Id("versioned")])

    def test_save_non_string_data(self):                                                        # Tests saving non-string data
        data_dict = {"key": "value", "number": 42}
        saved_paths = self.storage.save(data_dict, self.test_config)

        loaded_file = self.storage.load(self.test_config)
        loaded_content = self.storage.load_content(self.test_config)

        # Content should be string representation of dict encoded as UTF-8
        assert loaded_content.decode('utf-8') == str(data_dict)
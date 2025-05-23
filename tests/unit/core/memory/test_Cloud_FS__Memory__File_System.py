from unittest                                                   import TestCase

from osbot_utils.type_safe.Type_Safe__Dict import Type_Safe__Dict

from osbot_utils.helpers.Safe_Id                                import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path          import Safe_Str__File__Path
from osbot_utils.helpers.safe_str.Safe_Str__Hash                import safe_str_hash
from osbot_cloud_fs.core.memory.Cloud_FS__Memory__File_System   import Cloud_FS__Memory__File_System
from osbot_cloud_fs.core.schemas.Cloud_FS__File                 import Cloud_FS__File
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Config         import Cloud_FS__File__Config
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Content        import Cloud_FS__File__Content
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Content_Type   import Cloud_FS__File__Content_Type
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Metadata       import Cloud_FS__File__Metadata


class test_Cloud_FS__Memory__File_System(TestCase):

    def setUp(self):                                                                             # Initialize test data
        self.file_system   = Cloud_FS__Memory__File_System()
        self.test_path     = Safe_Str__File__Path("test/folder/file.json")
        self.test_content  = Cloud_FS__File__Content(content="test content")
        self.test_config   = Cloud_FS__File__Config()
        self.test_metadata = Cloud_FS__File__Metadata(paths         = {Safe_Id("test"): self.test_path},
                                                      content_hash  = safe_str_hash("test content")     )
        self.test_file     = Cloud_FS__File(config        = self.test_config                  ,
                                             content      = self.test_content                 ,
                                             content_type = Cloud_FS__File__Content_Type.JSON ,
                                             metadata     = self.test_metadata                )

    def test_init(self):                                                                         # Tests basic initialization
        assert type(self.file_system)        is Cloud_FS__Memory__File_System
        assert type(self.file_system.files)  is Type_Safe__Dict
        assert len(self.file_system.files)   == 0

    def test_save_and_exists(self):                                                             # Tests saving files and checking existence
        assert self.file_system.exists(self.test_path)               is False
        assert self.file_system.save(self.test_path, self.test_file) is True
        assert self.file_system.exists(self.test_path)               is True

    def test_load(self):                                                                         # Tests loading files
        assert self.file_system.load(self.test_path)                is None

        self.file_system.save(self.test_path, self.test_file)
        loaded_file = self.file_system.load(self.test_path)

        assert loaded_file                    is self.test_file
        assert loaded_file.content.content    == "test content"
        assert loaded_file.metadata.content_hash == safe_str_hash("test content")

    def test_delete(self):                                                                       # Tests deleting files
        self.file_system.save(self.test_path, self.test_file)

        assert self.file_system.delete(self.test_path)               is True
        assert self.file_system.exists(self.test_path)               is False
        assert self.file_system.delete(self.test_path)               is False                    # Delete non-existent file

    def test_list_files(self):                                                                   # Tests listing files
        path_1 = Safe_Str__File__Path("folder1/file1.json")
        path_2 = Safe_Str__File__Path("folder1/file2.json")
        path_3 = Safe_Str__File__Path("folder2/file3.json")

        self.file_system.save(path_1, self.test_file)
        self.file_system.save(path_2, self.test_file)
        self.file_system.save(path_3, self.test_file)

        all_files    = self.file_system.list_files()
        folder1_files = self.file_system.list_files(Safe_Str__File__Path("folder1"))

        assert len(all_files)     == 3
        assert path_1             in all_files
        assert path_2             in all_files
        assert path_3             in all_files
        assert len(folder1_files) == 2
        assert path_1             in folder1_files
        assert path_2             in folder1_files
        assert path_3         not in folder1_files

    def test_get_file_info(self):                                                                # Tests getting file information
        assert self.file_system.get_file_info(self.test_path) is None

        self.file_system.save(self.test_path, self.test_file)
        info = self.file_system.get_file_info(self.test_path)

        assert info[Safe_Id("exists")]       is True
        assert info[Safe_Id("size")]         == len("test content")
        assert info[Safe_Id("content_hash")] == safe_str_hash("test content")
        assert info[Safe_Id("timestamp")]    == self.test_metadata.timestamp
        assert info[Safe_Id("content_type")] == "application/json; charset=utf-8"
        assert info[Safe_Id("paths")]        == {Safe_Id("test"): self.test_path}

    def test_move(self):                                                                         # Tests moving files
        source_path = Safe_Str__File__Path("source/file.json")
        dest_path   = Safe_Str__File__Path("destination/file.json")

        self.file_system.save(source_path, self.test_file)

        assert self.file_system.move(source_path, dest_path)    is True
        assert self.file_system.exists(source_path)             is False
        assert self.file_system.exists(dest_path)               is True
        assert self.file_system.load(dest_path)                 is self.test_file

        assert self.file_system.move(source_path, dest_path)    is False                        # Move non-existent file

    def test_copy(self):                                                                         # Tests copying files
        source_path = Safe_Str__File__Path("source/file.json")
        dest_path   = Safe_Str__File__Path("destination/file.json")

        self.file_system.save(source_path, self.test_file)

        assert self.file_system.copy(source_path, dest_path)    is True
        assert self.file_system.exists(source_path)             is True
        assert self.file_system.exists(dest_path)               is True
        assert self.file_system.load(source_path)               is self.test_file
        assert self.file_system.load(dest_path)                 is self.test_file

        assert self.file_system.copy(Safe_Str__File__Path("missing"), dest_path) is False       # Copy non-existent file

    def test_clear(self):                                                                        # Tests clearing all files and directories
        self.file_system.save(Safe_Str__File__Path("file1.json"), self.test_file)
        self.file_system.save(Safe_Str__File__Path("file2.json"), self.test_file)

        assert len(self.file_system.files)       > 0

        self.file_system.clear()

        assert len(self.file_system.files)       == 0

    def test_stats(self):                                                                        # Tests file system statistics
        content_1 = Cloud_FS__File__Content(content="short")
        content_2 = Cloud_FS__File__Content(content="much longer content")
        file_1    = Cloud_FS__File(config       = self.test_config  ,
                                   content      = content_1         ,
                                   content_type = Cloud_FS__File__Content_Type.TXT,
                                   metadata     = self.test_metadata)
        file_2    = Cloud_FS__File(config       = self.test_config  ,
                                   content      = content_2         ,
                                   content_type = Cloud_FS__File__Content_Type.TXT,
                                   metadata     = self.test_metadata)

        self.file_system.save(Safe_Str__File__Path("dir1/file1.txt"), file_1)
        self.file_system.save(Safe_Str__File__Path("dir2/file2.txt"), file_2)

        stats = self.file_system.stats()

        assert stats[Safe_Id("type")]            == Safe_Id("memory")
        assert stats[Safe_Id("file_count")]      == 2
        assert stats[Safe_Id("total_size")]      == len("short") + len("much longer content")
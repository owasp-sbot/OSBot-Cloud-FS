from typing                                                         import Dict, List, Optional, Any
from osbot_utils.helpers.Safe_Id                                    import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path              import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_cloud_fs.core.schemas.Cloud_FS__File                     import Cloud_FS__File


class Cloud_FS__Memory__File_System(Type_Safe):                                                # In-memory file system that maintains directory structure and file storage
    files        : Dict[Safe_Str__File__Path, Cloud_FS__File]                                  # Path -> File metadata mapping
    content_data : Dict[Safe_Str__File__Path, bytes]                                           # Path -> Raw content mapping

    def exists(self, path : Safe_Str__File__Path                                               # Check if a file exists at the given path
                ) -> bool:
        return path in self.files

    def exists_content(self, path : Safe_Str__File__Path                                       # Check if content exists at the given path
                        ) -> bool:
        return path in self.content_data

    def save(self, path : Safe_Str__File__Path ,                                               # Save a file metadata at the given path
                   file : Cloud_FS__File
              ) -> bool:
        self.files[path] = file                                                                # Store the file metadata
        return True

    def save_content(self, path    : Safe_Str__File__Path ,                                    # Save raw content at the given path
                           content : bytes
                      ) -> bool:
        self.content_data[path] = content                                                       # Store the raw content
        return True

    def load(self, path : Safe_Str__File__Path                                                 # Load a file metadata from the given path
              ) -> Optional[Cloud_FS__File]:
        return self.files.get(path)

    def load_content(self, path : Safe_Str__File__Path                                         # Load raw content from the given path
                      ) -> Optional[bytes]:
        return self.content_data.get(path)

    def delete(self, path : Safe_Str__File__Path                                               # Delete a file at the given path
                ) -> bool:
        if path in self.files:
            del self.files[path]
            return True
        return False

    def delete_content(self, path : Safe_Str__File__Path                                       # Delete content at the given path
                        ) -> bool:
        if path in self.content_data:
            del self.content_data[path]
            return True
        return False

    def list_files(self, prefix : Safe_Str__File__Path = None                                  # List all files, optionally filtered by prefix
                    ) -> List[Safe_Str__File__Path]:
        if prefix is None:
            return list(self.files.keys())

        prefix_str = str(prefix)
        if not prefix_str.endswith('/'):
            prefix_str += '/'

        return [path for path in self.files.keys()
                if str(path).startswith(prefix_str)]

    def get_file_info(self, path : Safe_Str__File__Path                                        # Get file information (size, hash, etc.)
                       ) -> Optional[Dict[Safe_Id, Any]]:
        file = self.files.get(path)
        if not file:
            return None

        content_size = 0
        if file.info and file.info.content:
            content_size = int(file.info.content.size)                                         # Get size from metadata

        return {Safe_Id("exists")       : True                                               ,
                Safe_Id("size")         : content_size                                       ,
                Safe_Id("content_hash") : file.metadata.content_hash                         ,
                Safe_Id("timestamp")    : file.metadata.timestamp                            ,
                Safe_Id("content_type") : str(file.info.content_type.value) if file.info else None,
                Safe_Id("paths")        : file.metadata.paths                                }

    def move(self, source      : Safe_Str__File__Path ,                                        # Move a file from source to destination
                   destination : Safe_Str__File__Path
              ) -> bool:
        if source not in self.files:
            return False

        file = self.files[source]
        self.save(destination, file)
        self.delete(source)

        # Also move content if it exists
        if source in self.content_data:
            self.save_content(destination, self.content_data[source])
            self.delete_content(source)

        return True

    def copy(self, source      : Safe_Str__File__Path ,                                        # Copy a file from source to destination
                   destination : Safe_Str__File__Path
              ) -> bool:
        if source not in self.files:
            return False

        file = self.files[source]
        self.save(destination, file)

        # Also copy content if it exists
        if source in self.content_data:
            self.save_content(destination, self.content_data[source])

        return True

    def clear(self) -> None:                                                                    # Clear all files and directories
        self.files.clear()
        self.content_data.clear()

    def stats(self) -> Dict[Safe_Id, Any]:                                                     # Get file system statistics
        total_size = 0
        for path, content in self.content_data.items():
            total_size += len(content)

        return {Safe_Id("type")            : Safe_Id("memory")       ,
                Safe_Id("file_count")      : len(self.files)        ,
                Safe_Id("content_count")   : len(self.content_data) ,
                Safe_Id("total_size")      : total_size             }
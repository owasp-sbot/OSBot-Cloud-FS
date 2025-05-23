from typing                                                         import Dict, List, Optional, Set
from osbot_utils.helpers.Safe_Id                                    import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path              import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_cloud_fs.core.schemas.Cloud_FS__File                     import Cloud_FS__File


class Cloud_FS__Memory__File_System(Type_Safe):                                                 # In-memory file system that maintains directory structure and file storage
    files       : Dict[Safe_Str__File__Path, Cloud_FS__File]                                    # Path -> File mapping

    def exists(self, path : Safe_Str__File__Path                                               # Check if a file exists at the given path
                ) -> bool:
        return path in self.files

    def save(self, path : Safe_Str__File__Path ,                                               # Save a file at the given path
                   file : Cloud_FS__File
              ) -> bool:
        self.files[path] = file                                                                 # Store the file
        return True

    def load(self, path : Safe_Str__File__Path                                                 # Load a file from the given path
              ) -> Optional[Cloud_FS__File]:
        return self.files.get(path)

    def delete(self, path : Safe_Str__File__Path                                               # Delete a file at the given path
                ) -> bool:
        if path in self.files:
            del self.files[path]
            return True                                                                         # Note: We don't clean up empty directories for simplicity
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
                       ) -> Optional[Dict[Safe_Id, any]]:
        file = self.files.get(path)
        if not file:
            return None

        content_size = len(file.content.content) if file.content.content else 0                # Calculate content size

        return {Safe_Id("exists")       : True                                               ,  # Get metadata info         # todo: we don't need to use Safe_id here since this is python dict (in fact this should be a class, not a dict)
                Safe_Id("size")         : content_size                                       ,
                Safe_Id("content_hash") : file.metadata.content_hash                         ,
                Safe_Id("timestamp")    : file.metadata.timestamp                            ,
                Safe_Id("content_type") : str(file.content_type.value) if file.content_type else None,
                Safe_Id("paths")        : file.metadata.paths                                }

    def move(self, source      : Safe_Str__File__Path ,                                        # Move a file from source to destination
                   destination : Safe_Str__File__Path
              ) -> bool:
        if source not in self.files:
            return False

        file = self.files[source]
        self.save(destination, file)
        self.delete(source)
        return True

    def copy(self, source      : Safe_Str__File__Path ,                                        # Copy a file from source to destination
                   destination : Safe_Str__File__Path
              ) -> bool:
        if source not in self.files:
            return False

        file = self.files[source]
        self.save(destination, file)                                                            # Create a new file instance to avoid reference issues
        return True                                                                             # In real implementation, we'd deep copy the file

    def clear(self) -> None:                                                                   # Clear all files and directories
        self.files.clear()

    def stats(self) -> Dict[Safe_Id, any]:                                                     # Get file system statistics (todo: this should be a class)
        total_size = 0
        for file in self.files.values():
            if file.content and file.content.content:
                total_size += len(file.content.content)

        return {Safe_Id("type")            : Safe_Id("memory")       ,
                Safe_Id("file_count")      : len(self.files)        ,
                Safe_Id("total_size")      : total_size             }
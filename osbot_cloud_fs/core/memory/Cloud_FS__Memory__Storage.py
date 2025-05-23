from typing                                                    import Dict, List, Optional, Any
from osbot_utils.helpers.Safe_Id                               import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path         import Safe_Str__File__Path
from osbot_utils.helpers.safe_str.Safe_Str__Hash               import Safe_Str__Hash, safe_str_hash
from osbot_utils.type_safe.Type_Safe                           import Type_Safe
from osbot_cloud_fs.core.memory.Cloud_FS__Memory__File_System  import Cloud_FS__Memory__File_System
from osbot_cloud_fs.core.schemas.Cloud_FS__File                import Cloud_FS__File
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Config        import Cloud_FS__File__Config
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Content       import Cloud_FS__File__Content
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Metadata      import Cloud_FS__File__Metadata
from osbot_cloud_fs.core.schemas.Cloud_FS__Path__Handler       import Cloud_FS__Path__Handler


class Cloud_FS__Memory__Storage(Type_Safe):                                                      # Storage implementation that coordinates file operations with path handlers

    file_system   : Cloud_FS__Memory__File_System
    path_handlers : List[Cloud_FS__Path__Handler]

    def save(self, file_data    : Any                          ,                                 # Save file data using all configured path handlers
                   file_config  : Cloud_FS__File__Config       ,
                   content_type : Any                    = None
              ) -> Dict[Safe_Id, Safe_Str__File__Path]:

        if isinstance(file_data, str):                                                           # Create file content
            content = Cloud_FS__File__Content(content=file_data)
        elif isinstance(file_data, Cloud_FS__File__Content):
            content = file_data
        else:                                                                                    # For now, convert to string - in real implementation handle bytes
            content = Cloud_FS__File__Content(content=str(file_data))

        content_hash = safe_str_hash(content.content)                                           # Calculate content hash
        paths        = self._generate_paths(file_config)                                        # Generate paths from all handlers

        metadata = Cloud_FS__File__Metadata(paths        = paths       ,                      # Create metadata
                                            content_hash = content_hash,
                                            config       = file_config )

        file = Cloud_FS__File(config       = file_config  ,                                     # Create the complete file
                              content      = content      ,
                              content_type = content_type ,
                              metadata     = metadata     )

        saved_paths = {}                                                                         # Save to all paths
        for handler_name, path in paths.items():
            if self.file_system.save(path, file):
                saved_paths[handler_name] = path

        return saved_paths

    def load(self, file_config : Cloud_FS__File__Config                                         # Load file from the first available path
              ) -> Optional[Cloud_FS__File]:
        paths = self._generate_paths(file_config)

        for handler in sorted(self.path_handlers, key=lambda h: h.priority, reverse=True):      # Try each path in handler priority order
            if handler.enabled and handler.name in paths:
                path = paths[handler.name]
                file = self.file_system.load(path)
                if file:
                    return file

        return None

    def load_from_path(self, path : Safe_Str__File__Path                                        # Load file from a specific path
                        ) -> Optional[Cloud_FS__File]:
        return self.file_system.load(path)

    def exists(self, file_config : Cloud_FS__File__Config                                       # Check if file exists in any configured path
                ) -> bool:
        paths = self._generate_paths(file_config)

        for path in paths.values():
            if self.file_system.exists(path):
                return True

        return False

    def delete(self, file_config : Cloud_FS__File__Config                                       # Delete file from all configured paths
                ) -> Dict[Safe_Id, bool]:
        paths   = self._generate_paths(file_config)
        results = {}

        for handler_name, path in paths.items():
            results[handler_name] = self.file_system.delete(path)

        return results

    def get_paths(self, file_config : Cloud_FS__File__Config                                    # Get all paths where this file would be stored
                   ) -> Dict[Safe_Id, Safe_Str__File__Path]:
        return self._generate_paths(file_config)

    def list_files(self, prefix : Safe_Str__File__Path = None                                   # List all files in storage
                    ) -> List[Safe_Str__File__Path]:
        return self.file_system.list_files(prefix)

    def _generate_paths(self, file_config : Cloud_FS__File__Config                              # Generate paths from all enabled handlers
                         ) -> Dict[Safe_Id, Safe_Str__File__Path]:
        paths = {}

        for handler in self.path_handlers:
            if handler.enabled:                                                                  # In real implementation, handlers would have a generate_path method
                path = self._simulate_handler_path(handler, file_config)                        # For now, we'll simulate basic path generation
                if path:
                    paths[handler.name] = path

        if file_config.custom_paths:                                                            # Add any custom paths from config
            paths.update(file_config.custom_paths)

        return paths

    def _simulate_handler_path(self, handler : Cloud_FS__Path__Handler ,                        # Simulate path generation for different handler types
                                     config  : Cloud_FS__File__Config
                                ) -> Optional[Safe_Str__File__Path]:                            # This is a placeholder - in real implementation, each handler would have its own logic

        if handler.name == Safe_Id("latest"):                                                   # Latest handler: /latest/file_id.ext
            return Safe_Str__File__Path("latest/file.json")

        elif handler.name == Safe_Id("temporal"):                                               # Temporal handler: /YYYY/MM/DD/HH/areas/file_id.ext
            from datetime import datetime
            now        = datetime.now()
            time_path  = now.strftime("%Y/%m/%d/%H")
            areas_path = "/".join(str(area) for area in config.areas) if config.areas else ""
            full_path  = f"{time_path}/{areas_path}/file.json" if areas_path else f"{time_path}/file.json"
            return Safe_Str__File__Path(full_path)

        elif handler.name == Safe_Id("versioned"):                                              # Versioned handler: /v{version}/file_id.ext
            return Safe_Str__File__Path(f"v{config.version}/file.json")

        return None

    def add_path_handler(self, handler : Cloud_FS__Path__Handler                                # Add a new path handler
                          ) -> None:
        self.path_handlers.append(handler)

    def remove_path_handler(self, handler_name : Safe_Id                                        # Remove a path handler by name
                             ) -> bool:
        initial_count        = len(self.path_handlers)
        self.path_handlers   = [h for h in self.path_handlers if h.name != handler_name]
        return len(self.path_handlers) < initial_count

    def clear(self) -> None:                                                                    # Clear all stored files
        self.file_system.clear()

    def stats(self) -> Dict[Safe_Id, Any]:                                                      # Get storage statistics
        fs_stats = self.file_system.stats()

        fs_stats[Safe_Id("path_handlers")]    = len(self.path_handlers)                         # Add storage-specific stats
        fs_stats[Safe_Id("enabled_handlers")] = len([h for h in self.path_handlers if h.enabled])

        return fs_stats
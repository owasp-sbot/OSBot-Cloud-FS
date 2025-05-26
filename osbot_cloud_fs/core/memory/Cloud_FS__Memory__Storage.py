from typing                                                             import Dict, List, Optional, Any
from osbot_utils.helpers.Safe_Id                                        import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path                  import Safe_Str__File__Path
from osbot_utils.helpers.safe_str.Safe_Str__Hash                        import safe_str_hash
from osbot_utils.helpers.safe_str.Safe_Str__File__Name                  import Safe_Str__File__Name
from osbot_utils.helpers.safe_int.Safe_UInt__FileSize                   import Safe_UInt__FileSize
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_cloud_fs.core.memory.Cloud_FS__Memory__File_System           import Cloud_FS__Memory__File_System
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File                 import Schema__Cloud_FS__File
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Config         import Schema__Cloud_FS__File__Config
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Content        import Schema__Cloud_FS__File__Content
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Content_Type     import Enum__Cloud_FS__File__Content_Type
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Encoding         import Enum__Cloud_FS__File__Encoding
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Info           import Schema__Cloud_FS__File__Info
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Metadata       import Schema__Cloud_FS__File__Metadata
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__Path__Handler        import Schema__Cloud_FS__Path__Handler


class Cloud_FS__Memory__Storage(Type_Safe):                                                      # Storage implementation that coordinates file operations with path handlers

    file_system   : Cloud_FS__Memory__File_System
    path_handlers : List[Schema__Cloud_FS__Path__Handler]

    def save(self, file_data    : Any,  # Save file data using all configured path handlers
             file_config  : Schema__Cloud_FS__File__Config,
             content_type : Enum__Cloud_FS__File__Content_Type = None
             ) -> Dict[Safe_Id, Safe_Str__File__Path]:

        # Convert data to bytes
        if isinstance(file_data, str):
            content_bytes = file_data.encode('utf-8')
            encoding = Enum__Cloud_FS__File__Encoding.UTF_8
        elif isinstance(file_data, bytes):
            content_bytes = file_data
            encoding = Enum__Cloud_FS__File__Encoding.BINARY
        else:
            # For now, convert to string then bytes
            content_bytes = str(file_data).encode('utf-8')
            encoding = Enum__Cloud_FS__File__Encoding.UTF_8

        # Calculate content hash and size
        content_hash = safe_str_hash(content_bytes.decode('utf-8') if encoding != Enum__Cloud_FS__File__Encoding.BINARY else str(content_bytes))
        content_size = Safe_UInt__FileSize(len(content_bytes))

        # Determine content type if not provided
        if content_type is None:
            content_type = Enum__Cloud_FS__File__Content_Type.JSON

        # Generate all paths for metadata and content
        metadata_paths = self._generate_paths(file_config, is_metadata=True)
        content_paths  = self._generate_paths(file_config, is_metadata=False)

        # Extract file info from the path
        sample_path = list(metadata_paths.values())[0] if metadata_paths else Safe_Str__File__Path("file.json")
        file_name = Safe_Str__File__Name(sample_path.split('/')[-1])
        file_ext = Safe_Id(file_name.split('.')[-1] if '.' in file_name else '')

        # Create file content reference
        file_content = Schema__Cloud_FS__File__Content(
            size         = content_size,
            encoding     = encoding,
            content_path = list(content_paths.values())[0] if content_paths else Safe_Str__File__Path("")
        )

        # Create file info
        file_info = Schema__Cloud_FS__File__Info(
            file_name    = file_name,
            file_ext     = file_ext,
            content_type = content_type,
            content      = file_content
        )

        # Create metadata
        metadata = Schema__Cloud_FS__File__Metadata(
            paths         = metadata_paths,
            content_paths = content_paths,
            content_hash  = content_hash,
            config        = file_config
        )

        # Create the complete file
        file = Schema__Cloud_FS__File(
            config   = file_config,
            info     = file_info,
            metadata = metadata
        )

        saved_paths = {}

        # Save metadata files
        for handler_name, path in metadata_paths.items():
            if self.file_system.save(path, file):
                saved_paths[handler_name] = path

        # Save content files
        for handler_name, path in content_paths.items():
            if self.file_system.save_content(path, content_bytes):
                # Content saved successfully
                pass

        return saved_paths

    def load(self, file_config : Schema__Cloud_FS__File__Config  # Load file from the first available path
             ) -> Optional[Schema__Cloud_FS__File]:
        paths = self._generate_paths(file_config, is_metadata=True)

        # Try each path in handler priority order
        for handler in sorted(self.path_handlers, key=lambda h: h.priority, reverse=True):
            if handler.enabled and handler.name in paths:
                path = paths[handler.name]
                file = self.file_system.load(path)
                if file:
                    return file

        return None

    def load_content(self, file_config : Schema__Cloud_FS__File__Config  # Load content for a file
                     ) -> Optional[bytes]:
        # First load the metadata to get content path
        file = self.load(file_config)
        if not file:
            return None

        # Get the content path from metadata
        if file.metadata.content_paths:
            # Try to load from the first available content path
            for content_path in file.metadata.content_paths.values():
                content = self.file_system.load_content(content_path)
                if content:
                    return content

        return None

    def load_from_path(self, path : Safe_Str__File__Path                                        # Load file from a specific path
                        ) -> Optional[Schema__Cloud_FS__File]:
        return self.file_system.load(path)

    def exists(self, file_config : Schema__Cloud_FS__File__Config  # Check if file exists in any configured path
               ) -> bool:
        paths = self._generate_paths(file_config, is_metadata=True)

        for path in paths.values():
            if self.file_system.exists(path):
                return True

        return False

    def delete(self, file_config : Schema__Cloud_FS__File__Config  # Delete file from all configured paths
               ) -> Dict[Safe_Id, bool]:
        metadata_paths = self._generate_paths(file_config, is_metadata=True)
        content_paths = self._generate_paths(file_config, is_metadata=False)
        results = {}

        # Delete metadata files
        for handler_name, path in metadata_paths.items():
            results[handler_name] = self.file_system.delete(path)

        # Delete content files
        for handler_name, path in content_paths.items():
            self.file_system.delete_content(path)

        return results

    def get_paths(self, file_config : Schema__Cloud_FS__File__Config  # Get all paths where this file would be stored
                  ) -> Dict[Safe_Id, Safe_Str__File__Path]:
        return self._generate_paths(file_config, is_metadata=True)

    def list_files(self, prefix : Safe_Str__File__Path = None                                   # List all files in storage
                    ) -> List[Safe_Str__File__Path]:
        return self.file_system.list_files(prefix)

    def _generate_paths(self, file_config : Schema__Cloud_FS__File__Config,  # Generate paths from all enabled handlers
                        is_metadata : bool = True
                        ) -> Dict[Safe_Id, Safe_Str__File__Path]:
        paths = {}

        for handler in self.path_handlers:
            if handler.enabled:
                path = self._simulate_handler_path(handler, file_config, is_metadata)
                if path:
                    paths[handler.name] = path

        # Add any custom paths from config
        if is_metadata and file_config.custom_paths:
            paths.update(file_config.custom_paths)

        return paths

    def _simulate_handler_path(self, handler     : Schema__Cloud_FS__Path__Handler,  # Simulate path generation for different handler types
                               config      : Schema__Cloud_FS__File__Config,
                               is_metadata : bool = True
                               ) -> Optional[Safe_Str__File__Path]:

        # Determine file extension based on whether it's metadata or content
        ext = ".json" if is_metadata else ".html"  # Default to .html for content, but this should be dynamic

        if handler.name == Safe_Id("latest"):
            # Latest handler: /latest/file_id.ext
            base_path = "latest/file"
            return Safe_Str__File__Path(f"{base_path}{ext}")

        elif handler.name == Safe_Id("temporal"):
            # Temporal handler: /YYYY/MM/DD/HH/areas/file_id.ext
            from datetime import datetime
            now = datetime.now()
            time_path = now.strftime("%Y/%m/%d/%H")
            areas_path = "/".join(str(area) for area in config.areas) if config.areas else ""

            if areas_path:
                full_path = f"{time_path}/{areas_path}/file{ext}"
            else:
                full_path = f"{time_path}/file{ext}"

            return Safe_Str__File__Path(full_path)

        elif handler.name == Safe_Id("versioned"):
            # Versioned handler: /v{version}/file_id.ext
            return Safe_Str__File__Path(f"v{config.version}/file{ext}")

        return None

    def add_path_handler(self, handler : Schema__Cloud_FS__Path__Handler  # Add a new path handler
                         ) -> None:
        self.path_handlers.append(handler)

    def remove_path_handler(self, handler_name : Safe_Id                                        # Remove a path handler by name
                             ) -> bool:
        initial_count = len(self.path_handlers)
        self.path_handlers = [h for h in self.path_handlers if h.name != handler_name]
        return len(self.path_handlers) < initial_count

    def clear(self) -> None:                                                                    # Clear all stored files
        self.file_system.clear()

    def stats(self) -> Dict[Safe_Id, Any]:                                                      # Get storage statistics
        fs_stats = self.file_system.stats()

        # Add storage-specific stats
        fs_stats[Safe_Id("path_handlers")] = len(self.path_handlers)
        fs_stats[Safe_Id("enabled_handlers")] = len([h for h in self.path_handlers if h.enabled])

        return fs_stats
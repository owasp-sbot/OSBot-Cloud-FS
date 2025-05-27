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
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Info           import Schema__Cloud_FS__File__Info
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Metadata       import Schema__Cloud_FS__File__Metadata
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__Path__Handler        import Schema__Cloud_FS__Path__Handler
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Encoding         import Enum__Cloud_FS__File__Encoding
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__Serialization          import Enum__Cloud_FS__Serialization


class Cloud_FS__Memory__Storage(Type_Safe):                                                      # Storage implementation that coordinates file operations with path handlers
    file_system : Cloud_FS__Memory__File_System

    def list_files(self, prefix: Safe_Str__File__Path = None                                    # List all files in storage
                    ) -> List[Safe_Str__File__Path]:
        return self.file_system.list_files(prefix)

    def save(self, file_data   : Any,                                                           # Save file data using all configured path handlers
                   file_config : Schema__Cloud_FS__File__Config,
                   file_name   : str = "file"
              ) -> Dict[Safe_Id, Safe_Str__File__Path]:

        # Get file type from config
        file_type = file_config.file_type
        if not file_type:
            raise ValueError("file_config.file_type is required")

        # Convert data to bytes based on file type's serialization method
        content_bytes = self._serialize_data(file_data, file_type)

        # Calculate content hash and size
        if file_type.encoding == Enum__Cloud_FS__File__Encoding.BINARY:
            content_hash = safe_str_hash(str(content_bytes))
        else:
            content_hash = safe_str_hash(content_bytes.decode(file_type.encoding.value))

        content_size = Safe_UInt__FileSize(len(content_bytes))

        # Generate all paths for metadata and content using handlers from config
        metadata_paths = {}
        content_paths  = {}

        for handler in file_config.path_handlers:
            if handler.enabled:
                handler_name = handler.name
                # For now, simulate path generation - in real implementation,
                # handlers would have their own generate_path method
                metadata_path = self._simulate_handler_path(handler, file_name, file_type.file_extension, True)
                content_path  = self._simulate_handler_path(handler, file_name, file_type.file_extension, False)

                if metadata_path:
                    metadata_paths[handler_name] = metadata_path
                if content_path:
                    content_paths[handler_name] = content_path

        # Use first content path for the content reference
        first_content_path = list(content_paths.values())[0] if content_paths else Safe_Str__File__Path("")

        # Create file content reference
        file_content = Schema__Cloud_FS__File__Content(
            size         = content_size,
            encoding     = file_type.encoding,
            content_path = first_content_path
        )

        # Create file info
        file_info = Schema__Cloud_FS__File__Info(
            file_name    = Safe_Str__File__Name(f"{file_name}.{file_type.file_extension}"),
            file_ext     = file_type.file_extension,
            content_type = file_type.content_type,
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
            self.file_system.save_content(path, content_bytes)

        return saved_paths

    def load(self, file_config : Schema__Cloud_FS__File__Config                                 # Load file from the appropriate path based on config
              ) -> Optional[Schema__Cloud_FS__File]:

        if file_config.default_handler:
            # Load from default handler's path only
            path = self._get_handler_path(file_config, file_config.default_handler)
            if path:
                return self.file_system.load(path)
        else:
            # Try each handler in order until we find the file
            for handler in file_config.path_handlers:
                if handler.enabled:
                    path = self._get_handler_path(file_config, handler)
                    if path and self.file_system.exists(path):
                        file = self.file_system.load(path)
                        if file:
                            return file

        return None

    def load_content(self, file_config : Schema__Cloud_FS__File__Config                         # Load content for a file
                      ) -> Optional[bytes]:
        # First load the metadata to get content path
        file = self.load(file_config)
        if not file:
            return None

        # Get the content path from metadata
        if file.metadata.content_paths:
            # If there's a default handler, try its content path first
            if file_config.default_handler and file_config.default_handler.name in file.metadata.content_paths:
                content_path = file.metadata.content_paths[file_config.default_handler.name]
                content = self.file_system.load_content(content_path)
                if content:
                    return content

            # Otherwise try any available content path
            for content_path in file.metadata.content_paths.values():
                content = self.file_system.load_content(content_path)
                if content:
                    return content

        return None

    def load_data(self, file_config : Schema__Cloud_FS__File__Config                            # Load and deserialize file data
                   ) -> Optional[Any]:
        # Load raw content
        content_bytes = self.load_content(file_config)
        if not content_bytes:
            return None

        # Load metadata to get file type info
        file = self.load(file_config)
        if not file:
            return None

        # Deserialize based on file type
        return self._deserialize_data(content_bytes, file_config.file_type)

    def exists(self, file_config : Schema__Cloud_FS__File__Config                               # Check if file exists based on config strategy
                ) -> bool:

        if file_config.default_handler:
            # Check only the default handler's path
            path = self._get_handler_path(file_config, file_config.default_handler)
            return path is not None and self.file_system.exists(path)
        else:
            # Check ALL paths - file exists only if present in all configured paths
            for handler in file_config.path_handlers:
                if handler.enabled:
                    path = self._get_handler_path(file_config, handler)
                    if not path or not self.file_system.exists(path):
                        return False
            return len(file_config.path_handlers) > 0  # At least one handler must be configured

    def delete(self, file_config : Schema__Cloud_FS__File__Config                               # Delete file from all configured paths
                ) -> Dict[Safe_Id, bool]:
        results = {}

        # First, try to load the file to get all its paths
        file = self.load(file_config)

        if file and file.metadata.paths:
            # Delete using actual paths from metadata
            for handler_name, path in file.metadata.paths.items():
                results[handler_name] = self.file_system.delete(path)

            # Also delete content files
            if file.metadata.content_paths:
                for path in file.metadata.content_paths.values():
                    self.file_system.delete_content(path)
        else:
            # Fallback: try to delete from all configured handlers
            for handler in file_config.path_handlers:
                if handler.enabled:
                    # Generate expected paths and try to delete
                    # This is a simplified version - in reality, we'd need more info
                    results[handler.name] = False

        return results

    def _serialize_data(self, data: Any, file_type) -> bytes:                                   # Serialize data based on file type's serialization method
        serialization = file_type.serialization

        if serialization == Enum__Cloud_FS__Serialization.STRING:
            if isinstance(data, str):
                return data.encode(file_type.encoding.value)
            else:
                return str(data).encode(file_type.encoding.value)

        elif serialization == Enum__Cloud_FS__Serialization.JSON:
            import json
            json_str = json.dumps(data, indent=2)
            return json_str.encode(file_type.encoding.value)

        elif serialization == Enum__Cloud_FS__Serialization.BINARY:
            if isinstance(data, bytes):
                return data
            else:
                raise ValueError(f"Binary serialization expects bytes, got {type(data)}")

        elif serialization == Enum__Cloud_FS__Serialization.BASE64:
            import base64
            if isinstance(data, bytes):
                return base64.b64encode(data)
            else:
                return base64.b64encode(str(data).encode('utf-8'))

        elif serialization == Enum__Cloud_FS__Serialization.TYPE_SAFE:
            if hasattr(data, 'json'):
                json_str = data.json()
                return json_str.encode(file_type.encoding.value)
            else:
                raise ValueError(f"TYPE_SAFE serialization requires object with json() method, got {type(data)}")

        else:
            raise ValueError(f"Unknown serialization method: {serialization}")

    def _deserialize_data(self, content_bytes: bytes, file_type) -> Any:                        # Deserialize data based on file type's serialization method
        serialization = file_type.serialization

        if serialization == Enum__Cloud_FS__Serialization.STRING:
            return content_bytes.decode(file_type.encoding.value)

        elif serialization == Enum__Cloud_FS__Serialization.JSON:
            import json
            json_str = content_bytes.decode(file_type.encoding.value)
            return json.loads(json_str)

        elif serialization == Enum__Cloud_FS__Serialization.BINARY:
            return content_bytes

        elif serialization == Enum__Cloud_FS__Serialization.BASE64:
            import base64
            return base64.b64decode(content_bytes)

        elif serialization == Enum__Cloud_FS__Serialization.TYPE_SAFE:
            # This would need the actual Type_Safe class to deserialize
            # For now, return the JSON string
            return content_bytes.decode(file_type.encoding.value)

        else:
            raise ValueError(f"Unknown serialization method: {serialization}")

    def _get_handler_path(self, file_config : Schema__Cloud_FS__File__Config,                   # Get the path for a specific handler
                                handler     : Schema__Cloud_FS__Path__Handler,
                                file_name   : str = "file"
                         ) -> Optional[Safe_Str__File__Path]:
        # This is simplified - in reality, would need the actual file info
        # For now, generate a basic path
        file_ext = file_config.file_type.file_extension if file_config.file_type else "json"
        return self._simulate_handler_path(handler, file_name, file_ext, True)

    def _simulate_handler_path(self, handler     : Schema__Cloud_FS__Path__Handler,             # Simulate path generation for different handler types
                                    file_name   : str,
                                    file_ext    : str,
                                    is_metadata : bool = True
                               ) -> Optional[Safe_Str__File__Path]:

        # Determine file extension
        ext = ".json" if is_metadata else f".{file_ext}"

        if handler.name == Safe_Id("latest"):
            return Safe_Str__File__Path(f"latest/{file_name}{ext}")

        elif handler.name == Safe_Id("temporal"):
            from datetime import datetime
            now = datetime.now()
            time_path = now.strftime("%Y/%m/%d/%H")
            # In real implementation, areas would come from the handler
            return Safe_Str__File__Path(f"{time_path}/{file_name}{ext}")

        elif handler.name == Safe_Id("versioned"):
            # In real implementation, version would be calculated from chain
            version = 1
            return Safe_Str__File__Path(f"v{version}/{file_name}{ext}")

        elif handler.name == Safe_Id("custom"):
            # In real implementation, would use handler's custom path
            return Safe_Str__File__Path(f"custom/{file_name}{ext}")

        return None

    def clear(self) -> None:                                                                    # Clear all stored files
        self.file_system.clear()

    def stats(self) -> Dict[Safe_Id, Any]:                                                      # Get storage statistics
        return self.file_system.stats()
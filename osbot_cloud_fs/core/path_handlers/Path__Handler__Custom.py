from osbot_utils.helpers.Safe_Id                                 import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path           import Safe_Str__File__Path
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__Path__Handler import Schema__Cloud_FS__Path__Handler


class Path__Handler__Custom(Schema__Cloud_FS__Path__Handler):       # Handler that uses a custom path
    name        : Safe_Id               = Safe_Id("custom")
    custom_path : Safe_Str__File__Path

    def generate_path(self, file_name: str, file_ext: str, is_metadata: bool = True) -> Safe_Str__File__Path:
        # Return the custom path as-is
        return self.custom_path
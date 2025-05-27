from osbot_utils.helpers.Safe_Id                                 import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path           import Safe_Str__File__Path
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__Path__Handler import Schema__Cloud_FS__Path__Handler


class Path__Handler__Versioned(Schema__Cloud_FS__Path__Handler):    # Handler that stores files with version numbers (calculated from chain)
    name : Safe_Id = Safe_Id("versioned")

    def generate_path(self, file_name: str, file_ext: str, is_metadata: bool = True, version: int = 1) -> Safe_Str__File__Path:
        ext = ".json" if is_metadata else f".{file_ext}"
        return Safe_Str__File__Path(f"v{version}/{file_name}{ext}")

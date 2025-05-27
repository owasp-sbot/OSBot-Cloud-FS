from typing import List

from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Content_Type import Enum__Cloud_FS__File__Content_Type
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Encoding     import Enum__Cloud_FS__File__Encoding
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__Serialization      import Enum__Cloud_FS__Serialization
from osbot_utils.helpers.Safe_Id                                    import Safe_Id
from osbot_utils.type_safe.Type_Safe                                import Type_Safe


class Schema__Cloud_FS__File__Type(Type_Safe):
    name           : Safe_Id                             # Logical name: "json", "jpeg", "markdown"
    content_type   : Enum__Cloud_FS__File__Content_Type  # Validated HTTP content type
    file_extension : Safe_Id                             # Primary extension: "jpg", "md", "yml"
    encoding       : Enum__Cloud_FS__File__Encoding
    serialization  : Enum__Cloud_FS__Serialization
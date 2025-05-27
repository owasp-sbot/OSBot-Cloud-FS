from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Content_Type import Enum__Cloud_FS__File__Content_Type
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Encoding     import Enum__Cloud_FS__File__Encoding
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__Serialization      import Enum__Cloud_FS__Serialization
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Type       import Schema__Cloud_FS__File__Type
from osbot_utils.helpers.Safe_Id                                    import Safe_Id


class Cloud_FS__File__Type__Png(Schema__Cloud_FS__File__Type):
    name           = Safe_Id("png")
    content_type   = Enum__Cloud_FS__File__Content_Type.PNG
    file_extension = Safe_Id("png")
    encoding       = Enum__Cloud_FS__File__Encoding.BINARY
    serialization  = Enum__Cloud_FS__Serialization.BINARY
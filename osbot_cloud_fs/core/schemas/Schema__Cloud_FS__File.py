from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Info     import Schema__Cloud_FS__File__Info
from osbot_utils.type_safe.Type_Safe                              import Type_Safe
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Config   import Schema__Cloud_FS__File__Config
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Metadata import Schema__Cloud_FS__File__Metadata


class Schema__Cloud_FS__File(Type_Safe):
    config   : Schema__Cloud_FS__File__Config
    info     : Schema__Cloud_FS__File__Info
    metadata : Schema__Cloud_FS__File__Metadata
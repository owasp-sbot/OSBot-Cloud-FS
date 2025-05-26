from osbot_cloud_fs.core.schemas.Cloud_FS__File__Info         import Cloud_FS__File__Info
from osbot_utils.type_safe.Type_Safe                          import Type_Safe
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Config       import Cloud_FS__File__Config
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Metadata     import Cloud_FS__File__Metadata


class Cloud_FS__File(Type_Safe):
    config   : Cloud_FS__File__Config
    info     : Cloud_FS__File__Info
    metadata : Cloud_FS__File__Metadata
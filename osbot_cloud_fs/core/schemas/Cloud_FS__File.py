from osbot_utils.type_safe.Type_Safe                          import Type_Safe
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Config       import Cloud_FS__File__Config
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Content      import Cloud_FS__File__Content
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Content_Type import Cloud_FS__File__Content_Type
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Metadata     import Cloud_FS__File__Metadata


class Cloud_FS__File(Type_Safe):
    config      : Cloud_FS__File__Config
    content     : Cloud_FS__File__Content
    content_type: Cloud_FS__File__Content_Type               # todo: is this the best place to store this?
    metadata    : Cloud_FS__File__Metadata

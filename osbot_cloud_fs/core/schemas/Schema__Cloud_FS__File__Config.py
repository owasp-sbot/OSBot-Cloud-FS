from typing                                                      import List, Set, Type
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Type    import Schema__Cloud_FS__File__Type
from osbot_utils.helpers.Safe_Id                                 import Safe_Id
from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__Path__Handler import Schema__Cloud_FS__Path__Handler


class Schema__Cloud_FS__File__Config(Type_Safe):
    path_handlers   : List[Schema__Cloud_FS__Path__Handler]                                 # Which handlers to use to get the file paths to save the file
    default_handler : Schema__Cloud_FS__Path__Handler       = None                          # Which handler to use for loading and exists() calls
    file_type       : Schema__Cloud_FS__File__Type          = None
    tags            : Set[Safe_Id]
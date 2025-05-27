from unittest                                                   import TestCase
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Type   import Schema__Cloud_FS__File__Type
from osbot_utils.utils.Objects                                  import __, full_type_name
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Config import Schema__Cloud_FS__File__Config


class test_Schema__Cloud_FS__File__Config(TestCase):

    def test__init__(self):
        with Schema__Cloud_FS__File__Config() as _:
            assert type(_) is Schema__Cloud_FS__File__Config
            assert _.obj() ==__(default_handler = None ,
                                file_type       = None ,
                                path_handlers   = []   ,
                                tags            = []   )
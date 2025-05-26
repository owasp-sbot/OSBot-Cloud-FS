from unittest                                                    import TestCase
from osbot_utils.helpers.safe_str.Safe_Str__File__Path           import Safe_Str__File__Path
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Content import Schema__Cloud_FS__File__Content
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Encoding  import Enum__Cloud_FS__File__Encoding
from osbot_utils.helpers.safe_int.Safe_UInt__FileSize            import Safe_UInt__FileSize
from osbot_utils.utils.Objects                                   import __


class test_Cloud_FS__File__Content(TestCase):

    def test___init__(self):
        with Schema__Cloud_FS__File__Content() as _:
            assert type(_) == Schema__Cloud_FS__File__Content
            assert _.obj() == __(size=None, encoding=None, content_path=None)

        kwargs = dict(size         = 123        ,
                      encoding     = 'UTF_8'    ,
                      content_path = 'an/path'  )
        with Schema__Cloud_FS__File__Content(**kwargs) as _:
            assert _.obj() == __(size         = 123,
                                 encoding     = 'UTF_8',
                                 content_path = 'an/path')
            assert type(_.size        ) is Safe_UInt__FileSize
            assert type(_.encoding    ) is Enum__Cloud_FS__File__Encoding
            assert type(_.content_path) is Safe_Str__File__Path
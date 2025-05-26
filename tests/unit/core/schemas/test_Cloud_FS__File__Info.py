from unittest                                                       import TestCase
from osbot_utils.helpers.safe_str.Safe_Str__File__Path              import Safe_Str__File__Path
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Content    import Schema__Cloud_FS__File__Content
from osbot_cloud_fs.core.schemas.Enum__Cloud_FS__File__Content_Type import Enum__Cloud_FS__File__Content_Type
from osbot_utils.helpers.Safe_Id                                    import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Name              import Safe_Str__File__Name
from osbot_utils.utils.Objects                                      import __
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Info       import Schema__Cloud_FS__File__Info


class test_Cloud_FS__File__Info(TestCase):

    def test__init__(self):
        with Schema__Cloud_FS__File__Info() as _:
            assert type(_) is Schema__Cloud_FS__File__Info
            assert _.obj() == __(file_name    = None,
                                 file_ext     = None,
                                 content_type = None,
                                 content      =  __(size         = None ,
                                                    encoding     = None ,
                                                    content_path = None ))
        kwargs =  dict(file_name    = Safe_Str__File__Name("file.json"),
                       file_ext     = Safe_Id             ("json"     ),
                       content_type = Enum__Cloud_FS__File__Content_Type.JSON,
                       content      = Schema__Cloud_FS__File__Content(content_path='/abc'))
        with Schema__Cloud_FS__File__Info(**kwargs) as _:
            assert _.obj() == __(file_name    = Safe_Str__File__Name('file.json'),
                                 file_ext     = Safe_Id('json'),
                                 content_type = 'JSON',
                                 content      = __(size        = None,
                                                   encoding     = None,
                                                   content_path = Safe_Str__File__Path('/abc')))
            json_data = _.json()
            assert json_data == { 'content'     : { 'content_path': Safe_Str__File__Path('/abc'),
                                                    'encoding'    : None                        ,
                                                    'size'        : None                        },
                                  'content_type': 'JSON'                                         ,
                                  'file_ext'    : Safe_Id('json')                                ,
                                  'file_name'   : Safe_Str__File__Name('file.json')              }

            assert type(json_data.get('file_ext' )) is str
            assert type(json_data.get('file_name')) is str

            roundtrip = Schema__Cloud_FS__File__Info.from_json(json_data)
            assert roundtrip.json()            == json_data
            assert type(roundtrip.file_name   ) is Safe_Str__File__Name
            assert type(roundtrip.file_ext    ) is Safe_Id
            assert type(roundtrip.content_type) is Enum__Cloud_FS__File__Content_Type
            assert type(roundtrip.content     ) is Schema__Cloud_FS__File__Content





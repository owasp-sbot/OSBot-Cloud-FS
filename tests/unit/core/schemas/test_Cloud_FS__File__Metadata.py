import re
from unittest                                                       import TestCase
import pytest
from osbot_utils.type_safe.Type_Safe__Dict                          import Type_Safe__Dict
from osbot_utils.helpers.safe_str.Safe_Str__File__Path              import Safe_Str__File__Path
from osbot_utils.helpers.Safe_Id                                    import Safe_Id
from osbot_utils.utils.Objects                                      import __
from osbot_cloud_fs.core.schemas.Schema__Cloud_FS__File__Metadata   import Schema__Cloud_FS__File__Metadata


class test_Cloud_FS__File__Metadata(TestCase):

    def test__init__(self):
        with Schema__Cloud_FS__File__Metadata() as _:
            assert type(_) is Schema__Cloud_FS__File__Metadata
            assert _.obj() == __(content_hash          = None,
                                 chain_hash            = None,
                                 previous_version_path = None,
                                 paths                 = __(),
                                 content_paths         = __(),
                                 timestamp             = _.timestamp,
                                 file_id               = _.file_id,
                                 config                =__(version           = 1    ,
                                                           enable_versioning = True ,
                                                           enable_latest     = True ,
                                                           areas             = []   ,
                                                           custom_paths      = __() ,
                                                           tags              = []   ))

            kwargs = dict(paths = {"path_id":"an_path"})
            with Schema__Cloud_FS__File__Metadata(**kwargs) as _:
                assert _.paths                     != {        "path_id" :"an_path"         }                   # direct comparison doesn't work because paths is of type Dict[Safe_Id, Safe_Str__File__Path]
                assert _.paths                     != {Safe_Id("path_id"): Safe_Id("an_path")}                  # types don't match
                assert _.paths                     == {Safe_Id("path_id"): Safe_Str__File__Path("an_path")}
                assert type(_.paths)               is Type_Safe__Dict
                assert type(_.paths["path_id"])    is Safe_Str__File__Path
                assert _.paths['path_id']          == 'an_path'
                assert _.paths['path_id']          == Safe_Str__File__Path('an_path')
                assert _.paths['path_id']          != Safe_Id('an_path')
                assert _.paths[Safe_Id('path_id')] == 'an_path'
                assert _.paths[Safe_Id('path_id')] == Safe_Str__File__Path('an_path')
                expected_exception = "assert Safe_Str__File__Path('an_path') == Safe_Id('an_path')\n  \n    an_path"
                with pytest.raises(AssertionError) as excinfo:
                    assert _.paths[Safe_Id('path_id')] == Safe_Id('an_path')
                print("********")
                print(excinfo.value)
                print("********")
                assert str(excinfo.value) == expected_exception


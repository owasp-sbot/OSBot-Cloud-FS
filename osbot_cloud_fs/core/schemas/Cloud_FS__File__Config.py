from typing                                             import List, Dict, Set
from osbot_utils.helpers.Safe_Id                        import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class Cloud_FS__File__Config(Type_Safe):
    areas               : List[Safe_Id]                          # todo: see if we need to hard code this here (or this this should handled by a sub class)
    version             : int           = 1
    enable_versioning   : bool          = True
    enable_latest       : bool          = True                   # todo: see if we need to hard code this here (or this this should handled by a sub class)
    custom_paths        : Dict[Safe_Id, Safe_Str__File__Path]
    tags                : Set[Safe_Id]
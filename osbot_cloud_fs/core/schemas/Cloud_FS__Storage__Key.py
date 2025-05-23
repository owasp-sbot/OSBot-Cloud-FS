from typing                                             import Optional
from osbot_utils.helpers.Safe_Id                        import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class Cloud_FS__Storage__Key(Type_Safe):
    provider: Safe_Id  # "s3", "filesystem", "memory"           # todo: see if we need this
    bucket  : Optional[Safe_Id]                                 # todo: see if we need to hard code this here, since this is S3 specific
    prefix  : Optional[Safe_Str__File__Path]
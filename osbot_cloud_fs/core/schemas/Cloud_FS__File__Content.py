from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from osbot_cloud_fs.core.schemas.Cloud_FS__File__Content_Type   import Cloud_FS__File__Content_Type


class Cloud_FS__File__Content(Type_Safe):
    content     : str                               # this is the only place where we use a raw string (since it is the only one we can serialise)
                                                    # that said, it would also make sense for this be bytes, since that is the best way to store data with no transformations
                                                    #            and since this entire part of the code base works in memory (with no storage), we don't have here the problem that bytes don't serialise ok (i.e. the prob that we will have when calling Abc(Type_Safe).json()


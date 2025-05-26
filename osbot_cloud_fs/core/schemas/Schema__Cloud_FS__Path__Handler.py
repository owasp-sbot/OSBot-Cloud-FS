from osbot_utils.helpers.Safe_Id     import Safe_Id
from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Cloud_FS__Path__Handler(Type_Safe):
    name            : Safe_Id
    priority        : int = 0
    enabled         : bool = True
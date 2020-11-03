from enum import IntEnum

class Visibility(IntEnum):
    PUBLIC = 0
    REGISTERED = 1
    FRIEND_GROUP = 2
    GROUP = 3

class JoinPermission(IntEnum):
    PUBLIC = 0
    MODERATOR_APPROVE = 1

class GroupJoinRequestStatus(IntEnum):
    UNPROCESSED = 0
    APPROVED = 1
    DENIED = 2

def getListForForm(enumClass):
    return [(int(value), label) for label, value in enumClass.__members__.items()]
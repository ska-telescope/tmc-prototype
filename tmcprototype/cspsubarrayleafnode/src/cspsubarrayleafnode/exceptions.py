# Custom exception classes for AssignResources() command on CSP Subarray Node

class InvalidObsStateError(ValueError):
    """Raised when the device obs State does not allow to invoke the command as per SKA state model"""


''' This will be handled through CDM
class JsonKeyMissingError(KeyError):
    """Raised when a mandatory key in the input string is missing"""

    def __init__(self, message):
        self.msg = message


class JsonValueTypeMismatch(TypeError):
    """Raised when the key data type is different than that of value"""



class JsonValueMissing(ValueError):
    """Raised when the value is missing"""
'''

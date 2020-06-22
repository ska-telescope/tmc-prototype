# Custom exception classes for AssignResources() command on CSP Subarray Node

''' This will be handled through CDM
class InvalidJSONError(Exception):
    """Raised when a not listed exception occur with regards to json"""

    def __init__(self, message):
        self.msg = message
'''

class InvalidDeviceObsStateError(ValueError):
    """Raised when the obs State of Subarray Leaf Node is not ready"""

    def __init__(self, message):
        self.msg = message

''' This will be handled through CDM
class JsonKeyMissingError(KeyError):
    """Raised when a mandatory key in the input string is missing"""

    def __init__(self, message):
        self.msg = message


class JsonValueTypeMismatch(TypeError):
    """Raised when the key data type is different than that of value"""

    def __init__(self, message):
        self.msg = message


class JsonValueMissing(ValueError):
    """Raised when the value is missing"""

    def __init__(self, message):
        self.msg = message
'''

class ResourceAlreadyAssigned(Exception):
    """Raised when the resource is already assigned to csp subarray while attempting the assignment of
    resources to it """

    def __init__(self, message):
        self.msg = message


''' This will be handled through CDM
class JsonValueTooLong(OverflowError):
    """Raised when the entry in the value field is longer than character limit"""

    def __init__(self, message):
        self.msg = message


class JsonNotFound(OSError):
    """Raised when the JSON is not found"""

    def __init__(self, message):
        self.msg = message
'''

'''Not required
class ReceptorIDListFull(OverflowError):
    """Raised while attempting to enter receptor id in the receptor id list after it has reached
    character limit"""

    def __init__(self, message):
        self.msg = message
'''


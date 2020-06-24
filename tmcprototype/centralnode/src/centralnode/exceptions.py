from json import JSONDecodeError

class InvalidObsStateError(ValueError):
    """Raised when the device obsState does not allow to invoke the command as per SKA state model"""

class ResourceReassignmentError(Exception):
    """Raised when the resource is already assigned to another subarray"""
    def __init__(self, message, resources=None):
        # super.__init__()
        self.value = message
        self.resources_reallocation = []
        self.resources_reallocation = resources

class InvalidJSONError(JSONDecodeError):
    """Raised when The JSON format is invalid"""

class ResourceNotPresentError(ValueError):
    """Raised when a resource is requested but not present."""

class SubarrayNotPresentError(ValueError):
    """Raised when a subarray is requested but not present."""

# class JsonKeyMissingError(KeyError):
#     """Raised when a mandatory key in the input string is missing"""

# class JsonValueTypeMismatchError(TypeError):
#     """Raised when the key data type is different than that of value"""

# class JsonValueMissingError(ValueError):
#     """Raised when the key is missing"""

# class InvalidParameterValue(ValueError):
#     """Raised when there is a violation of business rule."""
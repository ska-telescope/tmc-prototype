from json import JSONDecodeError

class InvalidJSONError(JSONDecodeError):
    def __init__(self, message):
        self.msg = message

class JsonKeyMissingError(KeyError):
    """Raised when a mandatory key in the input string is missing"""

class JsonValueTypeMismatchError(TypeError):
    """Raised when the key data type is different than that of value"""

# class JsonValueMissingError(ValueError):
#     """Raised when the key is missing"""

class InvalidParameterValue(Exception):
    """Raised when there is a violation of business rule."""

    def __init__(self, message):
        self.msg = message
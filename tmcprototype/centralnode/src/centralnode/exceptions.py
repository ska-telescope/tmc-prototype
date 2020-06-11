class InvalidJSONError(Exception):
    def __init__(self, message):
        self.msg = message

class JsonKeyMissingError(KeyError):
    """Raised when a mandatory key in the input string is missing"""


class JsonValueTypeMismatch(TypeError):
    """Raised when the key data type is different than that of value"""

class JsonValueMissing(ValueError):
    """Raised when the key is missing"""

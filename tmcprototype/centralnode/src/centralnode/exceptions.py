'''
class InvalidJSONError(Exception):
    pass
'''


class JsonKeyMissing(KeyError):

    """Raised when the key is missing"""
    pass


class JsonValueTypeMismatch(TypeError):
    """Raised when the key data type is different than that of value"""
    pass


class JsonValueMissing(ValueError):
    """Raised when the key is missing"""
    pass

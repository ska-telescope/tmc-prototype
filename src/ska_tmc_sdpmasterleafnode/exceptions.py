from marshmallow import ValidationError

class InvalidJSONError(ValidationError):
    """Raised when The JSON format is invalid"""

class CommandNotAllowed(Exception):
    """Raised when a command is not allowed."""

from marshmallow import ValidationError

class InvalidObsStateError(ValueError):
    """Raised when subarray is not in required obsState."""

class InvalidJSONError(ValidationError):
    """Raised when The JSON format is invalid"""

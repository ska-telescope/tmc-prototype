from marshmallow import ValidationError

class InvalidObsStateError(ValueError):
    """Raised when the device obsState does not allow to invoke the command as per SKA state model"""

class ResourceReassignmentError(Exception):
    """Raised when the resource is already assigned to another subarray"""
    def __init__(self, message, resources=None):
        super(ResourceReassignmentError, self).__init__(message)
        self.value = message
        self.resources_reallocation = resources

class InvalidJSONError(ValidationError):
    """Raised when The JSON format is invalid"""

class ResourceNotPresentError(ValueError):
    """Raised when a resource is requested but not present."""

class SubarrayNotPresentError(ValueError):
    """Raised when a subarray is requested but not present."""
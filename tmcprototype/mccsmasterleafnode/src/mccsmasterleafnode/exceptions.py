# Custom exception classes for AssignResources() command on Mccs Master Leaf Node

class InvalidObsStateError(ValueError):
    """Raised when the obsState requirements for AssignResources command are not met."""




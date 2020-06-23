class InvalidObsStateError(ValueError):
    """Raised when subarray is not in required obsState."""

    def __init__(self, message):
        self.msg = message
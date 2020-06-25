class InvalidObsStateError(Exception):
    """Raised when there is a violation of business rule."""

    def __init__(self, message):
        self.msg = message
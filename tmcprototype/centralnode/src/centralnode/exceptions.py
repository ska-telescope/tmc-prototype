class InvalidJSONError(Exception):
    """ Raised when the JSON is not correct"""

    def __init__(self, message):
        self.message = message
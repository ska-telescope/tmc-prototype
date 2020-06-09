import json
from json import JSONDecodeError
from exceptions import InvalidJSONError
class AssignResourceValidator():
    """Class to validate the input string of AssignResources command of Central Node"""

    def validate(self, input_string):
        """
        Validates the input string received as an argument of AssignResources command.

        :param: input_string: A JSON string

        :return: True if input string is valid.

        :throws:
            InvalidJSONError: When the JSON string is not formatted properly.

            InvalidParameterValue: When a value of a JSON key is not valid. E.g. Receptor id
            not present.
        """
        try:
            input_json = json.loads(input_string)
            print(input_json)
        except JSONDecodeError as json_error:
            raise InvalidJSONError(json_error.msg)
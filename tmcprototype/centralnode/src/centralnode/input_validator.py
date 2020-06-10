import json
from json import JSONDecodeError
from centralnode.exceptions import InvalidJSONError
# from ska_logging import logger

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
        ret_val = False
        print("Entry")
        try:
            input_json = json.loads(input_string)
            print("JSON load ok.")
        except JSONDecodeError as json_error:
            raise InvalidJSONError(json_error.msg)

        print("Checking subarray id value type")
        subarray_id = input_json["subarrayID"]
        
        assert type(subarray_id) == int

        print("Checking subarray id value in range. Value:", subarray_id)
        if not 1<= subarray_id <= 3:
            print("Raising exception")
            raise InvalidJSONError("Invalid subarray id. Subarray ID must be between 1 and 3.")

        ret_val = True
        print("Success")
        
        # except AssertionError:
        #     raise InvalidJSONError("Invalid datatype of subarray id. \
        #         Subarray id must be an integer value between 1 and 3")

        return ret_val
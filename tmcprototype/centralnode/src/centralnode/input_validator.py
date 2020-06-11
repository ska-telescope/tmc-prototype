# -*- coding: utf-8 -*-
#
# This file is part of the centralnode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# standard Python imports
import json
from json import JSONDecodeError
# import logging

# SKA specific imports
from centralnode.exceptions import InvalidJSONError
# import ska.logging as ska_logging

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
        
        # Check if JSON is correct
        try:
            input_json = json.loads(input_string)
            print("JSON load ok.")
        except JSONDecodeError as json_error:
            raise InvalidJSONError(json_error.msg)

        # Check subarray ID
        print("Checking subarray id value type")
        try:
            subarray_id = input_json["subarrayID"]
        except KeyError as ke:
            print(ke)
        
        assert type(subarray_id) == int

        print("Checking subarray id value in range. Value:", subarray_id)
        if not 1<= subarray_id <= 3:
            print("Raising exception")
            raise InvalidJSONError("Invalid subarray id. Subarray ID must be between 1 and 3.")

        # Check receptorIDList


        ret_val = True
        print("Success")
        
        # except AssertionError:
        #     raise InvalidJSONError("Invalid datatype of subarray id. \
        #         Subarray id must be an integer value between 1 and 3")

        return ret_val
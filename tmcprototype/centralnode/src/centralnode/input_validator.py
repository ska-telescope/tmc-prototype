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
from centralnode.exceptions import InvalidJSONError, JsonKeyMissingError, JsonValueTypeMismatchError
from centralnode.exceptions import InvalidParameterValue
# import ska.logging as ska_logging

# logger = ska_logging()
# logger.configure_logging(INFO)

class AssignResourceValidator():
    """Class to validate the input string of AssignResources command of Central Node"""

    def _validate_subarray_id(self, subarray_id):
        """Applies validation on Subarray ID value
        
        :param: subarray_id: Integer

        :return: None

        :throws:
            JsonValueTypeMismatchError: When subarray ID is not integer.

            InvalidParameterValue: When a value of a JSON key is not valid. E.g. Subarray device 
            for the specified id is not present.
        """
        try:
            assert type(subarray_id) == int
            print("subarrayID type correct.")
        except AssertionError as ae:
            print(ae)
            raise JsonValueTypeMismatchError("Subarray ID must be an integr value.")

        if not 1<= subarray_id <= 3:
            print("Subarray ID is not in valid range.")
            raise InvalidParameterValue("Invalid subarray ID. Subarray ID must be between 1 and 3.")

        print("subarrayID validation successful.")

    def _validate_receptor_id_list(self, receptor_id_list):
        """Applies validation on receptorIDList value
        
        :param: receptor_id_list: List of strings 

        :return: None

        :throws:
            JsonValueTypeMismatchError: When receptorIDList is not a list of strings.

            InvalidParameterValue: When a value of a JSON key is not valid. E.g. Non string value 
            is passed in the list.
        """
        try:
            assert type(receptor_id_list) == list
            print("receptorIDList type correct.")
        except AssertionError as ae:
            print(ae)
            raise InvalidParameterValue("The parameter receptorIDList must be a list.")

        for receptor_id in receptor_id_list:
            print(type(receptor_id))
            print(int(receptor_id))
            if (type(receptor_id) != str) or ( int(receptor_id) not in range(1,4)):
                raise InvalidJSONError("Invalid value in receptorIDList. All the values must be string. \
            Valid values are '0001', '0002', '0003', '0004'")

    def validate(self, input_string):
        """
        Validates the input string received as an argument of AssignResources command.

        :param: input_string: A JSON string

        :return: True if input string is valid.

        :throws:
            InvalidJSONError: When the JSON string is not formatted properly.

            JsonKeyMissingError: When a mandatory key from the JSON string is missing.
        """
        ret_val = False
        print("Entry")
        
        ## Check if JSON is correct
        print("Checking JSON format.")
        try:
            input_json = json.loads(input_string)
            print("JSON load ok.")
        except JSONDecodeError as json_error:
            print(json_error.msg)
            raise InvalidJSONError("Malformed input string. Please check the JSON format.")

        ## Validate subarray ID
        print("Validating subarrayID")
        try:
            subarray_id = input_json["subarrayID"]
        except KeyError as ke:
            print(ke)
            raise JsonKeyMissingError("A mandatory key subarrayID is missing from input JSON.")

        self._validate_subarray_id(subarray_id)

        ## Validate receptorIDList
        print("Validating receptorIDList")
        try:
            receptor_id_list = input_json["dish"]["receptorIDList"]
        except KeyError as ke:
            print(ke)
            raise JsonKeyMissingError("A mandatory key receptorIDList is missing from input JSON.")
        
        self._validate_receptor_id_list(receptor_id_list)

        ret_val = True
        print("Success")

        return ret_val
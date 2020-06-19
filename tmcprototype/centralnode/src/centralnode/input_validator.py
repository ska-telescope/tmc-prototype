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
import logging

# SKA specific imports
from centralnode.exceptions import InvalidJSONError, JsonKeyMissingError, JsonValueTypeMismatchError
from centralnode.exceptions import InvalidParameterValue
# import ska.logging as ska_logging

module_logger = logging.getLogger(__name__)

class AssignResourceValidator():
    
    """Class to validate the input string of AssignResources command of Central Node"""

    def __init__(self, subarray_list, receptor_list, logger=module_logger):
        self.logger = logger
        self.subarrays = []

        # get the ids of the numerical ids of  available subarrays
        for subarray in subarray_list:
            tokens = subarray.split('/')
            self.subarrays.append = int(tokens[2])
        self.logger.debug("Available subarray ids: %s", str(self.subarrays))
        self.receptors = receptor_list
        self.logger.debug("Available subarray ids: %s", str(self.receptor_list))

    def _validate_subarray_id(self, subarray_id):
        """Applies validation on Subarray ID value
        
        :param: subarray_id: Integer

        :return: None

        :throws:
            JsonValueTypeMismatchError: When subarray ID is not integer.

            InvalidParameterValue: When a value of a JSON key is not valid. E.g. Subarray device 
            for the speyes cified id is not present.
        """
        # try:
        #     assert type(subarray_id) == int
        #     self.logger.info("SubarrayID type correct.")
        # except AssertionError as ae:
        #     self.logger.exception("Exception: %s", ae)
        #     raise JsonValueTypeMismatchError("Subarray ID must be an integer value.")

        # if not 1<= subarray_id <= 3:
        if not subarray_id in self.subarrays:
            self.logger.error("Invalid subarray ID. Subarray ID must be between 1 and 3.")
            raise InvalidParameterValue("Invalid subarray ID. Subarray ID must be between 1 and 3.")

    def _validate_receptor_id_list(self, receptor_id_list):
        """Applies validation on receptorIDList value

        :param: receptor_id_list: List of strings 

        :return: None

        :throws:
            InvalidParameterValue: When a value of a JSON key is not valid. E.g. Non string value 
            is passed in the list.
        """
        try:
            assert type(receptor_id_list) == list
            self.logger.info("receptorIDList type correct.")
        except AssertionError as ae:
            self.logger.exception("Exception: %s", str(ae))
            raise InvalidParameterValue("The parameter receptorIDList must be a list.")

        for receptor_id in receptor_id_list:
            if (type(receptor_id) != str) or ( int(receptor_id) not in range(1,4)):
                self.logger.error("Invalid value in receptorIDList.")
                raise InvalidParameterValue("Invalid value in receptorIDList. Valid values are '0001', '0002', '0003', '0004'")

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
        
        ## Check if JSON is correct
        self.logger.info("Checking JSON format.")
        try:
            input_json = json.loads(input_string)
            self.logger.info("The JSON format is correct.")
        except JSONDecodeError as json_error:
            self.logger.exception("Exception: %s", str(json_error))
            raise InvalidJSONError("Malformed input string. Please check the JSON format.")

        ## Validate subarray ID
        self.logger.info("Validating subarrayID")
        try:
            subarray_id = input_json["subarrayID"]
        except KeyError as ke:
            self.logger.exception("Exception: %s", str(ke))
            raise JsonKeyMissingError("A mandatory key subarrayID is missing from input JSON.")

        self._validate_subarray_id(subarray_id)
        self.logger.info("SubarrayID validation successful.")

        ## Validate receptorIDList
        self.logger.info("Validating receptorIDList")
        try:
            receptor_id_list = input_json["dish"]["receptorIDList"]
        except KeyError as ke:
            self.logger.exception("Exception: %s", str(ke))
            raise JsonKeyMissingError("A mandatory key receptorIDList is missing from input JSON.")

        self._validate_receptor_id_list(receptor_id_list)
        self.logger.info("receptor_id_list validation successful.")

        ret_val = True
        return ret_val
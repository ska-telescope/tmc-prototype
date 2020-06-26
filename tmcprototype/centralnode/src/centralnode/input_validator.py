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
from centralnode.exceptions import ResourceNotPresentError
from centralnode.exceptions import SubarrayNotPresentError, InvalidJSONError
from ska.cdm.schemas import CODEC
from ska.cdm.messages.central_node.assign_resources import AssignResourcesRequest
from marshmallow import ValidationError

module_logger = logging.getLogger(__name__)

class AssignResourceValidator():
    
    """Class to validate the input string of AssignResources command of Central Node"""

    def __init__(self, subarray_list, receptor_list, dish_perfix, logger=module_logger):
        self.logger = logger
        self._subarrays = []

        # get the ids of the numerical ids of available subarrays
        for subarray in subarray_list:
            tokens = subarray.split('/')
            self._subarrays.append(int(tokens[2]))
        self.logger.debug("Available subarray ids: %s", str(self._subarrays))

        # Get available dish ids
        self._receptor_list = receptor_list
        self.logger.debug("Available dish ids: %s", str(self._receptor_list))

        self._dish_prefix = dish_perfix

    def _validate_subarray_id(self, subarray_id):
        """Applies validation on Subarray ID value
        
        :param: subarray_id: Integer

        :return: None.

        :throws:
            SubarrayNotPresentError: When a value of a JSON key is not valid. E.g. Subarray device 
            for the speyes cified id is not present.
        """
        self.logger.debug("Subarray ID: %d", subarray_id)
        if not subarray_id in self._subarrays:
            self.logger.error("Incorrect Subarray ID. The subarray does not exist.")
            exception_message = "Invalid subarray ID. Available subarrays are: " + str(self._subarrays)
            raise SubarrayNotPresentError(exception_message)

    def _validate_receptor_id_list(self, receptor_id_list):
        """Applies validation on receptorIDList value

        :param: receptor_id_list: List of strings 

        :return: None.

        :throws:
            ResourceNotPresentError: When a value of a JSON key is not valid. E.g. Non string value 
            is passed in the list.
        """
        self.logger.info("Available receptors: %s", self._receptor_list)
        for receptor_id in receptor_id_list:
            receptor_id = self._dish_prefix + receptor_id
            self.logger.info("Checking for receptor %s", receptor_id)
            if receptor_id not in self._receptor_list:
                self.logger.error("Invalid value in receptorIDList.")
                exception_message = "Invalid value in receptorIDList. Valid values are: " + str(self._receptor_list)
                raise ResourceNotPresentError(exception_message)
            self.logger.info("Receptor ID is valid")

    def validate(self, input_string):
        """
        Validates the input string received as an argument of AssignResources command.

        :param: input_string: A JSON string

        :return: True if input string is valid.

        :throws:
            InvalidJSONError: When the JSON string is not formatted properly.
        """
        
        ## Check if JSON is correct
        self.logger.info("Checking JSON format.")
        try:
            input_json = CODEC.loads(AssignResourcesRequest, input_string)
            self.logger.info("The JSON format is correct.")
        except(ValidationError, JSONDecodeError) as json_error:
            self.logger.exception("Exception: %s", str(json_error))
            raise InvalidJSONError("Malformed input string. Please check the JSON format.")

        ## Validate subarray ID
        self.logger.info("Validating subarrayID")
        # NOTE: To avoid refactoring the code to use the classes from 
        # cdm library which was integrated after this code was written.
        input_json = json.loads(input_string)

        self._validate_subarray_id(input_json["subarrayID"])
        self.logger.info("SubarrayID validation successful.")

        ## Validate receptorIDList
        self.logger.info("Validating receptorIDList")
        self._validate_receptor_id_list(input_json["dish"]["receptorIDList"])
        self.logger.info("receptor_id_list validation successful.")

        return input_json
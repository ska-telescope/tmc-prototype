# -*- coding: utf-8 -*-
#
# This file is part of the CentralNodeLow project
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
from centralnodelow.exceptions import SubarrayNotPresentError, InvalidJSONError
from ska.cdm.schemas import CODEC
#from ska.cdm.messages.central_node.assign_resources import AssignResourcesRequest
from ska.cdm.messages.central_node.release_resources import ReleaseResourcesRequest
from ska.cdm.messages.central_node.mccs import MCCSAllocate
from marshmallow import ValidationError

module_logger = logging.getLogger(__name__)


class AssignResourceValidator():
    
    """Class to validate the input string of AssignResources command of Central Node"""

    def __init__(self, subarray_list, logger=module_logger):
        self.logger = logger
        self._subarrays = []
        self._receptor_list = []

        # get the ids of the numerical ids of available subarrays
        for subarray in subarray_list:
            tokens = subarray.split('/')
            self._subarrays.append(int(tokens[2]))
        self.logger.debug("Available subarray ids: %s", self._subarrays)

    def _subarray_exists(self, subarray_id):
        """
        Checks if subarray is present.
        
        :param: subarray_id: Integer

        :return: True if subarray exists. False if the subarray is not present.
        """
        ret_val = False
        self.logger.debug("Subarray ID: %d", subarray_id)
        if not subarray_id in self._subarrays:
            self.logger.debug("The subarray does not exist.")
        else:
            ret_val = True
        
        return ret_val

    def loads(self, input_string):
        """
        Validates the input string received as an argument of AssignResources command. 
        If the request is correct, returns the deserialized JSON object. The cdm-shared-library
        is used to validate the JSON.

        :param: input_string: A JSON string

        :return: Deserialized JSON object if successful. 

        :throws:
            InvalidJSONError: When the JSON string is not formatted properly.

            SubarrayNotPresentError: If the subarray is not present.

        """

        # Check if JSON is correct
        self.logger.info("Checking JSON format.")
        try:
            assign_request = CODEC.loads(MCCSAllocate, input_string)
        except(ValidationError, JSONDecodeError) as json_error:
            self.logger.exception("Exception: %s", str(json_error))
            exception_message = "Malformed input string. Please check the JSON format." + \
                "Full exception info: " + \
                str(json_error)
            raise InvalidJSONError(exception_message)

        # Validate subarray ID
        # TODO: Use the object returned by cdm library instead of parsing JSON string.
        assign_request = json.loads(input_string)
        if(not self._subarray_exists(assign_request["subarray_id"])):
            exception_message = "The Subarray '" + str(assign_request["subarray_id"]) + "' does not exist."
            raise SubarrayNotPresentError(exception_message)
        self.logger.debug("SubarrayID validation successful for assign resources request.")

        return assign_request


class ReleaseResourceValidator():
    """Class to validate the input string of ReleaseResources command of Central Node"""

    def __init__(self, subarray_list, logger=module_logger):
        self.logger = logger
        self._subarrays = []
        self._release_all = False

        # get the ids of the numerical ids of available subarrays
        for subarray in subarray_list:
            tokens = subarray.split('/')
            self._subarrays.append(int(tokens[2]))
        self.logger.debug("Available subarray ids: %s", self._subarrays)

    def _subarray_exists(self, subarray_id):
        """Checks if subarray is present.

        :param: subarray_id: Integer

        :return: True if subarray exists. False if the subarray is not present.
        """
        ret_val = False
        self.logger.debug("Subarray ID: %d", subarray_id)
        if not subarray_id in self._subarrays:
            self.logger.debug("The subarray does not exist.")
        else:
            ret_val = True

        return ret_val

    def loads(self, input_string):
        """
        Validates the input string received as an argument of ReleaseResources command.
        If the request is correct, returns the deserialized JSON object. The cdm-shared-library
        is used to validate the JSON.

        :param: input_string: A JSON string

        :return: Deserialized JSON object if successful.

        :throws:
            InvalidJSONError: When the JSON string is not formatted properly.

            SubarrayNotPresentError: If the subarray is not present.

        """

        # Check if JSON is correct
        self.logger.info("Checking JSON format.")
        try:
            release_request = CODEC.loads(ReleaseResourcesRequest, input_string)
        except(ValidationError, JSONDecodeError) as json_error:
            self.logger.exception("Exception: %s", str(json_error))
            exception_message = "Malformed input string. Please check the JSON format." + \
                                "Full exception info: " + \
                                str(json_error)
            raise InvalidJSONError(exception_message)

        # Validate subarray ID
        # TODO: Use the object returned by cdm library instead of parsing JSON string.
        release_request = json.loads(input_string)
        if (not self._subarray_exists(release_request["subarray_id"])):
            exception_message = "The Subarray '" + str(release_request["subarray_id"]) + "' does not exist."
            raise SubarrayNotPresentError(exception_message)
        self.logger.debug("SubarrayID validation successful for release resources request.")

        return release_request

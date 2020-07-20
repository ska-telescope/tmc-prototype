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

    def __init__(self, subarray_list, receptor_list, dish_prefix, logger=module_logger):
        self.logger = logger
        self._subarrays = []

        # get the ids of the numerical ids of available subarrays
        for subarray in subarray_list:
            tokens = subarray.split('/')
            self._subarrays.append(int(tokens[2]))
        self.logger.debug("Available subarray ids: %s", self._subarrays)

        # Get available dish ids
        # self._receptor_list = receptor_list
        for receptor in receptor_list:
            self._receptor_list.append(receptor.replace(dish_prefix))
        self.logger.debug(self._receptor_list)

        self.logger.debug("Available dish ids: %s", self._receptor_list)

        self._dish_prefix = dish_prefix

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


    # def _receptor_exists(self, receptor_id_list):
    #     """Applies validation on receptor id list.

    #     :param: receptor_id_list: List of strings

    #     :return: True if all the receptors are present. False if a receptor is not present.
    #     """
    #     self.logger.debug("Existing receptors: %s", self._receptor_list)
    #     for receptor_id in receptor_id_list:
    #         receptor_id = self._dish_prefix + receptor_id
    #         self.logger.debug("Checking for receptor %s", receptor_id)
    #         if receptor_id not in self._receptor_list:
    #             self.logger.debug("Receptor %s. is not present.", receptor_id)
    #             return False

    #     return True

    def _search_invalid_receptors(self, receptor_id_list):
        """
        Searches the receptor ids in the received receptor id list and 
        returns the ones that do not exist.

        :param: receptor_id_list: List of strings

        :returns: List of receptors that do not exist. Empty list is returned
        when all receptors exist.

        """
        for receptor_id in receptor_id_list:
            self.logger.debug("Checking for receptor %s", receptor_id)
            if receptor_id not in self._receptor_list:
                self.logger.debug("Receptor %s. is not present.", receptor_id)
                non_existing_receptors.append(receptor_id)
        self.logger.debug(non_existing_receptors)


    def loads(self, input_string):
        """
        Validates the input string received as an argument of AssignResources command. 
        If the request is correct, returns the deserialized JSON object.

        :param: input_string: A JSON string

        :return: Deserialized JSON object if successful. 

        :throws:
            InvalidJSONError: When the JSON string is not formatted properly.

            SubarrayNotPresentError: If the subarray is not present.

            ResourceNotPresentError: When a receptor in the receptor_id_list is not present.
        """
        
        ## Check if JSON is correct
        self.logger.info("Checking JSON format.")
        try:
            assign_request = CODEC.loads(AssignResourcesRequest, input_string)
        except(ValidationError, JSONDecodeError) as json_error:
            self.logger.exception("Exception: %s", str(json_error))
            exception_message = "Malformed input string. Please check the JSON format." + \
                "Full exception info: " + \
                str(json_error)
            raise InvalidJSONError(exception_message)

        ## Validate subarray ID
        # TODO: Use the object returned by cdm library instead of parsing 
        # JSON string.
        assign_request = json.loads(input_string)
        if(not self._subarray_exists(assign_request["subarrayID"])):
            exception_message = "Subarray not present. Available subarrays are: " + str(self._subarrays)
            raise SubarrayNotPresentError(exception_message)
        self.logger.debug("SubarrayID validation successful.")

        ## Validate receptorIDList
        try:
            receptor_list = assign_request["dish"]["receptorIDList"]
            assert len(receptor_list) > 0
        except AssertionError as ae:
            raise ValueError("Empty receptorIDList") from ae

        if(not self._receptor_exists(assign_request["dish"]["receptorIDList"])):
            exception_message = "The following Receptor id(s) do not exist: " + str(self._receptor_list)
            raise ResourceNotPresentError(exception_message)
        self.logger.debug("receptor_id_list validation successful.")

        return assign_request
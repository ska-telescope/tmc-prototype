# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNodeLow project
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
from .exceptions import InvalidJSONError
from ska.cdm.schemas import CODEC
from ska.cdm.messages.subarray_node.scan import ScanRequest
from ska.cdm.messages.subarray_node.configure.__init__ import ConfigureRequest
from marshmallow import ValidationError

module_logger = logging.getLogger(__name__)


class ScanValidator():
    def __init__(self, logger=module_logger):
        self.logger = logger

    def loads(self, input_string):
        """
            Validates the input string received as an argument of Scan command.
            If the request is correct, returns the deserialized JSON object. The cdm-shared-library
            is used to validate the JSON.

            :param: input_string: A JSON string

            :return: Deserialized JSON object if successful.

            :throws:
                InvalidJSONError: When the JSON string is not formatted properly.
            """

        # Check if JSON is correct
        self.logger.info("Checking JSON format.")
        try:
            scan_request = CODEC.loads(ScanRequest, input_string)
        except(ValidationError, JSONDecodeError) as json_error:
            self.logger.exception("Exception: %s", str(json_error))
            exception_message = "Malformed input string. Please check the JSON format." + \
                                "Full exception info: " + \
                                str(json_error)
            raise InvalidJSONError(exception_message)
        return json.loads(input_string)


class ConfigureValidator():
    def __init__(self, logger=module_logger):
        self.logger = logger

    def loads(self, input_string):
        """
            Validates the input string received as an argument of Configure command.
            If the request is correct, returns the deserialized JSON object. The cdm-shared-library
            is used to validate the JSON.

            :param: input_string: A JSON string

            :return: Deserialized JSON object if successful.

            :throws:
                InvalidJSONError: When the JSON string is not formatted properly.
            """

        # Check if JSON is correct
        self.logger.info("Checking JSON format.")
        try:
            scan_request = CODEC.loads(ConfigureRequest, input_string)
        except(ValidationError, JSONDecodeError) as json_error:
            self.logger.exception("Exception: %s", str(json_error))
            exception_message = "Malformed input string. Please check the JSON format." + \
                                "Full exception info: " + \
                                str(json_error)
            raise InvalidJSONError(exception_message)
        return json.loads(input_string)

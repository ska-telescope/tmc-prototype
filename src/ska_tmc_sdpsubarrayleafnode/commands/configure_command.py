"""
Configure command class for SDPSubarrayLeafNode.
"""
import json
from json import JSONDecodeError

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

# from ska_tmc_common.adapters import AdapterFactory
from ska_tmc_common.exceptions import InvalidObsStateError
from tango import DevFailed

from ska_tmc_sdpsubarrayleafnode.adapters import AdapterFactory
from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class Configure(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's Configure() command.

    Configures the SDP Subarray device by providing the SDP PB
    configuration needed to execute the receive workflow

    """

    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=None,
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory or AdapterFactory()

    def check_allowed(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        component_manager = self.target

        self.check_op_state("Configure")
        self.check_unresponsive()
        obs_state_val = component_manager.get_device().obs_state
        if obs_state_val not in (ObsState.READY, ObsState.IDLE):
            message = (
                "Configure command is not allowed in current"
                + "observation state on device"
                + "{}".format(component_manager._sdp_subarray_dev_name)
                + "Reason: The current observation state for observation is"
                + "{}".format(obs_state_val)
                + 'The "Configure" command has NOT been executed.'
                + "This device will continue with normal operation."
            )
            raise InvalidObsStateError(message)
        return True

    def do(self, argin=None):
        """
        Method to invoke Configure command on SDP Subarray. \

        :param argin: The string in JSON format. \
        The JSON contains following values: \

        Example: \
            { \
            "interface": "https://schema.skao.int/ska-sdp-configure/0.3", \
            "scan_type": "science_A" \
            } \

        return: \
            None
        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message
        try:
            json_argument = json.loads(argin)
        except JSONDecodeError as e:
            log_msg = (
                "Execution of Configure command is failed."
                + "Reason: JSON parsing failed with exception: {}".format(e)
                + "The command is not executed successfully."
                + "The device will continue with normal operation"
            )
            self.logger.exception(log_msg)
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    """Exception occurred while parsing the JSON.
                    Please check the logs for details."""
                ),
            )

        if "interface" not in json_argument:
            return self.generate_command_result(
                ResultCode.FAILED,
                "interface key is not present in the input json argument.",
            )

        if "scan_type" not in json_argument:
            return self.generate_command_result(
                ResultCode.FAILED,
                "scan_type key is not present in the input json argument.",
            )

        if json_argument["scan_type"] == "":
            return self.generate_command_result(
                ResultCode.FAILED,
                "scan_type is not present in the input json argument.",
            )

        log_msg = "Invoking Configure command on:"
        "{}".format(self.sdp_subarray_adapter.dev_name)
        self.logger.info(log_msg)
        try:
            json_argument[
                "interface"
            ] = "https://schema.skao.int/ska-sdp-configure/0.3"
            log_msg = (
                "Input JSON for Configure command for SDP subarray"
                + "{}: {}".format(
                    self.sdp_subarray_adapter.dev_name, json_argument
                )
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.Configure(json.dumps(json_argument))

        except (AttributeError, ValueError, TypeError, DevFailed) as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the Configure command is failed on"
                + "Sdp Subarray Device {}".format(
                    self.sdp_subarray_adapter.dev_name
                )
                + "Reason: Error in invoking the Configure command on"
                "Sdp Subarray."
                + "The command has NOT been executed."
                + "This device will continue with normal operation.",
            )
        log_msg = "Configure command successfully invoked on:" + "{}".format(
            self.sdp_subarray_adapter.dev_name
        )
        self.logger.info(log_msg)
        return (ResultCode.OK, "")

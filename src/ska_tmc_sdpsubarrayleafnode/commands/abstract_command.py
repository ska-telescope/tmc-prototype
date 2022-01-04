from ska_tango_base.commands import BaseCommand, ResultCode
from tango import DevState

from ska_tmc_sdpsubarrayleafnode.exceptions import CommandNotAllowed
from ska_tmc_common.adapters import AdapterFactory
from ska_tmc_common.tmc_command import TMCCommand
from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid

class AbstractTelescopeOnOffCommand(TMCCommand):
    def __init__(
        self,
        target,
        pop_state_model,
        adapter_factory=AdapterFactory(),
        *args,
        logger=None,
        **kwargs,
    ):
        super().__init__(target, args, logger, kwargs)
        self.op_state_model = pop_state_model
        self._adapter_factory = adapter_factory
        self.sdp_subarray_adapter = None

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed
        It checks that the device is in a state
        to perform this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        component_manager = self.target

        if self.op_state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            raise CommandNotAllowed(
                "TelescopeOnOff() is not allowed in current state %s",
                self.op_state_model.op_state,
            )

        # for this command I need a number of sub-devices
        # import debugpy; debugpy.debug_this_thread()
        devInfo = component_manager.get_device(
            component_manager.input_parameter.sdp_subarray_dev_name
        )
        if devInfo is None or devInfo.unresponsive:
            raise CommandNotAllowed("SDP subarray device is not available")

        return True

    def init_adapters_mid(self):

        self.sdp_subarray_adapter = None
        component_manager = self.target
        try:
            self.sdp_subarray_adapter = (
                self._adapter_factory.get_or_create_adapter(
                    component_manager.input_parameter.sdp_subarray_dev_name
                )
            )
        except Exception as e:
            return self.adapter_error_message_result(
                component_manager.input_parameter.sdp_subarray_dev_name,
                e,
            )

        return ResultCode.OK, ""

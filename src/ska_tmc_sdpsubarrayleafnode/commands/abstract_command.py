from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory, AdapterType
from ska_tmc_common.tmc_command import TMCCommand
from tango import DevState

from ska_tmc_sdpsubarrayleafnode.exceptions import CommandNotAllowed
from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid


class SdpSLNCommand(TMCCommand):
    def check_allowed(self):
        component_manager = self.target

        if isinstance(component_manager.input_parameter, InputParameterMid):
            result = self.check_allowed_mid()

        return result

    def init_adapters(self):
        component_manager = self.target

        if isinstance(component_manager.input_parameter, InputParameterMid):
            result, message = self.init_adapters_mid()
        return result, message

    def do(self, argin=None):
        component_manager = self.target
        if isinstance(component_manager.input_parameter, InputParameterMid):
            result = self.do_mid(argin)
        return result


class AbstractTelescopeOnOff(SdpSLNCommand):
    def __init__(
        self,
        target,
        pop_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, logger)
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


class AbstractAssignReleaseResources(TMCCommand):
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

        if self.op_state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            raise CommandNotAllowed(
                "AssignResources and ReleaseResources command is not allowed in current state %s",
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
        dev_name = component_manager.input_parameter.sdp_subarray_dev_name
        devInfo = component_manager.get_device(dev_name)
        try:
            if not devInfo.unresponsive:
                self.sdp_subarray_adapter = (
                    self._adapter_factory.get_or_create_adapter(
                        dev_name, AdapterType.SDPSUBARRAY
                    )
                )
        except Exception as e:
            return self.adapter_error_message_result(
                component_manager.input_parameter.sdp_subarray_dev_name,
                e,
            )

        return ResultCode.OK, ""

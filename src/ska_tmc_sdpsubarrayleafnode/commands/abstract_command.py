from ska_tango_base.commands import BaseCommand, ResultCode
from tango import DevState

from ska_tmc_sdpsubarrayleafnode.exceptions import CommandNotAllowed
from ska_tmc_sdpsubarrayleafnode.manager.adapters import (
    AdapterFactory,
    AdapterType,
)
from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid


# Delete this class and import it once ska-tmc-common classes are ready
class TMCCommand(BaseCommand):
    def __init__(self, target, *args, logger=None, **kwargs):
        super().__init__(target, args, logger, kwargs)

    def generate_command_result(self, result_code, message):
        if result_code == ResultCode.FAILED:
            self.logger.error(message)
        self.logger.info(message)
        return (result_code, message)

    def adapter_error_message_result(self, dev_name, e):
        message = f"Error in creating adapter for {dev_name}: {e}"
        self.logger.error(message)
        return ResultCode.FAILED, message

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

    def check_allowed_mid(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapters_mid(self):
        raise NotImplementedError("This class must be inherited!")

    def do_mid(self, argin=None):
        raise NotImplementedError("This class must be inherited!")


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
        self.sdp_subarray_adapters = []

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
        subarray_count = 0
        for (
            dev_name
        ) in component_manager.input_parameter.sdp_subarray_dev_names:
            devInfo = component_manager.get_device(dev_name)
            if devInfo is not None and not devInfo.unresponsive:
                subarray_count += 1
        if subarray_count == 0:
            raise CommandNotAllowed("No Sdp Subarray available")

        return True

    def init_adapters_mid(self):

        self.sdp_subarray_adapters = []
        component_manager = self.target
        error_dev_names = []
        num_working = 0

        for (
            dev_name
        ) in component_manager.input_parameter.sdp_subarray_dev_names:
            devInfo = component_manager.get_device(dev_name)
            if not devInfo.unresponsive:
                try:
                    self.sdp_subarray_adapters.append(
                        self._adapter_factory.get_or_create_adapter(
                            dev_name, AdapterType.SDPSUBARRAY
                        )
                    )
                    num_working += 1
                except Exception as e:
                    self.logger.warning(
                        "Error in creating adapter for %s: %s", dev_name, e
                    )
                    error_dev_names.append(dev_name)

        if num_working == 0:
            message = f"Error in creating sdp subarray adapters {'.'.join(error_dev_names)}"
            return self.generate_command_result(ResultCode.FAILED, message)

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
        self.sdp_subarray_adapters = []

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        component_manager = self.target

        if self.op_state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            raise CommandNotAllowed(
                "AssignReleaseResources() is not allowed in current state %s",
                self.op_state_model.op_state,
            )

        subarray_count = 0
        for (
            dev_name
        ) in component_manager.input_parameter.sdp_subarray_dev_names:
            devInfo = component_manager.get_device(dev_name)
            if devInfo is not None and not devInfo.unresponsive:
                subarray_count += 1
        if subarray_count == 0:
            raise CommandNotAllowed("No sdp Subarray available")

        return True

    def init_adapters_mid(self):

        self.sdp_subarray_adapters = []
        component_manager = self.target

        error_dev_names = []
        num_working = 0

        for (
            dev_name
        ) in component_manager.input_parameter.sdp_subarray_dev_names:
            devInfo = component_manager.get_device(dev_name)
            if not devInfo.unresponsive:
                try:
                    self.sdp_subarray_adapters.append(
                        self._adapter_factory.get_or_create_adapter(
                            dev_name, AdapterType.SDPSUBARRAY
                        )
                    )
                    num_working += 1
                except Exception as e:
                    self.logger.warning(
                        "Error in creating adapter for %s: %s", dev_name, e
                    )
                    error_dev_names.append(dev_name)

        if num_working == 0:
            return self.generate_command_result(
                ResultCode.FAILED,
                f"Error in creating sdp subarray adapters {'.'.join(error_dev_names)}",
            )

        return (ResultCode.OK, "")

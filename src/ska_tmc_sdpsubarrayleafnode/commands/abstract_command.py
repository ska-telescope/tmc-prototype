from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterFactory, AdapterType
from ska_tmc_common.exceptions import (
    CommandNotAllowed,
    DeviceUnresponsive,
    InvalidObsStateError,
)
from ska_tmc_common.tmc_command import TmcLeafNodeCommand
from tango import DevState


class SdpSLNCommand(TmcLeafNodeCommand):
    def __init__(self, target, *args, logger=None, **kwargs):
        super().__init__(target, *args, logger=logger, **kwargs)

    def check_unresponsive(self):
        component_manager = self.target
        devInfo = component_manager.get_device()
        if devInfo is None or devInfo.unresponsive:
            raise DeviceUnresponsive("SDP subarray device is not available")

    def check_op_state(self, command_name):
        if self.op_state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            raise CommandNotAllowed(
                "%s command is not allowed in current operational state %s",
                command_name,
                self.op_state_model.op_state,
            )

    def init_adapter(self):
        self.sdp_subarray_adapter = None
        component_manager = self.target
        dev_name = component_manager._sdp_subarray_dev_name
        devInfo = component_manager.get_device()
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

    def do(self, argin=None):
        result = self.do(argin)
        return result

    def check_allowed(self):
        return super().check_allowed()


class AbstractOnOff(SdpSLNCommand):
    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory

    def check_allowed(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        if self.op_state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            raise CommandNotAllowed(
                "Command is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        component_manager = self.target
        devInfo = component_manager.get_device()
        if devInfo is None or devInfo.unresponsive:
            raise DeviceUnresponsive("SDP subarray device is not available")

        return True


class AbstractScanEnd(SdpSLNCommand):
    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory

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

        self.check_op_state("Scan/End")
        self.check_unresponsive()

        obs_state_val = component_manager.get_device().obsState

        if obs_state_val != ObsState.READY:
            message = f"""Scan and End commands are not allowed in current observation state on device {component_manager.get_device().dev_name}.
            Reason: The current observation state for observation is {obs_state_val}.
            The \"Scan/End\" command has NOT been executed. This device will continue with normal operation."""
            raise InvalidObsStateError(message)

        return True


class AbstractRestartObsReset(SdpSLNCommand):
    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory

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

        self.check_op_state("Restart/ObsReset")
        self.check_unresponsive()

        obs_state_val = component_manager.get_device().obsState

        if obs_state_val not in (ObsState.ABORTED, ObsState.FAULT):
            message = f"""ObsReset and Restart commands are not allowed in current observation state on {component_manager.get_device().dev_name}.
            Reason: The current observation state for observation is {obs_state_val}.
            The \"Restart/ObsReset\" command has NOT been executed. This device will continue with normal operation."""
            raise InvalidObsStateError(message)

        return True


# class AbstractConfigure(SdpSLNCommand):
#     def __init__(
#         self,
#         target,
#         op_state_model,
#         adapter_factory=AdapterFactory(),
#         logger=None,
#     ):
#         super().__init__(target, logger)
#         self.op_state_model = op_state_model
#         self._adapter_factory = adapter_factory

#     def check_allowed(self):
#         """
#         Checks whether this command is allowed
#         It checks that the device is in the right state
#         to execute this command and that all the
#         component needed for the operation are not unresponsive

#         :return: True if this command is allowed

#         :rtype: boolean

#         """
#         component_manager = self.target

#         if self.op_state_model.op_state in [
#             DevState.FAULT,
#             DevState.UNKNOWN,
#             DevState.DISABLE,
#         ]:
#             raise CommandNotAllowed(
#                 "Configure command is not allowed in current operational state %s",
#                 self.op_state_model.op_state,
#             )

#         self.check_unresponsive()
#         obs_state_val = component_manager.get_device().obsState
#         self.logger.info(
#             "ObsState value before invoking Configure command is %s",
#             obs_state_val,
#         )
#         if obs_state_val not in (ObsState.READY, ObsState.IDLE):
#             raise InvalidObsStateError(
#                 f"Configure command is not allowed in current observation state:{obs_state_val}"
#             )

#         return True

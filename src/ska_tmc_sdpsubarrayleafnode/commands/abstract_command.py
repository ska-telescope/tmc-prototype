# pylint: disable=no-member
# pylint: disable=abstract-method
"""Abstract Command for SDP Subarray Leaf Node"""
import time

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterFactory, AdapterType
from ska_tmc_common.exceptions import (
    CommandNotAllowed,
    DeviceUnresponsive,
    InvalidObsStateError,
)
from ska_tmc_common.tmc_command import TmcLeafNodeCommand
from tango import DevFailed, DevState


class SdpSLNCommand(TmcLeafNodeCommand):
    """SDP Subarray Leaf Node Class"""

    def check_unresponsive(self):
        """Checks whether the device is unresponsive"""
        component_manager = self.target
        devInfo = component_manager.get_device()
        if devInfo is None or devInfo.unresponsive:
            raise DeviceUnresponsive(
                """The invocation of the command on this device is not allowed.
                Reason: SDP subarray device is not available.
                The command has NOT been executed.
                This device will continue with normal operation."""
            )

    def check_op_state(self, command_name):
        """Checks the operational state of the device"""
        if self.op_state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            raise CommandNotAllowed(
                f"""The invocation of the {command_name} command on this
                device is not allowed.
                Reason: The current operational state is
                {self.op_state_model.op_state}.
                The command has NOT been executed.
                This device will continue with normal operation."""
            )

    # pylint: disable=attribute-defined-outside-init
    def init_adapter(self):
        self.sdp_subarray_adapter = None
        component_manager = self.target
        dev_name = component_manager._sdp_subarray_dev_name
        devInfo = component_manager.get_device()
        timeout = component_manager.timeout
        elapsed_time = 0
        start_time = time.time()

        while self.sdp_subarray_adapter is None and elapsed_time < timeout:
            try:
                if not devInfo.unresponsive:
                    self.sdp_subarray_adapter = (
                        self._adapter_factory.get_or_create_adapter(
                            dev_name, AdapterType.SUBARRAY
                        )
                    )
            except DevFailed as df:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    return self.adapter_error_message_result(
                        component_manager._sdp_subarray_dev_name,
                        df,
                    )
            except Exception as e:
                return self.adapter_error_message_result(
                    component_manager._sdp_subarray_dev_name,
                    e,
                )

        return ResultCode.OK, ""

    # pylint: enable=attribute-defined-outside-init


class AbstractOnOff(SdpSLNCommand):
    """Abstract class to process On and Off commands"""

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
        if self.op_state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            raise CommandNotAllowed(
                f"""The invocation of the command on this device
                is not allowed.
                Reason: The current operational state is
                {self.op_state_model.op_state}.
                The command has NOT been executed.
                This device will continue with normal operation."""
            )

        component_manager = self.target
        devInfo = component_manager.get_device()
        if devInfo is None or devInfo.unresponsive:
            raise DeviceUnresponsive(
                """The invocation of the command on this device is not allowed.
                Reason: SDP subarray device is not available.
                The command has NOT been executed.
                This device will continue with normal operation."""
            )

        return True


class AbstractScanEnd(SdpSLNCommand):
    """Abstract class to process Scan and End commands"""

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

        self.check_op_state("Scan/End")
        self.check_unresponsive()

        obs_state_val = component_manager.get_device().obs_state

        if obs_state_val != ObsState.READY:
            message = f"""Scan and End commands are not allowed in current
            observation state on device
            {component_manager._sdp_subarray_dev_name}.
            Reason: The current observation state for observation is
            {obs_state_val}.
            The \"Scan/End\" command has NOT been executed.
            This device will continue with normal operation."""
            raise InvalidObsStateError(message)

        return True


class AbstractRestartObsReset(SdpSLNCommand):
    """Abstract class to process Restart and Observation Reset commands"""

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

        self.check_op_state("Restart/ObsReset")
        self.check_unresponsive()

        obs_state_val = component_manager.get_device().obs_state

        if obs_state_val not in (ObsState.ABORTED, ObsState.FAULT):
            message = f"""ObsReset and Restart commands are not allowed in
            current observation state on
            {component_manager._sdp_subarray_dev_name}.
            Reason: The current observation state for observation is
            {obs_state_val}.
            The \"Restart/ObsReset\" command has NOT been executed.
            This device will continue with normal operation."""
            raise InvalidObsStateError(message)

        return True

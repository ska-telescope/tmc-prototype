from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterFactory, AdapterType
from ska_tmc_common.tmc_command import TMCCommand
from tango import DevState

from ska_tmc_sdpsubarrayleafnode.exceptions import (
    CommandNotAllowed,
    DeviceUnresponsive,
    InvalidObsStateError,
)
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter


class SdpSLNCommand(TMCCommand):
    def check_unresponsive(self):
        component_manager = self.target
        devInfo = component_manager.get_device(
            component_manager.input_parameter.sdp_subarray_dev_name
        )
        if devInfo is None or devInfo.unresponsive:
            raise DeviceUnresponsive("SDP subarray device is not available")

    def check_allowed(self):
        component_manager = self.target

        if isinstance(component_manager.input_parameter, SdpSLNInputParameter):
            result = self.check_allowed_mid()

        return result

    def init_adapters(self):
        component_manager = self.target

        if isinstance(component_manager.input_parameter, SdpSLNInputParameter):
            result, message = self.init_adapters_mid()
        return result, message

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

    def do(self, argin=None):
        component_manager = self.target
        if isinstance(component_manager.input_parameter, SdpSLNInputParameter):
            result = self.do_mid(argin)
        return result


class AbstractTelescopeOnOff(SdpSLNCommand):
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

    def check_allowed_mid(self):
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
                "TelescopeOnOff() is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        self.check_unresponsive()

        return True


class AbstractAssignResources(SdpSLNCommand):
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

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        if self.op_state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            raise CommandNotAllowed(
                "AssignResources command is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        self.check_unresponsive()

        return True


class AbstractReleaseResources(SdpSLNCommand):
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

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
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
                "ReleaseResources command is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        self.check_unresponsive()
        obs_state_val = component_manager.get_device(
            component_manager.input_parameter.sdp_subarray_dev_name
        ).obsState
        self.logger.info("sdp_subarray_obs_state value is: %s", obs_state_val)

        if obs_state_val != ObsState.IDLE:
            self.logger.info(
                "sdp_subarray_obs_state value is: %s", obs_state_val
            )
            raise InvalidObsStateError(
                f"ReleaseResources command is not allowed in current observation state:{obs_state_val}"
            )

        return True


class AbstractConfigure(SdpSLNCommand):
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

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
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
                "Configure command is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        self.check_unresponsive()
        obs_state_val = component_manager.get_device(
            component_manager.input_parameter.sdp_subarray_dev_name
        ).obsState
        if obs_state_val not in (ObsState.READY, ObsState.IDLE):
            raise InvalidObsStateError(
                "Configure command is not allowed in current observation state:{obs_state_val}"
            )

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

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
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
                "Scan and End commands are not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        self.check_unresponsive()

        obs_state_val = component_manager.get_device(
            component_manager.input_parameter.sdp_subarray_dev_name
        ).obsState

        if obs_state_val != ObsState.READY:
            raise InvalidObsStateError(
                f"Scan and End commands are not allowed in current observation state:{obs_state_val}"
            )

        return True


class AbstractEndScan(SdpSLNCommand):
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

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
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
                "EndScan command is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        self.check_unresponsive()

        obs_state_val = component_manager.get_device(
            component_manager.input_parameter.sdp_subarray_dev_name
        ).obsState

        if obs_state_val != ObsState.SCANNING:
            raise InvalidObsStateError(
                f"EndScan command is not allowed in current observation state:{obs_state_val}"
            )

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

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        component_manager = self.target

        if self.op_state_model.op_state in [
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            raise CommandNotAllowed(
                "ObsReset, Restart command is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )
        self.check_unresponsive()

        obs_state_val = component_manager.get_device(
            component_manager.input_parameter.sdp_subarray_dev_name
        ).obsState

        if obs_state_val not in (ObsState.ABORTED, ObsState.FAULT):
            raise InvalidObsStateError(
                f"ObsReset and Restart commands are not allowed in current observation state:{obs_state_val}"
            )

        return True


class AbstractAbort(SdpSLNCommand):
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

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
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
                "Abort command is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        self.check_unresponsive()

        obs_state_val = component_manager.get_device(
            component_manager.input_parameter.sdp_subarray_dev_name
        ).obsState

        if obs_state_val not in (
            ObsState.CONFIGURING,
            ObsState.SCANNING,
            ObsState.IDLE,
            ObsState.READY,
            ObsState.RESETTING,
        ):
            raise InvalidObsStateError(
                f"Abort command is not allowed in current observation state:{obs_state_val}"
            )

        return True


class AbstractReset(SdpSLNCommand):
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

    def check_allowed_mid(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        if self.op_state_model.op_state in [
            DevState.OFF,
            DevState.DISABLE,
            DevState.ON,
        ]:
            raise CommandNotAllowed(
                "Reset command is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        self.check_unresponsive()

        return True
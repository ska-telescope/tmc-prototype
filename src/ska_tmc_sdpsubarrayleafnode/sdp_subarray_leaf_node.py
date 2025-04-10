# pylint: disable=arguments-differ
"""SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution
"""

from typing import List, Tuple, Union

import tango
from ska_control_model import AdminMode, HealthState
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.control_model import ObsState
from ska_tango_base.executor import TaskStatus
from ska_tmc_common.device_info import SdpSubarrayDeviceInfo
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.exceptions import (
    CommandNotAllowed,
    DeviceUnresponsive,
    InvalidObsStateError,
)
from ska_tmc_common.v1.tmc_base_leaf_device import TMCBaseLeafDevice
from tango import ApiUtil, AttrWriteType, DebugIt
from tango.server import attribute, command, device_property, run

from ska_tmc_sdpsubarrayleafnode import release
from ska_tmc_sdpsubarrayleafnode.commands.set_sdp_subarray_admin_mode import (
    SetAdminMode,
)
from ska_tmc_sdpsubarrayleafnode.manager import SdpSLNComponentManager


class SdpSubarrayLeafNode(TMCBaseLeafDevice):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
    actions during an observation.
    """

    def __init__(self, *args, **kwargs):
        self._sdp_subarray_obs_state = ObsState.EMPTY
        self._sdp_subarray_admin_mode = AdminMode.ONLINE
        self._LastDeviceInfoChanged = ""
        self._command_result = ("", "")
        self._issubsystemavailable = False
        super().__init__(*args, **kwargs)

    def init_device(self):
        super().init_device()
        for attribute_name in [
            "sdpSubarrayObsState",
            "longRunningCommandResult",
            "isSubsystemAvailable",
        ]:
            self.set_change_event(attribute_name, True, False)
            self.set_archive_event(attribute_name, True)

    # -----------------
    # Device Properties
    # -----------------
    SdpSubarrayFQDN = device_property(
        dtype="str",
        doc="FQDN of the SDP Subarray Tango Device Server.",
    )
    CommandTimeOut = device_property(dtype="DevFloat", default_value=50)

    SDPSubarrayAdminModeEnabled = device_property(
        dtype=bool,
        doc="Toggle admin mode of SDP subarray leaf node",
        default_value=True,
    )

    # -----------------
    # Attributes
    # -----------------

    isSubsystemAvailable = attribute(
        dtype="DevBoolean",
        access=AttrWriteType.READ,
    )

    lastDeviceInfoChanged = attribute(
        dtype="DevString",
        access=AttrWriteType.READ,
        doc="""Json String representing the last device changed in the
        internal model.""",
    )

    sdpSubarrayDevName = attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
    )

    sdpSubarrayObsState = attribute(
        dtype=ObsState,
        access=AttrWriteType.READ,
    )

    # ---------------
    # General methods
    # ---------------
    def update_device_callback(self, dev_info: SdpSubarrayDeviceInfo) -> None:
        """Updates device callback info"""
        self._LastDeviceInfoChanged = dev_info.to_json()
        self.push_change_archive_events(
            "lastDeviceInfoChanged", dev_info.to_json()
        )

    def update_sdp_subarray_obs_state_callback(
        self, obs_state: ObsState
    ) -> None:
        """Updates SDP Subarray ObsState"""
        self._sdp_subarray_obs_state = obs_state
        self.push_change_archive_events(
            "sdpSubarrayObsState", self._sdp_subarray_obs_state
        )

    def update_lrcr_callback(
        self,
        lrc_result: Tuple[str, Union[ResultCode, TaskStatus, Exception, str]],
    ):
        """Change event callback for longRunningCommandResult"""
        self.push_change_archive_events("longRunningCommandResult", lrc_result)

    def update_availablity_callback(self, availablity):
        """Change event callback for isSubsystemAvailable"""
        if availablity != self._issubsystemavailable:
            self._issubsystemavailable = availablity
            self.push_change_archive_events(
                "isSubsystemAvailable", self._issubsystemavailable
            )

    def update_admin_mode_callback(self, admin_mode: AdminMode) -> None:
        """Update SDP subarray admin mode attribute callback"""
        try:
            self._sdp_subarray_admin_mode = admin_mode
            self.push_change_archive_events(
                "sdpSubarrayAdminMode",
                self._sdp_subarray_admin_mode,
            )
            self.logger.info(
                "Updated and pushed sdpSubarrayAdminMode "
                "attribute value to: %s",
                self._sdp_subarray_admin_mode,
            )
        except Exception as exception:
            self.logger.exception(
                "Exception while pushing event for "
                + "sdpSubarrayAdminMode: %s",
                exception,
            )

    class InitCommand(
        TMCBaseLeafDevice.InitCommand
    ):  # pylint: disable=too-few-public-methods
        """
        A class for the TMC SdpSubarrayLeafNode's init_device() method.
        """

        def do(self, *args, **kwargs) -> Tuple[ResultCode, str]:
            """
            Initializes the attributes and properties of the
            SdpSubarrayLeafNode.

            return:
                A tuple containing a return code and a string message
                indicating status.
                The message is for information purpose only.

            rtype:
                (ResultCode, str)
            """
            super().do()
            device = self._device
            device._build_state = (
                f"{release.name},{release.version},{release.description}"
            )
            device._health_state = HealthState.OK
            device._admin_mode = AdminMode.ONLINE
            device._sdp_subarray_admin_mode = AdminMode.ONLINE
            device._is_admin_mode_enabled = True
            device._version_id = release.version
            for attribute_name in [
                "healthState",
                "sdpSubarrayAdminMode",
                "isAdminModeEnabled",
            ]:
                device.set_change_event(attribute_name, True, False)
            device._isSubsystemAvailable = False
            ApiUtil.instance().set_asynch_cb_sub_model(
                tango.cb_sub_model.PUSH_CALLBACK
            )
            device.op_state_model.perform_action("component_on")
            return (ResultCode.OK, "")

    def always_executed_hook(self):
        pass

    def delete_device(self) -> None:
        # if the init is called more than once
        # I need to stop all threads
        if hasattr(self, "component_manager"):
            self.component_manager.stop()

    # ------------------
    # Attributes methods
    # ------------------

    def read_sdpSubarrayDevName(self) -> str:
        """Return the sdpsubarraydevname attribute."""
        return self.component_manager._sdp_subarray_dev_name

    def write_sdpSubarrayDevName(self, value: str) -> None:
        """Set the sdpsubarraydevname attribute."""
        self.component_manager._sdp_subarray_dev_name = value

    def read_isSubsystemAvailable(self) -> bool:
        """Read method for issubsystemavailable"""
        return self._issubsystemavailable

    def read_lastDeviceInfoChanged(self) -> str:
        """Return the last device info change"""
        return self._LastDeviceInfoChanged

    def read_sdpSubarrayObsState(self) -> ObsState:
        """Reads the current observation state of the SDP subarray"""
        return self._sdp_subarray_obs_state

    @attribute(
        dtype=AdminMode,
        access=AttrWriteType.READ,
        doc="Admin mode of SDP Subarray",
    )
    def sdpSubarrayAdminMode(self) -> AdminMode:
        """Get the current admin mode of SDP Subarray"""
        return self._sdp_subarray_admin_mode

    @attribute(
        dtype=bool,
        access=AttrWriteType.READ_WRITE,
        doc="Get or set the admin mode of SDP Subarray",
    )
    def isAdminModeEnabled(self) -> bool:
        """Get the current admin mode of SDP subarray."""
        return self.component_manager.is_admin_mode_enabled

    @isAdminModeEnabled.write
    def isAdminModeEnabled(self, value: bool) -> None:
        """Set the value of isAdminModeEnabled attribute"""
        self.component_manager.is_admin_mode_enabled = value

    # --------
    # Commands
    # --------

    def is_On_allowed(
        self,
    ) -> Union[
        bool, InvalidObsStateError, DeviceUnresponsive, CommandNotAllowed
    ]:
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device \
        state. \

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("On")

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def On(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This command invokes On() command on SDP Subarray.
        """
        handler = self.get_command_object("On")
        result_code, unique_id = handler()

        return [result_code], [unique_id]

    def is_AssignResources_allowed(self) -> bool:
        """
        Checks whether AssignResources command is allowed to be run in \
        current device state. \

        :return: True if AssignResources command is allowed to be run in \
        current device state.

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("AssignResources")

    @command(
        dtype_in="str",
        doc_in="The string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This command invokes the AssignResources() command on Sdp Subarray.
        """
        handler = self.get_command_object("AssignResources")
        result_code, unique_id = handler(argin)
        return [result_code], [unique_id]

    def is_Configure_allowed(self) -> bool:
        """
        Checks whether Configure command is allowed to be run in \
        current device state. \

        :return: True if Configure command is allowed to be run in \
        current device state \

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("Configure")

    @command(
        dtype_in="str",
        doc_in="The string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def Configure(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This command invokes the Configure() command on Sdp Subarray.
        """
        handler = self.get_command_object("Configure")
        result_code, unique_id = handler(argin)
        return [result_code], [unique_id]

    def is_Scan_allowed(self) -> bool:
        """
        Checks whether Scan command is allowed to be run in \
        current device state. \

        :return: True if Scan command is allowed to be run in \
        current device state \

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("Scan")

    @command(
        dtype_in="str",
        doc_in="The string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def Scan(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This command invokes the Scan() command on Sdp Subarray.
        """
        handler = self.get_command_object("Scan")
        result_code, unique_id = handler(argin)
        return [result_code], [unique_id]

    def is_Off_allowed(self):
        """
        Checks whether this command is allowed to be run in current \
        device state. \

        :return: True if this command is allowed to be run in current \
        device state. \

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("Off")

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def Off(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This command invokes Off() command on SDP Subarray.
        """
        handler = self.get_command_object("Off")
        result_code, unique_id = handler()

        return [result_code], [unique_id]

    def is_ReleaseAllResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device
        state.

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("ReleaseAllResources")

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def ReleaseAllResources(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This command invokes ReleaseAllResources() command on Sdp
        Subarray.
        """

        handler = self.get_command_object("ReleaseAllResources")
        return_code, unique_id = handler()

        return [return_code], [str(unique_id)]

    def is_End_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device
        state.

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("End")

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def End(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This command invokes End() command on Sdp
        Subarray.
        """

        handler = self.get_command_object("End")
        return_code, unique_id = handler()

        return [return_code], [str(unique_id)]

    def is_EndScan_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean
        """
        return self.component_manager.is_command_allowed("EndScan")

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def EndScan(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes EndScan command on Sdp Subarray.

        """
        handler = self.get_command_object("EndScan")
        return_code, unique_id = handler()
        return [return_code], [str(unique_id)]

    def is_Abort_allowed(self) -> bool:
        """
        Checks whether Abort command is allowed to be run in current device
        state

        return:
         True if Abort command is allowed to be run in current device state

        rtype:
            boolean

        """
        return self.component_manager.is_command_allowed("Abort")

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def Abort(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invoke Abort command on Sdp Subarray.
        """
        handler = self.get_command_object("Abort")
        result_code, unique_id = handler()
        return ([result_code], [unique_id])

    def is_Restart_allowed(self) -> bool:
        """
        Checks whether Restart command is allowed to be run in current device
         state

         return:
             True if Restart command is allowed to be run in current device
             state

         rtype:
             boolean

        """
        return self.component_manager.is_command_allowed("Restart")

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def Restart(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invoke Restart command on Sdp Subarray.
        """
        handler = self.get_command_object("Restart")
        result_code, unique_id = handler()
        return ([result_code], [unique_id])

    @command(
        dtype_in=AdminMode,
        doc_in="The adminMode in enum format",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def SetAdminMode(self, argin: AdminMode):
        """
        This command sets the adminMode command on SDP Subarray.
        """
        handler = self.get_command_object("SetAdminMode")
        result_code, message = handler(argin)

        return [result_code], [message]

    # default ska mid
    def create_component_manager(self):
        """Returns Sdp Subarray Leaf Node component manager object"""
        cm = SdpSLNComponentManager(
            _update_admin_mode_callback=self.update_admin_mode_callback,
            _sdp_subarray_admin_mode_enabled=self.SDPSubarrayAdminModeEnabled,
            sdp_subarray_dev_name=self.SdpSubarrayFQDN,
            logger=self.logger,
            _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE,
            _event_receiver=True,
            _update_sdp_subarray_obs_state_callback=(
                self.update_sdp_subarray_obs_state_callback
            ),
            _update_lrcr_callback=self.update_lrcr_callback,
            event_subscription_check_period=self.EventSubscriptionCheckPeriod,
            liveliness_check_period=self.LivelinessCheckPeriod,
            adapter_timeout=self.AdapterTimeOut,
            _update_availablity_callback=self.update_availablity_callback,
            command_timeout=self.CommandTimeOut,
        )
        return cm

    # pylint: disable=unexpected-keyword-arg
    def init_command_objects(self) -> None:
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()

        for command_name, method_name in [
            ("On", "on"),
            ("Off", "off"),
            ("AssignResources", "assign_resources"),
            ("Configure", "configure"),
            ("Scan", "scan"),
            ("EndScan", "end_scan"),
            ("End", "end"),
            ("Restart", "restart"),
            ("ReleaseAllResources", "release_all_resources"),
        ]:
            self.register_command_object(
                command_name,
                SubmittedSlowCommand(
                    command_name,
                    self._command_tracker,
                    self.component_manager,
                    method_name,
                    logger=None,
                ),
            )

        # as per base classes implementation, for SKABaseDevice
        # Abort is registered as AbortCommand
        self.register_command_object(
            "Abort",
            self.AbortCommand(
                self._command_tracker,
                self.component_manager,
                None,
                self.logger,
            ),
        )
        self.register_command_object(
            "SetAdminMode", SetAdminMode(self.logger, self.component_manager)
        )


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the SdpSubarrayLeafNode Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((SdpSubarrayLeafNode,), args=args, **kwargs)


if __name__ == "__main__":
    main()

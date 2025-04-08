"""
SDP Master Leaf node acts as a SDP contact point for the Master Node and also
monitors and issues commands to the SDP Master.
"""

from typing import Union

from ska_control_model import AdminMode, HealthState
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.exceptions import CommandNotAllowed, DeviceUnresponsive
from ska_tmc_common.v1.tmc_base_leaf_device import TMCBaseLeafDevice
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, device_property, run

from ska_tmc_sdpmasterleafnode.commands.set_controller_admin_mode import (
    SetAdminMode,
)
from ska_tmc_sdpmasterleafnode.manager import SdpMLNComponentManager
from ska_tmc_sdpmasterleafnode.release import description, name, version

__all__ = ["TmcLeafNodeSdp", "main"]


class TmcLeafNodeSdp(TMCBaseLeafDevice):
    """
    SDP Master Leaf node acts as a SDP contact point for Master Node and
    also to monitor
    and issue commands to the SDP Master.
    """

    # -----------------
    # Device Properties
    # -----------------
    SdpMasterFQDN = device_property(
        dtype="str",
        doc="FQDN of the SDP Master Tango Device Server.",
    )

    SDPMasterAdminModeEnabled = device_property(
        dtype=bool,
        doc="Toggle admin mode of SDP master leaf node",
        default_value=True,
    )

    # -----------------
    # Attributes
    # -----------------

    isSubsystemAvailable = attribute(
        dtype="DevBoolean",
        access=AttrWriteType.READ,
    )

    sdpMasterDevName = attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
    )

    # ---------------
    # General methods
    # ---------------

    def __init__(self, *args, **kwargs):
        self._issubsystemavailable: bool = False
        super().__init__(*args, **kwargs)

    class InitCommand(TMCBaseLeafDevice.InitCommand):
        """
        A class for the TMC SdpMasterLeafNode's init_device() method.
        """

        # pylint: disable= arguments-differ
        def do(self):
            """
            Initializes the attributes and properties of the SdpMasterLeafNode.

            return:
                A tuple containing a return code and a string message
                indicating status.
                The message is for information purpose only.

            rtype:
                (ResultCode, str)
            """
            super().do()
            device = self._device

            device._build_state = f"{name},{version},{description}"
            device._admin_mode = AdminMode.ONLINE
            device._sdp_master_admin_mode = AdminMode.ONLINE
            device._health_state = HealthState.OK
            device._version_id = version
            device._issubsystemavailable = False
            device.op_state_model.perform_action("component_on")
            for attribute_name in [
                "healthState",
                "isSubsystemAvailable",
                "sdpControllerAdminMode",
                "isAdminModeEnabled",
            ]:
                device.set_change_event(attribute_name, True, False)
                device.set_archive_event(attribute_name, True)
            return (ResultCode.OK, "")

    def always_executed_hook(self):
        pass

    # ------------------
    # Attributes methods
    # ------------------
    def update_availablity_callback(self, availablity: bool) -> None:
        """Change event callback for isSubsystemAvailable"""
        if availablity != self._issubsystemavailable:
            self._issubsystemavailable = availablity
            self.push_change_archive_events(
                "isSubsystemAvailable", self._issubsystemavailable
            )

    def update_admin_mode_callback(self, admin_mode: AdminMode):
        """Update SDPMLNAdminMode attribute callback"""
        # pylint:disable=attribute-defined-outside-init
        self._sdp_master_admin_mode = admin_mode

        try:
            self.push_change_archive_events(
                "sdpControllerAdminMode",
                AdminMode(admin_mode),
            )
            self.logger.info(
                "Successfully updated and "
                "sdpControllerAdminMode attribute value is set to: %s",
                self._sdp_master_admin_mode,
            )
        except Exception as exception:
            self.logger.exception(
                "Exception while pushing event for "
                + "sdpControllerAdminMode: %s",
                exception,
            )

    def read_isSubsystemAvailable(self) -> bool:
        """Returns the TMC Sdp MasterLeafNode
        isSubsystemAvailable attribute."""
        return self._issubsystemavailable

    def read_sdpMasterDevName(self) -> str:
        """Return the sdpmasterdevname attribute."""
        return self.component_manager.sdp_master_device_name

    def write_sdpMasterDevName(self, value: str) -> None:
        """Set the sdpmasterdevname attribute."""
        self.component_manager.sdp_master_device_name = value

    @attribute(
        dtype=AdminMode,
        access=AttrWriteType.READ,
        doc="Admin mode of SDP controller",
    )
    def sdpControllerAdminMode(self) -> AdminMode:
        """Read the admin mode of SDP Controller"""
        return self._sdp_master_admin_mode

    @attribute(
        dtype=bool,
        access=AttrWriteType.READ_WRITE,
        doc="Get or set the admin mode of SDP controller",
    )
    def isAdminModeEnabled(self) -> bool:
        """Get the current admin mode of SDP controller."""
        return self.component_manager.is_admin_mode_enabled

    @isAdminModeEnabled.write
    def isAdminModeEnabled(self, value: bool) -> None:
        """Set the value of isAdminModeEnabled attribute"""
        self.component_manager.is_admin_mode_enabled = value

    # --------
    # Commands
    # --------

    def is_Off_allowed(
        self,
    ) -> Union[bool, CommandNotAllowed, DeviceUnresponsive]:
        """
        Checks whether this command is allowed to be run in current
        device state.

        :return: True if this command is allowed to be run in current device
            state.

        :rtype: bool,CommandNotAllowed,DeviceUnresponsive
        """
        return self.component_manager.is_command_allowed("Off")

    @command(
        dtype_in=AdminMode,
        doc_in="The adminMode in enum format",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def SetAdminMode(self, argin: AdminMode):
        """
        This command sets the adminMode command on SDP Controller.
        """
        handler = self.get_command_object("SetAdminMode")
        result_code, message = handler(argin)

        return [result_code], [message]

    @command(dtype_out="DevVarLongStringArray")
    def Off(self):
        """
        This command invokes Off() command on Sdp Master.
        """
        handler = self.get_command_object("Off")
        return_code, unique_id = handler()
        return [[return_code], [str(unique_id)]]

    def is_On_allowed(
        self,
    ) -> Union[bool, CommandNotAllowed, DeviceUnresponsive]:
        """
        Checks whether this command is allowed to be run in current device
            state.

        :return: True if this command is allowed to be run in current device
            state.

        :rtype: bool,CommandNotAllowed,DeviceUnresponsive
        """
        return self.component_manager.is_command_allowed("On")

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def On(self):
        """
        This command invokes On() command on Sdp Master.
        """
        handler = self.get_command_object("On")
        return_code, unique_id = handler()
        return [[return_code], [str(unique_id)]]

    def is_Standby_allowed(
        self,
    ) -> Union[bool, CommandNotAllowed, DeviceUnresponsive]:
        """
        Checks whether this command is allowed to be run in current device
        state.

        :return: True if this command is allowed to be
            run in current device state.

        :rtype: bool,CommandNotAllowed,DeviceUnresponsive
        """
        return self.component_manager.is_command_allowed("Standby")

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def Standby(self):
        """
        This command invokes Standby() command on Sdp Master.
        """
        handler = self.get_command_object("Standby")
        return_code, unique_id = handler()
        return [[return_code], [str(unique_id)]]

    def is_Disable_allowed(
        self,
    ) -> Union[bool, CommandNotAllowed, DeviceUnresponsive]:
        """
        Checks whether this command is allowed to be run in current device
        state.

        :return: True if this command is allowed to be
            run in current device state.

        :rtype: bool,CommandNotAllowed,DeviceUnresponsive
        """
        return self.component_manager.is_command_allowed("Disable")

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def Disable(self):
        """
        This command invokes Disable() command on Sdp Master.
        """
        handler = self.get_command_object("Disable")
        result_code, unique_id = handler()

        return [[result_code], [unique_id]]

        # default ska mid

    # pylint: disable=attribute-defined-outside-init
    def create_component_manager(self):
        """Returns Sdp Master Leaf Node component manager object"""
        component_manager = SdpMLNComponentManager(
            sdp_master_admin_mode_enabled=self.SDPMasterAdminModeEnabled,
            _update_admin_mode_callback=self.update_admin_mode_callback,
            sdp_master_device_name=self.SdpMasterFQDN,
            logger=self.logger,
            _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE,
            _event_receiver=True,
            event_subscription_check_period=self.EventSubscriptionCheckPeriod,
            liveliness_check_period=self.LivelinessCheckPeriod,
            adapter_timeout=self.AdapterTimeOut,
            _update_availablity_callback=self.update_availablity_callback,
        )
        component_manager.sdp_master_device_name = self.SdpMasterFQDN or ""
        return component_manager

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()
        for command_name, method_name in [
            ("On", "on"),
            ("Off", "off"),
            ("Standby", "standby"),
            ("Disable", "disable"),
        ]:
            self.register_command_object(
                command_name,
                SubmittedSlowCommand(
                    command_name,
                    self._command_tracker,
                    self.component_manager,
                    method_name,
                    logger=self.logger,
                ),
            )

            self.register_command_object(
                "SetAdminMode",
                SetAdminMode(self.logger, self.component_manager),
            )


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the TmcLeafNodeSdp.

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: TmcLeafNodeSdp TANGO object.
    """
    return run((TmcLeafNodeSdp,), args=args, **kwargs)


if __name__ == "__main__":
    main()

"""
SDP Master Leaf node acts as a SDP contact point for Master Node and also to monitor
and issue commands to the SDP Master.
"""
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tmc_common.op_state_model import TMCOpStateModel
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, device_property, run

from ska_tmc_sdpmasterleafnode import release
from ska_tmc_sdpmasterleafnode.commands import TelescopeOn, TelescopeOff, TelescopeStandby, Disable
from ska_tmc_sdpmasterleafnode.manager import (
    SdpMLNComponentManager,
)

__all__ = ["SdpMasterLeafNode", "main"]


class SdpMasterLeafNode(SKABaseDevice):
    """
    SDP Master Leaf node acts as a SDP contact point for Master Node and also to monitor
    and issue commands to the SDP Master.
    """

    # -----------------
    # Device Properties
    # -----------------
    SdpMasterFQDN = device_property(
        default_value="mid_sdp/elt/master",
        dtype="str",
        doc="FQDN of the SDP Master Tango Device Server.",
    )

    # -----------------
    # Attributes
    # -----------------
    commandExecuted = attribute(
        dtype=(("DevString",),),
        max_dim_x=4,
        max_dim_y=100,
    )

    lastDeviceInfoChanged = attribute(
        dtype="DevString",
        access=AttrWriteType.READ,
        doc="Json String representing the last device changed in the internal model.",
    )

    sdpMasterDevName = attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
    )

    SleepTime = device_property(dtype="DevFloat", default_value=1)
    # ---------------
    # General methods
    # ---------------

    def update_device_callback(self, devInfo):
        self._LastDeviceInfoChanged = devInfo.to_json()
        self.push_change_event("lastDeviceInfoChanged", devInfo.to_json())

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC SdpMasterLeafNode's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the SdpMasterLeafNode.

            return:
                A tuple containing a return code and a string message indicating status.
                The message is for information purpose only.

            rtype:
                (ResultCode, str)
            """
            super().do()
            device = self.target

            device._build_state = "{},{},{}".format(
                release.name, release.version, release.description
            )
            device._version_id = release.version
            device._LastDeviceInfoChanged = ""

            device.op_state_model.perform_action("component_on")
            device.component_manager._command_executor.add_command_execution(
                "0", "Init", ResultCode.OK, ""
            )
            return (ResultCode.OK, "")

    def always_executed_hook(self):
        pass

    def delete_device(self):
        # if the init is called more than once
        # I need to stop all threads
        if hasattr(self, "component_manager"):
            self.component_manager.stop()

    # ------------------
    # Attributes methods
    # ------------------

    def read_sdpMasterDevName(self):
        """Return the sdpmasterdevname attribute."""
        return self.component_manager._sdp_master_dev_name

    def write_sdpMasterDevName(self, value):
        """Set the sdpmasterdevname attribute."""
        # self.component_manager._sdp_master_dev_name = value
        self.component_manager.update_device_info(value)

    def read_lastDeviceInfoChanged(self):
        return self._LastDeviceInfoChanged

    def read_commandExecuted(self):
        """Return the commandExecuted attribute."""
        result = []
        i = 0
        for command_executed in reversed(
            self.component_manager._command_executor.command_executed
        ):
            if i == 100:
                break
            single_res = [
                str(command_executed["Id"]),
                str(command_executed["Command"]),
                str(command_executed["ResultCode"]),
                str(command_executed["Message"]),
            ]
            result.append(single_res)
            i += 1
        return result

    # --------
    # Commands
    # --------

    def is_TelescopeOff_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("TelescopeOff")
        return handler.check_allowed()

    @command(dtype_out="DevVarLongStringArray")
    def TelescopeOff(self):
        """
        This command invokes Off() command on Sdp Master.
        """
        handler = self.get_command_object("TelescopeOff")
        if self.component_manager._command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager._command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_TelescopeOn_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("TelescopeOn")
        return handler.check_allowed()

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def TelescopeOn(self):
        """
        This command invokes On() command on Sdp Master.
        """
        handler = self.get_command_object("TelescopeOn")
        if self.component_manager._command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager._command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_TelescopeStandby_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("TelescopeStandby")
        return handler.check_allowed()

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def TelescopeStandby(self):
        """
        This command invokes Standby() command on Sdp Master.
        """
        handler = self.get_command_object("TelescopeStandby")
        if self.component_manager._command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager._command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Disable_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("Disable")
        return handler.check_allowed()

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def Disable(self):
        """
        This command invokes Disable() command on Sdp Master.
        """
        handler = self.get_command_object("Disable")
        if self.component_manager._command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager._command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    # default ska mid
    def create_component_manager(self):
        self.op_state_model = TMCOpStateModel(
            logger=self.logger, callback=super()._update_state
        )
        # sdp_master_dev_name = self.SdpMasterFQDN or ""
        cm = SdpMLNComponentManager(
            self.SdpMasterFQDN,
            self.op_state_model,
            logger=self.logger,
            sleep_time=self.SleepTime,
        )

        return cm

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()
        args = ()
        for (command_name, command_class) in [
            ("TelescopeOn", TelescopeOn),
            ("TelescopeOff", TelescopeOff),
            ("TelescopeStandby", TelescopeStandby),
            ("Disable", Disable),
        ]:
            command_obj = command_class(
                self.component_manager,
                self.op_state_model,
                *args,
                logger=self.logger,
            )
            self.register_command_object(command_name, command_obj)


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the SdpMasterLeafNodeMid.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: SdpMasterLeafNodeMid TANGO object.
    """
    return run((SdpMasterLeafNode,), args=args, **kwargs)


if __name__ == "__main__":
    main()

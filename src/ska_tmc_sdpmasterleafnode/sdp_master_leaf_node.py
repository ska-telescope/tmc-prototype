"""
SDP Master Leaf node acts as a SDP contact point for the Master Node and also
monitors and issues commands to the SDP Master.
"""
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tmc_common.adapters import AdapterFactory
from ska_tmc_common.enum import LivelinessProbeType
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, device_property, run

from ska_tmc_sdpmasterleafnode import release
from ska_tmc_sdpmasterleafnode.manager import SdpMLNComponentManager

__all__ = ["SdpMasterLeafNode", "main"]


class SdpMasterLeafNode(SKABaseDevice):
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

    # -----------------
    # Attributes
    # -----------------

    isSubsystemAvailable = attribute(
        dtype="DevBoolean",
        access=AttrWriteType.READ,
    )

    # commandExecuted = attribute(
    #     dtype=(("DevString",),),
    #     max_dim_x=4,
    #     max_dim_y=100,
    # )

    sdpMasterDevName = attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
    )
    SleepTime = device_property(dtype="DevFloat", default_value=1)
    TimeOut = device_property(dtype="DevFloat", default_value=2)
    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC SdpMasterLeafNode's init_device() method.
        """

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

            device._build_state = (
                f"{release.name},{release.version},{release.description}"
            )
            device._version_id = release.version
            device.set_change_event("healthState", True, False)
            device._isSubsystemAvailable = False
            device.op_state_model.perform_action("component_on")
            # device.component_manager._command_executor.add_command_execution(
            #     "0", "Init", ResultCode.OK, ""
            # )
            device.set_change_event("isSubsystemAvailable", True, False)
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

    def update_availablity_callback(self, availablity):
        """Change event callback for isSubsystemAvailable"""
        self._isSubsystemAvailable = availablity  # pylint: disable=W0201
        self.push_change_event("isSubsystemAvailable", availablity)

    def read_isSubsystemAvailable(self):
        """Returns the TMC Sdp MasterLeafNode
        isSubsystemAvailable attribute."""
        return self._isSubsystemAvailable

    def read_sdpMasterDevName(self):
        """Return the sdpmasterdevname attribute."""
        return self.component_manager.sdp_master_dev_name

    def write_sdpMasterDevName(self, value):
        """Set the sdpmasterdevname attribute."""
        self.component_manager.sdp_master_dev_name = value

    # --------
    # Commands
    # --------

    def is_Off_allowed(self):
        """
        Checks whether this command is allowed to be run in current \
        device state. \

        :return: True if this command is allowed to be run in current device \
        state. \

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("Off")

    @command(dtype_out="DevVarLongStringArray")
    def Off(self):
        """
        This command invokes Off() command on Sdp Master.
        """
        handler = self.get_command_object("On")
        return_code, message = handler()
        return return_code, message

    def is_On_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device \
        state. \

        :rtype: boolean
        """
        # handler = self.get_command_object("On")
        # return handler.check_allowed()
        return self.component_manager.is_command_allowed("On")

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def On(self):
        """
        This command invokes On() command on Sdp Master.
        """
        handler = self.get_command_object("On")
        return_code, message = handler()
        # if self.component_manager._command_executor.queue_full:
        #     message = """The invocation of the On command on this device
        #     failed.
        #     Reason: The command executor rejected the queuing of the command
        #     because its queue is full.
        #     The On command has NOT been queued and will not be executed.
        #     This device will continue with normal operation."""
        #     return [[ResultCode.FAILED], [message]]
        # unique_id = self.component_manager._command_executor.enqueue_command(
        #     handler
        # )
        # return [[ResultCode.QUEUED], [str(unique_id)]]
        return return_code, message

    # TODO : Will get Uncommented after refactoring for command is done.
    def is_Standby_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device \
        state. \

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("Standby")

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def Standby(self):
        """
        This command invokes Standby() command on Sdp Master.
        """
        handler = self.get_command_object("Standby")
        result_code, unique_id = handler()

        return [[result_code], [unique_id]]

    def is_Disable_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device \
        state. \

        :rtype: boolean
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
        _adapter_factory = AdapterFactory()
        cm = SdpMLNComponentManager(
            self.SdpMasterFQDN,
            _adapter_factory=_adapter_factory,
            logger=self.logger,
            _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE,
            _event_receiver=False,
            sleep_time=self.SleepTime,
            timeout=self.TimeOut,
            _update_availablity_callback=self.update_availablity_callback,
        )

        return cm

    # pylint: enable=attribute-defined-outside-init

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()
        for command_name, method_name in [
            ("On", "on_command"),
            ("Off", "off_command"),
            ("Standby", "standby_command"),
            ("Disable", "disable_command"),
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

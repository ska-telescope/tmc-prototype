"""
SDP Master Leaf node is to monitor the SDP Master and issue control actions during an observation.
It also acts as a SDP contact point for Master Node for observation execution
"""

from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tmc_common.op_state_model import TMCOpStateModel
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, device_property

from ska_tmc_sdpmasterleafnode import release
from ska_tmc_sdpmasterleafnode.manager.component_manager import (
    SdpMLNComponentManager,
)
from ska_tmc_sdpmasterleafnode.model.input import SdpMLNInputParameter


class AbstractSdpMasterLeafNode(SKABaseDevice):
    """
    SDP Master Leaf node is to monitor the SDP Master and issue control actions during an observation.

    """

    # -----------------
    # Device Properties
    # -----------------
    SdpMasterFQDN = device_property(
        dtype="str", doc="FQDN of the SDP Master Tango Device Server."
    )

    # -----------------
    # Attributes
    # -----------------
    commandExecuted = attribute(
        dtype=(("DevString",),),
        max_dim_x=4,
        max_dim_y=100,
    )

    

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

    # default ska mid
    def create_component_manager(self):
        self.op_state_model = TMCOpStateModel(
            logger=self.logger, callback=super()._update_state
        )
        cm = SdpMLNComponentManager(
            self.op_state_model,
            _input_parameter=SdpMLNInputParameter(None),
            logger=self.logger,
            sleep_time=self.SleepTime,
        )
        cm.input_parameter.sdp_master_dev_name = self.SdpMasterFQDN or ""
        cm.update_input_parameter()
        return cm

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()

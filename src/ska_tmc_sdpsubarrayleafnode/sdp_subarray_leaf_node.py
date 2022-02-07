"""
SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution
"""

from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tmc_common.op_state_model import TMCOpStateModel
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, device_property

from ska_tmc_sdpsubarrayleafnode import release
from ska_tmc_sdpsubarrayleafnode.manager.component_manager import (
    SdpSLNComponentManager,
)

# from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter


class AbstractSdpSubarrayLeafNode(SKABaseDevice):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.

    """

    # -----------------
    # Device Properties
    # -----------------
    SdpSubarrayFQDN = device_property(
        dtype="str", doc="FQDN of the SDP Subarray Tango Device Server."
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

    # ---------------
    # General methods
    # ---------------

    def update_device_callback(self, devInfo):
        self._LastDeviceInfoChanged = devInfo.to_json()
        self.push_change_event("lastDeviceInfoChanged", devInfo.to_json())

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC SdpSubarrayLeafNode's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the SdpSubarrayLeafNode.

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
            device.component_manager.command_executor.add_command_execution(
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

    def read_lastDeviceInfoChanged(self):
        return self._LastDeviceInfoChanged

    def read_commandExecuted(self):
        """Return the commandExecuted attribute."""
        result = []
        i = 0
        for command_executed in reversed(
            self.component_manager.command_executor.command_executed
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
        This command invokes Off() command on Sdp Subarray.
        """
        handler = self.get_command_object("TelescopeOff")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
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
        This command invokes On() command on Sdp Subarray.
        """
        handler = self.get_command_object("TelescopeOn")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_AssignResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean
        """
        handler = self.get_command_object("AssignResources")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="The string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        This command invokes the AssignResources() command on Sdp Subarray..
        """
        handler = self.get_command_object("AssignResources")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler, argin
        )
        print(
            ":::::::unique id after Assign Resources command:::::::::::::::",
            unique_id,
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_ReleaseResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("ReleaseResources")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def ReleaseResources(self):
        """
        This command invokes ReleaseResources() command on command on Sdp Subarray.
        """
        handler = self.get_command_object("ReleaseResources")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Configure_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        return:
            True if this command is allowed to be run in current device state

        rtype:
            boolean

        """
        handler = self.get_command_object("Configure")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="The string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def Configure(self, argin):
        """
        Invokes Configure command on Sdp Subarray.
        """
        handler = self.get_command_object("Configure")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler, argin
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Scan_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean

        """
        handler = self.get_command_object("Scan")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="The JSON input string consists of SB ID.",
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def Scan(self, argin):
        """Invoke Scan command on Sdp Subarray."""

        handler = self.get_command_object("Scan")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler, argin
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_EndScan_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.
        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean
        """
        handler = self.get_command_object("EndScan")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def EndScan(self):
        """
        Invokes EndScan command on Sdp Subarray.

        """
        handler = self.get_command_object("EndScan")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_End_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean

        """
        handler = self.get_command_object("End")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def End(self):
        """This command invokes End command on Sdp Subarray to end the current Scheduling block."""
        handler = self.get_command_object("End")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_ObsReset_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        return:
            True if this command is allowed to be run in current device state

        rtype:
            boolean

        """
        handler = self.get_command_object("ObsReset")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def ObsReset(self):
        """
        Invoke ObsReset command on Sdp Subarray.
        """
        handler = self.get_command_object("ObsReset")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Abort_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        return:
            True if this command is allowed to be run in current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("Abort")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def Abort(self):
        """
        Invoke Abort command on Sdp Subarray.
        """
        handler = self.get_command_object("Abort")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Restart_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        return:
            True if this command is allowed to be run in current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("Restart")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def Restart(self):
        """
        Invoke Restart command on Sdp Subarray.
        """
        handler = self.get_command_object("Restart")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    # default ska mid
    def create_component_manager(self):
        self.op_state_model = TMCOpStateModel(
            logger=self.logger, callback=super()._update_state
        )
        cm = SdpSLNComponentManager(
            self.op_state_model,
            # _input_parameter=SdpSLNInputParameter(None),
            logger=self.logger,
            # _update_device_callback=self.update_device_callback,
            sleep_time=self.SleepTime,
        )
        cm._sdp_subarray_dev_name = self.SdpSubarrayFQDN or ""
        # cm.update_input_parameter()
        return cm

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()

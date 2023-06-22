# pylint: disable=arguments-differ, no-value-for-parameter
"""
SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution
"""

# pylint: disable=attribute-defined-outside-init
import tango
from ska_control_model import HealthState
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.control_model import ObsState
from ska_tmc_common.enum import LivelinessProbeType
from tango import ApiUtil, AttrWriteType, DebugIt
from tango.server import attribute, command, device_property, run

from ska_tmc_sdpsubarrayleafnode import release
from ska_tmc_sdpsubarrayleafnode.manager import SdpSLNComponentManager


class SdpSubarrayLeafNode(SKABaseDevice):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
    actions during an observation.
    """

    def init_device(self):
        super().init_device()
        self._sdp_subarray_obs_state = ObsState.EMPTY
        self.set_change_event("sdpSubarrayObsState", True)
        self._command_result = ("", "")
        self.set_change_event("longRunningCommandResult", True)
        self._issubsystemavailable = False
        self.set_change_event("isSubsystemAvailable", True, False)

    # -----------------
    # Device Properties
    # -----------------
    SdpSubarrayFQDN = device_property(
        dtype="str", doc="FQDN of the SDP Subarray Tango Device Server."
    )

    SleepTime = device_property(dtype="DevFloat", default_value=1)
    TimeOut = device_property(dtype="DevFloat", default_value=2)

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

    # pylint: disable=attribute-defined-outside-init
    def update_device_callback(self, dev_info):
        """Updates device callback info"""
        self._LastDeviceInfoChanged = dev_info.to_json()
        self.push_change_event("lastDeviceInfoChanged", dev_info.to_json())

    # pylint: disable=attribute-defined-outside-init
    def update_sdp_subarray_obs_state_callback(
        self, obs_state: ObsState
    ) -> None:
        """Updates SDP Subarray ObsState"""
        self._sdp_subarray_obs_state = obs_state
        self.push_change_event(
            "sdpSubarrayObsState", self._sdp_subarray_obs_state
        )

    def update_lrcr_callback(self, lrc_result):
        """Change event callback for longRunningCommandResult"""
        self.push_change_event("longRunningCommandResult", lrc_result)

    def update_availablity_callback(self, availablity):
        """Change event callback for isSubsystemAvailable"""
        if availablity != self._issubsystemavailable:
            self._issubsystemavailable = availablity
            self.push_change_event(
                "isSubsystemAvailable", self._issubsystemavailable
            )

    class InitCommand(
        SKABaseDevice.InitCommand
    ):  # pylint: disable=too-few-public-methods
        """
        A class for the TMC SdpSubarrayLeafNode's init_device() method.
        """

        def do(self, *args, **kwargs) -> tuple:
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
            device._version_id = release.version
            device._LastDeviceInfoChanged = ""
            device.set_change_event("healthState", True, False)
            device._isSubsystemAvailable = False
            ApiUtil.instance().set_asynch_cb_sub_model(
                tango.cb_sub_model.PUSH_CALLBACK
            )
            device.op_state_model.perform_action("component_on")
            return (ResultCode.OK, "")

    def always_executed_hook(self):
        pass

    def delete_device(self):
        # if the init is called more than once
        # I need to stop all threads
        if hasattr(self, "component_manager"):
            self.component_manager.stop()

    def read_sdpSubarrayDevName(self):
        """Return the sdpsubarraydevname attribute."""
        # return self.component_manager.sdp_subarray_dev_name
        return self.component_manager._sdp_subarray_dev_name

    def write_sdpSubarrayDevName(self, value):
        """Set the sdpsubarraydevname attribute."""
        # self.component_manager.sdp_subarray_dev_name = value
        self.component_manager.update_device_info(value)

    # ------------------
    # Attributes methods
    # ------------------

    def read_isSubsystemAvailable(self):
        """Read method for issubsystemavailable"""
        return self._issubsystemavailable

    def read_lastDeviceInfoChanged(self):
        """Return the last device info change"""
        return self._LastDeviceInfoChanged

    def read_sdpSubarrayObsState(self):
        """Reads the current observation state of the SDP subarray"""
        return self._sdp_subarray_obs_state

    # --------
    # Commands
    # --------

    def is_On_allowed(self):
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
    def On(self):
        """
        This command invokes On() command on SDP Subarray.
        """
        handler = self.get_command_object("On")
        result_code, unique_id = handler()

        return [result_code], [unique_id]

    # This code will be enabled as part of SP-3237
    # def is_Off_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current \
    #     device state. \

    #     :return: True if this command is allowed to be run in current \
    #     device state. \

    #     :rtype: boolean
    #     """
    #     handler = self.get_command_object("Off")
    #     return handler.check_allowed()

    # @command(dtype_out="DevVarLongStringArray")
    # def Off(self):
    #     """
    #     This command invokes Off() command on Sdp Subarray.
    #     """
    #     handler = self.get_command_object("Off")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"Off\" command on this device
    #         failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"Off\" command has NOT been queued and will not be executed.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.command_executor.enqueue_command(
    #         handler
    #     )
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # def is_AssignResources_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current device \
    #     state. \

    #     :return: True if this command is allowed to be run in current device
    #     state \

    #     :rtype: boolean
    #     """
    #     handler = self.get_command_object("AssignResources")
    #     return handler.check_allowed()

    # @command(
    #     dtype_in="str",
    #     doc_in="The string in JSON format",
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="information-only string",
    # )
    # @DebugIt()
    # def AssignResources(self, argin):
    #     """
    #     This command invokes the AssignResources() command on Sdp Subarray..
    #     """
    #     handler = self.get_command_object("AssignResources")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"AssignResources\"command on
    #         this device failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"AssignResources\" command has NOT been queued and will not
    #         be executed.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.add_to_queue(handler, argin)
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # def is_ReleaseResources_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current device \
    #     state. \

    #     :return: True if this command is allowed to be run in current device
    #     state.

    #     :rtype: boolean
    #     """
    #     handler = self.get_command_object("ReleaseResources")
    #     return handler.check_allowed()

    # @command(
    #     dtype_in="str",
    #     doc_in="The string in JSON format",
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="information-only string",
    # )
    # @DebugIt()
    # def ReleaseResources(self, argin):
    #     """
    #     This command invokes ReleaseResources() command on command on Sdp
    #     Subarray.
    #     """
    #     handler = self.get_command_object("ReleaseResources")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"ReleaseResources\"commandon
    #         this device failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"ReleaseResources\" command has NOT been queued and willnot
    #         be executed.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.command_executor.enqueue_command(
    #         handler, argin
    #     )
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # def is_Configure_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current device \
    #     state \

    #     return:
    #         True if this command is allowed to be run in current devicestate

    #     rtype:
    #         boolean

    #     """
    #     handler = self.get_command_object("Configure")
    #     return handler.check_allowed()

    # @command(
    #     dtype_in="str",
    #     doc_in="The string in JSON format",
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="information-only string",
    # )
    # @DebugIt()
    # def Configure(self, argin):
    #     """
    #     Invokes Configure command on Sdp Subarray.
    #     """
    #     handler = self.get_command_object("Configure")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"Configure\" command on this
    #         device failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"Configure\" command has NOT been queued and will not be
    #         executed.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.command_executor.enqueue_command(
    #         handler, argin
    #     )
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # def is_Scan_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current device \
    #     state. \

    #     return:
    #         True if this command is allowed to be run in currentdevicestate.

    #     rtype:
    #         boolean

    #     """
    #     handler = self.get_command_object("Scan")
    #     return handler.check_allowed()

    # @command(
    #     dtype_in="str",
    #     doc_in="The JSON input string consists of SB ID.",
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="information-only string",
    # )
    # @DebugIt()
    # def Scan(self, argin):
    #     """Invoke Scan command on Sdp Subarray."""

    #     handler = self.get_command_object("Scan")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"Scan\" commandonthis device
    #         failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"Scan\" command has NOT been queued and will notbeexecuted.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.command_executor.enqueue_command(
    #         handler, argin
    #     )
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # def is_EndScan_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current device \
    #     state. \

    #     return:
    #         True if this command is allowed to be run in currentdevicestate.

    #     rtype:
    #         boolean
    #     """
    #     handler = self.get_command_object("EndScan")
    #     return handler.check_allowed()

    # @command(
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="information-only string",
    # )
    # @DebugIt()
    # def EndScan(self):
    #     """
    #     Invokes EndScan command on Sdp Subarray.

    #     """
    #     handler = self.get_command_object("EndScan")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"EndScan\" command on this
    #         device failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"EndScan\" command has NOT been queued and will not be
    #         executed.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.command_executor.enqueue_command(
    #         handler
    #     )
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # def is_End_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current device \
    #     state. \

    #     return:
    #         True if this command is allowed to be run in current device \
    #         state. \

    #     rtype:
    #         boolean

    #     """
    #     handler = self.get_command_object("End")
    #     return handler.check_allowed()

    # @command(
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="information-only string",
    # )
    # @DebugIt()
    # def End(self):
    #     """This command invokes End command on Sdp Subarray toendthe current
    #     Scheduling block."""
    #     handler = self.get_command_object("End")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"End\" commandon this device
    #         failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"End\" command has NOT been queued and will notbe executed.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.command_executor.enqueue_command(
    #         handler
    #     )
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # def is_ObsReset_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current device \
    #     state \

    #     return:
    #         True if this command is allowed to be run in currentdevice state

    #     rtype:
    #         boolean

    #     """
    #     handler = self.get_command_object("ObsReset")
    #     return handler.check_allowed()

    # @command(
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="information-only string",
    # )
    # @DebugIt()
    # def ObsReset(self):
    #     """
    #     Invoke ObsReset command on Sdp Subarray.
    #     """
    #     handler = self.get_command_object("ObsReset")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"ObsReset\" command on this
    #         device failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"ObsReset\" command has NOT been queued and will not be
    #         executed.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.command_executor.enqueue_command(
    #         handler
    #     )
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # def is_Abort_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current device \
    #     state \

    #     return:
    #         True if this command is allowed to be run in currentdevice state

    #     rtype:
    #         boolean

    #     raises:
    #         DevFailed if this command is not allowed to be run in current \
    #         device state \

    #     """
    #     handler = self.get_command_object("Abort")
    #     return handler.check_allowed()

    # @command(
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="information-only string",
    # )
    # @DebugIt()
    # def Abort(self):
    #     """
    #     Invoke Abort command on Sdp Subarray.
    #     """
    #     handler = self.get_command_object("Abort")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"Abort\"commandonthis device
    #         failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"Abort\" command has NOT been queuedand willnot beexecuted.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.command_executor.enqueue_command(
    #         handler
    #     )
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # def is_Restart_allowed(self):
    #     """
    #     Checks whether this command is allowed to be run in current device \
    #     state \

    #     return:
    #         True if this command is allowedtoberun in current device state \

    #     rtype:
    #         boolean

    #     raises:
    #         DevFailed if this command is not allowed to be run in current \
    #         device state

    #     """
    #     handler = self.get_command_object("Restart")
    #     return handler.check_allowed()

    # @command(
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="information-only string",
    # )
    # @DebugIt()
    # def Restart(self):
    #     """
    #     Invoke Restart command on Sdp Subarray.
    #     """
    #     handler = self.get_command_object("Restart")
    #     if self.component_manager.command_executor.queue_full:
    #         message = """The invocation of the \"Restart\" command on this
    #         device failed.
    #         Reason: The command executor rejected the queuing of the command
    #         because its queue is full.
    #         The \"Restart\" command has NOT been queued and will not be
    #         executed.
    #         This device will continue with normal operation."""

    #         return [[ResultCode.FAILED], [message]]
    #     unique_id = self.component_manager.command_executor.enqueue_command(
    #         handler
    #     )
    #     return [[ResultCode.QUEUED], [str(unique_id)]]

    # default ska mid
    def create_component_manager(self):
        """Returns Sdp Subarray Leaf Node component manager object"""
        cm = SdpSLNComponentManager(
            self.SdpSubarrayFQDN,
            logger=self.logger,
            communication_state_callback=None,
            component_state_callback=None,
            _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE,
            _event_receiver=True,
            _update_sdp_subarray_obs_state_callback=self.update_sdp_subarray_obs_state_callback,  # noqa: E501
            _update_lrcr_callback=self.update_lrcr_callback,
            sleep_time=self.SleepTime,
            timeout=self.TimeOut,
            _update_availablity_callback=self.update_availablity_callback,
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

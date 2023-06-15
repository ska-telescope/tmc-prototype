"""
SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution
"""
import tango

# from logging import Logger
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.op_state_model import TMCOpStateModel
from tango import ApiUtil, AttrWriteType, DebugIt
from tango.server import attribute, command, device_property, run

from ska_tmc_sdpsubarrayleafnode import release
from ska_tmc_sdpsubarrayleafnode.commands import (
    Abort,
    AssignResources,
    Configure,
    End,
    EndScan,
    ObsReset,
    Off,
    On,
    ReleaseResources,
    Reset,
    Restart,
    Scan,
)
from ska_tmc_sdpsubarrayleafnode.manager import SdpSLNComponentManager


class SdpSubarrayLeafNode(SKABaseDevice):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
    actions during an observation.

    """

    def init_device(self):
        super().init_device()
        self._sdpSubarrayObsState = ObsState.EMPTY
        self._command_result = ("", "")
        self.set_change_event("longRunningCommandResult", True)
        self.set_change_event("sdpSubarrayObsState", True)

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

    commandExecuted = attribute(
        dtype=(("DevString",),),
        max_dim_x=4,
        max_dim_y=10000,
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
        dtype=int,
        access=AttrWriteType.READ_WRITE,
    )

    # Always the last result (unique_id, JSON-encoded result)
    @attribute(  # type: ignore[misc]
        dtype=("str",),
        max_dim_x=2,
    )
    def longRunningCommandResult(self) -> tuple[str, str]:
        """
        Read the result of the completed long running command.

        Reports unique_id, json-encoded result.
        Clients can subscribe to on_change event and wait for
        the ID they are interested in.

        :return: ID, result.
        """
        return self._command_result

    # ---------------
    # General methods
    # ---------------

    # pylint: disable=attribute-defined-outside-init
    def update_device_callback(self, devInfo):
        """Updates device callback info"""
        self._LastDeviceInfoChanged = devInfo.to_json()
        self.push_change_event("lastDeviceInfoChanged", devInfo.to_json())

    # pylint: disable=attribute-defined-outside-init
    def update_sdp_subarray_obs_state_callback(
        self, obs_state: ObsState
    ) -> None:
        """Updates SDP Subarray ObsState"""
        self._sdp_subarray_obs_state = obs_state
        self.push_change_event("sdpSubarrayObsState", self._command_result)

    def update_lrcr_callback(self, lrc_result):
        """Change event callback for longRunningCommandResult"""
        self._command_result = lrc_result
        self.push_change_event(
            "longRunningCommandResult", self._command_result
        )

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC SdpSubarrayLeafNode's init_device() method.
        """

        def do(self):
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
            device = self.target

            device._build_state = (
                f"{release.name},{release.version},{release.description}"
            )
            device._version_id = release.version
            device._LastDeviceInfoChanged = ""
            device.set_change_event("healthState", True, False)
            device._isSubsystemAvailable = False
            device.set_change_event("longRunningCommandResult", True)
            ApiUtil.instance().set_asynch_cb_sub_model(
                tango.cb_sub_model.PUSH_CALLBACK
            )
            device.op_state_model.perform_action("component_on")
            device.component_manager.command_executor.add_command_execution(
                "0", "Init", ResultCode.OK, ""
            )
            device.set_change_event("isSubsystemAvailable", True, False)
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

    def update_availablity_callback(self, availablity):
        """Change event callback for isSubsystemAvailable"""
        self._isSubsystemAvailable = availablity  # pylint: disable=W0201
        self.push_change_event("isSubsystemAvailable", availablity)

    def read_isSubsystemAvailable(self):
        """Read method for isSubsystemAvailable"""
        return self._isSubsystemAvailable

    def read_lastDeviceInfoChanged(self):
        """Return the last device info change"""
        return self._LastDeviceInfoChanged

    def read_commandExecuted(self):
        """Return the commandExecuted attribute."""
        result = []
        for command_executed in reversed(
            self.component_manager.command_executor.command_executed
        ):
            single_res = [
                str(command_executed["Id"]),
                str(command_executed["Command"]),
                str(command_executed["ResultCode"]),
                str(command_executed["Message"]),
            ]
            result.append(single_res)
        return result

    def read_longRunningCommandResult(self):
        """
        Read the result of the completed long running command.

        Reports unique_id, json-encoded result.
        Clients can subscribe to on_change event and wait for
        the ID they are interested in.

        :return: ID, result.
        """
        return self.component_manager.lrc_result

    def read_sdpSubarrayObsState(self):
        """Read method for sdpSubarrayObsState"""
        return self._sdpSubarrayObsState

    def write_sdpSubarrayObsState(self, obs_state):
        """Read method for sdpSubarrayObsState"""
        self._sdpSubarrayObsState = obs_state

    # --------
    # Commands
    # --------

    def is_Off_allowed(self):
        """
        Checks whether this command is allowed to be run in current \
        device state. \

        :return: True if this command is allowed to be run in current \
        device state. \

        :rtype: boolean
        """
        handler = self.get_command_object("Off")
        return handler.check_allowed()

    @command(dtype_out="DevVarLongStringArray")
    def Off(self):
        """
        This command invokes Off() command on Sdp Subarray.
        """
        handler = self.get_command_object("Off")
        if self.component_manager.command_executor.queue_full:
            message = """The invocation of the \"Off\" command on this device
            failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"Off\" command has NOT been queued and will not be executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_On_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device \
        state. \

        :rtype: boolean
        """
        handler = self.get_command_object("On")
        return handler.check_allowed()

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def On(self):
        """
        This command invokes On() command on Sdp Subarray.
        """
        handler = self.get_command_object("On")
        if self.component_manager.command_executor.queue_full:
            message = """The invocation of the \"On\" command on this device
            failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"On\" command has NOT been queued and will not be executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_AssignResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device \
        state \

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
            message = """The invocation of the \"AssignResources\" command on
            this device failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"AssignResources\" command has NOT been queued and will not
            be executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.add_to_queue(handler, argin)
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_ReleaseResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device
        state.

        :rtype: boolean
        """
        handler = self.get_command_object("ReleaseResources")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="The string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        """
        This command invokes ReleaseResources() command on command on Sdp
        Subarray.
        """
        handler = self.get_command_object("ReleaseResources")
        if self.component_manager.command_executor.queue_full:
            message = """The invocation of the \"ReleaseResources\" command on
            this device failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"ReleaseResources\" command has NOT been queued and will not
            be executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler, argin
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Configure_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state \

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
            message = """The invocation of the \"Configure\" command on this
            device failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"Configure\" command has NOT been queued and will not be
            executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler, argin
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Scan_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

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
            message = """The invocation of the \"Scan\" command on this device
            failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"Scan\" command has NOT been queued and will not be executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler, argin
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_EndScan_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

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
            message = """The invocation of the \"EndScan\" command on this
            device failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"EndScan\" command has NOT been queued and will not be
            executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_End_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        return:
            True if this command is allowed to be run in current device \
            state. \

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
        """This command invokes End command on Sdp Subarray to end the current
        Scheduling block."""
        handler = self.get_command_object("End")
        if self.component_manager.command_executor.queue_full:
            message = """The invocation of the \"End\" command on this device
            failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"End\" command has NOT been queued and will not be executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_ObsReset_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state \

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
            message = """The invocation of the \"ObsReset\" command on this
            device failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"ObsReset\" command has NOT been queued and will not be
            executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Abort_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state \

        return:
            True if this command is allowed to be run in current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run in current \
            device state \

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
            message = """The invocation of the \"Abort\" command on this device
            failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"Abort\" command has NOT been queued and will not be executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Restart_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state \

        return:
            True if this command is allowed to be run in current device state \

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run in current \
            device state

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
            message = """The invocation of the \"Restart\" command on this
            device failed.
            Reason: The command executor rejected the queuing of the command
            because its queue is full.
            The \"Restart\" command has NOT been queued and will not be
            executed.
            This device will continue with normal operation."""

            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    # default ska mid
    # pylint: disable=attribute-defined-outside-init
    def create_component_manager(self):
        """Returns Sdp Subarray Leaf Node component manager object"""
        self.op_state_model = TMCOpStateModel(
            logger=self.logger, callback=super()._update_state
        )
        cm = SdpSLNComponentManager(
            self.SdpSubarrayFQDN,
            self.op_state_model,
            logger=self.logger,
            _update_device_callback=self.update_device_callback,
            _update_lrcr_callback=self.update_lrcr_callback,
            sleep_time=self.SleepTime,
            timeout=self.TimeOut,
            _update_availablity_callback=self.update_availablity_callback,
        )
        return cm

    # pylint: enable=attribute-defined-outside-init
    # pylint: disable=unexpected-keyword-arg

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()
        args = ()
        for (command_name, command_class) in [
            ("On", On),
            ("Off", Off),
            ("AssignResources", AssignResources),
            ("ReleaseResources", ReleaseResources),
            ("Configure", Configure),
            ("Scan", Scan),
            ("EndScan", EndScan),
            ("End", End),
            ("ObsReset", ObsReset),
            ("Abort", Abort),
            ("Restart", Restart),
        ]:

            command_obj = command_class(
                self.component_manager,
                self.op_state_model,
                *args,
                logger=self.logger,
            )
            self.register_command_object(command_name, command_obj)
        self.register_command_object(
            "Reset",
            Reset(
                self.component_manager,
                self.op_state_model,
                self.logger,
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

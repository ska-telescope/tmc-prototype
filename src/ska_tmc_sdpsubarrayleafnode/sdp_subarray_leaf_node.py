"""
SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution
"""
import json

from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, device_property

from ska_tmc_sdpsubarrayleafnode import release
from ska_tmc_sdpsubarrayleafnode.manager.component_manager import (
    SdpSLNComponentManager,
)
from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid
from ska_tmc_sdpsubarrayleafnode.model.op_state_model import TMCOpStateModel


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

    SleepTime = device_property(
        dtype="DevFloat", default_value=1
    )  # kept it for now, might delete in further refactoring

    # ----------
    # Attributes
    # ----------

    receiveAddresses = attribute(
        dtype="str",
        access=AttrWriteType.READ_WRITE,
        doc="This attribute is used for testing purposes. In the unit test cases, "
        "it is used to provide FQDN of receiveAddresses attribute from SDP.",
    )

    activityMessage = attribute(
        dtype="str",
        access=AttrWriteType.READ_WRITE,
        doc="String providing information about the current activity in SDP Subarray Leaf Node",
    )

    activeProcessingBlocks = attribute(
        dtype="str",
        doc="This is a attribute from SDP Subarray which depicts the active Processing Blocks in "
        "the SDP Subarray.",
    )

    def update_device_callback(self, devInfo):
        self._LastDeviceInfoChanged = devInfo.to_json()
        self.push_change_event("lastDeviceInfoChanged", devInfo.to_json())

    # ---------------
    # General methods
    # ---------------
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

            # Need to check below how to initialise the sdpsaln attr

            # device.set_change_event("receiveAddresses", True, False)
            # device.set_change_event("activityMessage", True, False)
            # device.set_change_event("activeProcessingBlocks", True, False)

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

    # ------------------
    # Attributes methods
    # ------------------
    def read_sdpSubarrayDevName(self):
        """Return the sdpsubarraydevname attribute."""
        return self.component_manager.input_parameter.sdp_subarray_dev_name

    def write_sdpSubarrayDevName(self, value):
        """Set the sdpsubarraydevname attribute."""
        self.component_manager.input_parameter.sdp_subarray_dev_name = value
        self.component_manager.update_input_parameter()

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
        This command invokes SetStandbyLPMode() command on DishLeafNode, Off() command
        on CspMasterLeafNode and SdpMasterLeafNode.

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
        This command invokes TelescopeOn() command on DishLeadNode, CspMasterLeafNode,
        SdpMasterLeafNode.
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
        doc_in="The string in JSON format. The JSON contains following values:\nsubarrayID: "
        "DevShort\ndish: JSON object consisting\n- receptor_ids: DevVarStringArray. "
        "The individual string should contain dish numbers in string format with "
        "preceding zeroes upto 3 digits. E.g. 0001, 0002",
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        AssignResources command invokes the AssignResources command on lower level devices.
        """
        handler = self.get_command_object("AssignResources")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler, argin
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
        dtype_in="str",
        doc_in="The string in JSON format. The JSON contains following values:\nsubarrayID: "
        "releaseALL boolean as true and receptor_ids.",
        dtype_out="DevVarLongStringArray",
        doc_out="information-only string",
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        """
        Release all the resources assigned to the given Subarray.
        """
        handler = self.get_command_object("ReleaseResources")
        if self.component_manager.command_executor.queue_full:
            return [[ResultCode.FAILED], ["Queue is full!"]]
        unique_id = self.component_manager.command_executor.enqueue_command(
            handler, argin
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    # default ska mid
    def create_component_manager(self):
        self.op_state_model = TMCOpStateModel(
            logger=self.logger, callback=super()._update_state
        )
        cm = SdpSLNComponentManager(
            self.op_state_model,
            logger=self.logger,
            _update_device_callback=self.update_device_callback,
            _input_parameter=InputParameterMid(None),
            sleep_time=self.SleepTime,
        )
        cm.input_parameter.sdp_subarray_dev_name = self.SdpSubarrayFQDN or ""
        cm.update_input_parameter()
        return cm

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()

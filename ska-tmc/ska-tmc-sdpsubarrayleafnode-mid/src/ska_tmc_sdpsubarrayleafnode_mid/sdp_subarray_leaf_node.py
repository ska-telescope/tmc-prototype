# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution.

"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #
# Third party imports
import os

# PyTango imports
import tango
import threading
from tango import DebugIt, AttrWriteType, ApiUtil
from tango.server import run, command, device_property, attribute

# Additional imports
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState
from ska.base.commands import ResultCode

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const, release
from .assign_resources_command import AssignResources
from .release_resources_command import ReleaseAllResources
from .configure_command import Configure
from .scan_command import Scan
from .endscan_command import EndScan
from .end_command import End
from .abort_command import Abort
from .restart_command import Restart
from .obsreset_command import ObsReset
from .telescope_on_command import TelescopeOn
from .telescope_off_command import TelescopeOff
from .reset_command import ResetCommand
from .device_data import DeviceData
from .exceptions import InvalidObsStateError


# PROTECTED REGION END #    //  SdpSubarrayLeafNode.additionnal_import

__all__ = [
    "SdpSubarrayLeafNode",
    "main",
    "AssignResources",
    "const",
    "release",
    "ReleaseAllResources",
    "TelescopeOn",
    "TelescopeOff",
    "Configure",
    "Abort",
    "Restart",
    "ObsReset",
    "Scan",
    "End",
    "EndScan",
    "ResetCommand"
]

# pylint: disable=unused-argument,unused-variable, implicit-str-concat
class SdpSubarrayLeafNode(SKABaseDevice):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.

    :Device Properties:

        SdpSubarrayFQDN:
            FQDN of the SDP Subarray Tango Device Server.

    :Device Attributes:

        receiveAddresses:
            This attribute is used for testing purposes. In the unit test cases
            it is used to provide FQDN of receiveAddresses attribute from SDP.

        activityMessage:
            String providing information about the current activity in SDP Subarray Leaf Node.

        activeProcessingBlocks:
            This is a attribute from SDP Subarray which depicts the active Processing
            Blocks in the SDP Subarray.


    """

    # -----------------
    # Device Properties
    # -----------------
    SdpSubarrayFQDN = device_property(
        dtype="str", doc="FQDN of the SDP Subarray Tango Device Server."
    )

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
            self.this_server = TangoServerHelper.get_instance()
            self.this_server.set_tango_class(device)
            device.attr_map = {}
            device.attr_map["receiveAddresses"] = ""
            device.attr_map["activeProcessingBlocks"] = ""
            device.attr_map["activityMessage"] = ""

            # Initialise attributes
            device._sdp_subarray_health_state = HealthState.OK
            device._build_state = "{},{},{}".format(
                release.name, release.version, release.description
            )
            device._version_id = release.version

            # Create DeviceData class instance
            device_data = DeviceData.get_instance()
            device.device_data = device_data
            standalone_mode = os.environ.get("STANDALONE_MODE")
            self.logger.info("Device running in standalone_mode:%s", standalone_mode)

            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_msg = f"{const.STR_SETTING_CB_MODEL}{ApiUtil.instance().get_asynch_cb_sub_model()}"
            self.logger.debug(log_msg)

            self.this_server.write_attr(
                "activityMessage", const.STR_SDPSALN_INIT_SUCCESS, False
            )
            # Initialise Device status
            device.set_status(const.STR_SDPSALN_INIT_SUCCESS)
            self.logger.info(const.STR_SDPSALN_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_SDPSALN_INIT_SUCCESS)

    # ---------------
    # General methods
    # ---------------

    def always_executed_hook(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.always_executed_hook) ENABLED START #
        """Internal construct of TANGO."""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.delete_device) ENABLED START #
        """Internal construct of TANGO."""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_receiveAddresses(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.receiveAddresses_read) ENABLED START #
        """Internal construct of TANGO. Returns the Receive Addresses.
        receiveAddresses is a forwarded attribute from SDP Master which depicts State of the SDP."""
        return self.attr_map["receiveAddresses"]
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.receiveAddresses_read

    def write_receiveAddresses(self, value):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.receiveAddresses_read) ENABLED START #
        """Internal construct of TANGO. Sets the Receive Addresses.
        receiveAddresses is a forwarded attribute from SDP Master which depicts State of the SDP."""
        self.attr_map["receiveAddresses"] = value
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.receiveAddresses_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activityMessage_read) ENABLED START #
        """Internal construct of TANGO. Returns Activity Messages.
        activityMessage is a String providing information about the current activity in SDP Subarray Leaf Node"""
        return self.attr_map["activityMessage"]
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activityMessage_write) ENABLED START #
        """Internal construct of TANGO. Sets the activity message.
        activityMessage is a String providing information about the current activity in SDP Subarray Leaf Node"""
        self.update_attr_map("activityMessage", value)
        # PROTECTED REGION END # // SdpSubarrayLeafNode.activityMessage_write

    def update_attr_map(self, attr, val):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.update_attr_map) ENABLED START #
        """This method updates attribute value in attribute map. Once a thread has acquired a lock,
        subsequent attempts to acquire it are blocked, until it is released."""
        lock = threading.Lock()
        lock.acquire()
        self.attr_map[attr] = val
        lock.release()
        # PROTECTED REGION END # // SdpSubarrayLeafNode.update_attr_map

    def read_activeProcessingBlocks(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activeProcessingBlocks_read) ENABLED START #
        """Internal construct of TANGO. Returns Active Processing Blocks.activeProcessingBlocks is a forwarded attribute
        from SDP Subarray which depicts the active Processing Blocks in the SDP Subarray"""
        return self.attr_map["activeProcessingBlocks"]
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activeProcessingBlocks_read

    # --------
    # Commands
    # --------

    def is_telescope_on_allowed(self):
        """
        Checks Whether this command is allowed to be run in current device state.

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean

        raises: DevF
            ailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("TelescopeOn")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def TelescopeOn(self):
        """
        Sets the opState to ON.

        :param argin: None

        :return: None

        """
        handler = self.get_command_object("TelescopeOn")
        handler()

    def is_telescope_off_allowed(self):
        """
        Checks Whether this command is allowed to be run in current device state.

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean

        raises: DevF
            ailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("TelescopeOff")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def TelescopeOff(self):
        """
        Sets the opState to Off.

        :param argin: None

        :return: None

        """
        handler = self.get_command_object("TelescopeOff")
        handler()

    @command()
    @DebugIt()
    def Abort(self):
        """
        Invoke Abort on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("Abort")
        handler()

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
        dtype_in=("str"),
        doc_in="The input JSON string consists of information related to id, max_length, scan_types"
        " and processing_blocks.",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        Assigns resources to given SDP subarray.
        """

        handler = self.get_command_object("AssignResources")
        try:
            self.validate_obs_state()
        except InvalidObsStateError as error:
            self.logger.exception(error)
            tango.Except.throw_exception(
                const.ERR_DEVICE_NOT_IN_EMPTY_IDLE,
                const.ERR_ASSGN_RESOURCES,
                "SdpSubarrayLeafNode.AssignResources()",
                tango.ErrSeverity.ERR,
            )
        handler(argin)

    def is_AssignResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        return:
        True if this command is allowed to be run in current device state

        rtype:
            boolean

        """
        handler = self.get_command_object("AssignResources")
        return handler.check_allowed()

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
        dtype_in=("str"),
        doc_in="The JSON input string consists of scan type.",
    )
    @DebugIt()
    def Configure(self, argin):
        """
        Invokes Configure on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("Configure")
        handler(argin)

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

    @command()
    @DebugIt()
    def End(self):
        """This command invokes End command on SDP subarray to end the current Scheduling block."""
        handler = self.get_command_object("End")
        handler()

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

    @command()
    @DebugIt()
    def EndScan(self):
        """
        Invokes EndScan on SdpSubarrayLeafNode.

        """
        handler = self.get_command_object("EndScan")
        handler()

    @command()
    @DebugIt()
    def ObsReset(self):
        """
        Invoke ObsReset command on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("ObsReset")
        handler()

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

    def is_ReleaseAllResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        return:
            True if this command is allowed to be run in current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("ReleaseAllResources")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def ReleaseAllResources(self):
        """
        Invokes ReleaseAllResources command on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("ReleaseAllResources")
        handler()

    @command()
    @DebugIt()
    def Restart(self):
        """
        Invoke Restart command on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("Restart")
        handler()

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
        dtype_in=("str"),
        doc_in="The JSON input string consists of SB ID.",
    )
    @DebugIt()
    def Scan(self, argin):
        """Invoke Scan command to SDP subarray."""

        handler = self.get_command_object("Scan")
        handler(argin)

    def validate_obs_state(self):
        self.this_server = TangoServerHelper.get_instance()
        sdp_subarray_fqdn = self.this_server.read_property("SdpSubarrayFQDN")[0]
        sdp_sa_client = TangoClient(sdp_subarray_fqdn)
        if sdp_sa_client.get_attribute("obsState").value in [
            ObsState.EMPTY,
            ObsState.IDLE,
        ]:
            self.logger.info(
                "SDP subarray is in required obstate,Hence resources to SDP can be assign."
            )
        else:
            self.logger.error("Subarray is not in EMPTY obstate")
            log_msg = "Error in device obstate."
            self.this_server.write_attr("activityMessage", log_msg, False)
            raise InvalidObsStateError("SDP subarray is not in EMPTY obstate.")

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()

        # Create device_data class object
        device_data = DeviceData.get_instance()
        args = (device_data, self.state_model, self.logger)
        self.register_command_object("AssignResources", AssignResources(*args))
        self.register_command_object("ReleaseAllResources", ReleaseAllResources(*args))
        self.register_command_object("Scan", Scan(*args))
        self.register_command_object("End", End(*args))
        self.register_command_object("Restart", Restart(*args))
        self.register_command_object("Configure", Configure(*args))
        self.register_command_object("EndScan", EndScan(*args))
        self.register_command_object("Abort", Abort(*args))
        self.register_command_object("ObsReset", ObsReset(*args))
        self.register_command_object("TelescopeOff", TelescopeOff(*args))
        self.register_command_object("TelescopeOn", TelescopeOn(*args))
        self.register_command_object("Reset", ResetCommand(*args))



# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpSubarrayLeafNode.main) ENABLED START #
    """
    Runs the SdpSubarrayLeafNode

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: SdpSubarrayLeafNode TANGO object

    """
    # PROTECTED REGION ID(SdpSubarrayLeafNode.main) ENABLED START #
    ret_val = run((SdpSubarrayLeafNode,), args=args, **kwargs)

    return ret_val
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.main


if __name__ == "__main__":
    main()

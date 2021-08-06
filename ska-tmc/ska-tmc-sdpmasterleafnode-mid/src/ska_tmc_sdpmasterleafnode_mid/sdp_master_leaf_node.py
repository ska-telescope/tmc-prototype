# -*- coding: utf-8 -*-
#
# This file is part of the SdpMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
The primary responsibility of the SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
actions during an observation. It also acts as a SDP contact point for Subarray Node for observation
execution. There is one to one mapping between SDP Subarray Leaf Node and SDP subarray.
"""

# PROTECTED REGION ID(SdpMasterLeafNode.additional_import) ENABLED START #
# Standard python imports
import os
import threading

# Tango imports
import tango
from tango import ApiUtil, DebugIt, AttrWriteType
from tango.server import run, command, device_property, attribute


# PROTECTED REGION ID(SdpMasterLeafNode.additional_import) ENABLED START #
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, SimulationMode, TestMode
from tmc.common.tango_server_helper import TangoServerHelper
from . import const, release
from .telescope_on_command import TelescopeOn
from .telescope_off_command import TelescopeOff
from .telescope_standby_command import TelescopeStandby
from .disable_command import Disable
from .device_data import DeviceData
from .simulator import get_sdp_master_sim

# PROTECTED REGION END #    //  SdpMasterLeafNode.additional_import

__all__ = ["SdpMasterLeafNode", "main", "TelescopeOn", "TelescopeOff", "TelescopeStandby", "Disable"]


class SdpMasterLeafNode(SKABaseDevice):
    """
    The primary responsibility of the SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
    actions during an observation.

    :Device Properties:

        SdpMasterFQDN:
            Property to provide FQDN of SDP Master Device

    :Device Attributes:

        versionInfo:
            Provides Version information of TANGO device.

        activityMessage:
            String providing information about the current activity in SDP Master Leaf Node.

        ProcessingBlockList:
            List of Processing Block devices

    """

    # -----------------
    # Device Properties
    # -----------------
    SdpMasterFQDN = device_property(
        dtype='str'
    )
    # ----------
    # Attributes
    # ----------

    versionInfo = attribute(
        dtype="str",
        doc="Version information of TANGO device.",
    )

    activityMessage = attribute(
        dtype="str",
        access=AttrWriteType.READ_WRITE,
        doc="String providing information about the current activity in SDPLeafNode.",
    )

    ProcessingBlockList = attribute(
        dtype="str",
        doc="List of Processing Block devices.",
    )


    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the SDP master's init_device() method"
        """

        def do(self):
            """
            Initializes the attributes and properties of the SdpMasterLeafNode.

            return:
                A tuple containing a return code and a string message indicating status.
                The message is for information purpose only.

            rtype:
                (ReturnCode, str)
            """

            super().do()
            device = self.target
            device_data = DeviceData.get_instance()
            device.device_data = device_data
            # Creating Instance of TangoServerHelper class
            self.this_server = TangoServerHelper.get_instance()
            self.this_server.device = device

            device.attr_map = {}
            # Initialising Attributes 
            device.attr_map["versionInfo"]=""
            device.attr_map["activityMessage"]=""
            device.attr_map["ProcessingBlockList"]= "test"


            device._health_state = HealthState.OK  # Setting healthState to "OK"
            device._simulation_mode = (
                SimulationMode.FALSE
            )  # Enabling the simulation mode
            device._test_mode = TestMode.NONE
            device.set_status(const.STR_INIT_SUCCESS)
            device._build_state = "{},{},{}".format(
                release.name, release.version, release.description
            )
            device._version_id = release.version
            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_msg = f"{const.STR_SETTING_CB_MODEL}{ApiUtil.instance().get_asynch_cb_sub_model()}"
            self.logger.debug(log_msg)

            self.this_server.write_attr("activityMessage", const.STR_INIT_SUCCESS, False)
            self.logger.info(const.STR_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_INIT_SUCCESS)

    def always_executed_hook(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  SdpMasterLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  SdpMasterLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_versionInfo(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.versionInfo_read) ENABLED START #
        """ Internal construct of TANGO. Version information of TANGO device."""
        return self.attr_map["versionInfo"]
        # PROTECTED REGION END #    //  SdpMasterLeafNode.versionInfo_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.activityMessage_read) ENABLED START #
        """Internal construct of TANGO. String providing information about the current activity in
        SDPLeafNode."""
        return self.attr_map["activityMessage"]
        # PROTECTED REGION END #    //  SdpMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(SdpMasterLeafNode.activityMessage_write) ENABLED START #
        """
        Internal construct of TANGO. Sets the activity message.
        """
        self.update_attr_map("activityMessage", value)
        # PROTECTED REGION END #    //  SdpMasterLeafNode.activityMessage_write

    def read_ProcessingBlockList(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.ProcessingBlockList_read) ENABLED START #
        """
        Internal construct of TANGO.
        :return:
        """
        return self.attr_map["ProcessingBlockList"]
        # PROTECTED REGION END #    //  SdpMasterLeafNode.ProcessingBlockList_read

    def update_attr_map(self, attr, val):
        """
        This method updates attribute value in attribute map. Once a thread has acquired a lock,
        subsequent attempts to acquire it are blocked, until it is released.
        """
        lock = threading.Lock()
        lock.acquire()
        self.attr_map[attr] = val
        lock.release()

    # --------
    # Commands
    # --------

    def is_Disable_allowed(self):
        """
        Checks Whether this command is allowed to be run in current device state.

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean

        raises: DevF
            ailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("Disable")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def Disable(self):
        """
        Sets the opState to Disable.

        :param argin: None

        :return: None

        """
        handler = self.get_command_object("Disable")
        handler()

    def is_telescope_on_allowed(self):
        """
        Checks Whether this command is allowed to be run in current device state.

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean

        raises: 
            DevFailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("TelescopeOn")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def TelescopeOn(self):
        """
        Invokes On command on SDP Master.

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

        raises: 
            DevFailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("TelescopeOff")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def TelescopeOff(self):
        """
        Invokes Off command on SDP Master.

        :param argin: None

        :return: None

        """
        handler = self.get_command_object("TelescopeOff")
        handler()

    
    def is_telescope_standby_allowed(self):
        """
        Checks Whether this command is allowed to be run in current device state.

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean

        raises: 
            DevFailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("TelescopeStandby")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def TelescopeStandby(self):
        """
        Invokes Standby command on SDP Master.

        :param argin: None

        :return: None

        """
        handler = self.get_command_object("TelescopeStandby")
        handler()

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        device_data = DeviceData.get_instance()
        args = (device_data, self.state_model, self.logger)
        self.register_command_object("TelescopeOn", TelescopeOn(*args))
        self.register_command_object("TelescopeOff", TelescopeOff(*args))
        self.register_command_object("Disable", Disable(*args))
        self.register_command_object("TelescopeStandby", TelescopeStandby(*args))


# ----------
# Run server
# ----------

def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpMasterLeafNode.main) ENABLED START #

    # Check if standalone mode is enabled
    try:
        standalone_mode = os.environ['STANDALONE_MODE']
        print(f"standalone_mode: {standalone_mode}")
    except KeyError:
        standalone_mode = "FALSE"

    if standalone_mode == "TRUE":
        print("running in standalone mode")
        ## Get simulator object
        device_name = "mid_sdp/elt/master"
        sdp_master_simulator = get_sdp_master_sim(device_name)
        ret_val = run((SdpMasterLeafNode, sdp_master_simulator), args=args, **kwargs)
    else:
        print("running in standalone mode")
        ret_val = run((SdpMasterLeafNode,), args=args, **kwargs)

    return ret_val
    # PROTECTED REGION END #    //  SdpMasterLeafNode.main


if __name__ == "__main__":
    main()

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
# Third party imports
# Tango imports
import tango
from tango import ApiUtil, DebugIt, AttrWriteType
from tango.server import run, command, device_property, attribute

# PROTECTED REGION ID(SdpMasterLeafNode.additional_import) ENABLED START #
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, SimulationMode, TestMode
from . import const, release
from .on_command import On
from .off_command import Off
from .standby_command import Standby
from .disable_command import Disable
from .device_data import DeviceData
# PROTECTED REGION END #    //  SdpMasterLeafNode.additional_import

__all__ = ["SdpMasterLeafNode", "main", "On", "Off", "Standby", "Disable"]


class SdpMasterLeafNode(SKABaseDevice):
    """
    The primary responsibility of the SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
    actions during an observation.
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
        dtype='str',
        doc="Version information of TANGO device.",
    )

    activityMessage = attribute(

        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="String providing information about the current activity in SDPLeafNode.",
    )

    ProcessingBlockList = attribute(
        dtype='str',
        doc="List of Processing Block devices.",
    )

    sdpHealthState = attribute(name="sdpHealthState", label="sdpHealthState", forwarded=True)

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

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises:

            """

            super().do()
            device = self.target
            device_data = DeviceData.get_instance()
            device.device_data = device_data
            device._health_state = HealthState.OK  # Setting healthState to "OK"
            device._simulation_mode = SimulationMode.FALSE  # Enabling the simulation mode
            device._test_mode = TestMode.NONE
            device._processing_block_list = "test"
            device_data._read_activity_message = 'OK'
            device.set_status(const.STR_INIT_SUCCESS)
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device_data.sdp_master_ln_fqdn = device.SdpMasterFQDN
            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_msg = const.STR_SETTING_CB_MODEL + str(ApiUtil.instance().get_asynch_cb_sub_model())
            self.logger.debug(log_msg)
            device_data._read_activity_message = const.STR_INIT_SUCCESS
            self.logger.info(device_data._read_activity_message)
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
        return self._version_info
        # PROTECTED REGION END #    //  SdpMasterLeafNode.versionInfo_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.activityMessage_read) ENABLED START #
        """ Internal construct of TANGO. String providing information about the current activity in
        SDPLeafNode. """
        return self.device_data._read_activity_message
        # PROTECTED REGION END #    //  SdpMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(SdpMasterLeafNode.activityMessage_write) ENABLED START #
        """
        Internal construct of TANGO. Sets the activity message.
        """
        self.device_data._read_activity_message = value
        # PROTECTED REGION END #    //  SdpMasterLeafNode.activityMessage_write

    def read_ProcessingBlockList(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.ProcessingBlockList_read) ENABLED START #
        """
        Internal construct of TANGO.
        :return:
        """
        return self._processing_block_list
        # PROTECTED REGION END #    //  SdpMasterLeafNode.ProcessingBlockList_read

    # --------
    # Commands
    # --------

    def is_Disable_allowed(self):
        """
        Checks Whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("Disable")
        return handler.check_allowed()

    @command(
    )
    @DebugIt()
    def Disable(self):
        """
        Sets the OperatingState to Disable.

        :param argin: None

        :return: None

        """
        handler = self.get_command_object("Disable")
        handler()

    @command(
    )
    @DebugIt()
    def Standby(self):
        """
        Invokes Standby command .

        :param argin: None

        :return: None

        """
        handler = self.get_command_object("Standby")
        handler()

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        device_data = DeviceData.get_instance()
        args = (device_data, self.state_model, self.logger)
        self.register_command_object("On", On(*args))
        self.register_command_object("Off", Off(*args))
        self.register_command_object("Disable", Disable(*args))
        self.register_command_object("Standby", Standby(*args))




# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpMasterLeafNode.main) ENABLED START #
    return run((SdpMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpMasterLeafNode.main


if __name__ == '__main__':
    main()

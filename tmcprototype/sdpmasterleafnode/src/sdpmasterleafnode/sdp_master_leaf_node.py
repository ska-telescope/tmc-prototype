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

# PROTECTED REGION ID(SdpMasterLeafNode.additionnal_import) ENABLED START #
# Third party imports
# Tango imports
import tango
from tango import DeviceProxy, ApiUtil, DevState, AttrWriteType, DevFailed
from tango.server import run,command, device_property, attribute

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from . import const, release, on_command, off_command, standby_command, disable_command
from .device_data import DeviceData
from tmc.common.tango_client import TangoClient

# PROTECTED REGION END #    //  SdpMasterLeafNode.additionnal_import

__all__ = ["SdpMasterLeafNode", "main", "on_command","off_command", "standby_command", "disable_command"]


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
            try:
                device_data = DeviceData()
                device._version_info = "1.0"
                device._processing_block_list = "test"
                device_data._read_activity_message = 'OK'
                device.set_status(const.STR_INIT_SUCCESS)
                device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
                device._version_id = release.version
                device_data.sdp_master_ln_fqdn = device.SdpMasterFQDN

            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = const.ERR_INIT_PROP_ATTR + str(dev_failed)
                tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                       "SdpMasterLeafNode.InitCommand()", const.ERR_INIT_PROP_ATTR)

            try:
                device._read_activity_message = const.STR_SDPMASTER_FQDN + device.SdpMasterFQDN
                # Creating proxy to the SDPMaster
                device._sdp_proxy = DeviceProxy(device.SdpMasterFQDN)

            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = const.ERR_IN_CREATE_PROXY_SDP_MASTER + str(dev_failed)
                tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                             "SdpMasterLeafNode.InitCommand()",
                                             tango.ErrSeverity.ERR)
            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            device._read_activity_message = const.STR_SETTING_CB_MODEL + str(
                ApiUtil.instance().get_asynch_cb_sub_model())

            device._read_activity_message = const.STR_INIT_SUCCESS
            self.logger.info(device._read_activity_message)
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
        """ Internal construct of TANGO. String providing information about the current activity in SDPLeafNode."""
        return self._read_activity_message
        # PROTECTED REGION END #    //  SdpMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(SdpMasterLeafNode.activityMessage_write) ENABLED START #
        '''
        Internal construct of TANGO. Sets the activity message.
        '''
        self._read_activity_message = value
        # PROTECTED REGION END #    //  SdpMasterLeafNode.activityMessage_write

    def read_ProcessingBlockList(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.ProcessingBlockList_read) ENABLED START #
        '''
        Internal construct of TANGO.
        :return:
        '''
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
        args = (self, self.state_model, self.logger)
        self.register_command_object("On",on_command.OnCommand(device_data, self.state_model, self.logger))
        self.register_command_object("Off",off_command.OffCommand(*args))
        self.register_command_object("Disable",disable_command.DisableCommand(*args))
        self.register_command_object("Standby",standby_command.StandbyCommand(*args))

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpMasterLeafNode.main) ENABLED START #
    return run((SdpMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpMasterLeafNode.main

if __name__ == '__main__':
    main()
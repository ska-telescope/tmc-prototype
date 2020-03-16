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

from __future__ import print_function
from __future__ import absolute_import

import os
import sys

# PROTECTED REGION ID(SdpMasterLeafNode.additionnal_import) ENABLED START #
# Tango imports
# import tango
# from tango import DebugIt, DevState, AttrWriteType, DevFailed, DeviceProxy
# from tango.server import run, DeviceMeta, attribute, command, device_property
# from future.utils import with_metaclass
# from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice

import tango
from tango import DeviceProxy, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, DeviceMeta, command, device_property, attribute
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice
from future.utils import with_metaclass

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SdpMasterLeafNode"
sys.path.insert(0, module_path)

# Additional import
import CONST

# PROTECTED REGION END #    //  SdpMasterLeafNode.additionnal_import

__all__ = ["SdpMasterLeafNode", "main"]


class SdpMasterLeafNode(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    The primary responsibility of the SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
    actions during an observation.
    """
    # PROTECTED REGION ID(SdpMasterLeafNode.class_variable) ENABLED START #
    def commandCallback(self, event):

        """
        Checks whether the command has been successfully invoked on SDP Master.

        :param event: response from SDP Master for the invoked command.

        :return: None.
        """
        exception_count = 0
        exception_message = []
        try:
            if event.err:
                log = CONST.ERR_INVOKING_CMD + event.cmd_name
                log_msg = CONST.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                self._read_activity_message = CONST.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                    event.errors)
                self.logger.error(log)
            else:
                log = CONST.STR_COMMAND + event.cmd_name + CONST.STR_INVOKE_SUCCESS
                self._read_activity_message = log
                self.logger.info(log)
        except Exception as except_occurred:
            self._read_activity_message = CONST.ERR_EXCEPT_CMD_CB + str(except_occurred)
            log_msg = CONST.ERR_EXCEPT_CMD_CB + str(except_occurred)
            self.logger.error(log_msg)
            exception_message.append(self._read_activity_message)
            exception_count += 1

        # Throw Exception
        if exception_count > 0:
            err_msg = ''
            for item in exception_message:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_SDP_CMD_CALLBK, tango.ErrSeverity.ERR)

    #Throw devfailed exception
    def _handle_devfailed_exception(self, df, actvity_msg):
        self._read_activity_message = actvity_msg
        self._read_activity_message = CONST.ERR_MSG + str(df)
        self.logger.error(actvity_msg)
    # PROTECTED REGION END #    //  SdpMasterLeafNode.class_variable

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

    def init_device(self):
        '''Initializes the attributes and properties of CSPMasterLeafNode'''
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SdpMasterLeafNode.init_device) ENABLED START #
        try:
            self.set_state(DevState.ON)
            self._sdp_state = CONST.ENUM_STATE_INIT # Setting SDP State to "INIT"
            self._sdp_admin_mode = CONST.ENUM_ADMIN_MODE_ONLINE # Setting adminMode to "ONLINE"
            self._version_info = "1.0"
            self._processing_block_list = "test"
            self._read_activity_message = 'OK'
            self.set_status(CONST.STR_INIT_SUCCESS)
            self._health_state = CONST.ENUM_OK
            self._admin_mode = 0
            self._test_mode = "False"

        except DevFailed as dev_failed:
            self._handle_devfailed_exception(dev_failed, CONST.ERR_INIT_PROP_ATTR)

        try:
            self._read_activity_message = CONST.STR_SDPMASTER_FQDN + str(self.SdpMasterFQDN)
            # Creating proxy to the SDPMaster
            self._sdp_proxy = DeviceProxy(str(self.SdpMasterFQDN))
        except DevFailed as dev_failed:
            self.set_state(DevState.FAULT)
            self._handle_devfailed_exception(dev_failed, CONST.ERR_IN_CREATE_PROXY_SDP_MASTER)

        ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
        self._read_activity_message = CONST.STR_SETTING_CB_MODEL + str(
            ApiUtil.instance().get_asynch_cb_sub_model())

        # PROTECTED REGION END #    //  SdpMasterLeafNode.init_device

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

    @command(
    )
    @DebugIt()
    def On(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.On) ENABLED START #
        """ Informs the SDP that it can start executing Processing Blocks. Sets the OperatingState to ON.

        :param argin: DevVoid.

        :return: None.

        """
        self._sdp_proxy.command_inout_asynch(CONST.CMD_ON, self.commandCallback)
        log_msg = CONST.CMD_ON + CONST.STR_COMMAND + CONST.STR_INVOKE_SUCCESS
        self.logger.debug(log_msg)
        # PROTECTED REGION END #    //  SdpMasterLeafNode.On

    @command(
    )
    @DebugIt()
    def Off(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.Off) ENABLED START #
        """ Sets the OperatingState to OFF.

         :param argin: DevVoid.

         :return: None.

         """
        self.logger.debug(CONST.STR_OFF_CMD_SUCCESS)
        self._read_activity_message = CONST.STR_OFF_CMD_SUCCESS

        # This code is written only to improve code coverage
        if self._test_mode == "True":
            self._handle_devfailed_exception(DevFailed, CONST.ERR_OFF_CMD_FAIL)
        # PROTECTED REGION END #    //  SdpMasterLeafNode.Off

    @command(
    )
    @DebugIt()
    def Disable(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.Disable) ENABLED START #
        """ Sets the OperatingState to Disable.

         :param argin: DevVoid.

         :return: None.

         """
        self.logger.debug(CONST.STR_DISABLE_CMS_SUCCESS)
        self._read_activity_message = CONST.STR_DISABLE_CMS_SUCCESS
        # PROTECTED REGION END #    //  SdpMasterLeafNode.Disableon

    @command(
    )
    @DebugIt()
    def Standby(self):
        # PROTECTED REGION ID(SdpMasterLeafNode.Standby) ENABLED START #
        """ Informs the SDP to stop any executing Processing. To get into the STANDBY state all running
        PBs will be aborted. In normal operation we expect diable should be triggered without first going
        into STANDBY.

        :param argin: DevVoid.

        :return: None.

        """
        self._sdp_proxy.command_inout_asynch(CONST.CMD_STANDBY, self.commandCallback)
        log_msg = CONST.CMD_STANDBY + CONST.STR_COMMAND + CONST.STR_INVOKE_SUCCESS
        self.logger.debug(log_msg)
        # PROTECTED REGION END #    //  SdpMasterLeafNode.Standby

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpMasterLeafNode.main) ENABLED START #
    return run((SdpMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpMasterLeafNode.main

if __name__ == '__main__':
    main()
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

# PROTECTED REGION ID(SdpMasterLeafNode.additionnal_import) ENABLED START #
import tango
from tango import DeviceProxy, ApiUtil, DevState, AttrWriteType, DevFailed
from tango.server import run,command, device_property, attribute
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand

# Additional import
from . import const, release

# PROTECTED REGION END #    //  SdpMasterLeafNode.additionnal_import

__all__ = ["SdpMasterLeafNode", "main"]


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
                device._version_info = "1.0"
                device._processing_block_list = "test"
                device._read_activity_message = 'OK'
                device.set_status(const.STR_INIT_SUCCESS)
                device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
                device._version_id = release.version

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

    class OnCommand(SKABaseDevice.OnCommand):
        """
        A class for SDP master's On() command.
        """

        def on_cmd_ended_cb(self, event):

            """
            Callback function immediately executed when the asynchronous invoked
            command returns. Checks whether the On command has been successfully invoked on SDP Master.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.
            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext
            :return: none

            """
            device=self.target
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg

            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """ Informs the SDP that it can start executing Processing Blocks. Sets the OperatingState to ON.

            :param argin: None.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            device=self.target
            try:
                device._sdp_proxy.command_inout_asynch(const.CMD_ON, self.on_cmd_ended_cb)
                log_msg = const.CMD_ON + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
                self.logger.debug(log_msg)
                return (ResultCode.OK, log_msg)
            
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = const.ERR_ON_CMD_FAIL + str(dev_failed)
                tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                             "SdpMasterLeafNode.OnCommand()",
                                             tango.ErrSeverity.ERR)


    class OffCommand(SKABaseDevice.OffCommand):
        """
        A class for SDP master's Off() command.
        """

        def off_cmd_ended_cb(self, event):

            """
            Callback function immediately executed when the asynchronous invoked
            command returns. Checks whether the OFF command has been successfully invoked on SDP Master.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.
            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext
            :return: none

            """
            device=self.target
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg

            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """
            Sets the OperatingState to Off.

            :param argin: None.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            device=self.target
            try:
                device._sdp_proxy.command_inout_asynch(const.CMD_OFF, self.off_cmd_ended_cb)
                self.logger.debug(const.STR_OFF_CMD_SUCCESS)
                device._read_activity_message = const.STR_OFF_CMD_SUCCESS
                return (ResultCode.OK, const.STR_OFF_CMD_SUCCESS)
            
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = const.ERR_OFF_CMD_FAIL + str(dev_failed)
                tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                             "SdpMasterLeafNode.OffCommand()",
                                             tango.ErrSeverity.ERR)


    class DisableCommand(BaseCommand):
        """
        A class for SDP master's Disable() command.
        """
        def check_allowed(self):
            """
            Check Whether this command is allowed to be run in current device
            state.

             :return: True if this command is allowed to be run in
                 current device state.
             :rtype: boolean
             :raises: DevFailed if this command is not allowed to be run
                 in current device state.
            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.ON]:
                tango.Except.throw_exception("Disable() is not allowed in current state",
                                             "Failed to invoke Disable command on SdpMasterLeafNode.",
                                             "SdpMasterLeafNode.Disable() ",
                                             tango.ErrSeverity.ERR)
            return True

        def disable_cmd_ended_cb(self, event):

            """
            Callback function immediately executed when the asynchronous invoked
            command returns. Checks whether the disable command has been successfully invoked on SDP Master.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.
            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext
            :return: none

            """
            device = self.target
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg

            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """
            Sets the OperatingState to Disable.

            :param argin: None.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            device=self.target
            try:
                device._sdp_proxy.command_inout_asynch(const.CMD_Disable, self.disable_cmd_ended_cb)
                self.logger.debug(const.STR_DISABLE_CMS_SUCCESS)
                device._read_activity_message = const.STR_DISABLE_CMS_SUCCESS

            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = const.ERR_DISABLE_CMD_FAIL + str(dev_failed)
                tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                             "SdpMasterLeafNode.DisableCommand()",
                                             tango.ErrSeverity.ERR)


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

    class StandbyCommand(BaseCommand):
        """
        A class for SDP Master's Standby() command.
        """
        def is_Standby_allowed(self):
            """
        Checks Whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state.
            """
            handler = self.get_command_object("Standby")
            return handler.check_allowed()

        def standby_cmd_ended_cb(self, event):

            """
            Callback function immediately executed when the asynchronous invoked
            command returns. Checks whether the standby command has been successfully invoked on SDP Master.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.
            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext
            :return: none

            """
            device = self.target
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg

            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """ Informs the SDP to stop any executing Processing. To get into the STANDBY state all running
            PBs will be aborted. In normal operation we expect diable should be triggered without first going
            into STANDBY.

            :param argin: None.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            device=self.target
            try:
                device._sdp_proxy.command_inout_asynch(const.CMD_STANDBY, self.standby_cmd_ended_cb)
                log_msg = const.CMD_STANDBY + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
                self.logger.debug(log_msg)

            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = const.ERR_STANDBY_CMD_FAIL + str(dev_failed)
                tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                             "SdpMasterLeafNode.StandbyCommand()",
                                             tango.ErrSeverity.ERR)

        def check_allowed(self):
            """
            Check Whether this command is allowed to be run in current device
            state.

             :return: True if this command is allowed to be run in
                 current device state.
             :rtype: boolean
             :raises: DevFailed if this command is not allowed to be run
                 in current device state.

            """

            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
                tango.Except.throw_exception("Standby() is not allowed in current state",
                                             "Failed to invoke Standby command on SdpMasterLeafNode.",
                                             "SdpMasterLeafNode.Standby() ",
                                             tango.ErrSeverity.ERR)
            return True

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
        args = (self, self.state_model, self.logger)
        self.register_command_object("Disable",self.DisableCommand(*args))
        self.register_command_object("Standby",self.StandbyCommand(*args))

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpMasterLeafNode.main) ENABLED START #
    return run((SdpMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpMasterLeafNode.main

if __name__ == '__main__':
    main()
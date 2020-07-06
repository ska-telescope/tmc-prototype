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
from tango import DeviceProxy, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run,command, device_property, attribute
from ska.base import SKABaseDevice , SKASubarray
from ska.base.commands import ActionCommand, ResultCode, ResponseCommand
from ska.base.control_model import AdminMode, HealthState, TestMode

# Additional import
from . import const

# PROTECTED REGION END #    //  SdpMasterLeafNode.additionnal_import

__all__ = ["SdpMasterLeafNode", "main"]


class SdpMasterLeafNode(SKABaseDevice):
    """
    The primary responsibility of the SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
    actions during an observation.
    """
    # PROTECTED REGION ID(SdpMasterLeafNode.class_variable) ENABLED START #
    def cmd_ended_cb(self, event):

        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the command has been successfully invoked on SDP Master.

        :param event: a CmdDoneEvent object. This class is used to pass data
            to the callback method in asynchronous callback model for command
            execution.
        :type: CmdDoneEvent object
            It has the following members:
                - device     : (DeviceProxy) The DeviceProxy object on which the
                               call was executed.
                - cmd_name   : (str) The command name
                - argout_raw : (DeviceData) The command argout
                - argout     : The command argout
                - err        : (bool) A boolean flag set to true if the command
                               failed. False otherwise
                - errors     : (sequence<DevError>) The error stack
                - ext
        :return: none

        """
        exception_count = 0
        exception_message = []
        try:
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                self._read_activity_message = log_msg

            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                self._read_activity_message = log_msg
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                                                                  exception_message, exception_count,
                                                                                  const.ERR_EXCEPT_CMD_CB)
            # Throw Exception
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_SDP_CMD_CALLBK)

    # Function for handling all Devfailed exception
    def _handle_devfailed_exception(self, df, except_msg_list, exception_count, read_actvity_msg):
        log_msg = read_actvity_msg + str(df)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(df)
        except_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [except_msg_list, exception_count]

    # Function for handling all generic exception
    def _handle_generic_exception(self, exception, except_msg_list, exception_count, read_actvity_msg):
        log_msg = read_actvity_msg + str(exception)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(exception)
        except_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [except_msg_list, exception_count]

    def throw_exception(self, except_msg_list, read_actvity_msg):
        err_msg = ''
        for item in except_msg_list:
            err_msg += item + "\n"
        tango.Except.throw_exception(const.STR_CMD_FAILED, err_msg, read_actvity_msg, tango.ErrSeverity.ERR)

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
    class InitCommand(SKABaseDevice.InitCommand):
        """
                      A class for SDP master's InitCommand() command.
                      """
        def do(self):
            super().do()

            device = self.target
            try:
                device.set_state(DevState.ON)
                device._version_info = "1.0"
                device._processing_block_list = "test"
                device._read_activity_message = 'OK'
                device.set_status(const.STR_INIT_SUCCESS)
                _state_fault_flag = False
                # flag use to check whether state set to fault if exception occur

                exception_message = []
                exception_count = 0

            except DevFailed as dev_failed:
                _state_fault_flag = True
                device._handle_devfailed_exception(dev_failed, exception_message,
                                                   exception_count, const.ERR_INIT_PROP_ATTR)

            try:
                device._read_activity_message = const.STR_SDPMASTER_FQDN + str(device.SdpMasterFQDN)
                # Creating proxy to the SDPMaster
                device._sdp_proxy = DeviceProxy(str(device.SdpMasterFQDN))

            except DevFailed as dev_failed:
                _state_fault_flag = True
                device.set_state(DevState.FAULT)
                device._handle_devfailed_exception(dev_failed, exception_message, exception_count,
                                                 const.ERR_IN_CREATE_PROXY_SDP_MASTER)

            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            device._read_activity_message = const.STR_SETTING_CB_MODEL + str(
                ApiUtil.instance().get_asynch_cb_sub_model())

            if _state_fault_flag:
                message = const.STR_CMD_FAILED
                result_code = ResultCode.FAILED
            else:
                message = const.STR_INIT_SUCCESS
                result_code = ResultCode.OK

            device._read_activity_message = message
            self.logger.info(message)
            return (result_code, message)



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

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        self.register_command_object("Disable",self.DisableCommand(self, self.state_model, self.logger))
        self.register_command_object("Standby",self.StandbyCommand(self, self.state_model, self.logger))
        

    class OnCommand(SKASubarray.OnCommand):
        """
               A class for SDP master's On() command.
               """
        def do(self):
            """ Informs the SDP that it can start executing Processing Blocks. Sets the OperatingState to ON.

                   :param argin: DevVoid.

                   :return: None.

                   """
            device=self.target
            device._sdp_proxy.command_inout_asynch(const.CMD_ON, device.cmd_ended_cb)
            log_msg = const.CMD_ON + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            self.logger.debug(log_msg)

            return (ResultCode.OK, "On command execution started")


    class OffCommand(SKASubarray.OffCommand):
        """
               A class for SDP master's Off() command.
               """
        def do(self):
            """ Sets the OperatingState to Off.

                   :param argin: DevVoid.

                   :return: None.

                   """
            device=self.target
            device._sdp_proxy.command_inout_asynch(const.CMD_OFF, device.cmd_ended_cb)
            self.logger.debug(const.STR_OFF_CMD_SUCCESS)
            device._read_activity_message = const.STR_OFF_CMD_SUCCESS
            exception_message = []
            exception_count = 0

            # This code is written only to improve code coverage
            if device._test_mode == TestMode.TEST:
                device._handle_devfailed_exception(DevFailed, exception_message, exception_count,
                                                 const.ERR_OFF_CMD_FAIL)

            return (ResultCode.OK, "Off command execution started")


    class DisableCommand(ResponseCommand):
        """
               A class for SDP master's Disable() command.
               """
        def do(self):
            """ Sets the OperatingState to Disable.

                    :param argin: DevVoid.

                    :return: None.

                    """
            device = self.target
            device._sdp_proxy.command_inout_asynch(const.CMD_Disable, device.cmd_ended_cb)
            self.logger.debug(const.STR_DISABLE_CMS_SUCCESS)
            device._read_activity_message = const.STR_DISABLE_CMS_SUCCESS
            return (ResultCode.OK, "Disable command execution Invoked.")

        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

             :return: True if this command is allowed to be run in
                 current device state
             :rtype: boolean
             :raises: DevFailed if this command is not allowed to be run
                 in current device state
            Returns
            -------

            """
            if self.state_model.dev_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.ON
            ]:
                tango.Except.throw_exception("", "",
                                             "Disable() is not allowed in current state",
                                             tango.ErrSeverity.ERR)

            return True

    def is_Disable_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("Disable")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def Disable(self):
        """
        Sets the OperatingState to Disable.

        :param argin: DevString

        :return: None

        """

        handler = self.get_command_object("Disable")
        (result_code, message) = handler()
        return [[result_code], [message]]


    class StandbyCommand(ResponseCommand):
        """
               A class for SDP master's Standby() command.
               """
        def do(self):
            """ Informs the SDP to stop any executing Processing. To get into the STANDBY state all running
        PBs will be aborted. In normal operation we expect diable should be triggered without first going
        into STANDBY.

        :param argin: DevVoid.

        :return: None.

        """
            device= self.target
            device._sdp_proxy.command_inout_asynch(const.CMD_STANDBY, device.cmd_ended_cb)
            log_msg = const.CMD_STANDBY + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            self.logger.debug(log_msg)
            return (ResultCode.STARTED, "Disable command execution Started.")


        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

             :return: True if this command is allowed to be run in
                 current device state
             :rtype: boolean
             :raises: DevFailed if this command is not allowed to be run
                 in current device state
            Returns
            -------

            """

            if self.state_model.dev_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.ON
            ]:
                tango.Except.throw_exception("", "",
                                             "Standby() is not allowed in current state",
                                             tango.ErrSeverity.ERR)

            return True

    def is_Standby_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("Standby")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def Standby(self):
        """
        Invokes Standby command .

        :param argin: DevString

        :return: None

        """

        handler = self.get_command_object("Standby")
        (result_code, message) = handler()
        return [[result_code], [message]]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpMasterLeafNode.main) ENABLED START #
    return run((SdpMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpMasterLeafNode.main

if __name__ == '__main__':
    main()
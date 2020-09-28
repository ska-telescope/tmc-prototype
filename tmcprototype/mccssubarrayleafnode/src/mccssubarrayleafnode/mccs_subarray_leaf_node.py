# -*- coding: utf-8 -*-
#
# This file is part of the MccsSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" 

"""

# Tango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, DevState, DevFailed
from tango.server import run, attribute, command, device_property, DeviceMeta
from ska.base.commands import ResultCode, BaseCommand
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState

# Additional import
from . import const, release
# PROTECTED REGION ID(MccsSubarrayLeafNode.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  MccsSubarrayLeafNode.additionnal_import

__all__ = ["MccsSubarrayLeafNode", "main"]


class MccsSubarrayLeafNode(SKABaseDevice):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(MccsSubarrayLeafNode.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  MccsSubarrayLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------





    MccsSubarrayFQDN = device_property(
        dtype='str', default_value="low_mccs/elt/subarray_01"
    )

    # ----------
    # Attributes
    # ----------







    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )


    mccssubarrayHealthState = attribute(name="mccssubarrayHealthState", label="mccssubarrayHealthState",
        forwarded=True
    )
    mccsSubarrayObsState = attribute(name="mccsSubarrayObsState", label="mccsSubarrayObsState",
        forwarded=True
    )
    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the MccsSubarrayLeafNode's init_device() method"
        """

        def do(self):
            """
            Initializes the attributes and properties of the MCCSSubarrayLeafNode.

            :return: A tuple containing a return code and a string message indicating status. The message is
            for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if error occurs in creating proxy for MCCSSubarray.
            """
            super().do()
            device = self.target
            try:
                # create MccsSubarray Proxy
                device._mccs_subarray_proxy = DeviceProxy(device.MccsSubarrayFQDN)
            except DevFailed as dev_failed:
                log_msg = const.ERR_IN_CREATE_PROXY_MCCSSA + str(dev_failed)
                self.logger.debug(log_msg)
                return (ResultCode.FAILED, log_msg)
            #TODO
            # self.set_change_event("adminMode", True, True)
            # self.set_archive_event("adminMode", True, True)
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device._read_activity_message = " "
            device._versioninfo = " "
            device.set_status(const.STR_MCCSSALN_INIT_SUCCESS)
            device._mccs_subarray_health_state = HealthState.OK
            self.logger.info(const.STR_MCCSSALN_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_MCCSSALN_INIT_SUCCESS)
        # PROTECTED REGION ID(MccsSubarrayLeafNode.init_device) ENABLED START #
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.init_device


    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("Scan", self.ScanCommand(*args))
        self.register_command_object("End", self.EndCommand(*args))
        self.register_command_object("EndScan", self.EndScanCommand(*args))

    def always_executed_hook(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.activitymessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.activitymessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.activitymessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.activitymessage_write


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.AssignResources) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.AssignResources

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.ReleaseResources) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.ReleaseResources

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.Configure) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.Configure

    class ScanCommand(BaseCommand):
        """
        A class for MccsSubarrayLeafNode's StartScan() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in
                current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
                in current device state

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Scan() is not allowed in current state",
                                             "Failed to invoke Scan command on mccssubarrayleafnode.",
                                             "mccssubarrayleafnode.Scan()",
                                             tango.ErrSeverity.ERR)

            return True

        def scan_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

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

            device = self.target
            # Update logs and activity message attribute with received event
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self, argin):
            """
            This command invokes Scan command on MccsSubarray. It is allowed only when MccsSubarray is in
            ObsState READY.

            :param argin: JSON string consists of scan id (int).

            Example:
            {"id":1}

            Note: Enter the json string without spaces as a input.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if the command execution is not successful
            """
            device = self.target
            try:
                assert device._mccs_subarray_proxy.obsState == ObsState.READY
                device._mccs_subarray_proxy.command_inout_asynch(const.CMD_STARTSCAN, argin,
                                                             self.scan_cmd_ended_cb)
                device._read_activity_message = const.STR_STARTSCAN_SUCCESS
                self.logger.info(const.STR_STARTSCAN_SUCCESS)

            except AssertionError as assertion_error:
                log_msg = const.ERR_DEVICE_NOT_READY + str(assertion_error)
                device._read_activity_message = log_msg
                self.logger.exception(log_msg)
                tango.Except.throw_exception(const.STR_START_SCAN_EXEC, log_msg,
                                             "MccsSubarrayLeafNode.ScanCommand",
                                             tango.ErrSeverity.ERR)

            except DevFailed as dev_failed:
                log_msg = const.ERR_STARTSCAN_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_START_SCAN_EXEC, log_msg,
                                             "MccsSubarrayLeafNode.ScanCommand",
                                             tango.ErrSeverity.ERR)

    @command(
        dtype_in=('str',)
    )
    @DebugIt()
    def Scan(self, argin):
        """ Invokes StartScan command on mccssubarrayleafnode"""
        handler = self.get_command_object("Scan")
        handler(argin)

    def is_Scan_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
        current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
        in current device state

        """
        handler = self.get_command_object("Scan")
        return handler.check_allowed()


    class EndScanCommand(BaseCommand):
        """
        A class for MccsSubarrayLeafNode's EndScan() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in
                current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
                in current device state

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("EndScan() is not allowed in current state",
                                             "Failed to invoke EndScan command on mccssubarrayleafnode.",
                                             "mccssubarrayleafnode.EndScan()",
                                             tango.ErrSeverity.ERR)

            return True

        def endscan_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

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
            device = self.target
            # Update logs and activity message attribute with received event
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
            This command invokes EndScan command on MccsSubarray. It is allowed only when MccsSubarray is in
            ObsState SCANNING.

            :raises: DevFailed if the command execution is not successful.
                     AssertionError if MccsSubarray is not in SCANNING obsState.
            """
            device = self.target
            try:
                assert device._mccs_subarray_proxy.obsState == ObsState.SCANNING
                device._mccs_subarray_proxy.command_inout_asynch(const.CMD_ENDSCAN,
                                                                 self.endscan_cmd_ended_cb)
                device._read_activity_message = const.STR_ENDSCAN_SUCCESS
                self.logger.info(const.STR_ENDSCAN_SUCCESS)

            except AssertionError:
                device._read_activity_message = const.ERR_DEVICE_NOT_SCANNING
                self.logger.error(const.ERR_DEVICE_NOT_SCANNING)
                tango.Except.throw_exception(const.STR_END_SCAN_EXEC, const.ERR_DEVICE_NOT_SCANNING,
                                             "MCCSSubarrayLeafNode.EndScanCommand",
                                             tango.ErrSeverity.ERR)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ENDSCAN_COMMAND + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_END_SCAN_EXEC, log_msg,
                                             "MccsSubarrayLeafNode.EndScanCommand",
                                             tango.ErrSeverity.ERR)

    @command()
    def EndScan(self):
        """ Invokes EndScan command on MccsSubarray."""
        handler = self.get_command_object("EndScan")
        handler()

    def is_EndScan_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state.

        :return: True if this command is allowed to be run in
        current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
        in current device state

        """
        handler = self.get_command_object("EndScan")
        return handler.check_allowed()


    class EndCommand(BaseCommand):
        """
        A class for MccsSubarrayLeafNode's End() command.
        """
        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in
                current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
                in current device state

            """
            if self.state_model.op_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("End() is not allowed in current state",
                                             "Failed to invoke End command on MccsSubarrayLeafNode.",
                                             "Mccssubarrayleafnode.End()",
                                             tango.ErrSeverity.ERR)
            return True

        def end_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

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
            device = self.target
            # Update logs and activity message attribute with received event
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
            This command invokes End command on MCCS Subarray in order to end current scheduling block.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if the command execution is not successful
            """
            device = self.target
            try:
                assert device._mccs_subarray_proxy.obsState == ObsState.READY
                device._mccs_subarray_proxy.command_inout_asynch(const.CMD_END,
                                                                self.end_cmd_ended_cb)
                device._read_activity_message = const.STR_END_SUCCESS
                self.logger.info(const.STR_END_SUCCESS)

            except AssertionError:
                log_msg = const.STR_OBS_STATE
                device._read_activity_message = const.ERR_DEVICE_NOT_READY
                self.logger.error(log_msg)
                tango.Except.throw_exception(const.STR_END_EXEC, const.ERR_DEVICE_NOT_READY,
                                             "MCCSSubarrayLeafNode.EndCommand",
                                             tango.ErrSeverity.ERR)
            except DevFailed as dev_failed:
                log_msg = const.ERR_END_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.ERR_END_INVOKING_CMD, log_msg,
                                             "MccsSubarrayLeafNode.EndCommand",
                                             tango.ErrSeverity.ERR)

    def is_End_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
        current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
        in current device state

        """
        handler = self.get_command_object("End")
        return handler.check_allowed()


    @command(
    )
    @DebugIt()
    def End(self):
        """ Invokes End command on MccsSubarrayLeafNode. """
        handler = self.get_command_object("End")
        handler()


    @command(
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.Abort) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.Abort

    @command(
    )
    @DebugIt()
    def Restart(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.Restart) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.Restart

    @command(
    )
    @DebugIt()
    def obsReset(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.obsReset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.obsReset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MccsSubarrayLeafNode.main) ENABLED START #
    return run((MccsSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MccsSubarrayLeafNode.main

if __name__ == '__main__':
    main()

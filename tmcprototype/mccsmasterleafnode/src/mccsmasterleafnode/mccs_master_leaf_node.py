# -*- coding: utf-8 -*-
#
# This file is part of the MCCSMasterLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

"""
from __future__ import print_function
from __future__ import absolute_import

# Tango imports
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute, Device, DeviceMeta
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, ResponseCommand
from ska.base.control_model import HealthState, SimulationMode, TestMode

# Additional import
# PROTECTED REGION ID(MCCSMasterLeafNode.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  MCCSMasterLeafNode.additionnal_import

__all__ = ["MCCSMasterLeafNode", "main"]


class MCCSMasterLeafNode(SKABaseDevice):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(MCCSMasterLeafNode.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------





    MCCSMasterFQDN = device_property(
        dtype='str', default_value="low_mccs/elt/master"
    )

    # ----------
    # Attributes
    # ----------









    activitymessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )


    mccsHealthState = attribute(name="mccsHealthState", label="mccsHealthState", forwarded=True)
    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC MCCS Master Leaf Node's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the MccsMasterLeafNode.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if error occurs while creating the device proxy for MCCS Master or
                    subscribing the evennts.
            """
            super().do()
            device = self.target
            device._health_state = HealthState.OK  # Setting healthState to "OK"
            device._simulation_mode = SimulationMode.FALSE  # Enabling the simulation mode
            device._test_mode = TestMode.NONE
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device._read_activity_message = const.STR_MCCS_INIT_LEAF_NODE
            try:
                device._read_activity_message = const.STR_MCCSMASTER_FQDN + str(device.MCCSMasterFQDN)
                # Creating proxy to the MCCSMaster
                log_msg = "MCCS Master name: " + str(device.MCCSMasterFQDN)
                self.logger.debug(log_msg)
                device._mccs_master_proxy = DeviceProxy(str(device.MCCSMasterFQDN))
            except DevFailed as dev_failed:
                log_msg = const.ERR_IN_CREATE_PROXY + str(device.MCCSMasterFQDN)
                self.logger.debug(log_msg)
                self.logger.exception(dev_failed)
                device._read_activity_message = log_msg
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "MccsMasterLeafNode.InitCommand.do()",
                                             tango.ErrSeverity.ERR)

            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_msg = const.STR_SETTING_CB_MODEL + str(ApiUtil.instance().get_asynch_cb_sub_model())
            self.logger.debug(log_msg)

            device._read_activity_message = const.STR_INIT_SUCCESS
            self.logger.info(device._read_activity_message)
            return (ResultCode.OK, device._read_activity_message)

    def always_executed_hook(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activitymessage(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.activitymessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.activitymessage_read

    def write_activitymessage(self, value):
        # PROTECTED REGION ID(MCCSMasterLeafNode.activitymessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.activitymessage_write


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def AssignResource(self, argin):
        # PROTECTED REGION ID(MCCSMasterLeafNode.AssignResource) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.AssignResource

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(MCCSMasterLeafNode.ReleaseResources) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.ReleaseResources


    class OnCommand(SKABaseDevice.OnCommand):
        """
        A class for MCCSMasterLeafNode's On() command.
        """

        def on_cmd_ended_cb(self, event):
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
            Invokes On command on the MCCS Element.

            :param argin: None

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            device = self.target
            # Pass argin to mccs master .
            # If the array length is 0, the command applies to the whole MCCS Element.
            # If the array length is > 1 each array element specifies the FQDN of the MCCS SubElement to switch ON.
            argin = []
            device._mccs_master_proxy.command_inout_asynch(const.CMD_ON, argin, self.on_cmd_ended_cb)
            self.logger.debug(const.STR_ON_CMD_ISSUED)
            return (ResultCode.OK, const.STR_ON_CMD_ISSUED)

    @command(
    )
    @DebugIt()
    def On(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.On) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.On
    
    class OffCommand(SKABaseDevice.OffCommand):
        """
        A class for MCCSMasterLeafNode's Off() command.
        """

        def off_cmd_ended_cb(self, event):
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
            Invokes Off command on the MCCS Element.

            :param argin: None.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            device = self.target
            # pass argin to mccs master.
            # If the array length is 0, the command applies to the whole MCCS Element.
            # If the array length is >, each array element specifies the FQDN of the MCCS SubElement to switch OFF.
            argin = []
            device._mccs_master_proxy.command_inout_asynch(const.CMD_OFF, argin, self.off_cmd_ended_cb)
            self.logger.debug(const.STR_OFF_CMD_ISSUED)
            device._read_activity_message = const.STR_OFF_CMD_ISSUED
            return (ResultCode.OK, const.STR_OFF_CMD_ISSUED)

    @command(
    )
    @DebugIt()
    def Off(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.Off) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.Off

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        # self.register_command_object("Disable",self.DisableCommand(*args))
        # self.register_command_object("Standby",self.StandbyCommand(*args))
        
# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MCCSMasterLeafNode.main) ENABLED START #
    """
    Runs the MccsMasterLeafNode.

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: MccsMasterLeafNode TANGO object.
    """
    return run((MCCSMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.main

if __name__ == '__main__':
    main()

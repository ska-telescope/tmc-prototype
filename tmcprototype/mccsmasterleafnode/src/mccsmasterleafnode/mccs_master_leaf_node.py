# -*- coding: utf-8 -*-
#
# This file is part of the MccsMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #
from __future__ import print_function
from __future__ import absolute_import

# Tango imports
import tango
from tango import DeviceProxy, ApiUtil, AttrWriteType, DevFailed
from tango.server import run, device_property, attribute
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, SimulationMode, TestMode

# Additional import
from . import const, release

# PROTECTED REGION END #    //  MccsMasterLeafNode imports

__all__ = ["MccsMasterLeafNode", "main"]

class MccsMasterLeafNode(SKABaseDevice):
    """
    **Properties:**

    - MccsMasterFQDN   - Property to provide FQDN of MCCS Master Device

    **Attributes:**

    - mccsHealthState  - Forwarded attribute to provide MCCS Master Health State
    - activityMessage - Attribute to provide activity message

    """
    # PROTECTED REGION ID(MccsMasterLeafNode.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  MccsMasterLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------





    MccsMasterFQDN = device_property(
        dtype='str', default_value="low_mccs/elt/master"
    )

    






    # ----------
    # Attributes
    # ----------

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
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

            :raises: DevFailed if error occurs while creating the device proxy for Mccs Master or
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
                device._read_activity_message = const.STR_MCCSMASTER_FQDN + str(device.MccsMasterFQDN)
                # Creating proxy to the CSPMaster
                log_msg = "MCCS Master name: " + str(device.MccsMasterFQDN)
                self.logger.debug(log_msg)
                device._mccs_master_proxy = DeviceProxy(str(device.MccsMasterFQDN))
            except DevFailed as dev_failed:
                log_msg = const.ERR_IN_CREATE_PROXY + str(device.MccsMasterFQDN)
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
        # PROTECTED REGION ID(MccsMasterLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsMasterLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(MccsMasterLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsMasterLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(MccsMasterLeafNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  MccsMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(MccsMasterLeafNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  MccsMasterLeafNode.activityMessage_write


    # --------
    # Commands
    # --------

    class OnCommand(SKABaseDevice.OnCommand):
        """
        A class for MccsMasterLeafNode's On() command.
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
            device._mccs_master_proxy.command_inout_asynch(const.CMD_ON, self.on_cmd_ended_cb)
            self.logger.debug(const.STR_ON_CMD_ISSUED)
            return (ResultCode.OK, const.STR_ON_CMD_ISSUED)


    class OffCommand(SKABaseDevice.OffCommand):
        """
        A class for MccsMasterLeafNode's Off() command.
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
            device._mccs_master_proxy.command_inout_asynch(const.CMD_OFF, self.off_cmd_ended_cb)
            self.logger.debug(const.STR_OFF_CMD_ISSUED)
            device._read_activity_message = const.STR_OFF_CMD_ISSUED
            return (ResultCode.OK, const.STR_OFF_CMD_ISSUED)

    #TODO : Commented out for now to resolve pylint warnings
    # def init_command_objects(self):
    #     """
    #     Initialises the command handlers for commands supported by this
    #     device.
    #     """
    #     super().init_command_objects()
    #     args = (self, self.state_model, self.logger)
        
# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MccsMasterLeafNode.main) ENABLED START #
    """
    Runs the MccsMasterLeafNode.

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: MccsMasterLeafNode TANGO object.
    """
    return run((MccsMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MccsMasterLeafNode.main

if __name__ == '__main__':
    main()

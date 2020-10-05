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
from tango import DeviceProxy, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from ska.base.control_model import HealthState, SimulationMode, TestMode, ObsState

# Additional import
from . import const, release
from .exceptions import InvalidObsStateError

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

    # -----------------
    # Device Properties
    # -----------------

    MccsMasterFQDN = device_property(
        dtype='str', default_value="low-mccs/control/control"
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

    def validate_obs_state(self):
        if self._mccs_master_proxy.obsState == ObsState.EMPTY:
            self.logger.info("Mccs Master is in required obsState, resources will be assigned")
        else:
            self.logger.error("Mccs Master is not in EMPTY obsState")
            self._read_activity_message = "Error in device obsState"
            raise InvalidObsStateError("Mccs Master is not in EMPTY obsState")

    
    class AssignResourcesCommand(BaseCommand):
        """
        A class for MccsMasterLeafNode's AssignResources() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
                in current device state

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("AssignResources() is not allowed in current state",
                                             "Failed to invoke AssignResources command on "
                                             "mccsmasterleafnode.",
                                             "mccsmasterleafnode.AssignResources()",
                                             tango.ErrSeverity.ERR)
            return True

        def allocate_ended(self, event):
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

            :raises: DevFailed if this command is not allowed to be run
            in current device state

            """
            device = self.target
            self.logger.info("Executing callback allocate_ended")
            try:
                if event.err:
                    device._read_activity_message = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                        event.errors)
                    log = const.ERR_INVOKING_CMD + event.cmd_name
                    self.logger.error(log)
                else:
                    log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                    device._read_activity_message = log
                    self.logger.info(log)

            except tango.DevFailed as df:
                self.logger.exception(df)
                tango.Except.re_throw_exception(df, "MCCS master gave an error response",
                                                "MCCS master threw error in Allocate MCCS LMC_CommandFailed",
                                                "Allocate", tango.ErrSeverity.ERR)

        def do(self, argin):
            """
            It accepts stationiDList list, channels and stationBeamiDList in JSON string format and invokes allocate command on MccsMaster
            with JSON string as an input argument.

            :param argin:StringType. The string in JSON format.
               
            Example:
            {
                "subarray_id": 1,
                "station_ids": [1,2],
                "channels": [1,2,3,4,5,6,7,8],
                "station_beam_ids": [1],
                "tile_ids": [1,2,3,4]
        
            }

            :return: None

            Note: Enter the json string without spaces as an input.

            :raises: ValueError if input argument json string contains invalid value
                     KeyError if input argument json string contains invalid key
                     DevFailed if the command execution is not successful
            """
            device = self.target
            try:
                log_msg = "Input JSON for MCCS master leaf node AssignResources command is: " + argin
                self.logger.debug(log_msg)
                self.logger.info("Invoking Allocate on MCCS master")
                device._mccs_master_proxy.command_inout_asynch(const.CMD_ALLOCATE, argin,
                                                        self.allocate_ended)
                self.logger.info("After invoking Allocate on MCCS master")
                device._read_activity_message = const.STR_ALLOCATE_SUCCESS
                self.logger.info(const.STR_ALLOCATE_SUCCESS)

            except ValueError as value_error:
                log_msg = const.ERR_INVALID_JSON_ASSIGN_RES_MCCS + str(value_error)
                device._read_activity_message = const.ERR_INVALID_JSON_ASSIGN_RES_MCCS + str(value_error)
                self.logger.exception(value_error)
                tango.Except.re_throw_exception(value_error, const.STR_ASSIGN_RES_EXEC, log_msg,
                                             "MccsMasterLeafNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)

            except KeyError as key_error:
                log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                device._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                self.logger.exception(key_error)
                tango.Except.re_throw_exception(key_error,const.STR_ASSIGN_RES_EXEC, log_msg,
                                             "MccsMasterLeafNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)
            except DevFailed as dev_failed:
                log_msg = const.ERR_ASSGN_RESOURCE_MCCS + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.re_throw_exception(dev_failed, const.STR_ASSIGN_RES_EXEC, log_msg,
                                             "MccsMasterLeafNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)
                                             
    @command(
        dtype_in='str',
    )
    @DebugIt()
    def AssignResources(self, argin):
        """ Invokes AssignResources command on Mcccs Master"""
        handler = self.get_command_object("AssignResources")
        try:
            self.validate_obs_state()

        except InvalidObsStateError as error:
            self.logger.exception(error)
            tango.Except.throw_exception("ObsState is not in EMPTY state",
                                         "Mccs master node raised exception",
                                         "MccsMaster.Allocate",
                                         tango.ErrSeverity.ERR)
        handler(argin)
    

    def is_AssignResources_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean
        """
        handler = self.get_command_object("AssignResources")
        return handler.check_allowed()

    class ReleaseResourcesCommand(BaseCommand):
        """
        A class for MccsMasterLeafNode's ReleaseResources() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: ValueError if input argument json string contains invalid value
                    DevFailed if this command is not allowed to be run in current device state

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("ReleaseResources() is not allowed in current state",
                                             "Failed to invoke ReleaseResources command on "
                                             "mccsmasterleafnode.",
                                             "mccsmasterleafnode.ReleaseResources()",
                                             tango.ErrSeverity.ERR)
            return True

        def releaseresources_cmd_ended_cb(self, event):
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

        def do(self, argin):
            """
            It invokes ReleaseResources command on MccsMaster and releases all the resources assigned to
            MccsMaster.

            :param argin:StringType. The string in JSON format.

            Example: 
                {
                    "subarray_id": 1,
                    "release_all": true,
                }

            :return: None.

            :raises: DevFailed if the command execution is not successful


            """
            device = self.target
            log_msg = "Input JSON for MCCS master leaf node Release command is: " + argin
            self.logger.debug(log_msg)
            self.logger.info("Invoking Release on MCCS master")

            try:
                device._mccs_master_proxy.command_inout_asynch(const.CMD_Release, argin,
                                                        self.releaseresources_cmd_ended_cb)
                device._read_activity_message = const.STR_REMOVE_ALL_RECEPTORS_SUCCESS
                self.logger.info(const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)

            except ValueError as value_error:
                log_msg = const.ERR_INVALID_JSON_RELEASE_RES_MCCS + str(value_error)
                device._read_activity_message = const.ERR_INVALID_JSON_RELEASE_RES_MCCS + str(value_error)
                self.logger.exception(value_error)
                tango.Except.re_throw_exception(value_error, const.STR_RELEASE_RES_EXEC, log_msg,
                                             "MccsMasterLeafNode.ReleaseResourcesCommand",
                                             tango.ErrSeverity.ERR)
            
            except DevFailed as dev_failed:
                log_msg = const.ERR_RELEASE_ALL_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.re_throw_exception(dev_failed, const.STR_RELEASE_RES_EXEC, log_msg,
                                             "MccsMasterLeafNode.ReleaseAllResourcesCommand",
                                             tango.ErrSeverity.ERR)
    @command(
        dtype_in='str',
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        """ Invokes ReleaseResources command on MccsMasterLeafNode"""
        handler = self.get_command_object("ReleaseResources")
        handler(argin)

    def is_ReleaseResources_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
                 current device state

        :rtype: boolean

        """
        handler = self.get_command_object("ReleaseResources")
        return handler.check_allowed()
    
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
            try:
                device._mccs_master_proxy.command_inout_asynch(const.CMD_ON, self.on_cmd_ended_cb)
                self.logger.debug(const.STR_ON_CMD_ISSUED)
                return (ResultCode.OK, const.STR_ON_CMD_ISSUED)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ON_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                             "MccsMasterLeafNode.On",
                                             tango.ErrSeverity.ERR)


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
            # If the array length is 0, the command applies to the whole MCCS Element.
            # If the array length is >, each array element specifies the FQDN of the MCCS SubElement to switch OFF.
            try:
                device._mccs_master_proxy.command_inout_asynch(const.CMD_OFF, self.off_cmd_ended_cb)
                self.logger.debug(const.STR_OFF_CMD_ISSUED)
                device._read_activity_message = const.STR_OFF_CMD_ISSUED
                return (ResultCode.OK, const.STR_OFF_CMD_ISSUED)

            except DevFailed as dev_failed:
                log_msg = const.ERR_OFF_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_OFF_EXEC, log_msg,
                                             "MccsMasterLeafNode.Off",
                                             tango.ErrSeverity.ERR)

            

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("AssignResources", self.AssignResourcesCommand(*args))
        self.register_command_object("ReleaseResources", self.ReleaseResourcesCommand(*args))
# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MccsMasterLeafNode.main) ENABLED START #
    """
    Runs the MccsMasterLeafNode.

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: An object of CompletedProcess class returned by the subprocess.
    """
    return run((MccsMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MccsMasterLeafNode.main

if __name__ == '__main__':
    main()

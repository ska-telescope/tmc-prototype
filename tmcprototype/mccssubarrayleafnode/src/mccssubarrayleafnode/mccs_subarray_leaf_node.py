"""
MCCS Subarray Leaf node monitors the MCCS Subarray and issues control actions during an observation.
It also acts as a MCCS contact point for Subarray Node for observation execution for TMC.
"""
# -*- coding: utf-8 -*-
#
# This file is part of the MccsSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PROTECTED REGION ID(MccSubarrayLeafNode.additional_import) ENABLED START #
# Tango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, DevState, DevFailed
from tango.server import run, attribute, command, device_property
from ska.base.commands import ResultCode, BaseCommand
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState

# Additional import
from . import const, release
import json
from datetime import datetime, timedelta
import pytz
# PROTECTED REGION END #    //  MccsSubarrayLeafNode.additional_import

__all__ = ["MccsSubarrayLeafNode", "main"]


class MccsSubarrayLeafNode(SKABaseDevice):
    """
    MCCS Subarray Leaf node monitors the MCCS Subarray and issues control actions during an observation.
    """
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
            Initializes the attributes and properties of the MccsSubarrayLeafNode.

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
            device._sky_coordinates = []
            device.set_status(const.STR_MCCSSALN_INIT_SUCCESS)
            device._mccs_subarray_health_state = HealthState.OK
            self.logger.info(const.STR_MCCSSALN_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_MCCSSALN_INIT_SUCCESS)
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.init_device) ENABLED START #
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.init_device

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
        # PROTECTED REGION ID(MccsSubarrayLeafNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.activityMessage_write


    # --------
    # Commands
    # --------

    class ConfigureCommand(BaseCommand):
        """
        A class for MccsSubarrayLeafNode's Configure() command.
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
                tango.Except.throw_exception("Configure() is not allowed in current state",
                                             "Failed to invoke Configure command on mccssubarrayleafnode.",
                                             "mccssubarrayleafnode.Configure()",
                                             tango.ErrSeverity.ERR)
            return True

        def configure_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.

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
            This command configures a scan. It accepts configuration information in JSON string format and
            invokes Configure command on MccsSubarray.

            :param argin:DevString. The string in JSON format. The JSON contains following values:

            Example:
            {"stations":[{"station_id":1,"tile_ids":[1,2],},{"station_id":2,"tile_ids":[3,4]},],"station_beam_pointings":[{"station_beam_id":1,"target":{"system":"HORIZON","name":"DriftScan","Az":180.0,"El":45.0},"update_rate":0.0,"channels":[1,2,3,4,5,6,7,8]}]}

            Note: Enter the json string without spaces as a input.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if the command execution is not successful
                     ValueError if input argument json string contains invalid value
            """
            device = self.target
            try:
                assert (device._mccs_subarray_proxy.obsState in (ObsState.IDLE, ObsState.READY))
                log_msg = "Input JSON for MCCS Subarray Leaf Node Configure command is: " + argin
                self.logger.info(log_msg)
               
                argin_json = json.loads(argin)
                station_beam_pointings = argin_json["station_beam_pointings"][0]
                azimuth_coord = station_beam_pointings["target"]["Az"]
                elevation_coord = station_beam_pointings["target"]["El"]

                # Append current timestamp into sky_coordinates set
                time_t0 = datetime.today() + timedelta(seconds=0)
                time_t0_utc = (time_t0.astimezone(pytz.UTC)).timestamp()
                device._sky_coordinates.append(time_t0_utc)

                # Append Azimuth and Azimuth_rate into sky_coordinates set
                device._sky_coordinates.append(azimuth_coord)
                device._sky_coordinates.append(0.0)

                # Append Elevation and Elevation_rate into sky_coordinates set
                device._sky_coordinates.append(elevation_coord)
                device._sky_coordinates.append(0.0)

                # Add in sky_coordinates set in station_beam_pointings
                station_beam_pointings["sky_coordinates"] = device._sky_coordinates
                # Remove target block from station_beam_pointings
                station_beam_pointings.pop("target", None)

                argin_json["station_beam_pointings"][0] = station_beam_pointings
                
                device._mccs_subarray_proxy.command_inout_asynch(const.CMD_CONFIGURE, json.dumps(argin_json),
                                                        self.configure_cmd_ended_cb)
                device._read_activity_message = const.STR_CONFIGURE_SUCCESS
                self.logger.info(const.STR_CONFIGURE_SUCCESS)

            except AssertionError:
                log_msg = (f"Mccs Subarray is in ObsState {device._mccs_subarray_proxy.obsState.name}.""Unable to invoke Configure command")
                device._read_activity_message = log_msg
                self.logger.exception(log_msg)
                tango.Except.throw_exception(const.STR_CONFIGURE_EXEC, log_msg,
                                            "MccsSubarrayLeafNode.ConfigureCommand",
                                            tango.ErrSeverity.ERR)

            except DevFailed as dev_failed:
                log_msg = const.ERR_CONFIGURE_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.ERR_CONFIGURE_INVOKING_CMD, log_msg,
                                             "MccsSubarrayLeafNode.ConfigureCommand",
                                             tango.ErrSeverity.ERR)

    def is_Configure_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
        current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
        in current device state

        """
        handler = self.get_command_object("Configure")
        return handler.check_allowed()

    @command(
        dtype_in=('str')
    )
    @DebugIt()
    def Configure(self, argin):
        """ Invokes Configure command on MccsSubarrayLeafNode """
        handler = self.get_command_object("Configure")
        handler(argin)
    

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("Configure", self.ConfigureCommand(*args))
        # self.register_command_object("AssignResources", self.AssignResourcesCommand(*args))



# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MccsSubarrayLeafNode.main) ENABLED START #
    return run((MccsSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MccsSubarrayLeafNode.main

if __name__ == '__main__':
    main()

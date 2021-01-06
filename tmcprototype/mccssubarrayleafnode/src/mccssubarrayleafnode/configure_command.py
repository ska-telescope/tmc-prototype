# PROTECTED REGION ID(MccSubarrayLeafNode.additional_import) ENABLED START #
# Standard python imports
import json
from datetime import datetime, timedelta
import pytz

# Third party imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from tmc.common.tango_client import TangoClient
from . import const
# PROTECTED REGION END #    //  MccsSubarrayLeafNode.additional_import



class Configure(BaseCommand):
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
        device_data = self.target
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            self.logger.error(log_msg)
            device_data._read_activity_message = log_msg
        else:
            log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
            self.logger.info(log_msg)
            device_data._read_activity_message = log_msg

    def do(self, argin):
        """
        This command configures a scan. It accepts configuration information in JSON string format and
        invokes Configure command on MccsSubarray.

        :param argin:DevString. The string in JSON format. The JSON contains following values:

        Example:
        {"stations":[{"station_id":1},{"station_id":2}],"station_beam_pointings":[{"station_beam_id":1,"target":{"system":"HORIZON","name":"DriftScan","Az":180.0,"El":45.0},"update_rate":0.0,"channels":[1,2,3,4,5,6,7,8]}]}

        Note: Enter the json string without spaces as a input.

        :return: A tuple containing a return code and a string message indicating status.
         The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: DevFailed if the command execution is not successful
                 ValueError if input argument json string contains invalid value
                 KeyError if input argument json string contains invalid key
        """
        device_data = self.target
        try:
            mccs_subarray_client = TangoClient(device_data._mccs_subarray_fqdn)
            # TODO: Mock obs_state issue to be resolved
            # assert (mccs_subarray_client.get_attribute("obsState") in (ObsState.IDLE, ObsState.READY))
            log_msg = "Input JSON for MCCS Subarray Leaf Node Configure command is: " + argin
            self.logger.debug(log_msg)

            argin = json.loads(argin)
            station_beam_pointings = self.sky_coordinates(argin)

            # Add station_ids in station_beam_pointings
            updated_argin = self.update_station_ids(argin, station_beam_pointings)

            #Invoke Configure command on MCCSSubarray.
            self.configure_mccs_subarray(updated_argin, mccs_subarray_client)
            device_data._read_activity_message = const.STR_CONFIGURE_SUCCESS
            self.logger.info(const.STR_CONFIGURE_SUCCESS)

        # TODO: Mock obs_state issue to be resolved
        # except AssertionError:
        #     log_msg = (
        #         f"Mccs Subarray is in ObsState {mccs_subarray_client.deviceproxy.obsState.name}.""Unable to invoke Configure command")
        #     device_data._read_activity_message = log_msg
        #     self.logger.exception(log_msg)
        #     tango.Except.throw_exception(const.STR_CONFIGURE_EXEC, log_msg,
        #                                  "MccsSubarrayLeafNode.ConfigureCommand",
        #                                  tango.ErrSeverity.ERR)

        except ValueError as value_error:
            log_msg = const.ERR_INVALID_JSON_CONFIG + str(value_error)
            device_data._read_activity_message = log_msg
            self.logger.exception(value_error)
            tango.Except.throw_exception(const.ERR_CONFIGURE_INVOKING_CMD, log_msg,
                                         "MccsSubarrayLeafNode.Configure",
                                         tango.ErrSeverity.ERR)

        except KeyError as key_error:
            log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            device_data._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self.logger.exception(key_error)
            tango.Except.throw_exception(const.ERR_CONFIGURE_INVOKING_CMD, log_msg,
                                         "MccsSubarrayLeafNode.Configure",
                                         tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = const.ERR_CONFIGURE_INVOKING_CMD + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.ERR_CONFIGURE_INVOKING_CMD, log_msg,
                                         "MccsSubarrayLeafNode.Configure",
                                         tango.ErrSeverity.ERR)

    def sky_coordinates(self, argin):
        station_beam_pointings = argin["station_beam_pointings"][0]
        sky_coordinates = []
        azimuth_coord = station_beam_pointings["target"]["Az"]
        elevation_coord = station_beam_pointings["target"]["El"]

        # Append current timestamp into sky_coordinates set
        time_t0 = datetime.today() + timedelta(seconds=0)
        time_t0_utc = (time_t0.astimezone(pytz.UTC)).timestamp()
        sky_coordinates.append(time_t0_utc)

        # Append Azimuth and Azimuth_rate into sky_coordinates set
        sky_coordinates.append(azimuth_coord)
        sky_coordinates.append(0.0)

        # Append Elevation and Elevation_rate into sky_coordinates set
        sky_coordinates.append(elevation_coord)
        sky_coordinates.append(0.0)

        # Add in sky_coordinates set in station_beam_pointings
        station_beam_pointings["sky_coordinates"] = sky_coordinates
        return station_beam_pointings

    def update_station_ids(self, argin, station_beam_pointings):
        station_ids = []
        for station in argin["stations"]:
            log_msg = "Station is: " + str(station)
            self.logger.info(log_msg)
            station_ids.append(station["station_id"])
        station_beam_pointings["station_id"] = station_ids
        # Remove target block from station_beam_pointings
        station_beam_pointings.pop("target", None)

        # Update station_beam_pointings into output Configure JSON
        argin["station_beam_pointings"][0] = station_beam_pointings
        argin["station_beams"] = argin["station_beam_pointings"]
        argin.pop("station_beam_pointings", None)
        return argin

    def configure_mccs_subarray(self, argin, mccs_subarray_client):
        input_mccs_subarray = json.dumps(argin)
        log_msg = "Output Configure JSON is: " + input_mccs_subarray
        self.logger.info(log_msg)
        mccs_subarray_client.send_command_async(const.CMD_CONFIGURE, input_mccs_subarray,
                                                self.configure_cmd_ended_cb)
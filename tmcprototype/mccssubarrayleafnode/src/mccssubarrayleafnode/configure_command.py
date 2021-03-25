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
from tmc.common.tango_server_helper import TangoServerHelper


from . import const

# PROTECTED REGION END #    //  MccsSubarrayLeafNode.additional_import


class Configure(BaseCommand):
    """
    A class for MccsSubarrayLeafNode's Configure() command.

    This command configures a scan. It accepts configuration information in JSON string format and
    invokes Configure command on MCCS Subarray.

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
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Configure() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Configure command on mccssubarrayleafnode.",
                "mccssubarrayleafnode.Configure()",
                tango.ErrSeverity.ERR,
            )
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
        this_server = TangoServerHelper.get_instance()
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            this_server.write_attr("activityMessage", log_msg)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            this_server.write_attr("activityMessage", log_msg)

    def do(self, argin):
        """
        Method to invoke Configure command on MCCS Subarray.

        :param argin: DevString.
                      The string in JSON format. The JSON contains following values:

        Example:
        {"mccs":{"stations":[{"station_id":1},{"station_id":2}],"subarray_beams":[{"subarray_id":1,"subarray_beam_id":1,
        "target":{"system":"HORIZON","name":"DriftScan","Az":180.0,"El":45.0},"update_rate":0.0,"channels":[[0,8,1,1],
        [8,8,2,1],[24,16,2,1]]}]}}

        Note: Enter the json string without spaces as a input.

        return:
            None

        raises:
            DevFailed if the command execution is not successful

            ValueError if input argument json string contains invalid value

            KeyError if input argument json string contains invalid key
        """
        device_data = self.target
        this_server = TangoServerHelper.get_instance()
        try:
            mccs_subarray_fqdn = ""
            property_value = this_server.read_property("MccsSubarrayFQDN")
            mccs_subarray_fqdn = mccs_subarray_fqdn.join(property_value)
            mccs_subarray_client = TangoClient(mccs_subarray_fqdn)
            # TODO: Mock obs_state issue to be resolved
            # assert (mccs_subarray_client.get_attribute("obsState") in (ObsState.IDLE, ObsState.READY))
            log_msg = (
                "Input JSON for MCCS Subarray Leaf Node Configure command is: " + argin
            )
            self.logger.debug(log_msg)

            configuration_string = json.loads(argin)
            cmd_data = self.create_cmd_data(configuration_string)

            # Invoke Configure command on MCCSSubarray.
            log_msg = "Output Configure JSON is: " + cmd_data
            self.logger.info(log_msg)
            mccs_subarray_client.send_command_async(
                const.CMD_CONFIGURE, cmd_data, self.configure_cmd_ended_cb
            )
            this_server.write_attr("activityMessage", const.STR_CONFIGURE_SUCCESS)

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
            log_msg = f"{const.ERR_INVALID_JSON_CONFIG}{value_error}"
            this_server.write_attr("activityMessage", log_msg)
            self.logger.exception(value_error)
            tango.Except.throw_exception(
                const.ERR_CONFIGURE_INVOKING_CMD,
                log_msg,
                "MccsSubarrayLeafNode.Configure",
                tango.ErrSeverity.ERR,
            )

        except KeyError as key_error:
            log_msg = f"{const.ERR_JSON_KEY_NOT_FOUND}{key_error}"
            this_server.write_attr("activityMessage", log_msg)
            self.logger.exception(key_error)
            tango.Except.throw_exception(
                const.ERR_CONFIGURE_INVOKING_CMD,
                log_msg,
                "MccsSubarrayLeafNode.Configure",
                tango.ErrSeverity.ERR,
            )

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_CONFIGURE_INVOKING_CMD}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.ERR_CONFIGURE_INVOKING_CMD,
                log_msg,
                "MccsSubarrayLeafNode.Configure",
                tango.ErrSeverity.ERR,
            )

    def create_cmd_data(self, configuration_string):
        station_beam_pointings = configuration_string["subarray_beams"][0]
        sky_coordinates = self.get_sky_coordinates(station_beam_pointings)

        # Add in sky_coordinates set in station_beam_pointings
        station_beam_pointings["sky_coordinates"] = sky_coordinates

        station_ids = self.get_station_ids(configuration_string)

        station_beam_pointings["station_id"] = station_ids
        # Remove target block from station_beam_pointings
        station_beam_pointings.pop("target", None)

        mccs_sa_configuration_string = self.update_configuration_json(
            station_beam_pointings, configuration_string
        )
        cmd_data = json.dumps(mccs_sa_configuration_string)
        return cmd_data

    def get_sky_coordinates(self, station_beam_pointings):

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

        return sky_coordinates

    def get_station_ids(self, configuration_string):
        station_ids = []
        for station in configuration_string["stations"]:
            log_msg = f"Station is: {station}" 
            self.logger.info(log_msg)
            station_ids.append(station["station_id"])
        return station_ids

    def update_configuration_json(self, station_beam_pointings, configuration_string):
        # Update station_beam_pointings into output Configure JSON
        configuration_string["subarray_beams"][0] = station_beam_pointings
        configuration_string["station_beams"] = configuration_string["subarray_beams"]
        configuration_string.pop("subarray_beams", None)
        return configuration_string

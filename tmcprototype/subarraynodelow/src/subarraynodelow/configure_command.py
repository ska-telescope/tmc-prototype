"""
ConfigureCommand class for SubarrayNodeLow.
"""

# Standard Python imports
import json

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from . import const
from subarraynodelow.device_data import DeviceData
from tmc.common.tango_client import TangoClient


class Configure(SKASubarray.ConfigureCommand):
    """
    A class for SubarrayNodeLow's Configure() command.

    Configures the resources assigned to the Mccs Subarray.

    """

    def do(self, argin):
        """
        Method to invoke Configure command.

        :param argin: DevString.

        JSON string example is:

         {"mccs":{"stations":[{"station_id":1},{"station_id":2}],"subarray_beams":[{"subarray_id":1,
         "subarray_beam_id":1,"target":{"system":"HORIZON","name":"DriftScan","Az":180.0,"El":45.0},
         "update_rate":0.0,"channels":[[0,8,1,1],[8,8,2,1],[24,16,2,1]]}]},"tmc":{"scanDuration":10.0}}

        :return: A tuple containing a return code and a string message indicating status.
         The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: JSONDecodeError if input argument json string contains invalid value
                 DevFailed if the command execution is not successful.
        """
        device_data = self.target
        device_data.is_scan_completed = False
        device_data.is_release_resources = False
        self.logger.info(const.STR_CONFIGURE_CMD_INVOKED_SA_LOW)
        log_msg = const.STR_CONFIGURE_IP_ARG + str(argin)
        self.logger.info(log_msg)
        # device.set_status(const.STR_CONFIGURE_CMD_INVOKED_SA_LOW)
        device_data.activity_message = const.STR_CONFIGURE_CMD_INVOKED_SA_LOW
        try:
            scan_configuration = json.loads(argin)
        except json.JSONDecodeError as jerror:
            log_message = const.ERR_INVALID_JSON + str(jerror)
            self.logger.error(log_message)
            device_data.activity_message = log_message
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_message,
            const.STR_CONFIGURE_EXEC, tango.ErrSeverity.ERR)
        tmc_configure = scan_configuration["tmc"]
        device_data.scan_duration = int(tmc_configure["scanDuration"])
        self._configure_mccs_subarray(scan_configuration)
        message = "Configure command invoked"
        self.logger.info(message)
        return (ResultCode.STARTED, message)
        
    def _configure_mccs_subarray(self, scan_configuration):
        scan_configuration = scan_configuration["mccs"]
        if not scan_configuration:
            raise KeyError("MCCS configuration must be given. Aborting MCCS configuration.")
        self._configure_leaf_node("Configure", json.dumps(scan_configuration))
      
    def _configure_leaf_node(self, cmd_name, cmd_data):
        device_data = DeviceData.get_instance()
        try:
            mccs_subarray_ln_client = TangoClient(device_data.mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(cmd_name, cmd_data)
            # device_proxy.command_inout(cmd_name, cmd_data)
            log_msg = "%s configured succesfully." % device_data.mccs_subarray_ln_fqdn
            self.logger.debug(log_msg)
        except DevFailed as df:
            log_message = df[0].desc
            device_data.activity_message = log_message
            log_msg = "Failed to configure %s. %s" % (device_data.mccs_subarray_ln_fqdn, df)
            self.logger.error(log_msg)
            raise
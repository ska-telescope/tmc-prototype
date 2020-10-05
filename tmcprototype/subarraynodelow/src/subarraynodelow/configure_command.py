"""
ConfigureCommand class for SubarrayNodeLow.
"""

import json
# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class ConfigureCommand(SKASubarray.ConfigureCommand):
    """
    A class for SubarrayNodeLow's Configure() command.
    """

    def do(self, argin):
        """
        Configures the resources assigned to the Mccs Subarray.
    
        :param argin: DevString.

        JSON string example is:

         {"mccs":{"stations":[{"station_id":1,},{"station_id":2,}],"station_beam_pointings":
         [{"station_beam_id":1,"target":{"system":"HORIZON","name":"DriftScan","Az":180.0,"El":45.0},
         "update_rate":0.0,"channels":[1,2,3,4,5,6,7,8]}]},"tmc":{"scanDuration":10.0}}

        :return: A tuple containing a return code and a string message indicating status.
         The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: JSONDecodeError if input argument json string contains invalid value
                 DevFailed if the command execution is not successful.
        """
        device = self.target
        device.is_scan_completed = False
        device.is_release_resources = False
        self.logger.info(const.STR_CONFIGURE_CMD_INVOKED_SA_LOW)
        log_msg = const.STR_CONFIGURE_IP_ARG + str(argin)
        self.logger.info(log_msg)
        device.set_status(const.STR_CONFIGURE_CMD_INVOKED_SA_LOW)
        device._read_activity_message = const.STR_CONFIGURE_CMD_INVOKED_SA_LOW
        try:
          scan_configuration = json.loads(argin)
        except json.JSONDecodeError as jerror:
          log_message = const.ERR_INVALID_JSON + str(jerror)
          self.logger.error(log_message)
          device._read_activity_message = log_message
          tango.Except.throw_exception(const.STR_CMD_FAILED, log_message,
          const.STR_CONFIGURE_EXEC, tango.ErrSeverity.ERR)
        tmc_configure = scan_configuration["tmc"]
        device.scan_duration = int(tmc_configure["scanDuration"])
        scan_configuration = self._configure_mccs_subarray(scan_configuration)

        try:
          device._mccs_subarray_ln_proxy.command_inout(const.CMD_CONFIGURE, scan_configuration)
          message = "Configure command invoked"
          self.logger.info(message)
          return (ResultCode.STARTED, message)
        except DevFailed as df:
          log_message = df[0].desc
          device._read_activity_message = log_message
          self.logger.error(log_msg)
          raise

    def _configure_mccs_subarray(self, scan_configuration):
      device = self.target
      scan_configuration = scan_configuration["mccs"]
      if not scan_configuration:
        raise KeyError("MCCS configuration must be given. Aborting MCCS configuration.")
      return json.dumps(scan_configuration)
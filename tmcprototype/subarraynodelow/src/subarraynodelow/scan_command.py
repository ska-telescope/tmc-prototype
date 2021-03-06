"""
ScanCommand class for SubarrayNodeLow
"""
# Standard Python imports
import json
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from tmc.common.tango_client import TangoClient
from . import const


class Scan(SKASubarray.ScanCommand):
    """
    A class for SubarrayNodeLow's Scan() command.
    """

    def do(self, argin):
        """
        This command accepts id as input. And it Schedule scan on subarray
        from where scan command is invoked on MCCS subarray Leaf Node for the
        provided interval of time. It checks whether the scan is already in progress. If yes it
        throws error showing duplication of command.

        :param argin: DevString. JSON string containing id.

        JSON string example as follows:

        {"mccs":{"id":1,"scan_time":0.0}}
        Note: Above JSON string can be used as an input argument while invoking this command from JIVE.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device_data = self.target
        device_data.is_scan_completed = False
        device_data.is_release_resources = False
        try:
            input_scan = json.loads(argin)
            mccs_input_scan = input_scan["mccs"]
            log_msg = const.STR_SCAN_IP_ARG + str(argin)
            self.logger.info(log_msg)
            device_data.activity_message = log_msg
            device_data.isScanRunning = True
            # Invoke scan command on MCCS Subarray Leaf Node with input argument as scan id
            mccs_subarray_ln_client = TangoClient(device_data.mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_SCAN, json.dumps(mccs_input_scan))
            self.logger.info(const.STR_MCCS_SCAN_INIT)
            device_data.activity_message = const.STR_MCCS_SCAN_INIT
            self.logger.info(const.STR_SA_SCANNING)
            device_data.activity_message = const.STR_SCAN_SUCCESS
            # Once Scan Duration is complete call EndScan Command
            self.logger.info("Starting Scan Thread")
            device_data.scan_timer_handler.start_scan_timer(device_data.scan_duration)
            self.logger.info("Scan thread started")
            return (ResultCode.STARTED, const.STR_SCAN_SUCCESS)

        except json.JSONDecodeError as json_error:
            log_message = const.ERR_INVALID_JSON + str(json_error)
            self.logger.error(log_message)
            device_data.activity_message = log_message
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_message,
            const.STR_SCAN_EXEC, tango.ErrSeverity.ERR)

        except KeyError as key_error:
            self.logger.error(const.ERR_JSON_KEY_NOT_FOUND)
            device_data._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            log_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self.logger.exception(key_error)
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_message,
                                         const.STR_SCAN_EXEC, tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = const.ERR_SCAN_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_SCAN_EXEC,
                                         log_msg,
                                         "SubarrayNode.ScanCommand",
                                         tango.ErrSeverity.ERR)
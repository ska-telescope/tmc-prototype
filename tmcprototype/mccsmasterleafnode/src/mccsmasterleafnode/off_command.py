# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #
# Third party imports
# Tango imports
import tango
from tango import DeviceProxy, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from ska.base.control_model import HealthState, SimulationMode, TestMode
from tmc.common.tango_client import TangoClient
from . import const, release
# PROTECTED REGION END #    //  MccsMasterLeafNode imports


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
        # If the array length is >, each array element _CMD_ISSUED
            return (ResultCode.OK, const.STR_OFF_CMD_ISSUED)

        except DevFailed as dev_failed:
            log_msg = const.ERR_OFF_RESOURCES + str(dev_failed)
            device._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_OFF_EXEC, log_msg,
                                            "MccsMasterLeafNode.Off",
                                            tango.ErrSeverity.ERR)
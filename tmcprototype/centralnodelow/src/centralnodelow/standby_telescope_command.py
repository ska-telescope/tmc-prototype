"""
StandByTelescope class for CentralNodelow.
"""
# Tango imports
import tango
from tango import DevState, DevFailed
# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
# from ska.base.control_model import HealthState
from . import const
from .device_data import DeviceData
from tmc.common.tango_client import TangoClient

class StandByTelescope(SKABaseDevice.OffCommand):
    """
    A class for Low CentralNode's StandByTelescope() command.
    """

    def check_allowed(self):

        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state
        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Command StandByTelescope is not allowed in current state.",
                                         "Failed to invoke StandByTelescope command on CentralNodeLow.",
                                         "CentralNodeLow.StandByTelescope()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self):
        """
        Sets the CentralNodeLow into OFF state. Invokes the respective command on lower level nodes and devices.

        param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)
        """
        device_data = self.target
        self.create_mccs_client(device_data.mccs_master_ln_fqdn)
        self.create_subarray_client(device_data.subarray_low)
        device_data.health_aggreegator.unsubscribe_event()
        log_msg = const.STR_STANDBY_CMD_ISSUED
        self.logger.info(log_msg)
        device_data._read_activity_message = log_msg
        return (ResultCode.OK, const.STR_STANDBY_CMD_ISSUED)


    def create_mccs_client(self, mccs_master_fqdn):
        """
        Create TangoClient for MccsMasterLeafNode node and call
        standby method.

        :return: None
        """
        mccs_mln_client = TangoClient(mccs_master_fqdn)
        self.invoke_stnadby(mccs_mln_client)

    def create_subarray_client(self, subarray_fqdn_list):
        """
        Create TangoClient for Subarray node and call
        standby method.

        :return: None
        """
        for subarray_fqdn in subarray_fqdn_list:
            subarray_client = TangoClient(subarray_fqdn)
            self.invoke_stnadby(subarray_client)

    def invoke_stnadby(self, tango_client):
        """
        Invoke command Off leaf nodes.

        :param tango_client: proxy of corresponding leaf node
        :return: None

        :raises: Devfailed exception if error occures while executing command on leaf nodes.
        """

        device_data = DeviceData.get_instance()
        try:
            tango_client.send_command(const.CMD_OFF)
            log_msg = 'Command {} invoked successfully on {}'.format( const.CMD_OFF, tango_client.get_device_fqdn)
            self.logger.debug(log_msg)
            device_data._read_activity_message = log_msg

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_OFF_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_OFF_CMD
            tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                         "CentralNode.StandByTelescopeCommand",
                                         tango.ErrSeverity.ERR)
        return (ResultCode.OK, device_data._read_activity_message)

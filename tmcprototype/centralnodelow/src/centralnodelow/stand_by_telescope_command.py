"""
StandByTelescope class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
import tango
from tango import DevState, DevFailed
# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from . import const
from centralnode.device_data import DeviceData
from tmc.common.tango_client import TangoClient
# PROTECTED REGION END #    //  CentralNode.additional_import

class StandByTelescope(SKABaseDevice.OffCommand):
    """
    A class for CentralNode's StandByTelescope() command.
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
                                         "Failed to invoke StandByTelescope command on CentralNode.",
                                         "CentralNode.StandByTelescope()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self):
        """
        Sets the CentralNode into OFF state. Invokes the respective command on lower level nodes adn devices.

        :param: None

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)
        """
        self.logger.info(type(self.target))
        device_data = DeviceData.get_instance()
        self.standby_subarray(device_data.tm_low_subarray)
        self.standby_mccs(device_data.mccs_master_ln_fqdn)
        device_data.health_aggregator.unsubscribe_event()
        log_msg = const.STR_STANDBY_CMD_ISSUED
        self.logger.info(log_msg)
        device_data._read_activity_message = log_msg

        # stop obs state aggregation
        device_data.obs_state_aggregator.stop_aggregation()
        return (ResultCode.OK,const.STR_STANDBY_CMD_ISSUED)

    def standby_mccs(self, mccs_fqdn):
        """
        Create TangoClient for MccsMasterLeaf node and call standby method.
        :return: None
        """
        mccs_mln_client = TangoClient(mccs_fqdn)
        self.standby_leaf_node(mccs_mln_client, const.CMD_OFF)
        self.standby_leaf_node(mccs_mln_client, const.CMD_STANDBY, [])


    def standby_subarray(self, subarray_fqdn_list):
        """
        Create TangoClient for Subarray node and call
        standby method.

        :return: None
        """
        for subarrayID in range(1, len(subarray_fqdn_list) + 1):
            subarray_client = TangoClient(subarrayID)
            self.standby_leaf_node(subarray_client, const.CMD_OFF)
            self.standby_leaf_node(subarray_client, const.CMD_STANDBY)


    def standby_leaf_node(self, tango_client, cmd_name, param=None):
        """
        Invoke command on leaf nodes.

        :param tango_client: proxy of corresponding leaf node
        :param cmd_name: command name
        :param param: Empty list from cspsmn

        :return: None

        :raises: Devfailed exception if error occures while executing command on leaf nodes.
        """
        device_data = DeviceData.get_instance()
        try:
            tango_client.send_command(cmd_name, param)
            log_msg = 'Command {} invoked successfully on {}'.format(cmd_name, tango_client.get_device_fqdn)
            self.logger.debug(log_msg)
            device_data._read_activity_message = log_msg
        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_STANDBY_CMD
            tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                         "CentralNode.StandByTelescopeCommand",
                                         tango.ErrSeverity.ERR)



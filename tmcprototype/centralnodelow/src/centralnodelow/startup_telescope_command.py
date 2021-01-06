"""
StartUpTelescope class for CentralNodelow.
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

class StartUpTelescope(SKABaseDevice.OnCommand):
    """
    A class for Low CentralNode's StartupCommand() command.
    """

    def check_allowed(self):

        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Command StartUpTelescope is not allowed in current state.",
                                         "Failed to invoke StartUpTelescope command on CentralNodeLow.",
                                         "CentralNodeLow.StartUpTelescope()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self):
        """
        Setting the startup state to TRUE enables the telescope to accept subarray commands as per the subarray
        model. Set the CentralNode into ON state.

        :param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)
        """
        device_data = self.target
        self.startup_mccs(device_data.mccs_master_fqdn)
        self.startup_subarray(device_data.subarray_low)
        log_msg = const.STR_ON_CMD_ISSUED
        self.logger.info(log_msg)
        device_data._read_activity_message = log_msg
        return (ResultCode.OK, const.STR_ON_CMD_ISSUED)

    def startup_subarray(self, subarray_fqdn):
        """
        Create TangoClient for Subarray node and call
        startup method.

        :return: None
        """
        for subarray_id in range(1, len(subarray_fqdn) + 1):
            subarray_client = TangoClient(subarray_id)
            self.startup_leaf_node(subarray_client)


    def startup_mccs(self, mccs_fqdn):
        """
        Create TangoClient for MccsMasterLeafNode node and call
        startup method.

        :return: None
        """
        mccs_proxy = TangoClient(mccs_fqdn)
        self.startup_leaf_node(mccs_proxy)


    def startup_leaf_node(self, tango_client):
        """
        Invoke On command on leaf nodes.

        :param tango_client: Proxy of corresponding node.

        :return: None

        :raises: Devfailed exception if error occures while  executing On command on leaf node.
        """
        device_data = DeviceData.get_instance()
        try:
            tango_client.send_command(const.CMD_ON)
            log_msg = 'ON command invoked successfully on {}'.format(tango_client.get_device_fqdn)
            self.logger.debug(log_msg)
            device_data._read_activity_message = log_msg

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_ON_CMD
            tango.Except.re_throw_exception(dev_failed, const.STR_ON_EXEC, log_msg,
                                            "CentralNodeLow.StartUpTelescopeCommand",
                                            tango.ErrSeverity.ERR)
        return (ResultCode.OK, device_data._read_activity_message)

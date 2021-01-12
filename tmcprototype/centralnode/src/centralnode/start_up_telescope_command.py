"""
StartUpTelescope class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
import tango
import time
from tango import DevState, DevFailed
# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from . import const
from centralnode.device_data import DeviceData
from centralnode.health_state_aggreegator import HealthStateAggreegator
from tmc.common.tango_client import TangoClient
# PROTECTED REGION END #    //  CentralNode.additional_import

class StartUpTelescope(SKABaseDevice.OnCommand):
    """
    A class for CentralNode's StartupCommand() command.
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
                                         "Failed to invoke StartUpTelescope command on CentralNode.",
                                         "CentralNode.StartUpTelescope()",
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
        device_data = DeviceData.get_instance()
        self.logger.info(type(self.target))
        device_data.health_aggreegator = HealthStateAggreegator(self.logger)
        device_data.health_aggreegator.subscribe_event()
        self.startup_sdp(device_data.sdp_master_ln_fqdn)
        self.startup_dish(device_data._dish_leaf_node_devices)
        self.startup_csp(device_data.csp_master_ln_fqdn)
        self.startup_subarray(device_data.tm_mid_subarray)
        
        log_msg = const.STR_ON_CMD_ISSUED
        self.logger.info(log_msg)
        device_data._read_activity_message = log_msg
        
        # start obs state aggregation
        device_data.obs_state_aggregator.start_aggregation()

        # TODO: start healthState aggregation

        return (ResultCode.OK,const.STR_ON_CMD_ISSUED)


    def startup_csp(self, csp_fqdn):
        """
        Create TangoClient for CspMasterLeaf node and call
        startup method.

        :return: None
        """
        csp_mln_client = TangoClient(csp_fqdn)
        self.startup_leaf_node(csp_mln_client)

    def startup_sdp(self, sdp_fqdn):
        """
        Create TangoClient for SdpMasterLeaf node and call
        startup method.

        :return: None
        """
        sdp_mln_client = TangoClient(sdp_fqdn)
        self.startup_leaf_node(sdp_mln_client)

    def startup_dish(self, dish_fqdn):
        """
        Create TangoClient for DishLeaf node and call
        startup method.

        :return: None
        """
        for name in range(0, len(dish_fqdn)):
            dish_ln_client = TangoClient(dish_fqdn[name])
            self.startup_dish_leaf_node(dish_ln_client)

    def startup_subarray(self, subarray_fqdn_list):
        """
        Create TangoClient for Subarray node and call
        startup method.

        :return: None
        """
        for subarray_fqdn in subarray_fqdn_list:
            subarray_client = TangoClient(subarray_fqdn)
            self.startup_leaf_node(subarray_client)

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
            tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                         "CentralNode.StartUpTelescopeCommand",
                                         tango.ErrSeverity.ERR)

    def startup_dish_leaf_node(self, tango_client):
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

            tango_client.send_command(const.CMD_SET_STANDBYFP_MODE)
            log_msg = 'SetStandbyFPMode command invoked successfully on {}'.format(tango_client.get_device_fqdn)
            self.logger.debug(log_msg)
            device_data._read_activity_message = log_msg
            time.sleep(0.5)
            tango_client.send_command(const.CMD_SET_OPERATE_MODE)
            log_msg = 'SetOperateMode command invoked successfully on {}'.format(tango_client.get_device_fqdn)
            self.logger.debug(log_msg)
            device_data._read_activity_message = log_msg

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_ON_CMD
            tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                         "CentralNode.StartUpTelescopeCommand",
                                         tango.ErrSeverity.ERR)
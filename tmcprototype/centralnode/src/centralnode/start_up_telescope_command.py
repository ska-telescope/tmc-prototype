"""
StartUpTelescope class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState
from . import const
from centralnode.device_data import DeviceData
from centralnode.HealthStateCb import HealthStateCb
from centralnode.tango_client import TangoClient
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
        device_data = self.target
        self.logger.info(type(self.target))
        device_data.health_aggreegator.csp_health_subscribe_event()
        device_data.health_aggreegator.sdp_health_subscribe_event()
        device_data.health_aggreegator.subarray_health_subscribe_event()
        log_msg = const.STR_ON_CMD_ISSUED
        self.logger.info(log_msg)
        device_data._read_activity_message = log_msg
        self.startup_dish()
        self.startup_csp()
        self.startup_sdp()
        self.startup_subarray()
        return (ResultCode.OK, device._read_activity_message)


    def startup_csp(self):
        """
        Create TangoClient for CspMasterLeaf node and call
        startup method.

        :return: None
        """
        csp_mln_client = TangoClient(device_data.csp_master_ln_fqdn)
        self.startup_leaf_node(csp_mln_client)

    def startup_sdp(self):
        """
        Create TangoClient for SdpMasterLeaf node and call
        startup method.

        :return: None
        """
        sdp_mln_client = TangoClient(device_data.sdp_master_ln_fqdn)
        self.startup_leaf_node(sdp_mln_client)

    def startup_dish(self):
        """
        Create TangoClient for DishLeaf node and call
        startup method.

        :return: None
        """
        for name in range(0, len(device_data._dish_leaf_node_devices)):
            dish_ln_client = TangoClient(device_data._dish_leaf_node_devices[name])
            self.startup_leaf_node(dish_ln_client)

    def startup_subarray(self):
        """
        Create TangoClient for Subarray node and call
        startup method.

        :return: None
        """
        for subarrayID in range(1, len(device_data.tm_mid_subarray) + 1):
            subarray_client = TangoClient(subarrayID)
            self.startup_leaf_node(subarray_client)

    def startup_leaf_node(self, tango_client):
        """
        Invoke On command on leaf nodes.

        :param tango_client: Proxy of corresponding node.

        :return: None

        :raises: Devfailed exception if error occures while  executing On command on leaf node.
        """
        try:
            tango_client.send_command(const.CMD_ON)
            log_msg = 'ON command invoked successfully on {}'.format(tango_client.get_device_fqdn)
            self.logger.debug(log_msg)
            device_data._read_activity_message = log_msg
        except:
            log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_ON_CMD
            tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                         "CentralNode.StartUpTelescopeCommand",
                                         tango.ErrSeverity.ERR)
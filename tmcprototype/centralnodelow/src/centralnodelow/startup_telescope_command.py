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
from .health_state_aggreegator import HealthStateAggreegator
from tmc.common.tango_client import TangoClient

class StartUpTelescope(SKABaseDevice.OnCommand):
    """
    A class for Low CentralNode's StartupCommand() command.
    """

    def command_result_cb(self, event):
        """
        Attribute callback for commandResult.
        """
        device_data = DeviceData.get_instance()
        log_msg = 'MccsController.commandResult change event is : ' + str(event)
        device_data.cmd_res_evt_val = event.attr_value.value
        self.logger.debug(log_msg)
        # if not event.err:
        #     log_msg="commandResult attribute value is :" + str(device_data.cmd_res_evt_val)
        #     self.logger.info(log_msg)
        # else:
        #     self.loger.error("Error on subscribing commandResult attribute")

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
        # Subscribe to commandResult attribute of MccsController
        mccs_controller_obj = TangoClient(device_data.mccs_controller_fqdn)
        device_data.cmd_res_evt_id = mccs_controller_obj.subscribe_attribute("commandResult",
                                                                             self.command_result_cb)
        device_data.health_aggreegator = HealthStateAggreegator(self.logger)
        device_data.health_aggreegator.subscribe_event()
        try:
            # Check if Mccs Off command is completed
            assert device_data.cmd_res_evt_val == None or device_data.cmd_res_evt_val == 0
            self.create_mccs_client(device_data.mccs_master_ln_fqdn)
            self.create_subarray_client(device_data.subarray_low)
            log_msg = const.STR_ON_CMD_ISSUED
            self.logger.info(log_msg)
            device_data._read_activity_message = log_msg
            return (ResultCode.OK, const.STR_ON_CMD_ISSUED)
        except AssertionError as assertion_err:
            log_msg = const.ERR_STANDBY_CMD_UNCOMPLETE
            self.logger.exception(log_msg)
            device_data._read_activity_message = const.ERR_STANDBY_CMD_UNCOMPLETE
            tango.Except.re_throw_exception(assertion_err, const.ERR_STANDBY_CMD_UNCOMPLETE,
                                            log_msg, "CentralNodeLow.StartUpTelescopeCommand",
                                            tango.ErrSeverity.ERR)


    def create_subarray_client(self, subarray_fqdn_list):
        """
        Create TangoClient for Subarray node and call
        startup method.

        :return: None
        """
        for subarray_fqdn in subarray_fqdn_list:
            subarray_client = TangoClient(subarray_fqdn)
            self.invoke_startup(subarray_client)


    def create_mccs_client(self, mccs_master_fqdn):
        """
        Create TangoClient for MccsMasterLeafNode node and call
        startup method.

        :return: None
        """
        mccs_mln_client = TangoClient(mccs_master_fqdn)
        self.invoke_startup(mccs_mln_client)


    def invoke_startup(self, tango_client):
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

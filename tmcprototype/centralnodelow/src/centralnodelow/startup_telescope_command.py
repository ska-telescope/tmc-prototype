"""
StartUpTelescope class for CentralNodelow.
"""
# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from .device_data import DeviceData
from .health_state_aggreegator import HealthStateAggreegator
from .command_result_fetcher import CommandResultFetcher

class StartUpTelescope(SKABaseDevice.OnCommand):
    """
    A class for Low CentralNode's StartupCommand() command.

    StartUpTelescope command on Central Node Low enables the telescope to perform further operations
    and observations. It Invokes On command on lower level devices.

    """

    def check_allowed(self):

        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Command StartUpTelescope is not allowed in current state {self.state_model.op_state}.",
                "Failed to invoke StartUpTelescope command on CentralNodeLow.",
                "CentralNodeLow.StartUpTelescope()",
                tango.ErrSeverity.ERR,
            )
        return True

    def do(self):
        """
        Method to invoke ON command On lower level devices.

        param argin:
            None.

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            AssertionError if f Mccs Off command is not completed.

        """
        device_data = self.target
        attributes_to_subscribe_to = (
            "commandResult",
        )
        # Subscribe to commandResult attribute of MccsController
        cmd_res_subscriber_unsubscriber_obj = CommandResultFetcher()
        cmd_res_subscriber_unsubscriber_obj._subscribe_cmd_res_attribute_events(
            attributes_to_subscribe_to)
        device_data.health_aggreegator = HealthStateAggreegator(self.logger)
        device_data.health_aggreegator.subscribe_event()
        try:
            self.this_server = TangoServerHelper.get_instance()
            # Check if Mccs Off command is completed
            assert device_data.cmd_res_evt_val == None or device_data.cmd_res_evt_val == 0, const.ERR_STANDBY_CMD_UNCOMPLETE
            mccs_master_ln_fqdn = self.this_server.read_property("MCCSMasterLeafNodeFQDN")
            self.create_mccs_client(mccs_master_ln_fqdn)
            subarray_low = self.this_server.read_property("TMLowSubarrayNodes")
            self.create_subarray_client(subarray_low)
            log_msg = const.STR_ON_CMD_ISSUED
            self.logger.info(log_msg)
            self.this_server.write_attr("activityMessage", log_msg)
            return (ResultCode.OK, const.STR_ON_CMD_ISSUED)
        except AssertionError as assertion_err:
            log_msg = const.ERR_STANDBY_CMD_UNCOMPLETE
            self.logger.exception(log_msg)
            self.this_server.write_attr("activityMessage", const.ERR_STANDBY_CMD_UNCOMPLETE)
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
            log_msg = "ON command invoked successfully on {}".format(
                tango_client.get_device_fqdn
            )
            self.logger.debug(log_msg)
            self.this_server.write_attr("activityMessage", log_msg)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_EXE_ON_CMD}{dev_failed}"
            self.logger.exception(dev_failed)
            self.this_server.write_attr("activityMessage", const.ERR_EXE_ON_CMD)
            tango.Except.re_throw_exception(dev_failed, const.STR_ON_EXEC, log_msg,
                                            "CentralNodeLow.StartUpTelescopeCommand",
                                            tango.ErrSeverity.ERR)
        return (ResultCode.OK, self.this_server.read_attr("activityMessage"))

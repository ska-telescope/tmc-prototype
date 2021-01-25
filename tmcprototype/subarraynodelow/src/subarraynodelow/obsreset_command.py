"""
ObsReset Command for SubarrayNode.
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from tmc.common.tango_client import TangoClient
from subarraynodelow.device_data import DeviceData
from tmc.common.tango_server_helper import TangoServerHelper


class ObsReset(SKASubarray.ObsResetCommand):
    """
    A class for Low SubarrayNode's ObsReset() command.
    """

    def do(self):
        """
        This command invokes ObsReset command on MccsSubarrayLeafNode.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs while invoking command on MccsSubarrayLeafNode.
        """
        device = self.target
        device_data = DeviceData.get_instance()
        device_data.is_abort_command = False
        try:
            self.logger.info("ObsReset command invoked on SubarrayNodeLow.")
            #self.obsreset_mccs_subarray_leaf_node()
            mccs_subarray_ln_client = TangoClient(device.mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_OBSRESET)
            device_data._read_activity_message = const.STR_OBSRESET_SUCCESS
            self.logger.info(const.STR_OBSRESET_SUCCESS)

            tango_server_helper_obj = TangoServerHelper.get_instance()
            tango_server_helper_obj.set_status(const.STR_OBSRESET_SUCCESS)
            device_data.is_obsreset_command = True
            return (ResultCode.STARTED, const.STR_OBSRESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_OBSRESET_INVOKING_CMD + str(dev_failed)
            self.logger.exception(log_msg)
            tango.Except.throw_exception(const.STR_OBSRESET_EXEC,
                                         log_msg,
                                         "SKASubarrayLow.ObsReset",
                                         tango.ErrSeverity.ERR)

    # def obsreset_mccs_subarray_leaf_node(self):
    #     """
    #     set up MccsSubarray devices
    #     """
    #     #Invoke ObsReset command on Mccs Subarray Leaf Node.
    #     device = self.target
    #     mccs_subarray_ln_client = TangoClient(device.mccs_subarray_ln_fqdn)
    #     mccs_subarray_ln_client.send_command(const.CMD_OBSRESET)
    #     self.logger.info(const.STR_CMD_OBSRESET_INV_MCCSSLN)
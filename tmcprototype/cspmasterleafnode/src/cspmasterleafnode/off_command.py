from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from . import const


class Off(SKABaseDevice.OffCommand):
    """
    A class for CspMasterLeafNode's Off() command.
    """

    def do(self):
        """
        Invokes Off command on the CSP Element.

        :param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        :rtype: (ResultCode, str)

        """
        device_data = self.target
        # pass argin to csp master.
        # If the array length is 0, the command applies to the whole CSP Element.
        # If the array length is >, each array element specifies the FQDN of the CSP SubElement to switch OFF.
        self.logger.debug(const.STR_OFF_CMD_ISSUED)
        device_data._read_activity_message = const.STR_OFF_CMD_ISSUED
        device_data.cbf_health_updator.stop()
        device_data.pss_health_updator.stop()
        device_data.pst_health_updator.stop()

        return (ResultCode.OK, const.STR_OFF_CMD_ISSUED)

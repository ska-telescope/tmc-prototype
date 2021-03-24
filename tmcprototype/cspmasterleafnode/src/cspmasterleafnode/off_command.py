from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class Off(SKABaseDevice.OffCommand):
    """
    A class for CspMasterLeafNode's Off() command. Off command is inherited from SKABaseDevice.

    It Sets the State to Off.
    """

    def do(self):
        """
        Method to invoke Off command on CSP Element.

        param argin:
            None.

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        """
        device_data = self.target
        self.logger.debug(const.STR_OFF_CMD_ISSUED)
        this_device = TangoServerHelper.get_instance()
        this_device.write_attr("activityMessage", const.STR_OFF_CMD_ISSUED)
        device_data.cbf_health_updator.stop()
        device_data.pss_health_updator.stop()
        device_data.pst_health_updator.stop()

        return (ResultCode.OK, const.STR_OFF_CMD_ISSUED)

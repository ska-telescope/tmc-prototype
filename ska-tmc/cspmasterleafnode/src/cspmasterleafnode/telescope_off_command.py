# Additional import
from ska.base.commands import ResultCode
from ska.base.commands import BaseCommand
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class TelescopeOff(BaseCommand):
    """
    A class for CspMasterLeafNode's TelescopeOff() command. TelescopeOff command is inherited from BaseCommand.

    It Sets the State to Off.
    """

    def do(self):
        """
        Method to invoke Off command on CSP Element.

        param argin:
            None.

        """
        device_data = self.target
        self.logger.debug(const.STR_OFF_CMD_ISSUED)
        this_device = TangoServerHelper.get_instance()
        this_device.write_attr("activityMessage", const.STR_OFF_CMD_ISSUED, False)
        device_data.cbf_health_updator.stop()
        device_data.pss_health_updator.stop()
        device_data.pst_health_updator.stop()
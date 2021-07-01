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
        super().do()
        self.logger.debug(const.STR_OFF_CMD_ISSUED)
        return (ResultCode.OK, const.STR_OFF_CMD_ISSUED)

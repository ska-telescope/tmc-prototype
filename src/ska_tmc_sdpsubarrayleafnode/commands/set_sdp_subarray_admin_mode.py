"""
SetAdminMode command class for SDPSubarrayLeafNode.
"""

# pylint: disable=line-too-long
from typing import Tuple

from ska_control_model import AdminMode
from ska_tango_base.commands import ArgumentValidator, FastCommand, ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand


# pylint: disable = abstract-method
class SetAdminMode(SdpSLNCommand, FastCommand):
    """
    A class for SDP SubarrayLeafNode's SetAdminMode() command.

    SetAdminMode command on SDP Subarray LeafNode enables to set
    the adminMode of the SDP subarray device
    """

    def __init__(self, logger, component_manager):
        """Initialization.

        Args:
            logger (logging.Logger): Used for logging.
            component_manager (SDPSLNcomponentManager): Instance of
            SDPSLNComponentManager.
        """
        super().__init__(logger)
        self.component_manager = component_manager
        self._validator = ArgumentValidator()
        self._name = "SetAdminMode"

    # pylint: disable=signature-differs
    def do(self, argin: AdminMode) -> Tuple[ResultCode, str]:
        """
        A method to set the adminMode of the SDP Subarray device

        :param argin: An adminMode enum value to be set for
            SDP subarray device

        """
        if self.component_manager.is_admin_mode_enabled:
            return_code, message = self.init_adapter()
            if return_code == ResultCode.FAILED:
                return return_code, message
            try:
                self.logger.info(
                    "Invoking SetAdminMode command on %s",
                    self.sdp_subarray_adapter.dev_name,
                )
                self.sdp_subarray_adapter.adminMode = argin
            except Exception as e:
                self.logger.info(
                    "Failed to set the adminMode of the SDP Subarray."
                    + " Error occurred is : %s",
                    e,
                )
                return (ResultCode.FAILED, "Command Failed")
            return (ResultCode.OK, "Command Completed")

        self.logger.info(
            "AdminMode functionality is disabled, "
            + "Device will function normally"
        )
        return ResultCode.NOT_ALLOWED, (
            "AdminMode functionality is disabled, "
            + "Device will function normally"
        )

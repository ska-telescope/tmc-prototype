"""
SetAdminMode command class for SDPMasterLeafNode.
"""
from typing import Tuple

from ska_control_model import AdminMode
from ska_tango_base.commands import ArgumentValidator, FastCommand, ResultCode

from ska_tmc_sdpmasterleafnode.commands.sdp_mln_command import SdpMLNCommand


# pylint: disable = abstract-method
class SetAdminMode(SdpMLNCommand, FastCommand):
    """
    A class for SdpMasterLeafNode's SetAdminMode() command.

    SetAdminMode command on SdpMasterLeafNode enables to set the adminMode of
    the SDP controller device
    """

    def __init__(self, logger, component_manager):
        """Initialization.

        Args:
            logger (logging.Logger): Used for logging.
            component_manager (SDPMLNcomponentManager): Instance of
            SDPMLNComponentManager.
        """
        super().__init__(logger)
        self.component_manager = component_manager
        self._validator = ArgumentValidator()
        self._name = "SetAdminMode"

    # pylint: disable=signature-differs
    def do(self, argin: AdminMode) -> Tuple[ResultCode, str]:
        """
        A method to set the adminMode of the SDP controller device
        :param argin: adminMode enum value to be set for SDP controller device
        """
        if self.component_manager.is_admin_mode_enabled:
            return_code, message = self.init_adapter()
            if return_code == ResultCode.FAILED:
                return return_code, message
            try:
                self.sdp_master_adapter.adminMode = argin
                self.logger.info(
                    "Invoking SetAdminMode command on %s",
                    self.sdp_master_adapter.dev_name,
                )
            except Exception as e:
                self.logger.exception(
                    "Failed to invoke SetAdminMode Command "
                    + "on device: %s."
                    + " with exception: %s",
                    self.sdp_master_adapter.dev_name,
                    e,
                )
                return ResultCode.FAILED, "Command Failed"
            return ResultCode.OK, "Command Completed"
        self.logger.info(
            "AdminMode functionality is disabled, "
            + "Device will function with no effect of adminMode"
        )

        return ResultCode.NOT_ALLOWED, (
            "AdminMode functionality is disabled, "
            + "Device will function normally"
        )

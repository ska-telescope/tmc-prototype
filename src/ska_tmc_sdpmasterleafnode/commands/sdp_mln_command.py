"""SDP Master Leaf Node Base Command Class for SDP Master Leaf Node"""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any, Optional, Tuple

from ska_ser_logging import configure_logging
from ska_tango_base.commands import ResultCode
from ska_tmc_common import DeviceInfo
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.tmc_command import TmcLeafNodeCommand
from tango import ConnectionFailed, DevFailed

configure_logging()
LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..manager.component_manager import SdpMLNComponentManager


class SdpMLNCommand(TmcLeafNodeCommand):
    """Abstract command class for all SdpMasterLeafNode"""

    def __init__(
        self,
        component_manager: SdpMLNComponentManager,
        logger: logging.Logger = LOGGER,
    ):
        super().__init__(component_manager, logger)
        self.sdp_master_adapter = None

    def check_unresponsive(self):
        """Checks whether the device is unresponsive"""
        dev_info: DeviceInfo = self.component_manager.get_device()
        if dev_info is None or dev_info.unresponsive:
            raise DeviceUnresponsive(
                """Command invocation failed as the SDP subarray device is not
                available The command has NOT been executed.
                This device will continue with normal operation."""
            )

    def init_adapter_low(self):
        self.init_adapter()

    def init_adapter_mid(self):
        self.init_adapter()

    def init_adapter(self) -> Tuple[ResultCode, str]:
        dev_name: str = self.component_manager.sdp_master_device_name
        timeout: int = self.component_manager.timeout
        elapsed_time = 0
        start_time = time.time()
        while self.sdp_master_adapter is None and elapsed_time < timeout:
            try:
                self.sdp_master_adapter = (
                    self.adapter_factory.get_or_create_adapter(
                        dev_name, AdapterType.BASE
                    )
                )
            except ConnectionFailed as connection_failed:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = (
                        f"Error in creating adapter for "
                        f"{dev_name}: {connection_failed}"
                    )
                    return ResultCode.FAILED, message
            except DevFailed as dev_failed:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = (
                        f"Error in creating adapter for "
                        f"{dev_name}: {dev_failed}"
                    )
                    return ResultCode.FAILED, message
            except (AttributeError, ValueError, TypeError) as exception:
                message = (
                    f"Error in creating adapter for "
                    f"{dev_name}: {exception}"
                )
                return ResultCode.FAILED, message

        return (ResultCode.OK, "")

    def do_mid(self, argin: Optional[Any] = None):
        """Abstract Method from TmcLeafNodeCommand is
            defined here but not utilized by this Class.
        Args:
            argin (_type_, optional): Accepts argument if required.
            Defaults to None.
        """

    def do_low(self, argin: Optional[Any] = None):
        """Abstract Method from TmcLeafNodeCommand is
            defined here but not utilized by this Class.
        Args:
            argin (_type_, optional): Accepts argument if required.
            Defaults to None.
        """

    def do(self, argin: Optional[Any] = None):
        """Abstract Method from TmcLeafNodeCommand is
            defined here but not utilized by this Class.
        Args:
            argin (_type_, optional): Accepts argument if required.
            Defaults to None.
        """

    def update_task_status(self, **kwargs):
        """Abstract Method from TmcLeafNodeCommand is
        defined here but not utilized by this Class."""

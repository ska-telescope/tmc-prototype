"""Abstract Command module for SDP Master Leaf Node"""
import time

from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.tmc_command import TmcLeafNodeCommand
from tango import ConnectionFailed, DevFailed


class SdpMLNCommand(TmcLeafNodeCommand):
    """Abstract command class for all SdpMasterLeafNode"""

    def __init__(
        self,
        component_manager,
        logger=None,
    ):
        super().__init__(component_manager, logger)
        self.sdp_master_adapter = None

    def check_unresponsive(self):
        """Checks whether the device is unresponsive"""
        dev_info = self.component_manager.get_device()
        if dev_info is None or dev_info.unresponsive:
            raise DeviceUnresponsive(
                """Command invocation failed as the SDP subarray device is not
                available The command has NOT been executed.
                This device will continue with normal operation."""
            )

    def init_adapter(self) -> tuple:
        dev_name = self.component_manager.sdp_master_device_name
        timeout = self.component_manager.timeout
        elapsed_time = 0
        start_time = time.time()
        while self.sdp_master_adapter is None and elapsed_time < timeout:
            try:
                self.sdp_master_adapter = (
                    self.adapter_factory.get_or_create_adapter(
                        dev_name, AdapterType.SDPSUBARRAY
                    )
                )
            except ConnectionFailed as cf:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = (
                        f"Error in creating adapter for " f"{dev_name}: {cf}"
                    )
                    return ResultCode.FAILED, message
            except DevFailed as df:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = (
                        f"Error in creating adapter for " f"{dev_name}: {df}"
                    )
                    return ResultCode.FAILED, message
            except (AttributeError, ValueError, TypeError) as e:
                message = f"Error in creating adapter for " f"{dev_name}: {e}"
                return ResultCode.FAILED, message

        return (ResultCode.OK, "")

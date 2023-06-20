"""Abstract Command module for SDP Master Leaf Node"""
import time

from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory, AdapterType
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.tmc_command import TmcLeafNodeCommand
from tango import ConnectionFailed, DevFailed


class SdpMLNCommand(TmcLeafNodeCommand):
    """Abstract command class for all SdpMasterLeafNode"""

    def __init__(
        self,
        component_manager,
        op_state_model,
        adapter_factory=None,
        logger=None,
    ):
        super().__init__(component_manager, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory or AdapterFactory()

    def check_unresponsive(self):
        """Checks whether the device is unresponsive"""
        devInfo = self.component_manager.get_device()
        if devInfo is None or devInfo.unresponsive:
            raise DeviceUnresponsive(
                """The invocation of the command on this device is not allowed.
                Reason: SDP subarray device is not available.
                The command has NOT been executed.
                This device will continue with normal operation."""
            )

    # pylint: disable=attribute-defined-outside-init
    def init_adapter(self):
        self.sdp_master_adapter = None
        dev_name = self.component_manager.sdp_master_dev_name
        timeout = self.component_manager.timeout
        elapsed_time = 0
        start_time = time.time()
        while self.sdp_master_adapter is None and elapsed_time < timeout:
            try:
                self.sdp_master_adapter = (
                    self._adapter_factory.get_or_create_adapter(
                        dev_name, AdapterType.BASE
                    )
                )
            except ConnectionFailed as cf:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = (
                        f"Error in creating adapter for "
                        f"{self.component_manager.sdp_master_dev_name}: {cf}"
                    )
                    return ResultCode.FAILED, message
            except DevFailed as df:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = (
                        f"Error in creating adapter for "
                        f"{self.component_manager.sdp_master_dev_name}: {df}"
                    )
                    return ResultCode.FAILED, message
            except (AttributeError, ValueError, TypeError) as e:
                message = (
                    f"Error in creating adapter for "
                    f"{self.component_manager.sdp_master_dev_name}: {e}"
                )
                return ResultCode.FAILED, message

        return ResultCode.OK, ""

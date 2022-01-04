from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractTelescopeOnOffCommand,
)
from ska_tmc_sdpsubarrayleafnode.manager.adapters import AdapterFactory


class TelescopeOff(AbstractTelescopeOnOffCommand):
    """
    A class for SdpsubarrayleafNode's TelescopeOff() command.

    TelescopeOff command on SdpsubarrayleafNode enables the telescope to perform further operations
    and observations. It Invokes Off command on Sdp Subarray device.

    """

    def __init__(
        self,
        target,
        pop_state_model,
        adapter_factory=AdapterFactory(),
        timeout_sdp=3000,
        step_sleep=0.1,
        *args,
        logger=None,
        **kwargs,
    ):
        super().__init__(
            target, pop_state_model, adapter_factory, args, logger, kwargs
        )
        self._timeout_sdp = timeout_sdp
        self._step_sleep = step_sleep

    def do_mid(self, argin):
        """
        Method to invoke Telescope Off command on Sdp Subarray.

        """
        ret_code, message = self.init_adapters()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            self.sdp_subarray_adapter.Off()
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                f"Error in calling Telescope Off Sdp Subarray Device {self.sdp_subarray_adapter.dev_name}: {e}",
            )
        return (ResultCode.OK, "")

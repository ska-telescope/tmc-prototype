from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractTelescopeOnOff,
)

# from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid


class TelescopeOff(AbstractTelescopeOnOff):
    """
    A class for SdpsubarrayleafNode's TelescopeOff() command.

    TelescopeOff command on SdpsubarrayleafNode enables the telescope to perform further operations
    and observations. It Invokes Off command on Sdp Subarray device.

    """

    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, op_state_model, adapter_factory, logger)

    # def do(self, argin=None):
    #     component_manager = self.target
    #     if isinstance(component_manager.input_parameter, InputParameterMid):
    #         result = self.do_mid(argin)
    #     return result

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

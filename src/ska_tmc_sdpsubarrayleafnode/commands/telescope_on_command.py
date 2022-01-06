from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractTelescopeOnOffCommand,
)
from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid


class TelescopeOn(AbstractTelescopeOnOffCommand):
    """
    A class for SdpsubarrayleafNode's TelescopeOn() command.

    TelescopeOn command on SdpsubarrayleafNode enables the telescope to perform further operations
    and observations. It Invokes On command on Sdp Subarray device.

    """

    def __init__(
        self,
        target,
        pop_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(
            target,
            pop_state_model,
            adapter_factory,
            logger,
        )

    def do(self, argin=None):
        component_manager = self.target
        if isinstance(component_manager.input_parameter, InputParameterMid):
            result = self.do_mid(argin)
        return result

    def do_mid(self, argin=None):
        """
        Method to invoke Telescope On command on Sdp Subarray.

        """
        ret_code, message = self.init_adapters()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            self.sdp_subarray_adapter.On()
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                f"Error in calling Telescope On Sdp Subarray Device {self.sdp_subarray_adapter.dev_name}: {e}",
            )
        return (ResultCode.OK, "")

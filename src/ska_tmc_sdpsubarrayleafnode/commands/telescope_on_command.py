from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractTelescopeOnOffCommand,
)
from ska_tmc_sdpsubarrayleafnode.manager.adapters import AdapterFactory


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

    def do_mid(self, argin=None):
        """
        Method to invoke Telescope On command on Lower level devices.

        param argin:
            None.

        """
        # component_manager = self.target

        ret_code, message = self.init_adapters()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        # send commands to sub-devices
        # import debugpy; debugpy.debug_this_thread()

        for adapter in self.tm_subarray_adapters:
            try:
                adapter.On()  # WIP: needs an async way
            except Exception as e:
                return self.generate_command_result(
                    ResultCode.FAILED,
                    f"Error in calling Telescope On in TM Subarray {adapter.dev_name}: {e}",
                )

        return (ResultCode.OK, "")  # do we need return code here?

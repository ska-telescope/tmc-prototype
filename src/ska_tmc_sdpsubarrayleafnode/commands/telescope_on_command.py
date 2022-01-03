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

    # def telescopeon_cmd_ended_cb(self, event):
    #     """
    #     Callback function executes when the command invoked asynchronously returns from the server.

    #     :param event: A CmdDoneEvent object. This class is used to pass data to the callback method in asynchronous
    #                     callback model for command execution.

    #     :type: CmdDoneEvent object

    #         It has the following members:
    #             - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
    #             - cmd_name   : (str) The command name
    #             - argout_raw : (DeviceData) The command argout
    #             - argout     : The command argout
    #             - err        : (bool) A boolean flag set to true if the command failed. False otherwise
    #             - errors     : (sequence<DevError>) The error stack
    #             - ext

    #     :return: none
    #     """
    #     this_server = TangoServerHelper.get_instance()
    #     sdp_sa_ln_server = TangoServerHelper.get_instance()
    #     if event.err:
    #         log = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
    #         this_server.write_attr("activityMessage", log, False)
    #         sdp_sa_ln_server.set_status(log)
    #         self.logger.error(log)
    #     else:
    #         log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
    #         this_server.write_attr("activityMessage", log, False)
    #         sdp_sa_ln_server.set_status(log)
    #         self.logger.info(log)

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

        try:
            self.sdp_subarray_adapter.On()
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                f"Error in calling Telescope On Sdp Subarray Device {self.sdp_subarray_dev_name.dev_name}: {e}",
            )
        return (ResultCode.OK, "")  # do we need return code here?

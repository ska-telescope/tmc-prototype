from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory, AdapterType
from ska_tmc_common.exceptions import CommandNotAllowed, DeviceUnresponsive
from ska_tmc_common.tmc_command import TmcLeafNodeCommand
from tango import DevState


class SdpMLNCommand(TmcLeafNodeCommand):
    """Abstract command class for all SdpMasterLeafNode"""
    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory

    def check_unresponsive(self):
        component_manager = self.target
        devInfo = component_manager.get_device()
        if devInfo is None or devInfo.unresponsive:
            raise DeviceUnresponsive("SDP master device is not available")

    def check_allowed(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        if self.op_state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            raise CommandNotAllowed(
                "Command is not allowed in current operational state %s",
                self.op_state_model.op_state,
            )

        self.check_unresponsive()

        return True

    def init_adapter(self):
        self.sdp_master_adapter = None
        component_manager = self.target
        dev_name = component_manager._sdp_master_dev_name
        devInfo = component_manager.get_device()
        try:
            if not devInfo.unresponsive:
                self.sdp_master_adapter = (
                    self._adapter_factory.get_or_create_adapter(
                        dev_name, AdapterType.MASTER
                    )
                )
        except Exception as e:
            return self.adapter_error_message_result(
                component_manager.get_device(),
                e,
            )

        return ResultCode.OK, ""

    def do(self, argin=None):
        result = self.do(argin)
        return result

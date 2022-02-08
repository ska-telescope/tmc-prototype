import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpmasterleafnode.commands.disable_command import Disable
from tests.settings import (
    SDP_MASTER_DEVICE,
    create_cm,
    get_sdpmln_command_obj,
    logger,
)


@pytest.mark.sdpmln
def test_disable_command(tango_context):
    logger.info("%s", tango_context)
    _, disable_command, adapter_factory = get_sdpmln_command_obj(Disable)
    assert disable_command.check_allowed()
    (result_code, _) = disable_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(SDP_MASTER_DEVICE)
    adapter.proxy.Disable.assert_called()


@pytest.mark.sdpmln
def test_disable_command_fail_sdp_master(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", None, SDP_MASTER_DEVICE)
    adapter_factory = HelperAdapterFactory()
    cm._sdp_master_dev_name = SDP_MASTER_DEVICE
    # include exception in Disable command
    adapter_factory.get_or_create_adapter(
        SDP_MASTER_DEVICE, attrs={"Disable.side_effect": Exception}
    )

    disable_command = Disable(cm, cm.op_state_model, adapter_factory)
    assert disable_command.check_allowed()
    (result_code, message) = disable_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_MASTER_DEVICE in message


@pytest.mark.sdpmln
def test_disable_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, disable_command, _ = get_sdpmln_command_obj(Disable)
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        disable_command.check_allowed()

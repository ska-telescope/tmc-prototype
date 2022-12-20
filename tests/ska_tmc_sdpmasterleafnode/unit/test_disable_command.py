import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpmasterleafnode.commands import Disable
from tests.settings import (
    SDP_MASTER_DEVICE_LOW,
    SDP_MASTER_DEVICE_MID,
    create_cm,
    get_sdpmln_command_obj,
)


@pytest.mark.sdpmln
@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_disable_command(tango_context, sdp_master_device):
    _, disable_command, adapter_factory = get_sdpmln_command_obj(
        Disable, sdp_master_device
    )
    assert disable_command.check_allowed()
    (result_code, _) = disable_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(sdp_master_device)
    adapter.proxy.Disable.assert_called_once_with()


@pytest.mark.sdpmln
@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_disable_command_fail_sdp_master(tango_context, sdp_master_device):
    cm, _ = create_cm("SdpMLNComponentManager", sdp_master_device)
    adapter_factory = HelperAdapterFactory()
    cm.sdp_master_dev_name = sdp_master_device
    # include exception in Disable command
    adapter_factory.get_or_create_adapter(
        sdp_master_device, attrs={"Disable.side_effect": Exception}
    )
    disable_command = Disable(cm, cm.op_state_model, adapter_factory)
    assert disable_command.check_allowed()
    (result_code, message) = disable_command.do()
    assert result_code == ResultCode.FAILED
    assert sdp_master_device in message

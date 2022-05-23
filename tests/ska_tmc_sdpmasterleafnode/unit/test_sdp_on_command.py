import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpmasterleafnode.commands import On
from tests.settings import create_cm, get_sdpmln_command_obj


@pytest.mark.sdpmln
def test_on_command(tango_context, sdp_master_device):
    _, on_command, adapter_factory = get_sdpmln_command_obj(On)
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(sdp_master_device)
    adapter.proxy.On.assert_called_once_with()


@pytest.mark.sdpmln
def test_on_command_fail_sdp_master(tango_context, sdp_master_device):
    cm, _ = create_cm("SdpMLNComponentManager", sdp_master_device)
    adapter_factory = HelperAdapterFactory()
    cm.sdp_master_dev_name = sdp_master_device
    # include exception in On command
    adapter_factory.get_or_create_adapter(
        sdp_master_device, attrs={"On.side_effect": Exception}
    )
    on_command = On(cm, cm.op_state_model, adapter_factory)
    assert on_command.check_allowed()
    (result_code, message) = on_command.do()
    assert result_code == ResultCode.FAILED
    assert sdp_master_device in message

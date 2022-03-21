import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_cspmasterleafnode.commands.on_command import On
from tests.settings import create_cm, get_cspmln_command_obj


@pytest.mark.cspmln
def test_on_command(tango_context, csp_master_device):
    _, on_command, adapter_factory = get_cspmln_command_obj(On)
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(csp_master_device)
    adapter.proxy.On.assert_called()


@pytest.mark.cspmln
def test_on_command_fail_csp_master(tango_context, csp_master_device):
    cm, _ = create_cm("CspMLNComponentManager", csp_master_device)
    adapter_factory = HelperAdapterFactory()
    cm._csp_master_dev_name = csp_master_device

    # include exception in On command
    adapter_factory.get_or_create_adapter(
        csp_master_device, attrs={"On.side_effect": Exception}
    )

    on_command = On(cm, cm.op_state_model, adapter_factory)
    assert on_command.check_allowed()
    (result_code, message) = on_command.do()
    assert result_code == ResultCode.FAILED
    assert csp_master_device in message


@pytest.mark.cspmln
def test_on_fail_check_allowed(tango_context, csp_master_device):
    cm, on_command, _ = get_cspmln_command_obj(On)
    dev_info = cm.get_device()
    dev_info.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        on_command.check_allowed()

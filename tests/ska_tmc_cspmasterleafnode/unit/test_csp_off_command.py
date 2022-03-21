import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_cspmasterleafnode.commands.off_command import Off
from tests.settings import create_cm, get_cspmln_command_obj, logger


@pytest.mark.cspmln
def test_off_command(tango_context, csp_master_device):
    _, off_command, adapter_factory = get_cspmln_command_obj(Off)
    assert off_command.check_allowed()
    (result_code, _) = off_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(csp_master_device)
    adapter.proxy.Standby.assert_called()


@pytest.mark.cspmln
def test_off_command_fail_csp_master(tango_context, csp_master_device):
    cm, _ = create_cm("CspMLNComponentManager", csp_master_device)
    adapter_factory = HelperAdapterFactory()
    cm._csp_master_dev_name = csp_master_device

    # include exception in Off command
    adapter_factory.get_or_create_adapter(
        csp_master_device, attrs={"Off.side_effect": Exception}
    )

    off_command = Off(cm, cm.op_state_model, adapter_factory)
    assert off_command.check_allowed()
    (result_code, message) = off_command.do()
    assert result_code == ResultCode.FAILED
    assert csp_master_device in message


@pytest.mark.cspmln
def test_off_fail_check_allowed(tango_context, csp_master_device):
    cm, off_command, _ = get_cspmln_command_obj(Off)
    dev_info = cm.get_device()
    dev_info.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        off_command.check_allowed()

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpmasterleafnode.commands import On
from tests.settings import create_cm, get_sdpmln_command_obj, logger


@pytest.mark.sdpmln
def test_on_command(tango_context, sdp_master_device):
    logger.info("%s", tango_context)
    _, on_command, adapter_factory = get_sdpmln_command_obj(
        On, sdp_master_device
    )
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(sdp_master_device)
    adapter.proxy.On.assert_called()


@pytest.mark.sdpmln
def test_on_command_fail_sdp_master(tango_context, sdp_master_device):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", None, sdp_master_device)
    adapter_factory = HelperAdapterFactory()
    cm._sdp_master_dev_name = sdp_master_device

    # include exception in On command
    adapter_factory.get_or_create_adapter(
        sdp_master_device, attrs={"On.side_effect": Exception}
    )

    on_command = On(cm, cm.op_state_model, adapter_factory)
    assert on_command.check_allowed()
    (result_code, message) = on_command.do()
    assert result_code == ResultCode.FAILED
    assert sdp_master_device in message


@pytest.mark.sdpmln
def test_on_fail_check_allowed(tango_context, sdp_master_device):

    logger.info("%s", tango_context)
    cm, on_command, _ = get_sdpmln_command_obj(On, sdp_master_device)
    dev_info = cm.get_device()
    dev_info.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        on_command.check_allowed()

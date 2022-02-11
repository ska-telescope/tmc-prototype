import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpmasterleafnode.commands import TelescopeOff
from tests.settings import create_cm, get_sdpmln_command_obj, logger


@pytest.mark.sdpmln
def test_telescope_off_command(tango_context, sdp_master_device):
    logger.info("%s", tango_context)
    _, off_command, adapter_factory = get_sdpmln_command_obj(
        TelescopeOff, sdp_master_device
    )
    assert off_command.check_allowed()
    (result_code, _) = off_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(sdp_master_device)
    adapter.proxy.Off.assert_called()


@pytest.mark.sdpmln
def test_telescope_off_command_fail_sdp_master(
    tango_context, sdp_master_device
):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", None, sdp_master_device)
    adapter_factory = HelperAdapterFactory()
    cm._sdp_master_dev_name = sdp_master_device

    # include exception in TelescopeOff command
    adapter_factory.get_or_create_adapter(
        sdp_master_device, attrs={"TelescopeOff.side_effect": Exception}
    )

    off_command = TelescopeOff(cm, cm.op_state_model, adapter_factory)
    assert off_command.check_allowed()
    (result_code, message) = off_command.do()
    assert result_code == ResultCode.FAILED
    assert sdp_master_device in message


@pytest.mark.sdpmln
def test_telescope_off_fail_check_allowed(tango_context, sdp_master_device):

    logger.info("%s", tango_context)
    cm, off_command, _ = get_sdpmln_command_obj(
        TelescopeOff, sdp_master_device
    )
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        off_command.check_allowed()

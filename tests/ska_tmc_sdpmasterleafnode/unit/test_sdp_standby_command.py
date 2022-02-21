import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpmasterleafnode.commands import Standby
from tests.settings import create_cm, get_sdpmln_command_obj, logger


@pytest.mark.sdpmln
def test_standby_command(tango_context, sdp_master_device):
    logger.info("%s", tango_context)
    _, standby_command, adapter_factory = get_sdpmln_command_obj(
        Standby, sdp_master_device
    )
    assert standby_command.check_allowed()
    (result_code, _) = standby_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(sdp_master_device)
    adapter.proxy.Standby.assert_called()


@pytest.mark.sdpmln
def test_standby_command_fail_sdp_master(tango_context, sdp_master_device):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", None, sdp_master_device)
    adapter_factory = HelperAdapterFactory()
    cm._sdp_master_dev_name = sdp_master_device

    # include exception in Standby command
    adapter_factory.get_or_create_adapter(
        sdp_master_device, attrs={"Standby.side_effect": Exception}
    )

    standby_command = Standby(cm, cm.op_state_model, adapter_factory)
    assert standby_command.check_allowed()
    (result_code, message) = standby_command.do()
    assert result_code == ResultCode.FAILED
    assert sdp_master_device in message


@pytest.mark.sdpmln
def test_standby_fail_check_allowed(tango_context, sdp_master_device):

    logger.info("%s", tango_context)
    cm, standby_command, _ = get_sdpmln_command_obj(Standby, sdp_master_device)
    dev_info = cm.get_device
    dev_info.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        standby_command.check_allowed()

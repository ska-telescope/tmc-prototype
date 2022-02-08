import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpmasterleafnode.commands.telescope_standby_command import (
    TelescopeStandby,
)
from tests.settings import (
    SDP_MASTER_DEVICE,
    create_cm,
    get_sdpmln_command_obj,
    logger,
)


@pytest.mark.sdpmln
def test_telescope_standby_command(tango_context):
    logger.info("%s", tango_context)
    _, standby_command, adapter_factory = get_sdpmln_command_obj(
        TelescopeStandby
    )
    assert standby_command.check_allowed()
    (result_code, _) = standby_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(SDP_MASTER_DEVICE)
    adapter.proxy.Standby.assert_called()


@pytest.mark.sdpmln
def test_telescope_standby_command_fail_sdp_master(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", None, SDP_MASTER_DEVICE)
    adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeStandby command
    adapter_factory.get_or_create_adapter(
        SDP_MASTER_DEVICE, attrs={"TelescopeStandby.side_effect": Exception}
    )

    standby_command = TelescopeStandby(cm, cm.op_state_model, adapter_factory)
    assert standby_command.check_allowed()
    (result_code, message) = standby_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_MASTER_DEVICE in message


@pytest.mark.sdpmln
def test_telescope_standby_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, standby_command, _ = get_sdpmln_command_obj(TelescopeStandby)
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        standby_command.check_allowed()

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpmasterleafnode.commands.telescope_off_command import (
    TelescopeOff,
)
from tests.settings import (
    SDP_MASTER_DEVICE,
    create_cm,
    get_sdpmln_command_obj,
    logger,
)


@pytest.mark.sdpmln
def test_telescope_off_command(tango_context):
    logger.info("%s", tango_context)
    _, off_command, adapter_factory = get_sdpmln_command_obj(TelescopeOff)
    assert off_command.check_allowed()
    (result_code, _) = off_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(SDP_MASTER_DEVICE)
    adapter.proxy.Off.assert_called()


@pytest.mark.sdpmln
def test_telescope_off_command_fail_sdp_master(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", SDP_MASTER_DEVICE)
    adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeOff command
    adapter_factory.get_or_create_adapter(
        SDP_MASTER_DEVICE, attrs={"TelescopeOff.side_effect": Exception}
    )

    off_command = TelescopeOff(cm, cm.op_state_model, adapter_factory)
    assert off_command.check_allowed()
    (result_code, message) = off_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_MASTER_DEVICE in message


@pytest.mark.sdpmln
def test_telescope_off_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, off_command, _ = get_sdpmln_command_obj(TelescopeOff)
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        off_command.check_allowed()

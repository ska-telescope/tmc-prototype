import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands.telescope_on_command import (
    TelescopeOn,
)
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
def test_telescope_on_command(tango_context):
    logger.info("%s", tango_context)
    _, on_command, adapter_factory = get_sdpsln_command_obj(TelescopeOn, None)
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    adapter.proxy.On.assert_called()


@pytest.mark.sdpsln
def test_telescope_on_command_fail_sdp_subarray(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeOn command
    adapter_factory.get_or_create_adapter(
        SDP_SUBARRAY_DEVICE, attrs={"TelescopeOn.side_effect": Exception}
    )

    on_command = TelescopeOn(cm, cm.op_state_model, adapter_factory)
    assert on_command.check_allowed()
    (result_code, message) = on_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_SUBARRAY_DEVICE in message


@pytest.mark.xfail
def test_telescope_on_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, on_command, _ = get_sdpsln_command_obj(TelescopeOn, None)
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        on_command.check_allowed()

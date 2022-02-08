import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import SdpSubArrayAdapter
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands.telescope_off_command import (
    TelescopeOff,
)
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
def test_telescope_off_command(tango_context):
    logger.info("%s", tango_context)
    _, off_command, my_adapter_factory = get_sdpsln_command_obj(
        TelescopeOff, None
    )
    assert off_command.check_allowed()
    (result_code, _) = off_command.do()
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.Off.assert_called()


@pytest.mark.sdpsln
def test_telescope_off_command_fail_sdp_subarray(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeOff command
    adapter_factory.get_or_create_adapter(
        SDP_SUBARRAY_DEVICE, attrs={"TelescopeOff.side_effect": Exception}
    )

    off_command = TelescopeOff(cm, cm.op_state_model, adapter_factory)
    assert off_command.check_allowed()
    (result_code, message) = off_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_SUBARRAY_DEVICE in message


@pytest.mark.xfail
def test_telescope_off_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, off_command, _ = get_sdpsln_command_obj(TelescopeOff, None)
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        off_command.check_allowed()

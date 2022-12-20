import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import On
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_on_command(tango_context, devices):
    logger.info("%s", tango_context)
    _, on_command, adapter_factory = get_sdpsln_command_obj(On, devices, None)
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(devices)
    adapter.proxy.On.assert_called_once_with()


@pytest.mark.sdpsln
def test_on_command_fail_sdp_subarray(tango_context, devices):
    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeOn command
    failing_dev = devices

    adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"TelescopeOn.side_effect": Exception}
    )

    on_command = On(cm, cm.op_state_model, adapter_factory)
    assert on_command.check_allowed()
    (result_code, message) = on_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


@pytest.mark.sdpsln
def test_on_fail_check_allowed(tango_context, devices):

    logger.info("%s", tango_context)
    cm, on_command, _ = get_sdpsln_command_obj(On, devices, None)
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        on_command.check_allowed()

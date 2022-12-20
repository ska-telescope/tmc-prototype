import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.exceptions import DeviceUnresponsive

from ska_tmc_sdpsubarrayleafnode.commands import Reset
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_reset_command(tango_context, devices):
    logger.info("%s", tango_context)
    _, reset_command, _ = get_sdpsln_command_obj(Reset, devices, None)
    assert reset_command.check_allowed()
    (result_code, _) = reset_command.do()
    assert result_code == ResultCode.OK


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_reset_fail_check_allowed_with_device_unresponsive(
    tango_context, devices
):

    logger.info("%s", tango_context)
    cm, reset_command, _ = get_sdpsln_command_obj(Reset, devices, None)
    cm.get_device().update_unresponsive(True)
    with pytest.raises(
        DeviceUnresponsive, match="SDP subarray device is not available"
    ):
        reset_command.check_allowed()

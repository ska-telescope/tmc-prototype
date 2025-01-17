import pytest
from ska_control_model import AdminMode
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands import SetAdminMode
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    logger,
)


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_set_admin_mode_command_on_sdpsln(tango_context, sdp_subarray):
    """Test to check set admin mode command on SDPSLN"""

    cm = create_cm("SdpSLNComponentManager", sdp_subarray)
    set_admin_mode = SetAdminMode(logger=logger, component_manager=cm)
    result_code, message = set_admin_mode.do(AdminMode.ONLINE)

    assert result_code == ResultCode.OK
    assert message == "Command Completed"


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_invalid_admin_mode_on_sdpsln(tango_context, sdp_subarray):
    """Test to check failed set admin mode command on SDPSLN"""

    cm = create_cm("SdpSLNComponentManager", sdp_subarray)
    argin = 7  # arbitary adminMode value
    set_admin_mode = SetAdminMode(logger=logger, component_manager=cm)
    result_code, message = set_admin_mode.do(argin=argin)

    assert result_code == ResultCode.FAILED
    assert message == "Command Failed"


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_feature_toggle_adminMode(tango_context, sdp_subarray):
    """Test for feature toggle on SDPSLN"""

    cm = create_cm("SdpSLNComponentManager", sdp_subarray)
    cm.is_admin_mode_enabled = False
    set_admin_mode = SetAdminMode(logger=logger, component_manager=cm)
    result_code, message = set_admin_mode.do(AdminMode.ONLINE)

    assert result_code == ResultCode.NOT_ALLOWED
    assert message == (
        "AdminMode functionality is disabled, "
        + "Device will function normally"
    )

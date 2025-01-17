import pytest
from ska_control_model import AdminMode
from ska_tango_base.commands import ResultCode, TaskStatus

from ska_tmc_sdpmasterleafnode.commands import SetAdminMode
from tests.settings import (
    SDP_MASTER_DEVICE_LOW,
    SDP_MASTER_DEVICE_MID,
    create_cm,
    logger,
)


@pytest.mark.parametrize(
    "sdp_controller", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_set_admin_mode_command_on_sdpmln(tango_context, sdp_controller):
    """Test to set the adminMode on SDP master"""

    cm = create_cm("SdpMLNComponentManager", sdp_controller)
    set_admin_mode = SetAdminMode(logger=logger, component_manager=cm)
    result_code, message = set_admin_mode.do(AdminMode.ONLINE)

    assert result_code == ResultCode.OK
    assert message == "Command Completed"


@pytest.mark.parametrize(
    "sdp_controller", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_invalid_admin_mode_command_on_sdpmln(
    tango_context,
    sdp_controller,
):
    """Test to check failed set the adminMode on SDP master"""

    cm = create_cm("SdpMLNComponentManager", sdp_controller)
    argin = 7  # arbitary adminMode value
    set_admin_mode = SetAdminMode(logger=logger, component_manager=cm)
    result_code, message = set_admin_mode.do(argin)

    assert result_code == ResultCode.FAILED
    assert message == "Command Failed"


@pytest.mark.parametrize(
    "sdp_controller", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_feature_toggle_adminMode(tango_context, sdp_controller):
    """Test to check toggle feature"""

    cm = create_cm("SdpMLNComponentManager", sdp_controller)
    cm.is_admin_mode_enabled = False
    argin = AdminMode.ONLINE  # arbitary adminMode value
    set_admin_mode = SetAdminMode(logger=logger, component_manager=cm)
    result_code, message = set_admin_mode.do(argin)

    assert result_code == ResultCode.NOT_ALLOWED
    assert message == (
        "AdminMode functionality is disabled, "
        + "Device will function normally"
    )


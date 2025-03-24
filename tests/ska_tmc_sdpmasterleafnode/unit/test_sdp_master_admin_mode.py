from unittest import mock
from unittest.mock import MagicMock

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


@pytest.mark.parametrize(
    "sdp_controller", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_admin_mode_offline_on_sdpmln(
    tango_context, sdp_controller, task_callback
):
    """Test to check admin mode offline results in
    command failure on SDPMLN"""

    cm = create_cm("SdpMLNComponentManager", sdp_controller)
    set_admin_mode = SetAdminMode(logger=logger, component_manager=cm)
    result_code, message = set_admin_mode.do(AdminMode.OFFLINE)

    assert result_code == ResultCode.OK
    assert message == "Command Completed"

    assert cm.is_command_allowed("On")

    cm.on(task_callback=task_callback)
    task_callback.assert_against_call(status=TaskStatus.QUEUED)
    task_callback.assert_against_call(status=TaskStatus.IN_PROGRESS)
    call_kwargs = task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=mock.ANY,
    )

    assert (
        "On Command invocation failed on device"
        in call_kwargs["call_kwargs"]["result"][1]
    )


@pytest.mark.parametrize(
    "sdp_controller", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_update_admin_mode_callback(sdp_controller):
    """Test to check update admin mode callback in component manager"""
    # Create a mock event
    mock_logger = MagicMock()
    admin_mode = AdminMode.ENGINEERING
    cm = create_cm("SdpMLNComponentManager", sdp_controller)
    cm.logger = mock_logger
    cm.update_device_admin_mode(admin_mode)

    mock_logger.info.assert_has_calls(
        [
            # mock.call("Admin Mode value updated on device: %s", device_name),
            mock.call(
                "Admin Mode value updated to :%s", AdminMode.ENGINEERING.name
            ),
        ],
        any_order=False,
    )

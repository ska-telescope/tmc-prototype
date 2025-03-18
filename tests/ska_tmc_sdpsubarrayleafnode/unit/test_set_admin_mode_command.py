from unittest import mock
from unittest.mock import MagicMock

import pytest
from ska_control_model import AdminMode
from ska_tango_base.commands import ResultCode, TaskStatus
from ska_tmc_common.device_info import SubArrayDeviceInfo
from tango import EventType

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


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_admin_mode_offline_on_sdpsln(
    tango_context, sdp_subarray, task_callback
):
    """Test to check admin mode offline results in
    command failure on SDPSLN"""

    cm = create_cm("SdpSLNComponentManager", sdp_subarray)
    set_admin_mode = SetAdminMode(logger=logger, component_manager=cm)
    result_code, message = set_admin_mode.do(AdminMode.OFFLINE)

    assert result_code == ResultCode.OK
    assert message == "Command Completed"

    assert cm.is_command_allowed("Off")

    cm.off(task_callback=task_callback)
    task_callback.assert_against_call(status=TaskStatus.QUEUED)
    task_callback.assert_against_call(status=TaskStatus.IN_PROGRESS)
    call_kwargs = task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=mock.ANY,
    )

    assert (
        "The invocation of the Off command is failed on SDP Subarray"
        in call_kwargs["call_kwargs"]["result"][1]
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_check_handle_admin_mode_event(sdp_subarray):
    """Test for event receiver handle admin mode event"""
    # Create a mock event
    mock_event_receiver = MagicMock()
    mock_event = MagicMock()
    mock_event.type = EventType.CHANGE_EVENT
    cm = create_cm("SdpMLNComponentManager", sdp_subarray)
    cm._event_receiver = mock_event_receiver

    # Call the function
    cm._event_receiver.handle_admin_mode_event(event=mock_event)
    cm._event_receiver.handle_admin_mode_event.assert_called_once_with(
        event=mock_event
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_update_admin_mode_callback(sdp_subarray):
    """Test for component manager admin mode callback method"""
    # Create a mock event
    mock_logger = MagicMock()
    device_name = sdp_subarray
    admin_mode = AdminMode.ENGINEERING
    cm = create_cm("SdpMLNComponentManager", sdp_subarray)
    cm.logger = mock_logger
    cm.update_device_admin_mode(
        device_name=sdp_subarray, admin_mode=admin_mode
    )
    mock_logger.info.assert_has_calls(
        [
            mock.call("Admin Mode value updated on device: %s", device_name),
            mock.call(
                "Admin Mode value updated to :%s", AdminMode.ENGINEERING.name
            ),
        ],
        any_order=False,
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_cmd_ended_cb_with_valid_event(sdp_subarray):
    """Test for component manager cmd ended cb method"""
    # Create a mock event
    mock_logger = MagicMock()
    mock_event = MagicMock()
    mock_event.err = False
    mock_event.cmd_name = "test_command"
    # Call the method
    cm = create_cm("SdpSLNComponentManager", sdp_subarray)
    cm.logger = mock_logger
    cm.cmd_ended_cb(mock_event)
    cm.logger.info.assert_called_once_with(
        "Command %s invoked successfully.", mock_event.cmd_name
    )
    mock_event.err = True
    mock_event.errors = [MagicMock(desc="Test error description")]
    cm.cmd_ended_cb(mock_event)
    cm.logger.error.assert_called_once_with(
        "Error invoking command: %s failed with error : %s",
        mock_event.cmd_name,
        mock_event.errors,
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_get_device(sdp_subarray):
    """Test to check get device method of component manager"""
    # Call the method under test
    mock_device = MagicMock(spec=SubArrayDeviceInfo)
    cm = create_cm("SdpSLNComponentManager", sdp_subarray)
    cm._device = mock_device
    # Assert that the returned device is the same as the mocked _device
    device = cm.get_device()
    assert device == mock_device


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_update_event_failure(sdp_subarray):
    """Test to update event failure method"""
    # Record the current time before calling the method
    mock_device = MagicMock(spec=SubArrayDeviceInfo)
    cm = create_cm("SdpSLNComponentManager", sdp_subarray)
    cm.get_device = MagicMock(return_value=mock_device)
    cm.lock = MagicMock()
    # Call the method under test
    cm.update_event_failure(sdp_subarray)

    # Assert that the lock was acquired and released
    cm.lock.__enter__.assert_called_once()
    cm.lock.__exit__.assert_called_once()

    # Assert that get_device was called once
    cm.get_device.assert_called_once()


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "sdp_subarray", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_invoke_lrcr_callback_without_callback(sdp_subarray):
    """Test to check lrcr_callback_without callback method"""
    # Set the callback to None
    cm = create_cm("SdpSLNComponentManager", sdp_subarray)
    cm.update_lrcr_callback = MagicMock()
    cm._lrc_result = "sample_result"
    # Call the method
    cm._invoke_lrcr_callback()
    cm.update_lrcr_callback.assert_called_once_with("sample_result")
    cm.update_lrcr_callback = None
    cm._invoke_lrcr_callback()
    assert cm.update_lrcr_callback is None

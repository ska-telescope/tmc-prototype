from unittest import mock

import pytest
from ska_control_model import AdminMode
from ska_tango_base.commands import ResultCode, TaskStatus

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


@pytest.mark.test
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

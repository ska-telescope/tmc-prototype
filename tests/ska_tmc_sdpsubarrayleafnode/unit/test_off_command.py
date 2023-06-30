import mock
import pytest
from ska_tango_base.commands import ResultCode, TaskStatus
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.exceptions import CommandNotAllowed, DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)
from tango import DevState

from ska_tmc_sdpsubarrayleafnode.commands.off_command import Off
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    logger,
)


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_mid_off(tango_context, devices, task_callback):
    cm = create_cm("SdpSLNComponentManager", devices)
    assert cm.is_command_allowed("off")

    cm.off(task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.QUEUED}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.COMPLETED, "result": ResultCode.OK}
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_command_off_not_allowed(tango_context, devices):
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.op_state_model._op_state = DevState.FAULT
    with pytest.raises(CommandNotAllowed):
        cm.is_command_allowed("off")


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_command_off_with_failed_sdp_subarray(
    tango_context, devices, task_callback
):
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()
    failing_dev = devices

    # include exception in Off command
    attrs = {"Off.side_effect": Exception}

    sdp_subarray_mock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        failing_dev, AdapterType.SUBARRAY, proxy=sdp_subarray_mock
    )
    off_command = Off(cm, logger)
    off_command.adapter_factory = adapter_factory
    assert cm.is_command_allowed("off")
    off_command.off(logger, task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED, result=ResultCode.FAILED
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_off_command_is_allowed_device_unresponsive(tango_context, devices):
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    pytest.raises(DeviceUnresponsive)

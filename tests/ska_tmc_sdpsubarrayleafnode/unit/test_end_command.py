import mock
import pytest
from ska_tango_base.commands import ResultCode, TaskStatus
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from src.ska_tmc_sdpsubarrayleafnode.commands import End
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    logger,
    wait_for_cm_obstate_attribute_value,
)


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_end_command(tango_context, devices, task_callback):
    logger.info("%s", tango_context)
    DevFactory().get_device(devices).SetDirectObsState(ObsState.READY)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.update_device_obs_state(ObsState.READY)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.READY)
    assert cm.is_command_allowed("End")
    cm.end(task_callback=task_callback)
    task_callback.assert_against_call(status=TaskStatus.QUEUED)
    task_callback.assert_against_call(status=TaskStatus.IN_PROGRESS)
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(ResultCode.OK, "Command Completed"),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_end_command_fail_subarray(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()

    # include exception in End command
    attrs = {"EndScan.side_effect": Exception}
    sdpsubarrayrMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(devices, proxy=sdpsubarrayrMock)

    end_command = End(cm, logger)
    end_command.adapter_factory = adapter_factory
    end_command.end(logger, task_abort_event=None, task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(
            ResultCode.FAILED,
            "The invocation of the End command is "
            f"failed on SDP Subarray Device {devices} Reason: Error in "
            "invoking End command on SDP Subarray.The command has NOT been "
            "executed. This device will continue with normal operation.",
        ),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_end_command_not_allowed_with_invalid_obsState(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.update_device_obs_state(ObsState.EMPTY)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.EMPTY)
    cm.end(task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.QUEUED}
    )
    task_callback.assert_against_call(
        status=TaskStatus.REJECTED,
        result=(
            ResultCode.NOT_ALLOWED,
            "Command is not allowed",
        ),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_end_fail_check_allowed_with_device_unresponsive(devices):
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm.is_command_allowed_callable("End")()

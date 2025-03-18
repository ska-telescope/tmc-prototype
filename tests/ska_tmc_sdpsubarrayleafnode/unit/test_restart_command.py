import mock
import pytest
from ska_tango_base.commands import ResultCode, TaskStatus
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.exceptions import DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import Restart
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
def test_telescope_restart_command(tango_context, devices, task_callback):
    logger.info("%s", tango_context)
    DevFactory().get_device(devices).SetDirectObsState(ObsState.ABORTED)
    cm = create_cm("SdpSLNComponentManager", devices)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.ABORTED)
    assert cm.is_command_allowed("Restart")
    cm.restart(task_callback=task_callback)
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
def test_restart_command_fail_subarray(tango_context, devices, task_callback):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()

    # include exception in Restart command
    attrs = {"Restart.side_effect": Exception}
    sdpsubarrayrMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        devices, AdapterType.SDPSUBARRAY, proxy=sdpsubarrayrMock
    )
    end_command = Restart(cm, logger)
    end_command.adapter_factory = adapter_factory
    end_command.restart(logger, task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(
            ResultCode.FAILED,
            "Execution of Restart command is failed.Reason: Error in invoking"
            f" Restart                 command on Sdp Subarray - {devices}: ",
        ),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_restart_command_not_allowed_with_invalid_obsState(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.update_device_obs_state(devices, ObsState.READY)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.READY)

    cm.restart(task_callback=task_callback)
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
def test_restart_fail_check_allowed_with_device_unresponsive(devices):
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm.is_command_allowed_callable("Restart")()

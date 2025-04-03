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

from ska_tmc_sdpsubarrayleafnode.commands.end_scan_command import EndScan
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
def test_endscan_command(tango_context, devices, task_callback):
    logger.info("%s", tango_context)
    DevFactory().get_device(devices).SetDirectObsState(ObsState.SCANNING)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.update_device_obs_state(ObsState.SCANNING)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.SCANNING)
    assert cm.is_command_allowed("EndScan")
    cm.end_scan(task_callback=task_callback)
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
def test_endscan_fail_check_allowed_with_device_unresponsive(devices):
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm.is_command_allowed_callable("EndScan")()


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_endscan_command_not_allowed_with_invalid_obsState(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.update_device_obs_state(ObsState.EMPTY)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.EMPTY)
    cm.end_scan(task_callback=task_callback)
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
def test_telescope_end_scan_command_fail_subarray(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()

    # include exception in ReleaseAllResources command
    attrs = {"EndScan.side_effect": Exception}
    sdpsubarrayrMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(devices, proxy=sdpsubarrayrMock)
    release_command = EndScan(cm, logger)
    release_command.adapter_factory = adapter_factory
    release_command.end_scan(
        logger, task_abort_event=None, task_callback=task_callback
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(
            ResultCode.FAILED,
            "The invocation of the EndScan command is "
            + f"failed on SDP Subarray Device {devices} "
            + "Reason: Error in "
            + "invoking EndScan command on SDP Subarray ",
        ),
    )

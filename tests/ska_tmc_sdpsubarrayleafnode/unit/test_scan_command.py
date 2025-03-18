from os.path import dirname, join

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

from ska_tmc_sdpsubarrayleafnode.commands.scan_command import Scan
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    logger,
    wait_for_cm_obstate_attribute_value,
)


def get_scan_input_str(scan_input_file="command_Scan.json"):
    path = join(dirname(__file__), "..", "..", "data", scan_input_file)
    with open(path, "r") as f:
        scan_input_str = f.read()
    return scan_input_str


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_scan_command(tango_context, devices, task_callback):
    logger.info("%s", tango_context)
    DevFactory().get_device(devices).SetDirectObsState(ObsState.READY)
    cm = create_cm("SdpSLNComponentManager", devices)
    scan_input_str = get_scan_input_str()
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.READY)
    cm.scan(scan_input_str, task_callback=task_callback)
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
def test_scan_command_fail_subarray(tango_context, devices, task_callback):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()
    scan_input_str = get_scan_input_str()

    attrs = {"Scan.side_effect": Exception}
    sdpsubarrayrMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(devices, proxy=sdpsubarrayrMock)
    scan_command = Scan(
        cm,
        logger,
    )
    scan_command.adapter_factory = adapter_factory
    scan_command.scan(
        argin=scan_input_str,
        task_abort_event=None,
        task_callback=task_callback,
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(
            ResultCode.FAILED,
            "The invocation of the Scan command is failed on SdpSubarray "
            f"Device {devices}Reason: Error in calling the Scan command on "
            "Sdp Subarray.The command has NOT been executed."
            "This device will continue with normal operation.",
        ),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_scan_command_empty_input_json(tango_context, devices, task_callback):
    logger.info("%s", tango_context)
    DevFactory().get_device(devices).SetDirectObsState(ObsState.READY)
    cm = create_cm("SdpSLNComponentManager", devices)
    scan_input_str = ""
    cm.update_device_obs_state(devices, ObsState.READY)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.READY)
    cm.scan(scan_input_str, task_callback=task_callback)
    task_callback.assert_against_call(status=TaskStatus.QUEUED)
    task_callback.assert_against_call(status=TaskStatus.IN_PROGRESS)
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(
            ResultCode.FAILED,
            "Exception occurred while parsing the JSON."
            + "\n                    Please check the logs for details.",
        ),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_scan_command_not_allowed_with_invalid_obsState(
    devices, task_callback
):
    cm = create_cm("SdpSLNComponentManager", devices)
    scan_input_str = get_scan_input_str()
    cm.update_device_obs_state(devices, ObsState.IDLE)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.IDLE)
    cm.scan(scan_input_str, task_callback=task_callback)
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
def test_telescope_scan_command_fail_check_allowed_with_device_unresponsive(  # noqa:E501
    devices,
):
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm.is_command_allowed_callable("Scan")()

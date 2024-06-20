from os.path import dirname, join

import pytest
from ska_tango_base.commands import ResultCode, TaskStatus
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands.scan_command import Scan
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    logger,
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
    cm = create_cm("SdpSLNComponentManager", devices)
    scan_input_str = get_scan_input_str()
    cm.scan(scan_input_str, task_callback=task_callback)
    task_callback.assert_against_call(status=TaskStatus.QUEUED)
    task_callback.assert_against_call(status=TaskStatus.IN_PROGRESS)
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(ResultCode.OK, "Scan command invokation is complete"),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_scan_command_fail_subarray(tango_context, devices, task_callback):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()
    failing_dev = devices
    scan_input_str = get_scan_input_str()

    adapter_factory.get_or_create_adapter(
        failing_dev,
        AdapterType.SUBARRAY,
        attrs={"Scan.side_effect": Exception},
    )
    scan_command = Scan(cm, logger)
    scan_command.adapter_factory = adapter_factory
    scan_command.scan(scan_input_str, logger, task_callback)
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
    cm = create_cm("SdpSLNComponentManager", devices)
    scan_input_str = ""
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
def test_scan_command_fail_check_allowed_with_invalid_obsState(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.update_device_obs_state(ObsState.EMPTY)
    with pytest.raises(InvalidObsStateError):
        cm.is_command_allowed("Scan")


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_scan_command_fail_check_allowed_with_device_unresponsive(  # noqa:E501
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm.is_command_allowed("scan")

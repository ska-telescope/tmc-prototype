import time
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

from ska_tmc_sdpsubarrayleafnode.commands import AssignResources
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    logger,
    wait_for_cm_obstate_attribute_value,
)


def get_assign_input_str(assign_input_file="command_AssignResources.json"):
    path = join(dirname(__file__), "..", "..", "data", assign_input_file)
    with open(path, "r") as f:
        assign_input_str = f.read()
    return assign_input_str


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_assign_resources_command(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    assert cm.is_command_allowed("AssignResources")
    assign_input_str = get_assign_input_str()
    cm.assign_resources(assign_input_str, task_callback)
    task_callback.assert_against_call(status=TaskStatus.QUEUED)
    task_callback.assert_against_call(status=TaskStatus.IN_PROGRESS)
    cm.update_device_obs_state(ObsState.RESOURCING)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.RESOURCING)
    time.sleep(3)
    cm.update_device_obs_state(ObsState.IDLE)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.IDLE)
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(ResultCode.OK, "Command Completed"),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_assign_resources_command_fail_subarray(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()
    assign_input_str = get_assign_input_str()

    attrs = {"AssignResources.side_effect": Exception}
    sdpsubarrayrMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(devices, proxy=sdpsubarrayrMock)
    assign_command = AssignResources(cm, logger)
    assign_command.adapter_factory = adapter_factory
    assign_command.assign_resources(
        argin=assign_input_str,
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
            "The invocation of the AssignResources command is failed on "
            + "Sdp Subarray Device {devices} "
            + "Reason: Error in calling the "
            "AssignResources command on Sdp " + "Subarray.",
        ),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_assign_resources_command_empty_input_json(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    assign_input_str = ""
    cm.assign_resources(assign_input_str, task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.QUEUED}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(
            ResultCode.FAILED,
            "Exception occurred while parsing the JSON:"
            + " Expecting value: line 1 column 1 (char 0)",
        ),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_assign_resources_command_not_allowed(
    devices, task_callback, tango_context
):
    cm = create_cm("SdpSLNComponentManager", devices)
    assert cm.is_command_allowed("AssignResources")
    assign_input_str = get_assign_input_str()
    dev_factory = DevFactory()
    sdpsln_node = dev_factory.get_device(devices)
    sdpsln_node.SetDirectObsState(ObsState.SCANNING)

    cm.update_device_obs_state(ObsState.SCANNING)
    assert wait_for_cm_obstate_attribute_value(cm, ObsState.SCANNING)
    cm.assign_resources(assign_input_str, task_callback=task_callback)

    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.QUEUED}
    )
    task_callback.assert_against_call(
        status=TaskStatus.REJECTED,
        result=(ResultCode.NOT_ALLOWED, "Command is not allowed"),
        lookahead=5,
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_assign_resources_command_fail_check_allowed_with_device_unresponsive(  # noqa:E501
    devices,
):
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm.is_command_allowed_callable("AssignResources")()

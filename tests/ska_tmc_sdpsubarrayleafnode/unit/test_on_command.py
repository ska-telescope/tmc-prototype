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

from ska_tmc_sdpsubarrayleafnode.commands.on_command import On
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
def test_command_on(tango_context, devices, task_callback):
    cm = create_cm("SdpSLNComponentManager", devices)
    assert cm.is_command_allowed("On")

    cm.on(task_callback=task_callback)
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
def test_command_on_not_allowed(tango_context, devices):
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.op_state_model._op_state = DevState.FAULT
    with pytest.raises(CommandNotAllowed):
        cm.is_command_allowed("On")


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_command_on_with_failed_sdp_subarray(
    tango_context, devices, task_callback
):
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()
    failing_dev = devices

    # include exception in On command
    attrs = {"On.side_effect": Exception}

    sdp_subarray_mock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        failing_dev, AdapterType.SUBARRAY, proxy=sdp_subarray_mock
    )
    on_command = On(cm, logger)
    on_command.adapter_factory = adapter_factory
    assert cm.is_command_allowed("On")
    on_command.on(logger, task_callback=task_callback)
    task_callback.assert_against_call(status=TaskStatus.IN_PROGRESS)
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(
            ResultCode.FAILED,
            "The invocation of the On command is "
            + f"failed on SDP Subarray Device {devices} Reason: Error in "
            + "invoking On command on SDP Subarray.The command has NOT been "
            + "executed. This device will continue with normal operation.",
        ),
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_on_command_is_allowed_device_unresponsive(devices):
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm._check_if_sdp_sa_is_responsive()

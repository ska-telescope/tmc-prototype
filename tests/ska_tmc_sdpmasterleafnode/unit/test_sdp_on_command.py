import pytest
from ska_tango_base.commands import ResultCode, TaskStatus
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.exceptions import CommandNotAllowed, DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)
from tango import DevState

from ska_tmc_sdpmasterleafnode.commands import On
from tests.settings import (
    SDP_MASTER_DEVICE_LOW,
    SDP_MASTER_DEVICE_MID,
    create_cm,
    logger,
)


@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_on_command(tango_context, sdp_master_device, task_callback):
    cm = create_cm("SdpMLNComponentManager", sdp_master_device)
    assert cm.is_command_allowed("On")
    cm.on(task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.QUEUED}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        call_kwargs={
            "status": TaskStatus.COMPLETED,
            "result": (ResultCode.OK, "Command Completed"),
        }
    )


@pytest.mark.sdpmln
@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_on_command_fail_sdp_master1(
    tango_context, sdp_master_device, task_callback
):
    cm = create_cm("SdpMLNComponentManager", sdp_master_device)
    adapter_factory = HelperAdapterFactory()
    cm.sdp_master_device_name = sdp_master_device
    assert cm.is_command_allowed("On")
    adapter_factory.get_or_create_adapter(
        sdp_master_device, attrs={"On.side_effect": Exception}
    )
    on_command = On(cm, logger)
    on_command.adapter_factory = adapter_factory
    on_command.on(logger, task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=(
            ResultCode.FAILED,
            "On Command invocation"
            + f" failed on device: {sdp_master_device}."
            + " with exception:  Mock object has"
            + " no attribute 'On'",
        ),
        exception=(
            "On Command invocation"
            + f" failed on device: {sdp_master_device}."
            + " with exception:  Mock object has"
            + " no attribute 'On'"
        ),
    )


@pytest.mark.sdpmln
@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_on_command_is_not_allowed_device_unresponsive(
    tango_context, sdp_master_device
):
    cm = create_cm("SdpMLNComponentManager", sdp_master_device)
    cm._device = DeviceInfo(sdp_master_device, _unresponsive=True)
    pytest.raises(DeviceUnresponsive)


@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_on_fail_is_allowed(tango_context, sdp_master_device):
    logger.info("%s", tango_context)
    cm = create_cm("SdpMLNComponentManager", sdp_master_device)
    cm.op_state_model._op_state = DevState.FAULT
    with pytest.raises(CommandNotAllowed):
        cm.is_command_allowed("On")

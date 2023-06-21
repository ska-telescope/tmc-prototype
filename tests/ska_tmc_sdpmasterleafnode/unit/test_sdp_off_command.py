import logging

import pytest
from ska_tango_base.commands import ResultCode, TaskStatus
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.exceptions import CommandNotAllowed, DeviceUnresponsive
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)
from tango import DevState

from ska_tmc_sdpmasterleafnode.commands import Off
from tests.settings import (
    SDP_MASTER_DEVICE_LOW,
    SDP_MASTER_DEVICE_MID,
    create_cm,
    logger,
)


@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_off_command(tango_context, sdp_master_device, task_callback):
    cm, _ = create_cm("SdpMLNComponentManager", sdp_master_device)
    assert cm.is_command_allowed("Off")
    cm.submit_off_command(task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.QUEUED}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.COMPLETED, "result": ResultCode.OK}
    )


@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_off_command_fail_sdp_master(
    tango_context, sdp_master_device, task_callback, caplog
):
    cm, _ = create_cm("SdpMLNComponentManager", sdp_master_device)
    adapter_factory = HelperAdapterFactory()
    cm.sdp_master_dev_name = sdp_master_device
    # include exception in Off command
    adapter_factory.get_or_create_adapter(
        sdp_master_device, attrs={"Off.side_effect": Exception}
    )
    off_command = Off(cm, logger)
    off_command.adapter_factory = adapter_factory
    off_command.off(logger, task_callback=task_callback)
    caplog.set_level(logging.DEBUG, logger="ska_tango_testing.mock")
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED, result=ResultCode.FAILED
    )


@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_off_command_is_not_allowed_device_unresponsive(
    tango_context, sdp_master_device
):
    cm, _ = create_cm("SdpMLNComponentManager", sdp_master_device)
    cm._device = DeviceInfo(sdp_master_device, _unresponsive=True)
    pytest.raises(DeviceUnresponsive)


@pytest.mark.parametrize(
    "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
)
def test_off_fail_is_allowed(tango_context, sdp_master_device):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", sdp_master_device)
    cm.op_state_model._op_state = DevState.FAULT
    with pytest.raises(CommandNotAllowed):
        cm.is_command_allowed("Off")

import pytest
from ska_tango_base.commands import ResultCode, TaskStatus
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from src.ska_tmc_sdpsubarrayleafnode.commands import ReleaseAllResources
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.releasetest
@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_release_resources_command(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", devices)
    assert cm.is_command_allowed("ReleaseAllResources")

    cm.submit_release_resource(task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.QUEUED}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.COMPLETED, "result": ResultCode.OK}
    )


@pytest.mark.releasetest1
@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_release_resources_command_fail_subarray(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()
    failing_dev = devices

    # include exception in ReleaseAllResources command
    adapter_factory.get_or_create_adapter(
        failing_dev,
        AdapterType.SUBARRAY,
        attrs={"ReleaseAllResources.side_effect": Exception},
    )
    # cm.update_device_obs_state(ObsState.IDLE)
    release_command = ReleaseAllResources(cm, logger)
    release_command.adapter_factory = adapter_factory
    release_command.release_resources(logger, task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED, result=ResultCode.FAILED
    )


@pytest.mark.releasetest
@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_release_resources_command_fail_check_allowed_with_invalid_obsState(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm, release_command, _ = get_sdpsln_command_obj(
        ReleaseAllResources, devices, obsstate_value=ObsState.READY
    )
    with pytest.raises(InvalidObsStateError):
        cm.is_command_allowed("ReleaseAllResources")


@pytest.mark.releasetest
@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_release_resources_fail_check_allowed_with_device_unresponsive(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm.is_command_allowed("ReleaseAllResources")

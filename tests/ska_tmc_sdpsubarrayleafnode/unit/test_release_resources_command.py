import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import ReleaseResources
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_release_resources_command(tango_context, devices):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    cm, release_command, adapter_factory = get_sdpsln_command_obj(
        ReleaseResources, devices, obsstate_value=ObsState.IDLE
    )
    cm.get_device().obs_state == ObsState.EMPTY
    assert release_command.check_allowed()
    (result_code, _) = release_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(devices)
    adapter.proxy.ReleaseAllResources.assert_called()


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_release_resources_command_fail_subarray(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", devices)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", cm.get_device().dev_name, elapsed_time
    )

    adapter_factory = HelperAdapterFactory()

    # include exception in ReleaseResources command
    cm.update_device_obs_state(ObsState.IDLE)
    adapter_factory.get_or_create_adapter(
        devices,
        attrs={"ReleaseAllResources.side_effect": Exception},
    )

    release_command = ReleaseResources(cm, cm.op_state_model, adapter_factory)
    assert release_command.check_allowed()
    (result_code, message) = release_command.do()
    assert result_code == ResultCode.FAILED
    assert devices in message


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_release_resources_command_fail_check_allowed_with_invalid_obsState(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm, release_command, _ = get_sdpsln_command_obj(
        ReleaseResources, devices, obsstate_value=ObsState.EMPTY
    )
    cm.get_device().update_unresponsive(False)
    with pytest.raises(
        InvalidObsStateError,
        match="ReleaseResources command is not allowed",
    ):
        release_command.check_allowed()


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_release_resources_fail_check_allowed_with_device_unresponsive(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm, release_command, _ = get_sdpsln_command_obj(
        ReleaseResources, devices, obsstate_value=ObsState.IDLE
    )
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(
        DeviceUnresponsive, match="SDP subarray device is not available"
    ):
        release_command.check_allowed()

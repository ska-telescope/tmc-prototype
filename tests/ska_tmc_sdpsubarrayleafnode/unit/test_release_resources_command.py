import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import ReleaseResources
from tests.settings import create_cm, get_sdpsln_command_obj, logger


@pytest.mark.sdpsln
def test_telescope_release_resources_command(
    tango_context, sdp_subarray_device
):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    cm, release_command, adapter_factory = get_sdpsln_command_obj(
        ReleaseResources, obsstate_value=ObsState.IDLE
    )
    cm.get_device().obs_state == ObsState.EMPTY
    assert release_command.check_allowed()
    (result_code, _) = release_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(sdp_subarray_device)
    adapter.proxy.ReleaseResources.assert_called()


@pytest.mark.sdpsln
def test_telescope_release_resources_command_fail_subarray(
    tango_context, sdp_subarray_device
):
    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", sdp_subarray_device)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", cm.get_device().dev_name, elapsed_time
    )

    adapter_factory = HelperAdapterFactory()

    # include exception in ReleaseResources command
    cm.update_device_obs_state(ObsState.IDLE)
    adapter_factory.get_or_create_adapter(
        sdp_subarray_device,
        attrs={"ReleaseAllResources.side_effect": Exception},
    )

    release_command = ReleaseResources(cm, cm.op_state_model, adapter_factory)
    assert release_command.check_allowed()
    (result_code, message) = release_command.do()
    assert result_code == ResultCode.FAILED
    assert sdp_subarray_device in message


@pytest.mark.sdpsln
def test_release_resources_command_fail_check_allowed_with_invalid_obsState(
    tango_context,
):
    logger.info("%s", tango_context)
    cm, release_command, _ = get_sdpsln_command_obj(
        ReleaseResources, obsstate_value=ObsState.EMPTY
    )
    cm.get_device().update_unresponsive(False)
    with pytest.raises(
        InvalidObsStateError,
        match="ReleaseResources command is not allowed",
    ):
        release_command.check_allowed()


@pytest.mark.sdpsln
def test_release_resources_fail_check_allowed_with_device_unresponsive(
    tango_context,
):
    logger.info("%s", tango_context)
    cm, release_command, _ = get_sdpsln_command_obj(
        ReleaseResources, obsstate_value=ObsState.IDLE
    )
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(
        DeviceUnresponsive, match="SDP subarray device is not available"
    ):
        release_command.check_allowed()

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import (
    COMMAND_COMPLETED,
    SDPSUBARRAYLEAFNODE_LOW,
    SDPSUBARRAYLEAFNODE_MID,
)
from tests.settings import logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def release_resources(
    sdpsaln_name, device, json_factory, change_event_callbacks
):
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_name)
    sdp_subarray = dev_factory.get_device(device)
    lrcr_id = sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    obsstate_id = sdp_subarray_ln_proxy.subscribe_event(
        "sdpSubarrayObsState",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["sdpSubarrayObsState"],
    )
    try:
        result, unique_id = sdp_subarray_ln_proxy.On()
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], COMMAND_COMPLETED),
            lookahead=3,
        )
        assign_input_str = json_factory("command_AssignResources")
        result, unique_id = sdp_subarray_ln_proxy.AssignResources(
            assign_input_str
        )
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], COMMAND_COMPLETED),
            lookahead=4,
        )
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.IDLE,
            lookahead=4,
        )

        result, unique_id = sdp_subarray_ln_proxy.ReleaseAllResources()
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], COMMAND_COMPLETED),
            lookahead=4,
        )
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.EMPTY,
            lookahead=4,
        )

        sdp_subarray_ln_proxy.unsubscribe_event(lrcr_id)
        sdp_subarray_ln_proxy.unsubscribe_event(obsstate_id)
        tear_down(
            dev_factory,
            sdp_subarray,
            sdp_subarray_ln_proxy,
            change_event_callbacks,
        )

    except Exception as exception:
        sdp_subarray_ln_proxy.unsubscribe_event(lrcr_id)
        sdp_subarray_ln_proxy.unsubscribe_event(obsstate_id)
        tear_down(
            dev_factory,
            sdp_subarray,
            sdp_subarray_ln_proxy,
            change_event_callbacks,
        )

        raise Exception(exception)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    "device",
    [("mid-sdp/subarray/01")],
)
def test_release_res_command_mid(device, json_factory, change_event_callbacks):
    return release_resources(
        SDPSUBARRAYLEAFNODE_MID,
        device,
        json_factory,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
@pytest.mark.parametrize(
    "device",
    [("low-sdp/subarray/01")],
)
def test_release_res_command_low(
    device,
    json_factory,
    change_event_callbacks,
):
    return release_resources(
        SDPSUBARRAYLEAFNODE_LOW,
        device,
        json_factory,
        change_event_callbacks,
    )

"""Test cases for testing timeout on Configure command."""
from typing import Callable

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import COMMAND_COMPLETED, TIMEOUT_EXCEPTION
from tests.settings import (
    CONFIGURE_TIMEOUT,
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    SDP_SUBARRAY_LEAF_NODE_LOW,
    SDP_SUBARRAY_LEAF_NODE_MID,
    logger,
)
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def configure_timeout(
    sdpsaln_name: str,
    device: str,
    json_factory: Callable,
    change_event_callbacks: dict,
):
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_name)
    sdp_subarray = dev_factory.get_device(device)
    try:
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

        result, unique_id = sdp_subarray_ln_proxy.On()
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], COMMAND_COMPLETED),
            lookahead=4,
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

        sdp_subarray.SetDelayInfo(CONFIGURE_TIMEOUT)
        configure_input_str = json_factory("command_Configure")

        result, unique_id = sdp_subarray_ln_proxy.Configure(
            configure_input_str
        )

        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (
                unique_id[0],
                TIMEOUT_EXCEPTION,
            ),
            lookahead=3,
        )
        sdp_subarray.ResetDelayInfo()
        tear_down(
            dev_factory,
            sdp_subarray,
            sdp_subarray_ln_proxy,
            change_event_callbacks,
        )
        sdp_subarray_ln_proxy.unsubscribe_event(lrcr_id)
        sdp_subarray_ln_proxy.unsubscribe_event(obsstate_id)
        sdp_subarray.ClearCommandCallInfo()

    except Exception as exception:
        tear_down(
            dev_factory,
            sdp_subarray,
            sdp_subarray_ln_proxy,
            change_event_callbacks,
        )
        sdp_subarray.ResetDelayInfo()
        sdp_subarray_ln_proxy.unsubscribe_event(lrcr_id)
        sdp_subarray_ln_proxy.unsubscribe_event(obsstate_id)
        sdp_subarray.ClearCommandCallInfo()
        raise Exception(exception)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_configure_command_timeout_mid(json_factory, change_event_callbacks):
    return configure_timeout(
        SDP_SUBARRAY_LEAF_NODE_MID,
        SDP_SUBARRAY_DEVICE_MID,
        json_factory,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_lowm
def test_configure_command_timeout_low(json_factory, change_event_callbacks):
    return configure_timeout(
        SDP_SUBARRAY_LEAF_NODE_LOW,
        SDP_SUBARRAY_DEVICE_LOW,
        json_factory,
        change_event_callbacks,
    )

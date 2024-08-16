"""Test cases for testing timeout on assignResources."""
import json

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    SDP_SUBARRAY_LEAF_NODE_LOW,
    SDP_SUBARRAY_LEAF_NODE_MID,
    event_remover,
    logger,
)
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def assign_resources_timeout(
    sdpsln_name,
    assign_input_str,
    change_event_callbacks,
) -> None:
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsln_name)
    if sdpsln_name == SDP_SUBARRAY_LEAF_NODE_MID:
        sdp_subarray = dev_factory.get_device(SDP_SUBARRAY_DEVICE_MID)
    elif sdpsln_name == SDP_SUBARRAY_LEAF_NODE_LOW:
        sdp_subarray = dev_factory.get_device(SDP_SUBARRAY_DEVICE_LOW)
    sdp_subarray.SetDelayInfo(json.dumps({"AssignResources": 35}))
    # AssignResources
    result, unique_id = sdpsal_node.AssignResources(assign_input_str)
    logger.info(
        f"AssignResources Command ID: {unique_id} \
            ResultCode received: {result}"
    )
    obsstate_id = sdpsal_node.subscribe_event(
        "sdpSubarrayObsState",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["sdpSubarrayObsState"],
    )

    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED

    lrcr_id = sdpsal_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], '[3, "Timeout has occurred, command failed"]'),
        lookahead=3,
    )

    sdp_subarray.ResetDelayInfo()

    event_remover(
        change_event_callbacks,
        [
            "longRunningCommandResult",
            "longRunningCommandsInQueue",
            "sdpSubarrayObsState",
        ],
    )

    tear_down(dev_factory, sdp_subarray, sdpsal_node, change_event_callbacks)
    sdpsal_node.unsubscribe_event(lrcr_id)
    sdpsal_node.unsubscribe_event(obsstate_id)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_assign_resources_command_timeout_mid(
    json_factory,
    change_event_callbacks,
):
    return assign_resources_timeout(
        SDP_SUBARRAY_LEAF_NODE_MID,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_assign_resources_command_timeout_low(
    json_factory,
    change_event_callbacks,
):
    return assign_resources_timeout(
        SDP_SUBARRAY_LEAF_NODE_LOW,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )

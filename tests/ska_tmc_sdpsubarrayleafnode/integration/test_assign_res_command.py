import time

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import SLEEP_TIME, TIMEOUT, logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def assign_resouces(
    tango_context,
    sdpsaln_name,
    sdp_subarray,
    json_factory,
    change_event_callbacks,
):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsaln_name)
    sdp_subarray = dev_factory.get_device(sdp_subarray)

    initial_len = len(sdpsal_node.commandExecuted)
    (result, unique_id) = sdpsal_node.On()
    assign_input_str = json_factory("command_AssignResources")
    assert sdpsal_node.sdpSubarrayObsState == ObsState.EMPTY
    (result, unique_id) = sdpsal_node.AssignResources(assign_input_str)
    assert result[0] == ResultCode.QUEUED
    sdpsal_node.subscribe_event(
        "sdpSubarrayObsState",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["sdpSubarrayObsState"],
    )
    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.IDLE,
        lookahead=4,
    )
    start_time = time.time()
    while len(sdpsal_node.commandExecuted) != initial_len + 2:
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")

    for command in sdpsal_node.commandExecuted:
        if command[0] == unique_id[0]:
            logger.info("command result: %s", command)
            assert command[2] == "ResultCode.STARTED"

    tear_down(dev_factory, sdp_subarray)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    ["sdpsaln_name", "sdp_subarray"],
    [("ska_mid/tm_leaf_node/sdp_subarray01", "mid-sdp/subarray/01")],
)
def test_assign_res_command_mid(
    tango_context,
    sdpsaln_name,
    sdp_subarray,
    json_factory,
    change_event_callbacks,
):
    return assign_resouces(
        tango_context,
        sdpsaln_name,
        sdp_subarray,
        json_factory,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
@pytest.mark.parametrize(
    ["sdpsaln_name", "sdp_subarray"],
    [("ska_low/tm_leaf_node/sdp_subarray01", "low-sdp/subarray/01")],
)
def test_assign_res_command_low(
    tango_context,
    sdpsaln_name,
    sdp_subarray,
    json_factory,
    change_event_callbacks,
):
    return assign_resouces(
        tango_context,
        sdpsaln_name,
        sdp_subarray,
        json_factory,
        change_event_callbacks,
    )

import time

import pytest
import tango
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def assign_resources_error_propagation(
    tango_context, sdpsln_name, assign_input_str, change_event_callbacks
) -> None:

    dev_factory = DevFactory()
    sdpsln_device = dev_factory.get_device(sdpsln_name)

    if "mid" in sdpsln_name:
        sdp_subarray = dev_factory.get_device("mid-sdp/subarray/01")
    else:
        sdp_subarray = dev_factory.get_device("low-sdp/subarray/01")
    sdp_subarray.SetDirectObsState(ObsState.EMPTY)
    assert sdp_subarray.obsState == ObsState.EMPTY

    result, unique_id = sdpsln_device.AssignResources(assign_input_str)
    logger.info(
        f"AssignResources Command ID: {unique_id} Returned result: {result}"
    )
    time.sleep(2)
    sdp_subarray.SetDirectObsState(ObsState.IDLE)
    assert sdp_subarray.obsState == ObsState.IDLE

    sdpsln_device.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (
            unique_id[0],
            "eb_id not found in the input json string",
        ),
        lookahead=5,
    )
    time.sleep(2)
    tear_down(dev_factory, sdp_subarray)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_assign_resources_error_propagation(
    tango_context, json_factory, change_event_callbacks
):
    return assign_resources_error_propagation(
        tango_context,
        "ska_mid/tm_leaf_node/sdp_subarray01",
        json_factory("command_AssignResources_without_ebid"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_assign_resources_error_propagation_low(
    tango_context, json_factory, change_event_callbacks
):
    return assign_resources_error_propagation(
        tango_context,
        "ska_low/tm_leaf_node/sdp_subarray01",
        json_factory("command_AssignResources_without_ebid"),
        change_event_callbacks,
    )

import time

import pytest
import tango
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def assign_resources_timeout(
    tango_context, sdpsln_name, assign_input_str, change_event_callbacks
) -> None:
    dev_factory = DevFactory()
    sdpsln_device = dev_factory.get_device(sdpsln_name)

    if "mid" in sdpsln_name:
        sdp_subarray = dev_factory.get_device("mid-sdp/subarray/01")
    else:
        sdp_subarray = dev_factory.get_device("low-sdp/subarray/01")

    sdp_subarray.SetDefective(True)

    result, unique_id = sdpsln_device.AssignResources(assign_input_str)
    logger.info(
        f"AssignResources Command ID: {unique_id} Returned result: {result}"
    )

    sdpsln_device.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        ("ResultCode.FAILED", "Timeout has occured, command failed"),
        lookahead=5,
    )

    sdp_subarray.SetDefective(False)
    time.sleep(2)

    tear_down(dev_factory, sdp_subarray)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_assign_resources_timeout(
    tango_context, json_factory, change_event_callbacks
):
    return assign_resources_timeout(
        tango_context,
        "ska_mid/tm_leaf_node/sdp_subarray01",
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_assign_resources_timeout_low(
    tango_context, json_factory, change_event_callbacks
):
    return assign_resources_timeout(
        tango_context,
        "ska_low/tm_leaf_node/sdp_subarray01",
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )

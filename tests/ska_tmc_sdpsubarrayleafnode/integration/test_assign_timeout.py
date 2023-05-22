import pytest
import tango
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
        (
            "ResultCode.FAILED",
            "eb_id not found in the input json string",
        ),
        lookahead=5,
    )

    tear_down(dev_factory, sdp_subarray)

def assign_resources_timeout(
    tango_context, sdpsln_name, assign_input_str, change_event_callbacks
) -> None:
    dev_factory = DevFactory()
    sdpsln_device = dev_factory.get_device(sdpsln_name)

    if "mid" in sdpsln_name:
        sdp_subarray = dev_factory.get_device("mid-sdp/subarray/01")
    else:
        sdp_subarray = dev_factory.get_device("low-sdp/subarray/01")
    logger.info(f"------------------------{sdp_subarray}")
    
    sdp_subarray.SetDefective(True)

    result, unique_id = sdpsln_device.AssignResources(assign_input_str)
    logger.info(
        f"AssignResources Command ID: {unique_id} Returned result: {result}"
    )

    # assert unique_id[0].endswith("AssignResources")
    # assert result[0] == ResultCode.QUEUED

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

    tear_down(dev_factory, sdp_subarray, sdpsal_node)

@pytest.mark.aki
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_assign_without_ebid_mid(
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
def test_assign_without_ebid_low(
    tango_context, json_factory, change_event_callbacks
):
    return assign_resources_error_propagation(
        tango_context,
        "ska_low/tm_leaf_node/sdp_subarray01",
        json_factory("command_AssignResources_without_ebid"),
        change_event_callbacks,
    )

@pytest.mark.akii
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

import pytest
import tango
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import (
    tear_down,
    wait_and_assert_sdp_subarray_obsstate,
)


def assign_resources_error_propagation(
    tango_context,
    sdpsln_name,
    invalid_assign_input_json,
    change_event_callbacks,
) -> None:
    dev_factory = DevFactory()
    sdpsln_device = dev_factory.get_device(sdpsln_name)

    if "mid" in sdpsln_name:
        sdp_subarray = dev_factory.get_device("mid-sdp/subarray/01")
    else:
        sdp_subarray = dev_factory.get_device("low-sdp/subarray/01")
    try:
        unique_id, result_code = sdpsln_device.AssignResources(
            invalid_assign_input_json
        )
        logger.info(
            f"AssignResources Command ID: {unique_id} Returned result:\
                {result_code}"
        )

        LRCR_ID = sdpsln_device.subscribe_event(
            "longRunningCommandResult",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (
                result_code[0],
                '[3, "Missing eb_id in the AssignResources input json"]',
            ),
            lookahead=2,
        )
        wait_and_assert_sdp_subarray_obsstate(sdpsln_device, ObsState.EMPTY)
        tear_down(dev_factory, sdp_subarray, sdpsln_name)
        sdpsln_device.unsubscribe_event(LRCR_ID)
    except Exception as exception:
        tear_down(dev_factory, sdp_subarray, sdpsln_name)
        sdpsln_device.unsubscribe_event(LRCR_ID)
        raise Exception(exception)


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

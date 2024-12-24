import pytest
import tango
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def assign_resources_error_propagation(
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

        lrcr_id = sdpsln_device.subscribe_event(
            "longRunningCommandResult",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )
        obsstate_id = sdpsln_device.subscribe_event(
            "sdpSubarrayObsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["sdpSubarrayObsState"],
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (
                result_code[0],
                '[3, "Missing eb_id in the AssignResources input json"]',
            ),
            lookahead=2,
        )
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.EMPTY,
            lookahead=4,
        )
        tear_down(
            dev_factory, sdp_subarray, sdpsln_device, change_event_callbacks
        )
        sdpsln_device.unsubscribe_event(lrcr_id)
        sdpsln_device.unsubscribe_event(obsstate_id)
        sdp_subarray.ClearCommandCallInfo()

    except Exception as exception:
        tear_down(
            dev_factory, sdp_subarray, sdpsln_device, change_event_callbacks
        )
        sdpsln_device.unsubscribe_event(lrcr_id)

        sdpsln_device.unsubscribe_event(obsstate_id)
        sdp_subarray.ClearCommandCallInfo()
        raise Exception(exception)


@pytest.mark.post_deployment
@pytest.mark.SKA_midm
def test_assign_resources_error_propagation(
    json_factory, change_event_callbacks
):
    return assign_resources_error_propagation(
        "ska_mid/tm_leaf_node/sdp_subarray01",
        json_factory("command_AssignResources_without_ebid"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_assign_resources_error_propagation_low(
    json_factory, change_event_callbacks
):
    return assign_resources_error_propagation(
        "ska_low/tm_leaf_node/sdp_subarray01",
        json_factory("command_AssignResources_without_ebid"),
        change_event_callbacks,
    )

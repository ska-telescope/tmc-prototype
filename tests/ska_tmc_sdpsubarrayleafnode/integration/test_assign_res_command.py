import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import (
    COMMAND_COMPLETED,
    LOW_SDP_SUBARRAY,
    MID_SDP_SUBARRAY,
    SDPSUBARRAYLEAFNODE_LOW,
    SDPSUBARRAYLEAFNODE_MID,
)
from tests.settings import logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def assign_resources(
    sdpsln_name,
    assign_input_str,
    change_event_callbacks,
) -> None:
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsln_name)
    if sdpsln_name == SDPSUBARRAYLEAFNODE_MID:
        sdp_subarray = dev_factory.get_device(MID_SDP_SUBARRAY)
    else:
        sdp_subarray = dev_factory.get_device(LOW_SDP_SUBARRAY)
    try:
        result, unique_id = sdpsal_node.AssignResources(assign_input_str)
        logger.info(
            f"AssignResources Command ID: {unique_id} Returned \
                result: {result}"
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
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.IDLE,
            lookahead=4,
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], COMMAND_COMPLETED),
            lookahead=4,
        )
        tear_down(
            dev_factory, sdp_subarray, sdpsal_node, change_event_callbacks
        )

        sdpsal_node.unsubscribe_event(lrcr_id)
        sdpsal_node.unsubscribe_event(obsstate_id)
    except Exception as exception:
        tear_down(
            dev_factory, sdp_subarray, sdpsal_node, change_event_callbacks
        )
        sdpsal_node.unsubscribe_event(lrcr_id)
        sdpsal_node.unsubscribe_event(obsstate_id)
        raise Exception(exception)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_assign_res_command_mid(
    json_factory,
    change_event_callbacks,
):
    return assign_resources(
        SDPSUBARRAYLEAFNODE_MID,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_assign_res_command_low(json_factory, change_event_callbacks):
    return assign_resources(
        SDPSUBARRAYLEAFNODE_LOW,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )

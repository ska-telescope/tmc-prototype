import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import (
    SDPSUBARRAYLEAFNODE_LOW,
    SDPSUBARRAYLEAFNODE_MID,
    LOW_SDP_SUBARRAY,
    MID_SDP_SUBARRAY,
)
from tests.settings import event_remover, logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def assign_resources(
    tango_context,
    sdpsln_name,
    assign_input_str,
    change_event_callbacks,
) -> None:
    logger.info(f"{tango_context}")
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsln_name)
    if sdpsln_name == SDPSUBARRAYLEAFNODE_MID:
        sdp_subarray = dev_factory.get_device(MID_SDP_SUBARRAY)
    else:
        sdp_subarray = dev_factory.get_device(LOW_SDP_SUBARRAY)
    result, unique_id = sdpsal_node.AssignResources(assign_input_str)
    logger.info(
        f"AssignResources Command ID: {unique_id} Returned result: {result}"
    )

    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED

    sdpsal_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], str(ResultCode.OK.value)),
        lookahead=4,
    )
    event_remover(
        change_event_callbacks,
        ["longRunningCommandResult"],
    )
    tear_down(dev_factory, sdp_subarray)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_assign_res_command_mid(
    tango_context,
    json_factory,
    change_event_callbacks,
):
    return assign_resources(
        tango_context,
        SDPSUBARRAYLEAFNODE_MID,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_assign_res_command_low(
    tango_context, json_factory, change_event_callbacks
):
    return assign_resources(
        tango_context,
        SDPSUBARRAYLEAFNODE_LOW,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import (
    LOW_SDP_SUBARRAY,
    MID_SDP_SUBARRAY,
    SDPSUBARRAYLEAFNODE_LOW,
    SDPSUBARRAYLEAFNODE_MID,
)
from tests.settings import event_remover, logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import (
    tear_down,
    wait_and_assert_sdp_subarray_obsstate,
)


def assign_resources(
    tango_context,
    sdpsln_name,
    assign_input_str,
    change_event_callbacks,
) -> None:
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsln_name)
    event_remover(
        change_event_callbacks,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )
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

        assert unique_id[0].endswith("AssignResources")
        assert result[0] == ResultCode.QUEUED

        sdpsal_node.subscribe_event(
            "longRunningCommandResult",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )
        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(ResultCode.OK.value)),
            lookahead=2,
        )
        wait_and_assert_sdp_subarray_obsstate(sdpsal_node, ObsState.IDLE)
        event_remover(
            change_event_callbacks,
            ["longRunningCommandResult", "longRunningCommandsInQueue"],
        )
        tear_down(dev_factory, sdp_subarray, sdpsal_node)
    except Exception as e:
        tear_down(dev_factory, sdp_subarray, sdpsal_node)
        raise Exception(e)


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

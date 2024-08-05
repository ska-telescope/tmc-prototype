# TODO: This test needs to be refactored separately as we don't have a way to
# raise and exception in ReleaseAllResources command.
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
from tests.settings import (  # ERROR_PROPAGATION_DEFECT,
    ERROR_PROPAGATION_DEFECT,
    RESET_DEFECT,
    TIMEOUT_DEFECT,
    event_remover,
    logger,
)
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import (
    tear_down,
    wait_and_assert_sdp_subarray_obsstate,
)


def release_all_resources_error_propagation(
    tango_context,
    device,
    assign_input_str,
    change_event_callbacks,
) -> None:
    dev_factory = DevFactory()

    if device == MID_SDP_SUBARRAY:
        sdpsal_node = dev_factory.get_device(SDPSUBARRAYLEAFNODE_MID)
        sdp_subarray = dev_factory.get_device(MID_SDP_SUBARRAY)
    elif device == LOW_SDP_SUBARRAY:
        sdpsal_node = dev_factory.get_device(SDPSUBARRAYLEAFNODE_LOW)
        sdp_subarray = dev_factory.get_device(LOW_SDP_SUBARRAY)

    # AssignResources
    result, unique_id = sdpsal_node.AssignResources(assign_input_str)
    logger.info(
        f"AssignResources Command ID: {unique_id} \
            ResultCode received: {result}"
    )

    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED

    sdpsal_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=4,
    )

    wait_and_assert_sdp_subarray_obsstate(sdpsal_node, ObsState.IDLE)

    # Check error propagation
    sdp_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    result, unique_id = sdpsal_node.ReleaseAllResources()

    logger.info(
        "ReleaseAllResources Command ID: "
        + f"{unique_id} ResultCode received: {result}"
    )

    assert unique_id[0].endswith("ReleaseAllResources")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (
            unique_id[0],
            "ska_tmc_common.exceptions.CommandNotAllowed: Exception occured,"
            + " command failed.\n",
        ),
        lookahead=6,
    )

    sdp_subarray.SetDefective(RESET_DEFECT)
    event_remover(
        change_event_callbacks,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )
    tear_down(dev_factory, sdp_subarray, sdpsal_node)


def release_all_resources_timeout(
    tango_context,
    sdpsln_name,
    assign_input_str,
    change_event_callbacks,
) -> None:
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsln_name)

    if sdpsln_name == SDPSUBARRAYLEAFNODE_MID:
        sdp_subarray = dev_factory.get_device(MID_SDP_SUBARRAY)
    elif sdpsln_name == SDPSUBARRAYLEAFNODE_LOW:
        sdp_subarray = dev_factory.get_device(LOW_SDP_SUBARRAY)

    # AssignResources
    result, unique_id = sdpsal_node.AssignResources(assign_input_str)
    logger.info(
        f"AssignResources Command ID: {unique_id} \
            ResultCode received: {result}"
    )

    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED

    sdpsal_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=4,
    )
    wait_and_assert_sdp_subarray_obsstate(sdpsal_node, ObsState.IDLE)

    # Check timeout
    sdp_subarray.SetDefective(TIMEOUT_DEFECT)
    logger.info("defect set")
    result, unique_id = sdpsal_node.ReleaseAllResources()

    logger.info(
        f"ReleaseAllResources Command ID: \
            {unique_id} ResultCode received: {result}"
    )

    assert unique_id[0].endswith("ReleaseAllResources")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (
            unique_id[0],
            "Timeout has occurred, command failed",
        ),
        lookahead=6,
    )
    sdp_subarray.SetDefective(RESET_DEFECT)

    event_remover(
        change_event_callbacks,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )

    tear_down(dev_factory, sdp_subarray, sdpsal_node)


# @pytest.mark.skip(reason="pipeline failure")
@pytest.mark.t1
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_release_all_res_command_timeout_mid(
    tango_context,
    json_factory,
    change_event_callbacks,
):
    return release_all_resources_timeout(
        tango_context,
        SDPSUBARRAYLEAFNODE_MID,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


# @pytest.mark.skip(reason="pipeline failure")
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_release_all_res_command_error_propagation_mid(
    tango_context,
    json_factory,
    change_event_callbacks,
):
    return release_all_resources_error_propagation(
        tango_context,
        MID_SDP_SUBARRAY,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.skip(reason="pipeline failure")
@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_release_all_res_command_timeout_low(
    tango_context, json_factory, change_event_callbacks
):
    return release_all_resources_timeout(
        tango_context,
        SDPSUBARRAYLEAFNODE_LOW,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.skip(reason="pipeline failure")
@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_release_all_res_command_error_propagation_low(
    tango_context, json_factory, change_event_callbacks
):
    return release_all_resources_error_propagation(
        tango_context,
        LOW_SDP_SUBARRAY,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )

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
    TIMEOUT_EXCEPTION,
)
from tests.settings import (
    FAILED_RESULT_DEFECT,
    RELEASE_TIMEOUT,
    RESET_DEFECT,
    logger,
    wait_for_attribute_to_change_to,
)
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def release_all_resources_error_propagation(
    device: str,
    assign_input_str: str,
    change_event_callbacks: dict,
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

    lrcr_id = sdpsal_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    obsstate_id = sdpsal_node.subscribe_event(
        "sdpSubarrayObsState",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["sdpSubarrayObsState"],
    )

    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.IDLE,
        lookahead=4,
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=4,
    )
    # Check error propagation
    sdp_subarray.SetDefective(FAILED_RESULT_DEFECT)
    wait_for_attribute_to_change_to(
        sdp_subarray, "defective", FAILED_RESULT_DEFECT
    )
    result, unique_id = sdpsal_node.ReleaseAllResources()

    logger.info(
        "ReleaseAllResources Command ID: "
        + f"{unique_id} ResultCode received: {result}"
    )

    assert unique_id[0].endswith("ReleaseAllResources")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], '[3, "Exception occurred, command failed"]'),
        lookahead=6,
    )
    sdp_subarray.SetDefective(RESET_DEFECT)
    wait_for_attribute_to_change_to(sdp_subarray, "defective", RESET_DEFECT)
    tear_down(dev_factory, sdp_subarray, sdpsal_node, change_event_callbacks)
    sdpsal_node.unsubscribe_event(lrcr_id)
    sdpsal_node.unsubscribe_event(obsstate_id)


def release_all_resources_timeout(
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

    lrcr_id = sdpsal_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    obsstate_id = sdpsal_node.subscribe_event(
        "sdpSubarrayObsState",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["sdpSubarrayObsState"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=4,
    )
    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.IDLE,
        lookahead=4,
    )

    sdp_subarray.SetDelayInfo(RELEASE_TIMEOUT)
    result, unique_id = sdpsal_node.ReleaseAllResources()

    logger.info(
        f"ReleaseAllResources Command ID: \
            {unique_id} ResultCode received: {result}"
    )

    assert unique_id[0].endswith("ReleaseAllResources")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], TIMEOUT_EXCEPTION),
        lookahead=3,
    )
    sdp_subarray.ResetDelayInfo()
    tear_down(dev_factory, sdp_subarray, sdpsal_node, change_event_callbacks)
    sdpsal_node.unsubscribe_event(lrcr_id)
    sdpsal_node.unsubscribe_event(obsstate_id)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_release_all_resources_command_timeout_mid(
    json_factory,
    change_event_callbacks,
):
    return release_all_resources_timeout(
        SDPSUBARRAYLEAFNODE_MID,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_release_all_resources_command_error_propagation_mid(
    json_factory,
    change_event_callbacks,
):
    return release_all_resources_error_propagation(
        MID_SDP_SUBARRAY,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_release_all_res_command_timeout_low(
    json_factory, change_event_callbacks
):
    return release_all_resources_timeout(
        SDPSUBARRAYLEAFNODE_LOW,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_release_all_res_command_error_propagation_low(
    json_factory, change_event_callbacks
):
    return release_all_resources_error_propagation(
        LOW_SDP_SUBARRAY,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )

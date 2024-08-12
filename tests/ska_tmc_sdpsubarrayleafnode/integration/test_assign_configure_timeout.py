import json

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import COMMAND_COMPLETED
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    SDP_SUBARRAY_LEAF_NODE_LOW,
    SDP_SUBARRAY_LEAF_NODE_MID,
    event_remover,
    logger,
)
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import (
    tear_down,
    wait_and_assert_sdp_subarray_obsstate,
)


def assign_resources_timeout(
    tango_context,
    sdpsln_name,
    assign_input_str,
    change_event_callbacks,
) -> None:
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsln_name)
    if sdpsln_name == SDP_SUBARRAY_LEAF_NODE_MID:
        sdp_subarray = dev_factory.get_device(SDP_SUBARRAY_DEVICE_MID)
    elif sdpsln_name == SDP_SUBARRAY_LEAF_NODE_LOW:
        sdp_subarray = dev_factory.get_device(SDP_SUBARRAY_DEVICE_LOW)
    sdp_subarray.SetDelayInfo(json.dumps({"AssignResources": 35}))
    # AssignResources
    result, unique_id = sdpsal_node.AssignResources(assign_input_str)
    logger.info(
        f"AssignResources Command ID: {unique_id} \
            ResultCode received: {result}"
    )

    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED

    LRCR_ID = sdpsal_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], '[3, "Timeout has occurred, command failed"]'),
        lookahead=3,
    )

    sdp_subarray.ResetDelayInfo()

    event_remover(
        change_event_callbacks,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )
    sdpsal_node.unsubscribe_event(LRCR_ID)
    tear_down(dev_factory, sdp_subarray, sdpsal_node)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_release_all_res_command_timeout_mid(
    tango_context,
    json_factory,
    change_event_callbacks,
):
    return assign_resources_timeout(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_MID,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_release_all_res_command_timeout_low(
    tango_context,
    json_factory,
    change_event_callbacks,
):
    return assign_resources_timeout(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_LOW,
        json_factory("command_AssignResources"),
        change_event_callbacks,
    )


def configure_timeout(
    tango_context, sdpsaln_name, device, json_factory, change_event_callbacks
):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_name)
    sdp_subarray = dev_factory.get_device(device)
    try:
        event_remover(
            change_event_callbacks,
            ["longRunningCommandResult", "longRunningCommandsInQueue"],
        )
        LRCR_QUE_ID = sdp_subarray_ln_proxy.subscribe_event(
            "longRunningCommandsInQueue",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandsInQueue"],
        )

        LRCR_ID = sdp_subarray_ln_proxy.subscribe_event(
            "longRunningCommandResult",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(
            (),
        )
        result, unique_id = sdp_subarray_ln_proxy.On()
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(("On",), lookahead=2)

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], COMMAND_COMPLETED),
            lookahead=4,
        )
        assign_input_str = json_factory("command_AssignResources")
        result, unique_id = sdp_subarray_ln_proxy.AssignResources(
            assign_input_str
        )
        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(
            (
                "On",
                "AssignResources",
            ),
            lookahead=2,
        )
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], COMMAND_COMPLETED),
            lookahead=4,
        )
        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.IDLE
        )
        sdp_subarray.SetDelayInfo(json.dumps({"Configure": 35}))
        configure_input_str = json_factory("command_Configure")

        result, unique_id = sdp_subarray_ln_proxy.Configure(
            configure_input_str
        )

        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], '[3, "Timeout has occurred, command failed"]'),
            lookahead=3,
        )
        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.READY
        )

        event_remover(
            change_event_callbacks,
            ["longRunningCommandResult", "longRunningCommandsInQueue"],
        )
        sdp_subarray.ResetDelayInfo()
        tear_down(dev_factory, sdp_subarray, sdp_subarray_ln_proxy)
        sdp_subarray_ln_proxy.unsubscribe_event(LRCR_QUE_ID)
        sdp_subarray_ln_proxy.unsubscribe_event(LRCR_ID)

    except Exception as exception:
        tear_down(dev_factory, sdp_subarray, sdp_subarray_ln_proxy)
        sdp_subarray.ResetDelayInfo()
        sdp_subarray_ln_proxy.unsubscribe_event(LRCR_QUE_ID)
        sdp_subarray_ln_proxy.unsubscribe_event(LRCR_ID)
        raise Exception(exception)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_configure_command_timeout_mid(
    tango_context, json_factory, change_event_callbacks
):
    return configure_timeout(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_MID,
        SDP_SUBARRAY_DEVICE_MID,
        json_factory,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_configure_command_timeout_low(
    tango_context, json_factory, change_event_callbacks
):
    return configure_timeout(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_LOW,
        SDP_SUBARRAY_DEVICE_LOW,
        json_factory,
        change_event_callbacks,
    )

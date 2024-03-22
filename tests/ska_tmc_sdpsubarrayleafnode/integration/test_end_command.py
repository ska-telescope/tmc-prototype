import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

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


def end(
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
        sdp_subarray_ln_proxy.subscribe_event(
            "longRunningCommandsInQueue",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandsInQueue"],
        )

        sdp_subarray_ln_proxy.subscribe_event(
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
        ].assert_change_event(
            ("On",),
            lookahead=1,
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(int(ResultCode.OK))),
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

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(int(ResultCode.OK))),
            lookahead=4,
        )
        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.IDLE
        )

        configure_input_str = json_factory("command_Configure")
        result, unique_id = sdp_subarray_ln_proxy.Configure(
            configure_input_str
        )
        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(
            (
                "On",
                "AssignResources",
                "Configure",
            ),
            lookahead=2,
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(int(ResultCode.OK))),
            lookahead=3,
        )
        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.READY
        )

        result, unique_id = sdp_subarray_ln_proxy.End()
        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(
            (
                "On",
                "AssignResources",
                "Configure",
                "End",
            ),
            lookahead=3,
        )

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(int(ResultCode.OK))),
            lookahead=4,
        )
        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.IDLE
        )
        event_remover(
            change_event_callbacks,
            ["longRunningCommandResult", "longRunningCommandsInQueue"],
        )
        tear_down(dev_factory, sdp_subarray, sdp_subarray_ln_proxy)
    except Exception as exception:
        tear_down(dev_factory, sdp_subarray, sdp_subarray_ln_proxy)
        raise Exception(exception)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_end_command_mid(tango_context, json_factory, change_event_callbacks):
    return end(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_MID,
        SDP_SUBARRAY_DEVICE_MID,
        json_factory,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_end_command_low(
    tango_context,
    json_factory,
    change_event_callbacks,
):
    return end(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_LOW,
        SDP_SUBARRAY_DEVICE_LOW,
        json_factory,
        change_event_callbacks,
    )

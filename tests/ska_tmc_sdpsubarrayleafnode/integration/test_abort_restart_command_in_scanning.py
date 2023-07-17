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


def scanning_abort_restart_command(
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
            None,
        )
        result, unique_id = sdp_subarray_ln_proxy.On()
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(
            ("On",),
        )
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

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
        )
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

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
        )
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(int(ResultCode.OK))),
            lookahead=4,
        )
        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.READY
        )

        scan_input_str = json_factory("command_Scan")
        result, unique_id = sdp_subarray_ln_proxy.Scan(scan_input_str)
        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(
            (
                "On",
                "AssignResources",
                "Configure",
                "Scan",
            ),
        )
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], str(int(ResultCode.OK))),
            lookahead=6,
        )
        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.SCANNING
        )

        result, unique_id = sdp_subarray_ln_proxy.Abort()
        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.ABORTED
        )
        sdp_subarray_node_obs_state = sdp_subarray.read_attribute(
            "obsState"
        ).value
        assert sdp_subarray_node_obs_state == ObsState.ABORTED

        result, unique_id = sdp_subarray_ln_proxy.Restart()
        assert unique_id[0].endswith("Restart")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (unique_id[0], str(ResultCode.OK.value)),
            lookahead=6,
        )

        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.EMPTY
        )
        sdp_subarray_node_obs_state = sdp_subarray.read_attribute(
            "obsState"
        ).value
        assert sdp_subarray_node_obs_state == ObsState.EMPTY
        event_remover(
            change_event_callbacks,
            ["longRunningCommandResult", "longRunningCommandsInQueue"],
        )
        tear_down(dev_factory, sdp_subarray, sdp_subarray_ln_proxy)
    except Exception as e:
        tear_down(dev_factory, sdp_subarray, sdp_subarray_ln_proxy)
        raise Exception(e)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_scanning_abort_restart_command_mid(
    tango_context, json_factory, change_event_callbacks
):
    return scanning_abort_restart_command(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_MID,
        SDP_SUBARRAY_DEVICE_MID,
        json_factory,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_scanning_abort_restart_command_low(
    tango_context,
    json_factory,
    change_event_callbacks,
):
    return scanning_abort_restart_command(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_LOW,
        SDP_SUBARRAY_DEVICE_LOW,
        json_factory,
        change_event_callbacks,
    )

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
    logger,
)
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import (
    set_sdp_subarray_obsstate,
    tear_down,
    wait_and_assert_sdp_subarray_obsstate,
)

device_obsstate = [
    ObsState.RESOURCING,
    ObsState.IDLE,
    ObsState.CONFIGURING,
    ObsState.READY,
    ObsState.SCANNING,
]


def abort_restart_command(
    tango_context,
    sdpsaln_name,
    sdp_subarray_device,
    obsstate,
    change_event_callbacks,
):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_name)
    sdp_subarray = dev_factory.get_device(sdp_subarray_device)
    try:
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
        set_sdp_subarray_obsstate(dev_factory, obsstate, sdp_subarray)
        wait_and_assert_sdp_subarray_obsstate(sdp_subarray_ln_proxy, obsstate)
        result, unique_id = sdp_subarray_ln_proxy.Abort()

        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.ABORTED
        )
        result, unique_id = sdp_subarray_ln_proxy.Restart()
        assert unique_id[0].endswith("Restart")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (unique_id[0], COMMAND_COMPLETED),
            lookahead=6,
        )

        wait_and_assert_sdp_subarray_obsstate(
            sdp_subarray_ln_proxy, ObsState.EMPTY
        )

        sdp_subarray_ln_proxy.unsubscribe_event(LRCR_QUE_ID)
        sdp_subarray_ln_proxy.unsubscribe_event(LRCR_ID)

    except Exception as exception:
        tear_down(dev_factory, sdp_subarray, sdp_subarray_ln_proxy)
        raise Exception(exception)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize("obsstate", device_obsstate)
def test_abort_restart_command_mid(
    tango_context, obsstate, change_event_callbacks
):
    return abort_restart_command(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_MID,
        SDP_SUBARRAY_DEVICE_MID,
        obsstate,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
@pytest.mark.parametrize("obsstate", device_obsstate)
def test_abort_restart_command_low(
    tango_context,
    obsstate,
    change_event_callbacks,
):
    return abort_restart_command(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_LOW,
        SDP_SUBARRAY_DEVICE_LOW,
        obsstate,
        change_event_callbacks,
    )

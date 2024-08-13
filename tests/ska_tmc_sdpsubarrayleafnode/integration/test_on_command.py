import pytest
import tango
from ska_tango_base.commands import ResultCode
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
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def on_command(
    tango_context, sdpsaln_fqdn, sdpsa_fqdn, change_event_callbacks
):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_fqdn)
    sdp_subarray_proxy = dev_factory.get_device(sdpsa_fqdn)
    try:
        lrcr_in_que_id = sdp_subarray_ln_proxy.subscribe_event(
            "longRunningCommandsInQueue",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandsInQueue"],
        )
        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(
            (),
        )
        result, unique_id = sdp_subarray_ln_proxy.On()
        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(
            ("On",),
        )
        logger.info(f"Command ID: {unique_id} Returned result: {result}")
        assert result[0] == ResultCode.QUEUED
        lrcr_id = sdp_subarray_ln_proxy.subscribe_event(
            "longRunningCommandResult",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )
        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], COMMAND_COMPLETED),
            lookahead=4,
        )

        change_event_callbacks[
            "longRunningCommandsInQueue"
        ].assert_change_event(
            (),
            lookahead=2,
        )
        event_remover(
            change_event_callbacks,
            ["longRunningCommandResult", "longRunningCommandsInQueue"],
        )
        sdp_subarray_ln_proxy.unsubscribe_event(lrcr_in_que_id)
        sdp_subarray_ln_proxy.unsubscribe_event(lrcr_id)
        tear_down(
            dev_factory,
            sdp_subarray_proxy,
            sdp_subarray_ln_proxy,
            change_event_callbacks,
        )
    except Exception as exception:
        sdp_subarray_ln_proxy.unsubscribe_event(lrcr_in_que_id)
        sdp_subarray_ln_proxy.unsubscribe_event(lrcr_id)
        tear_down(
            dev_factory,
            sdp_subarray_proxy,
            sdp_subarray_ln_proxy,
            change_event_callbacks,
        )
        raise Exception(exception)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_on_command_mid(tango_context, change_event_callbacks):
    on_command(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_MID,
        SDP_SUBARRAY_DEVICE_MID,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_on_command_low(tango_context, change_event_callbacks):
    on_command(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_LOW,
        SDP_SUBARRAY_DEVICE_LOW,
        change_event_callbacks,
    )

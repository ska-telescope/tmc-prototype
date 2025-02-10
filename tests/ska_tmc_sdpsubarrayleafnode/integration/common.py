import time

import pytest
from ska_tango_base.control_model import ObsState
from ska_tmc_common.test_helpers.helper_sdp_subarray import HelperSdpSubarray

from ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node import (
    SdpSubarrayLeafNode,
)
from tests.settings import logger

pytest.event_arrived = False


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": HelperSdpSubarray,
            "devices": [
                {"name": "mid-sdp/subarray/01"},
            ],
        },
        {
            "class": SdpSubarrayLeafNode,
            "devices": [
                {
                    "name": "mid-tmc/leaf-node-sdp/0",
                    "properties": {
                        "SdpSubarrayFQDN": ["mid-sdp/subarray/01"],
                    },
                }
            ],
        },
    )


def checked_devices(json_model):
    result = 0
    for dev in json_model["devices"]:
        if int(dev["ping"]) > 0 and dev["unresponsive"] == "False":
            result += 1
    return result


def tear_down(dev_factory, sdp_subarray, sdpsal_node, change_event_callbacks):
    sdpsal_node_obsstate = sdpsal_node.read_attribute("sdpSubarrayObsState")
    logger.info(f"SDP Subarray ObsState: {sdpsal_node_obsstate.value}")

    if sdpsal_node_obsstate.value == ObsState.EMPTY:
        sdp_subarray.Off()

    if sdpsal_node_obsstate.value == ObsState.IDLE:
        sdp_subarray.ReleaseAllResources()
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.EMPTY,
            lookahead=8,
        )

        sdp_subarray.Off()
        sdpsal_node_obsstate = sdpsal_node.read_attribute(
            "sdpSubarrayObsState"
        )
        logger.info(f"SDP Subarray ObsState: {sdpsal_node_obsstate.value}")

    if sdpsal_node_obsstate.value == ObsState.READY:
        sdp_subarray.End()
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.IDLE,
            lookahead=8,
        )

        sdp_subarray.ReleaseAllResources()
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.EMPTY,
            lookahead=8,
        )
        sdp_subarray.Off()
        sdpsal_node_obsstate = sdpsal_node.read_attribute(
            "sdpSubarrayObsState"
        )
        logger.info(f"SDP Subarray ObsState: {sdpsal_node_obsstate.value}")

    if sdpsal_node_obsstate.value in (
        ObsState.RESOURCING,
        ObsState.SCANNING,
        ObsState.CONFIGURING,
    ):
        sdp_subarray.Abort()
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.ABORTED,
            lookahead=8,
        )

        sdp_subarray.Restart()
        time.sleep(3)
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.EMPTY,
            lookahead=8,
        )
        sdp_subarray.Off()
        sdpsal_node_obsstate = sdpsal_node.read_attribute(
            "sdpSubarrayObsState"
        )
        logger.info(f"SDP Subarray ObsState: {sdpsal_node_obsstate.value}")
    sdp_subarray.ClearCommandCallInfo()


def set_sdp_subarray_obsstate(dev_factory, obs_state, sdp_subarray):
    logger.debug("Setting Obsstate to : %s", obs_state)
    sdp_subarray.SetDirectObsState(obs_state)
    time.sleep(0.1)
    logger.debug("ObsState of sdp subarray: %s", sdp_subarray.ObsState)

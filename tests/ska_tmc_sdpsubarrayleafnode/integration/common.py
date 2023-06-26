import time

import pytest
from ska_tango_base.control_model import ObsState
from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)

from ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node import (
    SdpSubarrayLeafNode,
)
from tests.settings import TIMEOUT, logger

pytest.event_arrived = False


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": "mid-sdp/subarray/01"},
            ],
        },
        {
            "class": SdpSubarrayLeafNode,
            "devices": [
                {
                    "name": "ska_mid/tm_leaf_node/sdp_subarray01",
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


def tear_down(dev_factory, sdp_subarray):
    sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
    logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

    if sdp_subarray_obsstate.value == 0:
        sdp_subarray.Off()

    if sdp_subarray_obsstate.value == 2:
        sdp_subarray.ReleaseResources()
        sdp_subarray.SetDirectObsState(ObsState.EMPTY)
        time.sleep(0.5)
        sdp_subarray.Off()
        sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
        logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

    if sdp_subarray_obsstate.value in (ObsState.READY, ObsState.SCANNING):
        sdp_subarray.Abort()
        sdp_subarray.SetDirectObsState(ObsState.ABORTED)
        time.sleep(1)
        sdp_subarray.Restart()
        sdp_subarray.SetDirectObsState(ObsState.EMPTY)
        time.sleep(1)
        sdp_subarray.Off()
        sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
        logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

    if sdp_subarray_obsstate.value == 7:
        sdp_subarray.Restart()
        sdp_subarray.SetDirectObsState(ObsState.EMPTY)
        time.sleep(1)
        sdp_subarray.Off()
        sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
        logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")


def wait_for_final_sdp_subarray_obsstate(sdp_subarray_leaf_node, obs_state):
    logger.debug(f"Waiting for SdpSubarray obsState to be {obs_state}")
    sdp_subarray_obsstate = sdp_subarray_leaf_node.read_attribute(
        "sdpSubarrayObsState"
    )
    logger.debug(f"SdpSubarray obsState is {sdp_subarray_obsstate}")
    wait_time = 0
    while (sdp_subarray_obsstate.value) != obs_state:
        time.sleep(0.5)
        sdp_subarray_obsstate = sdp_subarray_leaf_node.read_attribute(
            "sdpSubarrayObsState"
        )
        logger.debug(
            f"SppSubarray obsState in loop: {sdp_subarray_obsstate.value}"
        )
        logger.debug(f"Expected SdpSubarray obsState: {obs_state}")
        wait_time = wait_time + 1
        logger.debug(f"wait_time in teardown  {wait_time}")
        if wait_time > TIMEOUT:
            pytest.fail(
                f"Timeout occurred in transitioning SdpSubarray\
                     obsState to {obs_state}"
            )

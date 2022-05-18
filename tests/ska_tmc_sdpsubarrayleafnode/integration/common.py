import time

import pytest
from ska_tango_base.control_model import ObsState
from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)

from ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node import (
    SdpSubarrayLeafNode,
)
from tests.settings import logger

pytest.event_arrived = False


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": "mid_sdp/elt/subarray_1"},
            ],
        },
        {
            "class": SdpSubarrayLeafNode,
            "devices": [
                {
                    "name": "ska_mid/tm_leaf_node/sdp_subarray01",
                    "properties": {
                        "SdpSubarrayFQDN": ["mid_sdp/elt/subarray_1"],
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
    sdp_subarray = dev_factory.get_device(sdp_subarray)
    sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
    logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

    if sdp_subarray_obsstate.value == 0:
        sdp_subarray.Off()

    if sdp_subarray_obsstate.value == 2:
        sdp_subarray.ReleaseResources("")
        sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_1")
        sdp_subarray.SetDirectObsState(ObsState.EMPTY)
        time.sleep(0.5)
        sdp_subarray.Off()
        sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
        logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

    if sdp_subarray_obsstate.value == 4 or 5:
        sdp_subarray.Abort()
        sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_1")
        sdp_subarray.SetDirectObsState(ObsState.ABORTED)
        time.sleep(1)
        sdp_subarray.Restart()
        sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_1")
        sdp_subarray.SetDirectObsState(ObsState.EMPTY)
        time.sleep(1)
        sdp_subarray.Off()
        sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
        logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

    if sdp_subarray_obsstate.value == 7:
        sdp_subarray.Restart()
        sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_1")
        sdp_subarray.SetDirectObsState(ObsState.EMPTY)
        time.sleep(1)
        sdp_subarray.Off()
        sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
        logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

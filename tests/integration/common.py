import pytest

from ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node_mid import (
    SdpSubarrayLeafNodeMid,
)
from tests.helpers.helper_subarray_device import HelperSubArrayDevice

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
            "class": SdpSubarrayLeafNodeMid,
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

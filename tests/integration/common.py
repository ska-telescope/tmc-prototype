import time

import pytest

from ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node_mid import (
    SdpSubarrayLeafNodeMid,
)
from tests.helpers.helper_state_device import HelperStateDevice
from tests.helpers.helper_subarray_device import HelperSubArrayDevice
from tests.settings import SLEEP_TIME, TIMEOUT

pytest.event_arrived = False


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": "mid_sdp/elt/subarray_01"},
            ],
        },
        {
            "class": HelperStateDevice,
            "devices": [
                {"name": "mid_sdp/elt/subarray_01"},
            ],
        },
        {
            "class": SdpSubarrayLeafNodeMid,
            "devices": [
                {
                    "name": "ska_mid/tm_leaf_node/sdp_subarray01",
                    "properties": {
                        "SdpSubarrayFQDN": ["mid_sdp/elt/subarray_01"],
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


# TODO: need to check if internalmodel attribute is required on sdpsaln
# def ensure_checked_devices(central_node):
#     json_model = json.loads(central_node.internalModel)
#     start_time = time.time()
#     checked_devs = checked_devices(json_model)
#     while checked_devs != len(json_model["devices"]):
#         new_checked_devs = checked_devices(json_model)
#         if checked_devs != new_checked_devs:
#             checked_devs = new_checked_devs
#             logger.debug("checked devices: %s", checked_devs)
#         time.sleep(SLEEP_TIME)
#         elapsed_time = time.time() - start_time
#         if elapsed_time > TIMEOUT:
#             logger.debug(central_node.internalModel)
#             pytest.fail("Timeout occurred while executing the test")
#         json_model = json.loads(central_node.internalModel)


def assert_event_arrived():
    start_time = time.time()
    while not pytest.event_arrived:
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")

    assert pytest.event_arrived

import pytest
import os
import logging
import time
from tango import DeviceProxy
from datetime import date, datetime
from resources.test_support.helpers import waiter, watch, resource
from resources.test_support.controls import telescope_is_in_standby, tmc_is_in_on, telescope_is_on, telescope_is_off
from resources.test_support.sync_decorators import sync_sdpsln_reset
from resources.test_support.logging_decorators import log_it
import resources.test_support.tmc_helpers as tmc

DEV_TEST_TOGGLE = os.environ.get("DISABLE_DEV_TESTS")
if DEV_TEST_TOGGLE == "False":
    DISABLE_TESTS_UNDER_DEVELOPMENT = False
else:
    DISABLE_TESTS_UNDER_DEVELOPMENT = True

devices_to_log = [
    "ska_mid/tm_subarray_node/1",
    "mid_csp/elt/subarray_01",
    "mid_sdp/elt/subarray_1",
    "mid_d0001/elt/master",
    "mid_d0002/elt/master",
    "mid_d0003/elt/master",
    "mid_d0004/elt/master",
]
non_default_states_to_check = {
    "mid_d0001/elt/master": "pointingState",
    "mid_d0002/elt/master": "pointingState",
    "mid_d0003/elt/master": "pointingState",
    "mid_d0004/elt/master": "pointingState",
}

LOGGER = logging.getLogger(__name__)

@pytest.mark.mid
# @pytest.mark.skipif(DISABLE_TESTS_UNDER_DEVELOPMENT, reason="disabaled by local env")
def test_sdpsln_reset():
    
    # given an interface to TMC to interact with a subarray node and a central node
    fixture = {}
    fixture["state"] = "Unknown"
    the_waiter = waiter()

    assert tmc_is_in_on()
    LOGGER.info("TMC devices are up")

    LOGGER.info("Calling TelescopeOn command now.")
    tmc.set_telescope_on()
    time.sleep(50)
    assert telescope_is_on()
    LOGGER.info("Telescope is on")
    fixture["state"] = "Telescope On"

    # and a subarray composed of two resources configured as perTMC_integration/assign_resources.json
    LOGGER.info("Composing the Subarray")

    resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals(
        "EMPTY"
    )

    SdpSubarrayLeafNode = DeviceProxy("ska_mid/tm_leaf_node/sdp_subarray01")
    try:
        LOGGER.info("Invoking Assign Resources command on SdpsubarrayLeafNode")
        SdpSubarrayLeafNode.AssignResources('"wrong json"')
    except:
        LOGGER.info("Assign Resources command is failed on SdpSubarrayLeafNode")
    resource("ska_mid/tm_leaf_node/sdp_subarray01").assert_attribute("State").equals(
            "FAULT"
        )
    LOGGER.info("SdpSubarrayLeafNode is in FAULT state")
    fixture["state"]  == "Device FAULT"

    @log_it("TMC_reset", devices_to_log, non_default_states_to_check)
    @sync_sdpsln_reset()
    def reset():
        
        SdpSubarrayLeafNode = DeviceProxy("ska_mid/tm_leaf_node/sdp_subarray01")
        SdpSubarrayLeafNode.Reset()
        LOGGER.info("Invoked Reset command on SdpSubarrayLeafNode")

    reset()
    LOGGER.info("Reset is complete on SdpSubarrayLeafNode")

    resource("ska_mid/tm_leaf_node/sdp_subarray01").assert_attribute("State").equals(
            "OFF"
        )

    LOGGER.info("Invoking On command on SdpSubarrayLeafNode to continue the standard operation.")
    SdpSubarrayLeafNode.On()
    LOGGER.info("Invoking On command on SdpSubarrayLeafNode.")

    resource("ska_mid/tm_leaf_node/sdp_subarray01").assert_attribute("State").equals(
            "ON"
        )
    
    tmc.compose_sub()
    fixture["state"] = "Subarray Assigned"

    tmc.release_resources()
    fixture["state"] = "Release Resources"

    LOGGER.info("Calling TelescopeOff command now.")
    tmc.set_telescope_off()
    time.sleep(20)
    assert telescope_is_off()
    fixture["state"] = "Telescope Off"

    # tear down
    LOGGER.info("TMC-Reset tests complete: tearing down...")
import pytest
import os
import logging
from tango import DeviceProxy
from datetime import date, datetime
from resources.test_support.helpers_low import waiter, watch, resource
from resources.test_support.controls_low import telescope_is_in_standby
from resources.test_support.sync_decorators_low import sync_reset
from resources.test_support.logging_decorators import log_it
import resources.test_support.tmc_helpers_low as tmc

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
def test_reset():
    try:
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

        CspSubarrayLeafNode = DeviceProxy("ska_mid/tm_leaf_node/csp_subarray1")
        CspSubarrayLeafNode.AssignResources('"wrong json"')
        resource("ska_mid/tm_leaf_node/csp_subarray1").assert_attribute("State").equals(
                "FAULT"
            )
        LOGGER.info("AssignResources is in FAULT state")
        fixture["state"]  == "Device FAULT"

        @log_it("TMC_reset", devices_to_log, non_default_states_to_check)
        @sync_reset()
        def reset():
            
            CspSubarrayLeafNode = DeviceProxy("ska_mid/tm_leaf_node/csp_subarray1")
            CspSubarrayLeafNode.Reset()
            LOGGER.info("Invoked Reset on CspSubarrayLeafNode")

        reset()
        LOGGER.info("Reset is complete on CspSubarrayLeafNode")

        resource("ska_mid/tm_leaf_node/csp_subarray1").assert_attribute("State").equals(
                "OFF"
            )
        CspSubarrayLeafNode.On()

        resource("ska_mid/tm_leaf_node/csp_subarray1").assert_attribute("State").equals(
                "ON"
            )

        LOGGER.info("Calling TelescopeOff command now.")
        tmc.set_telescope_off()
        time.sleep(20)
        assert telescope_is_off()
        fixture["state"] = "Telescope Off"

        # tear down
        LOGGER.info("TMC-Reset tests complete: tearing down...")

    except:
        LOGGER.info("Tearing down failed test, state = {}".format(fixture["state"]))
        if fixture["state"]  == "Telescope On":
            tmc.set_telescope_off()
        elif fixture["state"]  == "Device FAULT":
            CspSubarrayLeafNode.Reset()
            CspSubarrayLeafNode.On()
            tmc.set_telescope_off()
        pytest.fail("unable to complete test without exceptions")


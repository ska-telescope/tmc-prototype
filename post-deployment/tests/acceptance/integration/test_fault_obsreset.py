from tango import DeviceProxy
from datetime import date, datetime
import os
import pytest
import logging
from resources.test_support.helpers import waiter, resource
from resources.test_support.controls import tmc_is_in_on, telescope_is_on, telescope_is_off
from resources.test_support.sync_decorators import sync_obsreset_sa, sync_configure
from resources.test_support.persistance_helping import (
    load_config_from_file,
    update_scan_config_file
)
import resources.test_support.tmc_helpers as tmc
from resources.test_support.logging_decorators import log_it

import time

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

@pytest.mark.fault
# @pytest.mark.skipif(DISABLE_TESTS_UNDER_DEVELOPMENT, reason="disabaled by local env")
def test_fault_obsreset():
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
    sdp_block = tmc.compose_sub()
    fixture["state"] = "Subarray Assigned"

    @log_it("TMC_int_configure", devices_to_log, non_default_states_to_check)
    def configure_sub(sdp_block):
        wrong_configure_file = "resources/test_data/TMC_integration/wrong_config.json"
        LOGGER.info("Configuring a scan for subarray 1")
        fixture["state"] = "Subarray CONFIGURING"
        config = load_config_from_file(wrong_configure_file)
        SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
        try:
            LOGGER.info("Invoking Configure Command on Subarray Node.")
            SubarrayNode.Configure(config)
        except:
            LOGGER.info("Configure command is failed on Subarray Node")

    configure_sub(sdp_block)

    LOGGER.info("The obsstate of Subarray Node is in FAULT state")
    LOGGER.info(
        'resource("ska_mid/tm_subarray_node/1").get("State")'
        + str(resource("ska_mid/tm_subarray_node/1").get("State"))
    )
    
    @sync_obsreset_sa()
    def obsreset():
        resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals(
            "ON"
        )
        SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
        
        resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals(
            "FAULT"
        )
        SubarrayNode.ObsReset()
        LOGGER.info("Invoked obsreset on Subarray")
        LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
        
    obsreset()

    LOGGER.info("Subarray is in IDLE state")
    LOGGER.info("Obsreset is complete on Subarray")
    fixture["state"] = "Subarray IDLE"

    @sync_configure
    def configure_sub(sdp_block):
        configure1_file = "resources/test_data/TMC_integration/configure1.json"
        update_scan_config_file(configure1_file, sdp_block)
        config = load_config_from_file(configure1_file)
        fixture["state"] = "Subarray CONFIGURING"
        SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
        LOGGER.info("Invoking Configure on SubarrayNode again with the correct JSON.")
        SubarrayNode.Configure(config)
        LOGGER.info("Invoked Configure on Subarray")

    configure_sub(sdp_block)
    fixture["state"] = "Subarray Configured for SCAN"
    time.sleep(60)

    tmc.end_sb()
    fixture["state"] = "Subarray is in IDLE after EndCommand"

    LOGGER.info("Invoking Release Resources on Subarray")
    tmc.release_resources()
    fixture["state"] = "Released Resources" 
    
    LOGGER.info("Calling TelescopeOff command now.")
    tmc.set_telescope_off()
    time.sleep(20)
    assert telescope_is_off()
    fixture["state"] = "Telescope Off"

    # tear down
    LOGGER.info("TMC-ObsReset tests complete: tearing down...")

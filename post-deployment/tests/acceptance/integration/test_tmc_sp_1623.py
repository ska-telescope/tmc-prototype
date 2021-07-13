from tango import DeviceProxy
from datetime import date, datetime
import pytest
import os
import logging
import time
from resources.test_support.helpers import waiter, watch, resource
from resources.test_support.controls import (
    tmc_is_in_off,
    tmc_is_in_on,
    telescope_is_on,
    telescope_is_off,
    telescope_is_standby,
)
from resources.test_support.state_checking import StateChecker
from resources.test_support.log_helping import DeviceLogging
from resources.test_support.logging_decorators import log_states
from resources.test_support.persistance_helping import (
    load_config_from_file,
    update_scan_config_file,
    update_resource_config_file,
)
from resources.test_support.sync_decorators import (
    sync_tmc_on,
    sync_tmc_off,
    sync_tmc_standby,
    sync_assign_resources,
    sync_configure,
    sync_end_sb,
    sync_release_resources,
    sync_set_to_standby,
    time_it,
)
from resources.test_support.logging_decorators import log_it
import resources.test_support.tmc_helpers as tmc
from resources.test_support.sync_decorators import sync_scanning

DEV_TEST_TOGGLE = os.environ.get("DISABLE_DEV_TESTS")
if DEV_TEST_TOGGLE == "False":
    DISABLE_TESTS_UNDER_DEVELOPMENT = False
else:
    DISABLE_TESTS_UNDER_DEVELOPMENT = True

devices_to_log = [
    "ska_mid/tm_subarray_node/1",
    "mid_csp/elt/subarray_01",
    "mid_csp_cbf/sub_elt/subarray_01",
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


@pytest.mark.ncra
# @pytest.mark.skipif(DISABLE_TESTS_UNDER_DEVELOPMENT, reason="disabaled by local env")
def test_feature_sp_1623():

    try:
        # given an interface to TMC to interact with a subarray node and a central node
        the_waiter = waiter()
        fixture = {}
        fixture["state"] = "Unknown"

        assert tmc_is_in_on()
        LOGGER.info("TMC devices are up")
        LOGGER.info("Calling TelescopeOn command now.")
        tmc.set_telescope_on()
        the_waiter.wait()
        time.sleep(5)
        assert telescope_is_on()
        LOGGER.info("Telescope is on")
        LOGGER.info("TelescopeState is on")
        fixture["state"] = "Telescope On"

        # and a subarray composed of two resources configured as perTMC_integration/assign_resources1.json
        sdp_block = tmc.compose_sub()
        LOGGER.info("Composing the Subarray")
        fixture["state"] = "Subarray Assigned"

        # and for which the subarray is configured to perform a scan as per 'TMC_integration/configure1.json'
        fixture["state"] = "Subarray CONFIGURING"
        configure_file = "resources/test_data/TMC_integration/configure2.json"
        tmc.configure_sub(sdp_block, configure_file)
        LOGGER.info("Configuring the Subarray")
        fixture["state"] = "Subarray Configured for SCAN"

        # and for which the subarray has successfully completed a scan durating 6 seconds based on previos configuration
        resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals(
            "READY"
        )
        LOGGER.info("Starting a scan of 6 seconds")

        with log_states("TMC Scan", devices_to_log, non_default_states_to_check):
            with sync_scanning(200):
                SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
                SubarrayNode.Scan('{"id":1}')
                fixture["state"] = "Subarray SCANNING"
                LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
                LOGGER.info("Scan 1  is executing on Subarray")

        LOGGER.info("Scan1 complete")
        fixture["state"] = "Subarray Configured for SCAN"

        # The scanning should complete without any exceptions

        # tear down
        LOGGER.info("TMC Functionality test complete: tearing down...")
        tmc.end_sb()
        the_waiter.wait()
        LOGGER.info("Invoked EndSB on Subarray")
        tmc.release_resources()
        the_waiter.wait()
        LOGGER.info("Invoked ReleaseResources on Subarray")

        LOGGER.info("Calling Telescope Off command now.")
        tmc.set_telescope_off()
        the_waiter.wait()
        time.sleep(10)
        assert telescope_is_off()
        LOGGER.info("Telescope is Off")
        fixture["state"] = "Telescope Off"

        # LOGGER.info("Calling Telescope StandBy command now.")
        # tmc.set_telescope_standby()
        # the_waiter.wait()
        # time.sleep(5)
        # assert telescope_is_standby()
        # LOGGER.info("Telescope is StandBy")
        # fixture["state"] = "Telescope StandBy"

    except:
        LOGGER.info("Gathering logs")
        pytest.fail("unable to complete test without exceptions")

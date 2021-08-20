import time
from tango import DeviceProxy
from datetime import date, datetime
import pytest
import os
import logging
from resources.test_support.helpers import waiter, watch, resource
from resources.test_support.controls import telescope_is_in_standby, tmc_is_in_on, telescope_is_on, telescope_is_off
from resources.test_support.state_checking import StateChecker
from resources.test_support.log_helping import DeviceLogging
from resources.test_support.persistance_helping import (
    load_config_from_file,
    update_scan_config_file,
    update_resource_config_file,
)
from resources.test_support.sync_decorators import (
    sync_start_up_telescope,
    sync_assign_resources,
    sync_configure,
    sync_end_sb,
    sync_release_resources,
    sync_set_to_standby,
    time_it,
)
from resources.test_support.logging_decorators import log_it
import resources.test_support.tmc_helpers as tmc
from ska_ser_skuid.client import SkuidClient

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

@pytest.mark.mid
# @pytest.mark.skipif(DISABLE_TESTS_UNDER_DEVELOPMENT, reason="disabaled by local env")
def test_assign_resources():

    try:
        client = SkuidClient(os.environ['SKUID_URL'])
        # New type of id "eb_id" is used to distinguish between real SB and id used during testing
        eb_id = client.fetch_skuid("eb")

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

        # then when I assign a subarray composed of two resources configured as perTMC_integration/assign_resources.json
        @log_it("TMC_int_comp", devices_to_log, non_default_states_to_check)
        @sync_assign_resources(2, 800)
        def compose_sub():
            resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals(
                "ON"
            )
            resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals(
                "EMPTY"
            )
            assign_resources_file = (
                "resources/test_data/TMC_integration/assign_resources1.json"
            )
            update_resource_config_file(assign_resources_file)
            config = load_config_from_file(assign_resources_file)
            CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
            CentralNode.AssignResources(config)
            LOGGER.info("Invoked AssignResources on CentralNode")
        compose_sub()
        fixture["state"] = "Subarray Assigned"

        # tear down
        LOGGER.info("Tests complete: tearing down...")
        tmc.release_resources()
        time.sleep(20)
        fixture["state"] = "Released Resources"
        
        LOGGER.info("Calling TelescopeOff command now.")
        tmc.set_telescope_off()
        time.sleep(20)
        assert telescope_is_off()
        fixture["state"] = "Telescope Off"


    except:
        LOGGER.info("Tearing down failed test, state = {} ".format(fixture["state"]))
        if fixture["state"]  == "Telescope On":
            tmc.set_telescope_off()
        elif fixture["state"] == "Subarray Assigned":
            tmc.release_resources()
            tmc.set_telescope_off()
        elif fixture["state"] == "Released Resources":
            tmc.set_telescope_off()
        else:
            LOGGER.info("Tearing down completed...")
        assert 0

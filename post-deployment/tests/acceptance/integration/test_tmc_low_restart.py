from tango import DeviceProxy
from datetime import date, datetime
import pytest
import os
import logging
from resources.test_support.helpers_low import waiter, watch, resource
from resources.test_support.controls_low import telescope_is_in_standby
from resources.test_support.sync_decorators_low import sync_restart
from resources.test_support.logging_decorators import log_it
import resources.test_support.tmc_helpers_low as tmc

DEV_TEST_TOGGLE = os.environ.get("DISABLE_DEV_TESTS")
if DEV_TEST_TOGGLE == "False":
    DISABLE_TESTS_UNDER_DEVELOPMENT = False
else:
    DISABLE_TESTS_UNDER_DEVELOPMENT = True

devices_to_log = ["ska_low/tm_subarray_node/1", "low-mccs/subarray/01"]

LOGGER = logging.getLogger(__name__)


@pytest.mark.skip()
# @pytest.mark.low
def test_restart():
    try:
        # given an interface to TMC to interact with a subarray node and a central node
        fixture = {}
        fixture["state"] = "Unknown"
        the_waiter = waiter()

        # given a started up telescope
        assert telescope_is_in_standby()
        LOGGER.info("Starting up the Telescope")
        tmc.start_up()
        fixture["state"] = "Telescope On"

        # and a subarray composed of two resources configured as perTMC_integration/assign_resources.json
        LOGGER.info("Composing the Subarray")
        tmc.compose_sub()
        fixture["state"] = "Subarray Assigned"

        resource("ska_low/tm_subarray_node/1").assert_attribute("obsState").equals(
            "IDLE"
        )
        LOGGER.info("Aborting the subarray")
        fixture["state"] = "Subarray ABORTING"
        
        LOGGER.info("Invoking abort command")
        tmc.abort_sub()
        fixture["state"] = "Subarray Aborted"

        fixture["state"] = "Subarray Restarting"
        @sync_restart()
        def restart():
            SubarrayNodeLow = DeviceProxy("ska_low/tm_subarray_node/1")
            LOGGER.info(
                "Subarray obsState before Aborted assertion check is: "
                + str(SubarrayNodeLow.obsState)
            )
            resource("ska_low/tm_subarray_node/1").assert_attribute("obsState").equals(
                "ABORTED"
            )
            SubarrayNodeLow.Restart()
            LOGGER.info("Subarray obsState is: " + str(SubarrayNodeLow.obsState))
            LOGGER.info("Invoked restart on Subarray")

        restart()
        LOGGER.info("Restart is complete on Subarray")        
        LOGGER.info("TMC-Restart tests complete: tearing down...")
        resource("ska_low/tm_subarray_node/1").assert_attribute("obsState").equals(
            "EMPTY"
        )
        fixture["state"] = "Subarray empty"

        tmc.set_to_standby()

        LOGGER.info("Invoked StandBy on Subarray")
        fixture["state"] = "Subarray off"

        LOGGER.info("TMC-Low-Restart tests complete: tearing down...")

    except:
        LOGGER.info("Tearing down failed test, state = {}".format(fixture["state"]))
        if fixture["state"] == "Telescope On":
            tmc.set_to_standby()
        elif fixture["state"] == "Subarray Assigned":
            tmc.release_resources()
            tmc.set_to_standby()
        elif fixture["state"] == "Subarray ABORTING":
            # restart_subarray(1)
            raise Exception("unable to teardown subarray from being in ABORTING")
        elif fixture["state"] == "Subarray Aborted":
            # restart_subarray(1)
            raise Exception("unable to teardown subarray from being in Aborted")
        elif fixture["state"] == "Subarray Restarting":
            # restart_subarray(1)
            raise Exception("unable to teardown subarray from being in Restarting")
        elif fixture["state"] == "Subarray off":
            LOGGER.info("Subarray has completed StandBy execution")
        pytest.fail("unable to complete test without exceptions")

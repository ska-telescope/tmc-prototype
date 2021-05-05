import pytest
import os
import logging
from tango import DeviceProxy
from datetime import date, datetime
from resources.test_support.helpers_low import waiter, watch, resource
from resources.test_support.controls_low import telescope_is_in_standby
from resources.test_support.sync_decorators_low import sync_abort
from resources.test_support.logging_decorators import log_it
import resources.test_support.tmc_helpers_low as tmc

DEV_TEST_TOGGLE = os.environ.get("DISABLE_DEV_TESTS")
if DEV_TEST_TOGGLE == "False":
    DISABLE_TESTS_UNDER_DEVELOPMENT = False
else:
    DISABLE_TESTS_UNDER_DEVELOPMENT = True

devices_to_log = ["ska_low/tm_subarray_node/1", "low-mccs/subarray/01"]

LOGGER = logging.getLogger(__name__)



@pytest.fixture(
    scope="function",
    params=[
        ("IDLE"),
        ("READY"),
        ("SCANNING"),
    ],
)
def required_obstate(request):
    obs_state = request.param
    return obs_state

@pytest.mark.low
def test_abort(required_obstate):
    try:
        obs_state_val = required_obstate
        # given an interface to TMC to interact with a subarray node and a central node
        if obs_state_val == "IDLE":
            fixture = {}
            fixture["state"] = "Unknown"
            # given a started up telescope
            assert telescope_is_in_standby()
            LOGGER.info("Starting up the Telescope")
            tmc.start_up()
            fixture["state"] = "Telescope On"
            # and a subarray composed of two resources configured as perTMC_integration/mccs_assign_resources.json
            LOGGER.info("Composing the Subarray")
            tmc.compose_sub()
            fixture["state"] = "Subarray Assigned"
            resource("ska_low/tm_subarray_node/1").assert_attribute("obsState").equals(
                "IDLE"
            )
            LOGGER.info("Invoking abort command")
            tmc.abort_sub()
            fixture["state"] = "Obstate aborted"

            LOGGER.info("Invoking Obsreset command")
            tmc.obsreset_sub()
            LOGGER.info("Obsreset is complete on Subarray")
            fixture["state"] = "Subarray IDLE"
            tmc.release_resources()
            LOGGER.info("Invoked ReleaseResources on Subarray")
            tmc.set_to_standby()
            LOGGER.info("Invoked StandBy on Subarray")

        elif obs_state_val == "READY":
            fixture = {}
            fixture["state"] = "Unknown"

            # given a started up telescope
            assert telescope_is_in_standby()
            LOGGER.info("Starting up the Telescope")
            tmc.start_up()
            fixture["state"] = "Telescope On"
            # and a subarray composed of two resources configured as perTMC_integration/mccs_assign_resources.json
            LOGGER.info("Composing the Subarray")
            tmc.compose_sub()
            fixture["state"] = "Subarray Assigned"
            resource("ska_low/tm_subarray_node/1").assert_attribute("obsState").equals(
                "IDLE"
            )

            LOGGER.info("Configuring the Subarray")
            fixture["state"] = "Subarray CONFIGURING"
            tmc.configure_sub()
            fixture["state"] = "Subarray Configured for SCAN"
            resource("ska_low/tm_subarray_node/1").assert_attribute("obsState").equals(
                "READY"
            )

            LOGGER.info("Invoking abort command")
            tmc.abort_sub()
            fixture["state"] = "Obstate aborted"

            LOGGER.info("Invoking Obsreset command")
            tmc.obsreset_sub()
            LOGGER.info("Obsreset is complete on Subarray")
            fixture["state"] = "Subarray IDLE"
            tmc.release_resources()
            LOGGER.info("Invoked ReleaseResources on Subarray")
            tmc.set_to_standby()
            LOGGER.info("Invoked StandBy on Subarray")

        elif obs_state_val == "SCANNING":
            fixture = {}
            fixture["state"] = "Unknown"

            # given a started up telescope
            assert telescope_is_in_standby()
            LOGGER.info("Starting up the Telescope")
            tmc.start_up()
            fixture["state"] = "Telescope On"
            # and a subarray composed of two resources configured as perTMC_integration/mccs_assign_resources.json
            LOGGER.info("Composing the Subarray")
            tmc.compose_sub()
            fixture["state"] = "Subarray Assigned"
            resource("ska_low/tm_subarray_node/1").assert_attribute("obsState").equals(
                "IDLE"
            )
            LOGGER.info("Configuring the Subarray")
            fixture["state"] = "Subarray CONFIGURING"
            tmc.configure_sub()
            fixture["state"] = "Subarray Configured for SCAN"
            resource("ska_low/tm_subarray_node/1").assert_attribute("obsState").equals(
                "READY"
            )
            
            @sync_abort
            def abort():
                SubarrayNodeLow = DeviceProxy("ska_low/tm_subarray_node/1")
                tmc.scan_for_scanning()
                SubarrayNodeLow.Abort()
                LOGGER.info("Invoked Abort on Subarray")

            abort()
            LOGGER.info("Abort is complete on Subarray")
            fixture["state"] = "Subarray Aborted"

            tmc.obsreset_sub()
            LOGGER.info("Obsreset is complete on Subarray")
            fixture["state"] = "Subarray IDLE"
            tmc.release_resources()
            LOGGER.info("Invoked ReleaseResources on Subarray")
            tmc.set_to_standby()
            LOGGER.info("Invoked StandBy on Subarray")
        else:
            msg = "obsState {} is not settable with command methods"
            raise ValueError(msg.format(obs_state_val))
       
    except:
        LOGGER.info("Tearing down failed test, state = {}".format(fixture["state"]))
        if fixture["state"] == "Telescope On":
            tmc.set_to_standby()
        elif fixture["state"] == "Subarray Assigned":
            tmc.release_resources()
            tmc.set_to_standby()
        elif fixture["state"] == "Subarray CONFIGURING":
            raise Exception("unable to teardown subarray from being in Restarting")
        elif fixture["state"] == "Subarray ABORTING":
            raise Exception("unable to teardown subarray from being in ABORTING")
        elif fixture["state"] == "Subarray Aborted":
            raise Exception("unable to teardown subarray from being in Aborted")
        elif fixture["state"] == "Subarray Resetting":
            raise Exception("unable to teardown subarray from being in Restarting")
        elif fixture["state"] == "Subarray IDLE":
            tmc.release_resources()
            tmc.set_to_standby()
        pytest.fail("unable to complete test without exceptions")

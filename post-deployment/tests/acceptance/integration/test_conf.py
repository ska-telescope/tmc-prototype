#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_calc
----------------------------------
Acceptance tests for MVP.
"""
import random
import os
import signal
from concurrent import futures
from assertpy import assert_that
from pytest_bdd import scenario, given, when, then
# import oet
import pytest
# from oet.domain import SKAMid, SubArray, ResourceAllocation, Dish
from tango import DeviceProxy, DevState
from resources.test_support.helpers import  obsState, resource, watch, waiter, map_dish_nr_to_device_name
from resources.test_support.helpers_low import resource, watch, waiter, wait_before_test
from resources.test_support.logging_decorators import log_it
import logging
from resources.test_support.controls_low import telescope_is_in_standby
from resources.test_support.sync_decorators_low import sync_configure,time_it

from resources.test_support.persistance_helping import load_config_from_file
# from resources.test_support.controls_low import set_telescope_to_standby,set_telescope_to_running,telescope_is_in_standby,restart_subarray,sync_assign_resources
from resources.test_support.sync_decorators_low import sync_start_up_telescope,sync_assign_resources,sync_release_resources,sync_set_to_standby,time_it
from resources.test_support.tmc_helpers_low import compose_sub
import resources.test_support.tmc_helpers_low as tmc

LOGGER = logging.getLogger(__name__)

import json

DEV_TEST_TOGGLE = os.environ.get('DISABLE_DEV_TESTS')
if DEV_TEST_TOGGLE == "False":
    DISABLE_TESTS_UNDER_DEVELOPMENT = False
else:
    DISABLE_TESTS_UNDER_DEVELOPMENT = True


LOGGER = logging.getLogger(__name__)

devices_to_log = [
    'ska_low/tm_subarray_node/1',
    'ska_low/tm_leaf_node/mccs_subarray01',
    'low-mccs/subarray/01']

non_default_states_to_check = {}

@pytest.fixture
def result():
    return {}

@pytest.mark.low_conf
#@pytest.mark.skipif(DISABLE_TESTS_UNDER_DEVELOPMENT, reason="disabaled by local env")
# TODO: Need to change when feature file will be created.
# @scenario("1_XR-13_XTP-494.feature", "A2-Test, Sub-array transitions from IDLE to READY state")
def test_configure_subarray():
    # """Configure Subarray."""
# @given("I am accessing the console interface for the OET")
# def start_up():
    LOGGER.info("Given I am accessing the console interface for the OET")
    LOGGER.info("Check whether telescope is in StandBy")
    assert(telescope_is_in_standby())
    LOGGER.info("Starting up telescope")
    tmc.start_up()
    wait_before_test(timeout=20)
    LOGGER.info("Telescope is in ON state")

# TODO: Need to update given clause
# @given("sub-array is in IDLE state")
# def assign(result):
    LOGGER.info("Allocating resources to Low Subarray 1")
    compose_sub()
    LOGGER.info("Subarray 1 is ready and composed out of 2 dishes")

    @sync_configure
    @time_it(120)
    def conf():
        configure1_file = 'resources/test_data/TMC_integration/mccs_configure.json'    
        config = load_config_from_file(configure1_file)
        SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
        SubarrayNodeLow.Configure(config)
        LOGGER.info("Subarray obsState is: " + str(SubarrayNodeLow.obsState))
        LOGGER.info('Invoked Configure on Subarray')
        LOGGER.info("Configure command on Subarray 1 is successful")
    conf()
# TODO: Need to update then clause
# @then("sub-array is in READY state for which subsequent scan commands can be directed to deliver a basic imaging outcome")
# def check_state():
    LOGGER.info("Checking the results")
    # check that the TMC report subarray as being in the obsState = READY
    assert_that(resource('ska_low/tm_subarray_node/1').get('obsState')).is_equal_to('READY')
    # check that the MCCS report subarray as being in the obsState = READY
    assert_that(resource('low-mccs/subarray/01').get('obsState')).is_equal_to('READY')
    LOGGER.info("Results OK")


# def teardown_function(function):
    """ teardown any state that was previously setup with a setup_function
    call.
    """
    if (resource('ska_low/tm_subarray_node/1').get('State') == "ON"):
        #this means there must have been an error
        if (resource('ska_low/tm_subarray_node/1').get('obsState') == "IDLE"):
            LOGGER.info("tearing down composed subarray (IDLE)")
            release_resources()
    if (resource('ska_low/tm_subarray_node/1').get('obsState') == "READY"):
        #this means test must have passed
        LOGGER.info("tearing down configured subarray (READY)")
        tmc.end()
        tmc.release_resources()
        LOGGER.info("EndSb and ReleaseResources is involked on Subarray 1")
    # if (resource('ska_low/tm_subarray_node/1').get('obsState') == "CONFIGURING"):
    #     LOGGER.warn("Subarray is still in configuring! Please restart MVP manualy to complete tear down")
    #     restart_subarray(1)
    #     #raise exception since we are unable to continue with tear down
        # raise Exception("Unable to tear down test setup")
    LOGGER.info("Put Telescope back to standby")
    tmc.set_to_standby()
    LOGGER.info("Telescope is in standby")


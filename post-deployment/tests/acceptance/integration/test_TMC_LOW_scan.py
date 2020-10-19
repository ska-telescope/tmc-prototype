from tango import DeviceProxy   
from datetime import date,datetime
import pytest
import os
import logging
from resources.test_support.helpers_low import waiter,watch,resource, wait_before_test
from resources.test_support.controls_low import telescope_is_in_standby
from resources.test_support.sync_decorators_low import sync_start_up_telescope,sync_assign_resources,sync_configure,sync_end,sync_release_resources,\
    sync_set_to_standby,time_it,sync_scan
from resources.test_support.logging_decorators import log_it
import resources.test_support.tmc_helpers_low as tmc

DEV_TEST_TOGGLE = os.environ.get('DISABLE_DEV_TESTS')
if DEV_TEST_TOGGLE == "False":
    DISABLE_TESTS_UNDER_DEVELOPMENT = False
else:
    DISABLE_TESTS_UNDER_DEVELOPMENT = True

devices_to_log = [
    'ska_low/tm_subarray_node/1',
    'low-mccs/subarray/01']

LOGGER = logging.getLogger(__name__)

@pytest.mark.low
# @pytest.mark.skipif(DISABLE_TESTS_UNDER_DEVELOPMENT, reason="disabaled by local env")
def test_scan():
    
    try:
        # given an interface to TMC to interact with a subarray node and a central node
        wait_before_test(timeout=15)
        fixture = {}
        fixture['state'] = 'Unknown'

        # given a started up telescope
        assert(telescope_is_in_standby())
        LOGGER.info('Starting up the Telescope')
        tmc.start_up()
        fixture['state'] = 'Telescope On'
        wait_before_test(timeout=15)
        # and a subarray composed of two resources configured as perTMC_integration/mccs_assign_resources.json
        LOGGER.info('Composing the Subarray')
        tmc.compose_sub()
        fixture['state'] = 'Subarray Assigned'
        wait_before_test(timeout=10)
        #and a subarray configured to perform a scan as per 'TMC_integration/configure1.json'
        LOGGER.info('Configuring the Subarray')
        fixture['state'] = 'Subarray CONFIGURING'
        configure_file = 'resources/test_data/TMC_integration/mccs_configure.json'
        tmc.configure_sub(configure_file)
        fixture['state'] = 'Subarray Configured for SCAN'
        wait_before_test(timeout=10)
        #When I run a scan of 4 seconds based on previos configuration
        resource('ska_low/tm_subarray_node/1').assert_attribute('obsState').equals('READY')
        LOGGER.info('Starting a scan of 4 seconds')
        fixture['state'] = 'Subarray SCANNING'
        # @log_it('TMC_int_scan',devices_to_log)
        @sync_scan(200)
        def scan():
            SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
            SubarrayNodeLow.Scan('{"id":1}')
        scan()
        LOGGER.info('Scan complete')
        fixture['state'] = 'Subarray Configured for SCAN'
        wait_before_test(timeout=10)
        #tear down
        LOGGER.info('TMC-Scan tests complete: tearing down...')
        tmc.end()
        resource('ska_low/tm_subarray_node/1').assert_attribute('obsState').equals('IDLE')
        LOGGER.info('Invoked End on Subarray')
        wait_before_test(timeout=10)
        tmc.release_resources()
        LOGGER.info('Invoked ReleaseResources on Subarray')
        wait_before_test(timeout=10)
        tmc.set_to_standby()
        LOGGER.info('Invoked StandBy on Subarray')
        wait_before_test(timeout=10)
   
    except:        
        LOGGER.info('Tearing down failed test, state = {}'.format(fixture['state']))
        if fixture['state'] == 'Telescope On':
            tmc.set_to_standby()
        elif fixture['state'] == 'Subarray Assigned':
            tmc.release_resources()
            tmc.set_to_standby()
        elif fixture['state'] == 'Subarray Configured for SCAN':
            tmc.end()
            tmc.release_resources()
            tmc.set_to_standby()
        elif fixture['state'] == 'Subarray SCANNING':
            raise Exception('unable to teardown subarray from being in SCANNING')
        elif fixture['state'] == 'Subarray CONFIGURING':
            raise Exception('unable to teardown subarray from being in CONFIGURING')
        pytest.fail("unable to complete test without exceptions")

from tango import DeviceProxy   
from datetime import date,datetime
import pytest
import os
import logging
from resources.test_support.helpers_low import waiter,watch,resource
from resources.test_support.controls_low import telescope_is_in_standby
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
def test_endscan():
    
    try:
        # given an interface to TMC to interact with a subarray node and a central node
        fixture = {}
        fixture['state'] = 'Unknown'
        # given a started up telescope
        assert(telescope_is_in_standby())
        LOGGER.info('Starting up the Telescope')
        tmc.start_up()
        fixture['state'] = 'Telescope On'
        # and a subarray composed of two resources configured as perTMC_integration/mccs_assign_resources.json
        LOGGER.info('Composing the Subarray')
        tmc.compose_sub()
        fixture['state'] = 'Subarray Assigned'
        #and a subarray configured to perform a scan as per 'TMC_integration/configure1.json'
        LOGGER.info('Configuring the Subarray')
        fixture['state'] = 'Subarray CONFIGURING'
        tmc.configure_sub()
        fixture['state'] = 'Subarray Configured for SCAN'
        #When scan is run for provided duration based on previous configuuration
        resource('ska_low/tm_subarray_node/1').assert_attribute('obsState').equals('READY')
        LOGGER.info('Invoked Scan on Subarray')
        fixture['state'] = 'Subarray SCANNING'
        def endscan():
            SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
            SubarrayNodeLow.Scan('{"id":1}')
            SubarrayNodeLow.EndScan()
        endscan()
        LOGGER.info('EndScan complete')
        fixture['state'] = 'Subarray EndScan invoked'
        #tear down
        LOGGER.info('TMC-EndScan tests complete: tearing down...')
        tmc.end()
        resource('ska_low/tm_subarray_node/1').assert_attribute('obsState').equals('IDLE')
        LOGGER.info('Invoked End on Subarray')
        tmc.release_resources()
        LOGGER.info('Invoked ReleaseResources on Subarray')
        tmc.set_to_standby()
        LOGGER.info('Invoked StandBy on Subarray')
   
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

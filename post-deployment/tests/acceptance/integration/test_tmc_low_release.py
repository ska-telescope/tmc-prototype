from tango import DeviceProxy   
from datetime import date,datetime
import pytest
import os
import logging
from resources.test_support.helpers_low import waiter,watch,resource
from resources.test_support.controls_low import telescope_is_in_standby
from resources.test_support.sync_decorators_low import sync_release_resources
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
def test_release_resources():

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
        @sync_release_resources
        def release_resources():
            CentralNodeLow = DeviceProxy('ska_low/tm_central/central_node')
            CentralNodeLow.ReleaseResources('{"subarray_id":1,"release_all":true}')
            SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
        release_resources()
        LOGGER.info('Release Resources complete')
        fixture['state'] = 'Subarray Configured for RELEASE RESOURCES'
        #tear down
        LOGGER.info('TMC-release resources tests complete: tearing down...')
        tmc.set_to_standby()
        LOGGER.info('Invoked StandBy on Subarray')

    except:        
        LOGGER.info('Tearing down failed test, state = {}'.format(fixture['state']))
        if fixture['state'] == 'Telescope On':
            tmc.set_to_standby()
        elif fixture['state'] == 'Subarray Assigned':
            tmc.release_resources()
            tmc.set_to_standby()
        elif fixture['state'] == 'Release Resources Completed':
            LOGGER.info('Tearing down in , state = {}'.format(fixture['state']))
            tmc.set_to_standby()
        elif fixture['state'] == 'Subarray SCANNING':
            raise Exception('unable to teardown subarray from being in SCANNING')
        elif fixture['state'] == 'Subarray CONFIGURING':
            raise Exception('unable to teardown subarray from being in CONFIGURING')
        pytest.fail("unable to complete test without exceptions")

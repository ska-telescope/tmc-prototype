from resources.test_support.sync_decorators_low import sync_start_up_telescope, sync_assign_resources,\
                    sync_scan, sync_configure, sync_end, sync_release_resources, sync_abort, \
                    sync_obsreset,sync_set_to_standby, time_it
from resources.test_support.logging_decorators import log_it
from tango import DeviceProxy   
from resources.test_support.helpers_low import waiter,watch,resource
from resources.test_support.persistance_helping import load_config_from_file, update_scan_config_file, \
                                                                    update_resource_config_file

import logging

LOGGER = logging.getLogger(__name__)



@sync_start_up_telescope
def start_up():
    CentralNodeLow = DeviceProxy('ska_low/tm_central/central_node')
    LOGGER.info("Before Sending StartupTelescope command on CentralNodeLow state :" + str(CentralNodeLow.State()))   
    CentralNodeLow.StartUpTelescope()

@sync_assign_resources(300)
def compose_sub():
    resource('ska_low/tm_subarray_node/1').assert_attribute('State').equals('ON')
    resource('ska_low/tm_subarray_node/1').assert_attribute('obsState').equals('EMPTY')
    assign_resources_file = 'resources/test_data/TMC_integration/mccs_assign_resources.json'
    config = load_config_from_file(assign_resources_file)
    CentralNodeLow = DeviceProxy('ska_low/tm_central/central_node')
    CentralNodeLow.AssignResources(config)
    the_waiter = waiter()
    the_waiter.wait()
    LOGGER.info('Invoked AssignResources on CentralNodeLow')


@sync_end
def end():
    resource('ska_low/tm_subarray_node/1').assert_attribute('obsState').equals('READY')
    resource('low-mccs/subarray/01').assert_attribute('obsState').equals('READY')
    LOGGER.info('Before invoking End Command all the devices obsstate is ready')
    SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
    SubarrayNodeLow.End()
    LOGGER.info('Invoked End on Subarray')

@sync_release_resources
def release_resources():
    resource('ska_low/tm_subarray_node/1').assert_attribute('obsState').equals('IDLE')
    CentralNodeLow = DeviceProxy('ska_low/tm_central/central_node')
    CentralNodeLow.ReleaseResources('{"subarray_id":1,"release_all":true}')
    SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
    LOGGER.info('After Invoking Release Resource on Subarray, SubarrayNodeLow State and ObsState:' + str(SubarrayNodeLow.State()) + str(SubarrayNodeLow.ObsState))
    the_waiter = waiter()
    the_waiter.wait()
    LOGGER.info('finished ReleaseResources on CentralNodeLow')


@sync_set_to_standby
def set_to_standby():
    CentralNodeLow = DeviceProxy('ska_low/tm_central/central_node')
    CentralNodeLow.StandByTelescope()
    SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
    LOGGER.info('After Standby SubarrayNodeLow State and ObsState:' + str(SubarrayNodeLow.State()) + str(SubarrayNodeLow.ObsState))
    LOGGER.info('After Standby CentralNodeLow State:' + str(CentralNodeLow.State()))
    LOGGER.info('Standby the Telescope')

@sync_configure
def configure_sub():
    #resource('ska_low/tm_subarray_node/1').assert_attribute('State').equals('ON')
    configure_file = 'resources/test_data/TMC_integration/mccs_configure.json'
    config = load_config_from_file(configure_file)
    SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
    SubarrayNodeLow.Configure(config)
    LOGGER.info("Subarray obsState is: " + str(SubarrayNodeLow.obsState))
    LOGGER.info('Invoked Configure on Subarray')

@sync_abort
def abort():
    resource('ska_low/tm_subarray_node/1').assert_attribute('State').equals('ON')
    resource('ska_low/tm_subarray_node/1').assert_attribute('obsState').equals('IDLE')
    SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
    SubarrayNodeLow.Abort()
    LOGGER.info("Subarray obsState is: " + str(SubarrayNodeLow.obsState))
    LOGGER.info('Invoked Abort on Subarray')

@sync_scan(200)
def scan_sub():
    SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
    SubarrayNodeLow.Scan('{"id":1}')
    LOGGER.info('Scan Started')

@sync_abort
def abort_sub():
    SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
    SubarrayNodeLow.Abort()
    LOGGER.info('Abort command invoked on SubarrayNodeLow.')

@sync_obsreset
def ObsReset_sub():
    SubarrayNodeLow = DeviceProxy('ska_low/tm_subarray_node/1')
    SubarrayNodeLow.ObsReset()
    LOGGER.info('ObsReset command invoked on SubarrayNodeLow.')
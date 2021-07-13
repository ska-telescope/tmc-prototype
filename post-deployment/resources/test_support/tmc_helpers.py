# from resources.test_support.sync_decorators import (
#     sync_start_up_telescope,
#     sync_assign_resources,
#     sync_configure,
#     sync_end_sb,
#     sync_release_resources,
#     sync_set_to_standby,
#     time_it,
#     sync_abort,
#     sync_restart,
#     sync_obsreset,
    
# )
# from resources.test_support.logging_decorators import log_it
# from tango import DeviceProxy
# from resources.test_support.helpers import waiter, watch, resource
# from resources.test_support.controls import telescope_is_in_standby
# from resources.test_support.persistance_helping import (
#     load_config_from_file,
#     update_scan_config_file,
#     update_resource_config_file,
# )

# import logging

# LOGGER = logging.getLogger(__name__)


# @sync_start_up_telescope
# def start_up():
#     CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
#     LOGGER.info(
#         "Before Sending StartupTelescope command on CentralNode state :"
#         + str(CentralNode.State())
#     )
#     CentralNode.TelescopeOn()


# @sync_assign_resources(2, 300)
# def compose_sub():
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals("ON")
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals("EMPTY")
#     assign_resources_file = "resources/test_data/TMC_integration/assign_resources1.json"
#     sdp_block = update_resource_config_file(assign_resources_file)
#     LOGGER.info("_______sdp_block________" + str(sdp_block))
#     config = load_config_from_file(assign_resources_file)
#     CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
#     CentralNode.AssignResources(config)
#     the_waiter = waiter()
#     the_waiter.wait()
#     LOGGER.info("Invoked AssignResources on CentralNode")
#     return sdp_block


# @sync_end_sb
# def end_sb():
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals("READY")
#     resource("mid_csp/elt/subarray_01").assert_attribute("obsState").equals("READY")
#     resource("mid_sdp/elt/subarray_1").assert_attribute("obsState").equals("READY")
#     LOGGER.info("Before invoking End Command all the devices obsstate is ready")
#     SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
#     SubarrayNode.End()
#     LOGGER.info("Invoked End on Subarray")


# @sync_release_resources
# def release_resources():
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals("IDLE")
#     CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
#     CentralNode.ReleaseResources(
#         '{"subarrayID":1,"releaseALL":true,"receptorIDList":[]}'
#     )
#     SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
#     LOGGER.info(
#         "After Release Resource SubarrayNode State and ObsState:"
#         + str(SubarrayNode.State())
#         + str(SubarrayNode.ObsState)
#     )
#     LOGGER.info("Invoked ReleaseResources on Subarray")


# @sync_set_to_standby
# def set_to_standby():
#     CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
#     CentralNode.TelescopeOff()
#     SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
#     LOGGER.info(
#         "After Standby SubarrayNode State and ObsState:"
#         + str(SubarrayNode.State())
#         + str(SubarrayNode.ObsState)
#     )
#     LOGGER.info("After Standby CentralNode State:" + str(CentralNode.State()))
#     LOGGER.info("Standby the Telescope")


# @sync_configure
# def configure_sub(sdp_block, configure_file):
#     # resource('ska_mid/tm_subarray_node/1').assert_attribute('State').equals('ON')
#     update_scan_config_file(configure_file, sdp_block)
#     config = load_config_from_file(configure_file)
#     SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
#     SubarrayNode.Configure(config)
#     LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
#     LOGGER.info("Invoked Configure on Subarray")


# @sync_abort
# def abort():
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals("ON")
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals("IDLE")
#     SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
#     SubarrayNode.Abort()
#     LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
#     LOGGER.info("Invoked Abort on Subarray")


# @sync_restart
# def restart():
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals("ON")
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals(
#         "ABORTED"
#     )
#     SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
#     SubarrayNode.restart()
#     LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
#     LOGGER.info("Invoked restart on Subarray")


# @sync_obsreset
# def obsreset():
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals("ON")
#     resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals(
#         "ABORTED"
#     )
#     SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
#     SubarrayNode.ObsReset()
#     LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
#     LOGGER.info("Invoked Obsreset on Subarray")

from resources.test_support.sync_decorators import (
    sync_start_up_telescope,
    sync_assign_resources,
    sync_configure,
    sync_end_sb,
    sync_release_resources,
    sync_set_to_standby,
    time_it,
    sync_abort,
    sync_restart,
    sync_obsreset,
    # sync_tmc_on,
    # sync_tmc_off,
    # sync_tmc_standby
)
from resources.test_support.logging_decorators import log_it
from tango import DeviceProxy
from resources.test_support.helpers import waiter, watch, resource
from resources.test_support.controls import telescope_is_in_standby
from resources.test_support.persistance_helping import (
    load_config_from_file,
    update_scan_config_file,
    update_resource_config_file,
)

import logging

LOGGER = logging.getLogger(__name__)


@sync_start_up_telescope
def start_up():
    CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
    LOGGER.info(
        "Before Sending StartupTelescope command on CentralNode state :"
        + str(CentralNode.State())
    )
    CentralNode.StartUpTelescope()

def set_telescope_on():
    CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
    LOGGER.info(
        "Before Sending TelescopeOn command on CentralNode state :"
        + str(CentralNode.State())
    )
    CentralNode.TelescopeOn()


def set_telescope_off():
    CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
    LOGGER.info(
        "Before Sending TelescopeOff command on CentralNode state :"
        + str(CentralNode.State())
    )
    CentralNode.TelescopeOff()


def set_telescope_standby():
    CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
    LOGGER.info(
        "Before Sending TelescopeStandby command on CentralNode state :"
        + str(CentralNode.State())
    )
    CentralNode.TelescopeStandby()

@sync_assign_resources(2, 600)
def compose_sub():
    resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals("ON")
    resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals("EMPTY")
    assign_resources_file = "resources/test_data/TMC_integration/assign_resources1.json"
    sdp_block = update_resource_config_file(assign_resources_file)
    LOGGER.info("_______sdp_block________" + str(sdp_block))
    config = load_config_from_file(assign_resources_file)
    CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
    CentralNode.AssignResources(config)
    the_waiter = waiter()
    the_waiter.wait()
    LOGGER.info("Invoked AssignResources on CentralNode")
    return sdp_block


@sync_end_sb
def end_sb():
    resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals("READY")
    resource("mid_csp/elt/subarray_01").assert_attribute("obsState").equals("READY")
    resource("mid_sdp/elt/subarray_1").assert_attribute("obsState").equals("READY")
    LOGGER.info("Before invoking End Command all the devices obsstate is ready")
    SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
    SubarrayNode.End()
    LOGGER.info("Invoked End on Subarray")


@sync_release_resources
def release_resources():
    resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals("IDLE")
    CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
    CentralNode.ReleaseResources(
        '{"subarrayID":1,"releaseALL":true,"receptorIDList":[]}'
    )
    SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
    LOGGER.info(
        "After Release Resource SubarrayNode State and ObsState:"
        + str(SubarrayNode.State())
        + str(SubarrayNode.ObsState)
    )
    LOGGER.info("Invoked ReleaseResources on Subarray")


@sync_set_to_standby
def set_to_standby():
    print("INSIDE SET TO STANDBY----")
    CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
    CentralNode.StandByTelescope()
    SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
    LOGGER.info(
        "After Standby SubarrayNode State and ObsState:"
        + str(SubarrayNode.State())
        + str(SubarrayNode.ObsState)
    )
    LOGGER.info("After Standby CentralNode State:" + str(CentralNode.State()))
    LOGGER.info("Standby the Telescope")


@sync_configure
def configure_sub(sdp_block, configure_file):
    # resource('ska_mid/tm_subarray_node/1').assert_attribute('State').equals('ON')
    update_scan_config_file(configure_file, sdp_block)
    config = load_config_from_file(configure_file)
    SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
    SubarrayNode.Configure(config)
    LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
    LOGGER.info("Invoked Configure on Subarray")


@sync_abort
def abort():
    resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals("ON")
    resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals("IDLE")
    SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
    SubarrayNode.Abort()
    LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
    LOGGER.info("Invoked Abort on Subarray")


@sync_restart
def restart():
    resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals("ON")
    resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals(
        "ABORTED"
    )
    SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
    SubarrayNode.restart()
    LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
    LOGGER.info("Invoked restart on Subarray")


@sync_obsreset
def obsreset():
    resource("ska_mid/tm_subarray_node/1").assert_attribute("State").equals("ON")
    resource("ska_mid/tm_subarray_node/1").assert_attribute("obsState").equals(
        "ABORTED"
    )
    SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
    SubarrayNode.ObsReset()
    LOGGER.info("Subarray obsState is: " + str(SubarrayNode.obsState))
    LOGGER.info("Invoked Obsreset on Subarray")


#Note: make use of this method while updating integration tests for sp-1623
# @sync_tmc_on
# def set_tmc_on():
#     CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
#     LOGGER.info(
#         "Before Sending ON command on CentralNode state :"
#         + str(CentralNode.State())
#     )
#     CentralNode.On()


# #Note: make use of this method while updating integration tests for sp-1623
# @sync_tmc_off
# def set_tmc_off():
#     CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
#     CentralNode.Off()
#     SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
#     LOGGER.info(
#         "After Off command, SubarrayNode State and ObsState:"
#         + str(SubarrayNode.State())
#         + str(SubarrayNode.ObsState)
#     )
#     LOGGER.info("After Off command, CentralNode State:" + str(CentralNode.State()))
#     LOGGER.info("TMC is OFF")


# #Note: make use of this method while updating integration tests for sp-1623
# @sync_tmc_standby
# def set_tmc_standby():
#     CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
#     CentralNode.Standby()
#     SubarrayNode = DeviceProxy("ska_mid/tm_subarray_node/1")
#     CspSubarrayLeafNode = DeviceProxy("ska_mid/tm_leaf_node/csp_subarray01")
#     SdpSubarrayLeafNode = DeviceProxy("ska_mid/tm_leaf_node/sdp_subarray01")
#     CspMasterLeafNode = DeviceProxy("ska_mid/tm_leaf_node/csp_master")
#     SdpMasterLeafNode = DeviceProxy("ska_mid/tm_leaf_node/sdp_master")
#     LOGGER.info(
#         "After Standby command, SubarrayNode State and ObsState:"
#         + str(SubarrayNode.State())
#         + str(SubarrayNode.ObsState)
#     )
#     LOGGER.info(
#         "After Standby command, CspSubarrayLeafNode State and ObsState:"
#         + str(CspSubarrayLeafNode.State())
#         + str(CspSubarrayLeafNode.ObsState)
#     )
#     LOGGER.info(
#         "After Standby command, SdpSubarrayLeafNode State and ObsState:"
#         + str(SdpSubarrayLeafNode.State())
#         + str(SdpSubarrayLeafNode.ObsState)
#     )
#     LOGGER.info(
#         "After Standby command, CspMasterLeafNode State and ObsState:"
#         + str(CspMasterLeafNode.State())
#         + str(CspMasterLeafNode.ObsState)
#     )
#     LOGGER.info(
#         "After Standby command, SdpMasterLeafNode State and ObsState:"
#         + str(SdpMasterLeafNode.State())
#         + str(SdpMasterLeafNode.ObsState)
#     )
#     LOGGER.info("After Standby command, CentralNode State:" + str(CentralNode.State()))
#     LOGGER.info("TMC is in Standby")


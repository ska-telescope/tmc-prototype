import pytest
from datetime import date, datetime
import os
import logging


##local depencies
from resources.test_support.helpers import (
    subarray_devices,
    resource,
    ResourceGroup,
    waiter,
    watch,
)
from resources.test_support.persistance_helping import (
    update_scan_config_file,
    update_resource_config_file,
)
from resources.test_support.sync_decorators import (
    sync_assign_resources,
    sync_configure_oet,
    time_it,
    sync_release_resources,
    sync_end_sb,
    sync_scan_oet,
    sync_restart_sa,
)
from resources.test_support.mappings import device_to_subarrays

LOGGER = logging.getLogger(__name__)


def telescope_is_in_standby():
    LOGGER.info(
        'resource("ska_mid/tm_subarray_node/1").get("State")'
        + str(resource("ska_mid/tm_subarray_node/1").get("State"))
    )
    LOGGER.info(
        'resource("mid_csp/elt/subarray_01").get("State")'
        + str(resource("mid_csp/elt/subarray_01").get("State"))
    )
    LOGGER.info(
        'resource("mid_csp_cbf/sub_elt/subarray_01").get("State")'
        + str(resource("mid_csp_cbf/sub_elt/subarray_01").get("State"))
    )
    LOGGER.info(
        'resource("mid_sdp/elt/subarray_1").get("State")'
        + str(resource("mid_sdp/elt/subarray_1").get("State"))
    )
    # TODO: Check for sdp Subarray state to be added
    return [
        resource("ska_mid/tm_subarray_node/1").get("State"),
        resource("mid_csp/elt/subarray_01").get("State"),
        resource("mid_csp_cbf/sub_elt/subarray_01").get("State"),
    ] == ["OFF", "OFF", "OFF"]


#Note: make use of this method while updatating integration tests for sp-1623
def tmc_is_in_off():
    LOGGER.info(
        'resource("ska_mid/tm_central/central_node").get("State")'
        + str(resource("ska_mid/tm_central/central_node").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_subarray_node/1").get("State")'
        + str(resource("ska_mid/tm_subarray_node/1").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/csp_subarray01").get("State")'
        + str(resource("ska_mid/tm_leaf_node/csp_subarray01").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/sdp_subarray01").get("State")'
        + str(resource("ska_mid/tm_leaf_node/sdp_subarray01").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/csp_master").get("State")'
        + str(resource("ska_mid/tm_leaf_node/csp_master").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/sdp_master").get("State")'
        + str(resource("ska_mid/tm_leaf_node/sdp_master").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0001").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0001").get("State"))
    )
    return [
        resource("ska_mid/tm_central/central_node").get("State"),
        resource("ska_mid/tm_subarray_node/1").get("State"),
        resource("ska_mid/tm_leaf_node/csp_subarray01").get("State"),
        resource("ska_mid/tm_leaf_node/sdp_subarray01").get("State"),
        resource("ska_mid/tm_leaf_node/csp_master").get("State"),
        resource("ska_mid/tm_leaf_node/sdp_master").get("State"),
        resource("ska_mid/tm_leaf_node/d0001").get("State"),
    ] == ["OFF", "OFF", "OFF", "OFF", "OFF", "OFF", "OFF"]



#Note: make use of this method while updatating integration tests for sp-1623
def tmc_is_in_on():
    LOGGER.info(
        'resource("ska_mid/tm_central/central_node").get("State")'
        + str(resource("ska_mid/tm_central/central_node").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_subarray_node/1").get("State")'
        + str(resource("ska_mid/tm_subarray_node/1").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/csp_subarray01").get("State")'
        + str(resource("ska_mid/tm_leaf_node/csp_subarray01").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/sdp_subarray01").get("State")'
        + str(resource("ska_mid/tm_leaf_node/sdp_subarray01").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/csp_master").get("State")'
        + str(resource("ska_mid/tm_leaf_node/csp_master").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/sdp_master").get("State")'
        + str(resource("ska_mid/tm_leaf_node/sdp_master").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0001").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0001").get("State"))
    )
    return [
        resource("ska_mid/tm_central/central_node").get("State"),
        resource("ska_mid/tm_subarray_node/1").get("State"),
        resource("ska_mid/tm_leaf_node/csp_subarray01").get("State"),
        resource("ska_mid/tm_leaf_node/sdp_subarray01").get("State"),
        resource("ska_mid/tm_leaf_node/csp_master").get("State"),
        resource("ska_mid/tm_leaf_node/sdp_master").get("State"),
        resource("ska_mid/tm_leaf_node/d0001").get("State"),
    ] == ["ON", "ON", "ON", "ON", "ON", "ON", "ON"]

#Note: make use of this method while updatating integration tests for sp-1623
def telescope_is_on():
    LOGGER.info(
        'resource("ska_mid/tm_central/central_node").get("State")'
        + str(resource("ska_mid/tm_central/central_node").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_subarray_node/1").get("State")'
        + str(resource("ska_mid/tm_subarray_node/1").get("State"))
    )
    LOGGER.info(
        'resource("mid_csp/elt/subarray_01").get("State")'
        + str(resource("mid_csp/elt/subarray_01").get("State"))
    )
    LOGGER.info(
        'resource("mid_csp_cbf/sub_elt/subarray_01").get("State")'
        + str(resource("mid_csp_cbf/sub_elt/subarray_01").get("State"))
    )
    LOGGER.info(
        'resource("mid_sdp/elt/subarray_1").get("State")'
        + str(resource("mid_sdp/elt/subarray_1").get("State"))
    )
    LOGGER.info(
        'resource("mid_csp/elt/master").get("State")'
        + str(resource("mid_csp/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_sdp/elt/master").get("State")'
        + str(resource("mid_sdp/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0001").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0001").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0002").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0002").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0003").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0003").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0004").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0004").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0001/elt/master").get("State")'
        + str(resource("mid_d0001/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0002/elt/master").get("State")'
        + str(resource("mid_d0002/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0003/elt/master").get("State")'
        + str(resource("mid_d0003/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0004/elt/master").get("State")'
        + str(resource("mid_d0004/elt/master").get("State"))
    )
    return [
        resource("ska_mid/tm_central/central_node").get("State"),
        resource("ska_mid/tm_subarray_node/1").get("State"),
        resource("mid_csp/elt/subarray_01").get("State"),
        resource("mid_sdp/elt/subarray_1").get("State"),
        resource("mid_csp/elt/master").get("State"),
        resource("mid_sdp/elt/master").get("State"),
        resource("ska_mid/tm_leaf_node/d0001").get("State"),
        resource("ska_mid/tm_leaf_node/d0002").get("State"),
        resource("ska_mid/tm_leaf_node/d0003").get("State"),
        resource("ska_mid/tm_leaf_node/d0004").get("State"),
        resource("mid_d0001/elt/master").get("State"),
        resource("mid_d0002/elt/master").get("State"),
        resource("mid_d0003/elt/master").get("State"),
        resource("mid_d0004/elt/master").get("State")
    ] == ["ON", "ON", "ON", "ON", "ON", "ON", "ON", "ON", "ON", "ON", "ON", "ON", "ON", "ON"]

#Note: make use of this method while updatating integration tests for sp-1623
def telescope_is_off():
    LOGGER.info(
        'resource("ska_mid/tm_central/central_node").get("State")'
        + str(resource("ska_mid/tm_central/central_node").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_subarray_node/1").get("State")'
        + str(resource("ska_mid/tm_subarray_node/1").get("State"))
    )
    LOGGER.info(
        'resource("mid_csp/elt/subarray_01").get("State")'
        + str(resource("mid_csp/elt/subarray_01").get("State"))
    )
    LOGGER.info(
        'resource("mid_sdp/elt/subarray_1").get("State")'
        + str(resource("mid_sdp/elt/subarray_1").get("State"))
    )
    LOGGER.info(
        'resource("mid_csp/elt/master").get("State")'
        + str(resource("mid_csp/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_sdp/elt/master").get("State")'
        + str(resource("mid_sdp/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0001").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0001").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0002").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0002").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0003").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0003").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0004").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0004").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0001/elt/master").get("State")'
        + str(resource("mid_d0001/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0002/elt/master").get("State")'
        + str(resource("mid_d0002/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0003/elt/master").get("State")'
        + str(resource("mid_d0003/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0004/elt/master").get("State")'
        + str(resource("mid_d0004/elt/master").get("State"))
    )
    return [
        resource("ska_mid/tm_central/central_node").get("State"),
        resource("ska_mid/tm_subarray_node/1").get("State"),
        resource("mid_csp/elt/subarray_01").get("State"),
        resource("mid_sdp/elt/subarray_1").get("State"),
        resource("mid_csp/elt/master").get("State"),
        resource("mid_sdp/elt/master").get("State"),
        resource("mid_d0001/elt/master").get("State"),
        resource("mid_d0002/elt/master").get("State"),
        resource("mid_d0003/elt/master").get("State"),
        resource("mid_d0004/elt/master").get("State")
    ] == ["ON", "ON", "OFF", "OFF", "STANDBY", "OFF", "STANDBY", "STANDBY", "STANDBY", "STANDBY"]

def telescope_is_standby():
    LOGGER.info(
        'resource("ska_mid/tm_central/central_node").get("State")'
        + str(resource("ska_mid/tm_central/central_node").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_subarray_node/1").get("State")'
        + str(resource("ska_mid/tm_subarray_node/1").get("State"))
    )
    LOGGER.info(
        'resource("mid_csp/elt/subarray_01").get("State")'
        + str(resource("mid_csp/elt/subarray_01").get("State"))
    )
    LOGGER.info(
        'resource("mid_sdp/elt/subarray_1").get("State")'
        + str(resource("mid_sdp/elt/subarray_1").get("State"))
    )
    LOGGER.info(
        'resource("mid_csp/elt/master").get("State")'
        + str(resource("mid_csp/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_sdp/elt/master").get("State")'
        + str(resource("mid_sdp/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0001").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0001").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0002").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0002").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0003").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0003").get("State"))
    )
    LOGGER.info(
        'resource("ska_mid/tm_leaf_node/d0004").get("State")'
        + str(resource("ska_mid/tm_leaf_node/d0004").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0001/elt/master").get("State")'
        + str(resource("mid_d0001/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0002/elt/master").get("State")'
        + str(resource("mid_d0002/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0003/elt/master").get("State")'
        + str(resource("mid_d0003/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0004/elt/master").get("State")'
        + str(resource("mid_d0004/elt/master").get("State"))
    )
    return [
        resource("ska_mid/tm_central/central_node").get("State"),
        resource("ska_mid/tm_subarray_node/1").get("State"),
        resource("mid_csp/elt/subarray_01").get("State"),
        resource("mid_sdp/elt/subarray_1").get("State"),
        resource("mid_csp/elt/master").get("State"),
        resource("mid_sdp/elt/master").get("State"),
        resource("mid_d0001/elt/master").get("State"),
        resource("mid_d0002/elt/master").get("State"),
        resource("mid_d0003/elt/master").get("State"),
        resource("mid_d0004/elt/master").get("State")
    ] == ["ON", "ON", "OFF", "OFF", "STANDBY", "STANDBY", "STANDBY", "STANDBY", "STANDBY", "STANDBY"]

def telescope_state_after_telescope_on():
    LOGGER.info(
        'resource("ska_mid/tm_central/central_node").get("telescopeState")'
        + str(resource("ska_mid/tm_central/central_node").get("telescopeState"))
    )
    LOGGER.info(
        'resource("mid_csp/elt/master").get("State")'
        + str(resource("mid_csp/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_sdp/elt/master").get("State")'
        + str(resource("mid_sdp/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0001/elt/master").get("State")'
        + str(resource("mid_d0001/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0002/elt/master").get("State")'
        + str(resource("mid_d0002/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0003/elt/master").get("State")'
        + str(resource("mid_d0003/elt/master").get("State"))
    )
    LOGGER.info(
        'resource("mid_d0004/elt/master").get("State")'
        + str(resource("mid_d0004/elt/master").get("State"))
    )
    return [
        resource("ska_mid/tm_central/central_node").get("telescopeState")
    ] == ["ON"]

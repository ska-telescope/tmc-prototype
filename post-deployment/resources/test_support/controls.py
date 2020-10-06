import pytest
from datetime import date,datetime
import os
import logging


##local depencies
from resources.test_support.helpers import subarray_devices,resource,ResourceGroup,waiter,watch
from resources.test_support.persistance_helping import update_scan_config_file,update_resource_config_file
from resources.test_support.sync_decorators import sync_assign_resources,sync_configure_oet,time_it,\
    sync_release_resources,sync_end_sb,sync_scan_oet,sync_restart_sa
from resources.test_support.mappings import device_to_subarrays

LOGGER = logging.getLogger(__name__)

def take_subarray(id):
    return pilot(id)


def telescope_is_in_standby():
    LOGGER.info('resource("ska_mid/tm_subarray_node/1").get("State")'+ str(resource('ska_mid/tm_subarray_node/1').get("State")))
    LOGGER.info('resource("mid_csp/elt/subarray_01").get("State")' +
                str(resource('mid_csp/elt/subarray_01').get("State")))
    LOGGER.info('resource("mid_csp_cbf/sub_elt/subarray_01").get("State")' +
                str(resource('mid_csp_cbf/sub_elt/subarray_01').get("State")))

    return  [resource('ska_mid/tm_subarray_node/1').get("State"),
            resource('mid_csp/elt/subarray_01').get("State"),
            resource('mid_csp_cbf/sub_elt/subarray_01').get("State")] == \
            ['OFF','OFF','OFF']
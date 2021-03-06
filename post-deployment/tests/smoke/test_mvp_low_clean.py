import os, sys
import logging
import pytest
from assertpy import assert_that
from  functools import reduce
from resources.test_support.helpers_low import resource, subarray_devices

LOGGER = logging.getLogger(__name__)


####typical device sets
# subarray_devices = [
#         'ska_mid/tm_subarray_node/1',
#         'mid_csp/elt/subarray_01',
#         'mid_csp_cbf/sub_elt/subarray_01',
#         'mid_sdp/elt/subarray_1']

@pytest.mark.select
@pytest.mark.first
@pytest.mark.last
@pytest.mark.low
def test_smell_mvp(pre_or_post="#PRE"):

    header = f"\n###{pre_or_post}-TEST STATES###\n{'Device Name:':<34} {'State':<15}{'obsState':<15}\n"
    output = [f"{device:<35}{resource(device).get('State'):<15}{resource(device).get('obsState'):<15}" for device in subarray_devices]
    aggegate_output = reduce(lambda x,y:x +'\n'+y ,output)
    LOGGER.info(f'Current state of the MVP LOW:{header+aggegate_output}')

    assert_that(resource('ska_low/tm_subarray_node/1').get('State')).is_equal_to(resource('ska_low/tm_subarray_node/1').get('State'))
    assert_that(resource('low-mccs/subarray/01').get('State')).is_equal_to(resource('low-mccs/subarray/01').get('State'))

@pytest.mark.select   
@pytest.mark.last
def test_smell_mvp_after():
    test_smell_mvp("POST")
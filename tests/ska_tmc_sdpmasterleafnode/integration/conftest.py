"""Conftest file for SDP Master Leaf Node"""
import logging

import pytest
import tango
from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.test_helpers.helper_state_device import HelperStateDevice
from tango.test_context import MultiDeviceTestContext


@pytest.fixture
def devices_to_load():
    """Returns all devices to load"""
    return (
        {
            "class": HelperStateDevice,
            "devices": [
                {"name": "mid_sdp/elt/master"},
                {"name": "low_sdp/elt/master"},
                {"name": "ska_low/tm_leaf_node/sdp_master"},
                {"name": "ska_mid/tm_leaf_node/sdp_master"},
            ],
        },
    )


@pytest.fixture
def tango_context(devices_to_load, request):
    """Provide context to run devices without database"""
    true_context = request.config.getoption("--true-context")
    logging.info("true context: %s", true_context)
    if not true_context:
        with MultiDeviceTestContext(devices_to_load, process=False) as context:
            DevFactory._test_context = context
            logging.info("test context set")
            yield context
    else:
        yield None
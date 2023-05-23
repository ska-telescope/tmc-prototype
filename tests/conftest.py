# pylint: disable=unused-argument
"""Conftest file for SDP Leaf Node"""
import json
import logging
from os.path import dirname, join

import pytest
import tango
from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.test_helpers.helper_state_device import HelperStateDevice
from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)
from tango.test_context import MultiDeviceTestContext
from tango.test_utils import DeviceTestContext

from ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node import (
    SdpSubarrayLeafNode,
)


def pytest_sessionstart(session):
    """
    Pytest hook; prints info about tango version.
    :param session: a pytest Session object
    :type session: :py:class:`pytest.Session`
    """
    print(tango.utils.info())


def pytest_addoption(parser):
    """
    Pytest hook; implemented to add the `--true-context` option, used to
    indicate that a true Tango subsystem is available, so there is no
    need for a :py:class:`tango.test_context.MultiDeviceTestContext`.
    :param parser: the command line options parser
    :type parser: :py:class:`argparse.ArgumentParser`
    """
    parser.addoption(
        "--true-context",
        action="store_true",
        default=False,
        help=(
            "Tell pytest that you have a true Tango context and don't "
            "need to spin up a Tango test context"
        ),
    )


@pytest.fixture
def sdp_master_device():
    """Return SDP Master Device"""
    return "mid-sdp/control/0"


@pytest.fixture
def csp_master_device():
    """Return CSP Master Device"""
    return "mid_csp/elt/master"


# pylint: disable=redefined-outer-name
@pytest.fixture()
def devices_to_load():
    """Returns all devices to load"""
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": "mid-sdp/subarray/01"},
                {"name": "low-sdp/subarray/01"},
            ],
        },
        {
            "class": HelperStateDevice,
            "devices": [
                {"name": "mid-sdp/control/0"},
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


# pylint: enable=redefined-outer-name


@pytest.fixture
def sdpsln_device(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(SdpSubarrayLeafNode) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "SdpSubarrayLeafNode"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


@pytest.fixture(scope="session")
def sdp_subarray_device():
    """Returns SDP Subarray 1 device name"""
    return "mid-sdp/subarray/01"


def get_input_str(path):
    """
    Returns input json string
    :rtype: String
    """
    with open(path, "r", encoding="utf-8") as f:
        input_arg = json.load(f)
    return json.dumps(input_arg)


@pytest.fixture
def json_factory():
    """
    Json factory for getting json files
    """

    def _get_json(slug):
        return get_input_str(join(dirname(__file__), "data", f"{slug}.json"))

    return _get_json

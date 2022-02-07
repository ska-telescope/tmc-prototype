# pylint: disable=unused-argument
import logging

import pytest
import tango
from ska_tmc_common.dev_factory import DevFactory

# from tests.helpers.helper_subarray_device import HelperSubArrayDevice
from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)
from tango.test_context import MultiDeviceTestContext


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


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": "mid_sdp/elt/subarray_1"},
                {"name": "mid_sdp/elt/master"},
            ],
        },
    )


@pytest.fixture
def tango_context(devices_to_load, request):
    true_context = request.config.getoption("--true-context")
    logging.info("true context: %s", true_context)
    if not true_context:
        with MultiDeviceTestContext(devices_to_load, process=False) as context:
            DevFactory._test_context = context
            logging.info("test context set")
            yield context
    else:
        yield None

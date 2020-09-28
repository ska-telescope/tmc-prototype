# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #

# Standard Python imports
import contextlib
import importlib
import types
import sys
import mock
from mock import Mock, MagicMock

# Tango imports
import pytest
import tango
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from mccsmasterleafnode import MccsMasterLeafNode, const, release
from ska.base.control_model import HealthState
from ska.base.control_model import LoggingLevel

# PROTECTED REGION END #    //  MccsMasterLeafNode imports

@pytest.fixture(scope="function")
def tango_context():
    with fake_tango_system(MccsMasterLeafNode) as tango_context:
        yield tango_context

def test_read_activity_message(tango_context):
    # act & assert:
    tango_context.device.activityMessage = 'test'
    assert tango_context.device.activityMessage == 'test'


def test_write_activity_message(tango_context):
    # act & assert:
    tango_context.device.activityMessage = 'test'
    assert tango_context.device.activityMessage == 'test'

@contextlib.contextmanager
def fake_tango_system(device_under_test, initial_dut_properties={}, proxies_to_mock={},
                      device_proxy_import_path='tango.DeviceProxy'):
    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()

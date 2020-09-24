# Path
import contextlib
import importlib
import sys
import os
import pytest
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
import mock
from mock import Mock
from mock import MagicMock
from PyTango import DevFailed, DevState
from devicetest import DeviceTestCase, main
from MCCSMasterLeafNode import MCCSMasterLeafNode,const, release
from ska.base.control_model import HealthState, ObsState, LoggingLevel
from tango.test_context import DeviceTestContext


@pytest.fixture(scope="function")
def event_subscription_with_arg(mock_mccs_subarray):
    event_subscription_map = {}
    mock_mccs_subarray[1].command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def event_subscription_without_arg(mock_mccs_subarray):
    event_subscription_map = {}
    mock_mccs_subarray[1].command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def mock_mccs_subarray():
    mccs_subarray1_fqdn = "low_mccs/elt/subarray_01"
    dut_properties = {
        'MCCSSubarrayFQDN': mccs_subarray1_fqdn
    }
    mccs_subarray1_proxy_mock = Mock()
    proxies_to_mock = {
        mccs_subarray1_fqdn: mccs_subarray1_proxy_mock
    }
    with fake_tango_system(MCCSMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, mccs_subarray1_proxy_mock


def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def test_End_command_with_callback_method(mock_mccs_subarray, event_subscription_without_arg):
    # arrange:
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.End()
    dummy_event = command_callback(const.CMD_END)
    event_subscription_without_arg[const.CMD_END](dummy_event)
    assert const.STR_COMMAND + const.CMD_END in device_proxy.activityMessage
    assert mccs_subarray1_proxy_mock.obsState == ObsState.IDLE


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



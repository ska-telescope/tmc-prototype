# Standard Python imports
import contextlib
import importlib
import sys
import json
import types
import pytest
import tango
import mock
from mock import Mock
from mock import MagicMock
from os.path import dirname, join

# Tango imports
from tango.test_context import DeviceTestContext

# Additional import
from mccssubarrayleafnode import MccsSubarrayLeafNode, const, release
from ska.base.control_model import HealthState, ObsState, LoggingLevel


# scan_input_file= 'command_Scan.json'
# path= join(dirname(__file__), 'data', scan_input_file)
# with open(path, 'r') as f:
#     scan_input_str=f.read()


@pytest.fixture(scope="function")
def event_subscription(mock_mccs_subarray):
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
        'MccsSubarrayFQDN': mccs_subarray1_fqdn
    }
    mccs_subarray1_proxy_mock = Mock()
    proxies_to_mock = {
        mccs_subarray1_fqdn: mccs_subarray1_proxy_mock
    }
    with fake_tango_system(MccsSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, mccs_subarray1_proxy_mock


def test_start_scan_should_command_mccs_subarray_to_start_its_scan_when_it_is_ready(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    scan_input_str = '{"id":1}'
    device_proxy.Scan(scan_input_str)
    assert const.STR_STARTSCAN_SUCCESS in device_proxy.activityMessage


def test_startscan_command_with_callback_method(mock_mccs_subarray , event_subscription):
    # arrange:
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    scan_input_str = '{"id":1}'
    device_proxy.Scan(scan_input_str)
    dummy_event = command_callback(const.CMD_STARTSCAN)
    event_subscription[const.CMD_STARTSCAN](dummy_event)
    assert const.STR_COMMAND + const.CMD_STARTSCAN in device_proxy.activityMessage


def test_startscan_command_with_callback_method_with_event_error(mock_mccs_subarray, event_subscription ):
    # arrange:
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    scan_input_str = '{"id":1}'
    device_proxy.Scan(scan_input_str)
    dummy_event = command_callback_with_event_error(const.CMD_STARTSCAN)
    event_subscription[const.CMD_STARTSCAN](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_STARTSCAN in device_proxy.activityMessage


def test_start_scan_should_not_command_mccs_subarray_to_start_scan_when_it_is_idle(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.IDLE
    scan_input_str = '{"id":1}'
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Scan(scan_input_str)
    # assert_activity_message(device_proxy , const.ERR_DEVICE_NOT_READY)
    assert const.ERR_DEVICE_NOT_READY in str(df)


def test_Scan_should_raise_devfailed_exception(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    mccs_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    scan_input_str = '{"id":1}'
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Scan(scan_input_str)
    assert "raise_devfailed_exception" in str(df)


def test_End_command_with_callback_method(mock_mccs_subarray, event_subscription_without_arg):
    # arrange:
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.End()
    dummy_event = command_callback(const.CMD_END)
    event_subscription_without_arg[const.CMD_END](dummy_event)
    assert const.STR_COMMAND + const.CMD_END in device_proxy.activityMessage


def test_end_command_with_callback_method_with_event_error(mock_mccs_subarray,event_subscription_without_arg):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.End()
    dummy_event = command_callback_with_event_error(const.CMD_END)
    event_subscription_without_arg[const.CMD_END](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_END in device_proxy.activityMessage


def test_end_should_command_mccs_subarray_to_reset_when_it_is_ready(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.End()
    mccs_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_END,
                                                                any_method(with_name='end_cmd_ended_cb'))


def test_end_should_raise_devfailed_exception(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    mccs_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.End()
    assert const.ERR_END_INVOKING_CMD in str(df)


def test_endscan_should_command_mccs_subarray_to_end_scan_when_it_is_scanning(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.EndScan()
    mccs_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ENDSCAN,
                                                                any_method(with_name='endscan_cmd_ended_cb'))


def test_endscan_command_with_callback_method(mock_mccs_subarray , event_subscription):
    # arrange:
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.EndScan()
    dummy_event = command_callback(const.CMD_ENDSCAN)
    event_subscription[const.CMD_ENDSCAN](dummy_event)
    assert const.STR_COMMAND + const.CMD_ENDSCAN in device_proxy.activityMessage


def test_endscan_should_raise_devfailed_exception(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.SCANNING
    mccs_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.EndScan()
    assert const.ERR_ENDSCAN_COMMAND in str(df)


def test_endscan_command_with_callback_method_with_event_error(mock_mccs_subarray, event_subscription_without_arg):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.EndScan()
    dummy_event = command_callback_with_event_error(const.CMD_ENDSCAN)
    event_subscription_without_arg[const.CMD_ENDSCAN](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_ENDSCAN in device_proxy.activityMessage


def test_end_scan_should_not_command_mccs_subarray_to_end_scan_when_it_is_idle(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.IDLE
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.EndScan()
    # assert_activity_message(device_proxy , const.ERR_DEVICE_NOT_READY)
    assert const.ERR_DEVICE_NOT_SCANNING in str(df)


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False
            return other.__func__.__name__ == with_name if with_name else True
    return AnyMethod()


def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_event_error(command_name):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Event error in Command Callback'
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def raise_devfailed_exception_with_arg(cmd_name, input_str):
    tango.Except.throw_exception("MccsSubarrayLeafNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)


def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute



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
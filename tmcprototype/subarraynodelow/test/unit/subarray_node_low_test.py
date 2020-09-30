# Standard Python imports
import contextlib
import importlib
import sys
import json
import types
import time
import pytest
import mock
from mock import Mock, MagicMock
from os.path import dirname, join
import threading

# Tango imports
import tango
from tango import DevState, DeviceData, DevString, DevVarStringArray
from tango.test_context import DeviceTestContext

# Additional import
from subarraynodelow import SubarrayNode, const, release
from ska.base.control_model import AdminMode, HealthState, ObsState, ObsMode, TestMode, SimulationMode, \
    LoggingLevel
from subarraynodelow.exceptions import InvalidObsStateError


assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

scan_input_file= 'command_Scan.json'
path= join(dirname(__file__), 'data', scan_input_file)
with open(path, 'r') as f:
    scan_input_str=f.read()


configure_input_file= 'command_Configure.json'
path= join(dirname(__file__), 'data' , configure_input_file)
with open(path, 'r') as f:
    configure_str=f.read()


def set_timeout_event(timeout_event):
    timeout_event.set()


def wait_for(tango_context, obs_state_to_change, timeout=10):
    timer_event = threading.Event()
    timer_thread = threading.Timer(timeout, set_timeout_event, timer_event)
    timer_thread.start()

    # wait till timeout or obsState to change
    while (not timer_event.isSet() and tango_context.device.obsState != obs_state_to_change):
        print("tango_context.device.obsState: ", tango_context.device.obsState)
        continue

    if timer_event.isSet():
        return "timeout"
    else:
        timer_thread.cancel()
        return True


def test_scan_id():
    """Test for scanID"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.scanID == ""


def test_read_activity_message():
    """Test for activityMessage"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.activityMessage == const.STR_SA_INIT_SUCCESS


def test_write_activity_message():
    """Test for activityMessage"""
    with fake_tango_system(SubarrayNode) as tango_context:
        tango_context.device.activityMessage = 'test'
        assert tango_context.device.activityMessage == 'test'


# Test cases for Commands
def test_on_command_should_change_subarray_device_state_to_on():
    with fake_tango_system(SubarrayNode) as tango_context:
        tango_context.device.On()
        assert tango_context.device.state() == DevState.ON
        assert tango_context.device.obsState == ObsState.EMPTY

def test_off_command_should_change_subarray_device_state_to_off():
    with fake_tango_system(SubarrayNode) as tango_context:
        tango_context.device.On()
        tango_context.device.Off()
        assert tango_context.device.state() == DevState.OFF
        assert tango_context.device.obsState == ObsState.EMPTY

def test_start_scan_should_command_subarray_to_start_scan_when_it_is_ready(mock_lower_devices):
    tango_context, mccs_subarray1_ln_proxy_mock, mccs_subarray1_proxy_mock, mccs_subarray1_ln_fqdn, mccs_subarray1_fqdn, event_subscription_map = mock_lower_devices
    mccs_subarray1_obsstate_attribute = "mccsSubarrayObsState"
    tango_context.device.On()
    # Assign Resources to the Subarray which change the obsState to RESOURCING
    tango_context.device.AssignResources(assign_input_str)
    # Mock the behaviour of ObsState of Mccs Subarray to change the ObsState to IDLE
    # Marking Assign Resources Command Completed
    attribute = 'ObsState'
    dummy_event_mccs = create_dummy_event_state(mccs_subarray1_ln_proxy_mock, mccs_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[mccs_subarray1_obsstate_attribute](dummy_event_mccs)
    # Check the ObsState changes to IDLE
    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    # Confiure subarray with correct configuration which will change the obsState to CONFIGURING
    tango_context.device.Configure(configure_str)
    # Mock the behaviour of ObsState of Csp and Sdp Subarray to change the ObsState to READY
    # Marking Configure Command Completed
    attribute = 'ObsState'
    dummy_event_mccs = create_dummy_event_state(mccs_subarray1_ln_proxy_mock, mccs_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[mccs_subarray1_obsstate_attribute](dummy_event_mccs)

    # Check the ObsState changes to READY
    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY

    # Now subarrayNode obsState is READY we can send Scan() command which will change the
    # obsState to Scanning
    tango_context.device.Scan(scan_input_str)
    # Check the ObsState changes to SCANNING
    wait_for(tango_context, ObsState.SCANNING)
    mccs_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_SCAN, scan_input_str)
    assert tango_context.device.obsState == ObsState.SCANNING


def test_start_scan_should_raise_devfailed_exception(mock_lower_devices):
    tango_context, mccs_subarray1_ln_proxy_mock, mccs_subarray1_proxy_mock, mccs_subarray1_ln_fqdn, mccs_subarray1_fqdn, event_subscription_map = mock_lower_devices
    mccs_subarray1_obsstate_attribute = "mccsSubarrayObsState"
    mccs_subarray1_ln_proxy_mock.command_inout.side_effect = raise_devfailed_scan_command
    # Send On() command to SubarrayNode to change the DeviceState to On
    tango_context.device.On()
    # Assign Resources to the Subarray which change the obsState to RESOURCING
    tango_context.device.AssignResources(assign_input_str)
    # Mock the behaviour of ObsState of Csp and Sdp Subarray to change the ObsState to IDLE
    # Marking Assign Resources Command Completed
    attribute = 'ObsState'
    dummy_event_mccs = create_dummy_event_state(mccs_subarray1_ln_proxy_mock, mccs_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[mccs_subarray1_obsstate_attribute](dummy_event_mccs)
    # Check the ObsState changes to IDLE
    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    # Confiure subarray with correct configuration which will change the obsState to CONFIGURING
    tango_context.device.Configure(configure_str)
    # Mock the behaviour of ObsState of Csp and Sdp Subarray to change the ObsState to READY
    # Marking Configure Command Completed
    attribute = 'ObsState'
    dummy_event_mccs = create_dummy_event_state(mccs_subarray1_ln_proxy_mock, mccs_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[mccs_subarray1_obsstate_attribute](dummy_event_mccs)

    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY

    # Now subarrayNode obsState is READY we can send Scan() command which will change the
    # obsState to Scanning
    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.Scan(scan_input_str)
    assert tango_context.device.obsState == ObsState.FAULT
    assert "Failed to invoke StartScan command on subarraynode." in str(df.value)


def test_off_should_raise_devfailed_exception(mock_lower_devices):
    tango_context, mccs_subarray1_ln_proxy_mock = mock_lower_devices[:2]
    mccs_subarray1_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.Off()
    assert "Error executing command OffCommand" in str(df.value)


@pytest.fixture(scope="function")
def mock_lower_devices():
    mccs_subarray1_ln_fqdn = 'ska_low/tm_leaf_node/mccs_subarray01'
    mccs_subarray1_fqdn = 'low_mccs/elt/subarray_01'

    dut_properties = {
        'MccsSubarrayLNFQDN': mccs_subarray1_ln_fqdn,
        'MccsSubarrayFQDN': mccs_subarray1_fqdn
    }

    mccs_subarray1_ln_proxy_mock = Mock()
    mccs_subarray1_proxy_mock = Mock()

    proxies_to_mock = {
        mccs_subarray1_ln_fqdn: mccs_subarray1_ln_proxy_mock,
        mccs_subarray1_fqdn: mccs_subarray1_proxy_mock
    }

    event_subscription_map = {}

    mccs_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    mccs_subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context, mccs_subarray1_ln_proxy_mock, mccs_subarray1_proxy_mock, mccs_subarray1_ln_fqdn, mccs_subarray1_fqdn, event_subscription_map


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def create_dummy_event_state(proxy_mock, device_fqdn, attribute, attr_value):
    print("inside dummy event funct::::::::::::::")
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    fake_event.device = proxy_mock
    print("fake event is::::::", fake_event)
    return fake_event


def create_dummy_event_state_with_error(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Invalid Value'
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    fake_event.device = proxy_mock
    return fake_event


def create_dummy_event_custom_exception(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Invalid Value'
    fake_event.attr_name = "{device_fqdn}/{attribute}"
    fake_event.attr_value = "Subarray is not in IDLE obsState, please check the subarray obsState"
    fake_event.device = proxy_mock
    return fake_event


def raise_devfailed_exception(cmd_name):
    tango.Except.throw_exception("SubarrayNode_Commandfailed",
                                 "This is error message for devfailed",
                                 cmd_name, tango.ErrSeverity.ERR)


def raise_devfailed_with_arg(cmd_name, input_arg):
    tango.Except.throw_exception("SubarrayNode_Commandfailed",
                                 "This is error message for devfailed",
                                 cmd_name, tango.ErrSeverity.ERR)


def raise_devfailed_for_event_subscription(evt_name,evt_type,callaback, stateless=True):
    tango.Except.throw_exception("SubarrayNode_CommandCallbackfailed",
                                 "This is error message for devfailed",
                                 "From function test devfailed", tango.ErrSeverity.ERR)


def raise_devfailed_scan_command(cmd_name, input_arg):
    if cmd_name == 'StartScan':
        tango.Except.throw_exception("SubarrayNode_Commandfailed",
                                     "Failed to invoke StartScan command on subarraynode.",
                                     cmd_name, tango.ErrSeverity.ERR)



def command_callback_with_command_exception():
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = Exception("Exception in callback")
    return fake_event


def command_callback_with_devfailed_exception():
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = tango.Except.throw_exception("TestDevfailed", "This is error message for devfailed",
                                 "From function test devfailed", tango.ErrSeverity.ERR)
    return fake_event


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

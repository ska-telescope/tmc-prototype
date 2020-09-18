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
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from sdpsubarrayleafnode import SdpSubarrayLeafNode, const, release
from ska.base.control_model import ObsState, HealthState, AdminMode, TestMode, ControlMode, SimulationMode
from ska.base.control_model import LoggingLevel

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


@pytest.fixture(scope="function")
def event_subscription_with_arg(mock_sdp_subarray):
    event_subscription_map = {}
    mock_sdp_subarray[1].command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def event_subscription_without_arg(mock_sdp_subarray):
    event_subscription_map = {}
    mock_sdp_subarray[1].command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map

@pytest.fixture(scope="function")
def mock_sdp_subarray():
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_01'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }
    sdp_subarray1_proxy_mock = Mock()
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, sdp_subarray1_proxy_mock


def test_on_should_command_with_callback_method(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    device_proxy.On()
    dummy_event = command_callback(const.CMD_ON)
    event_subscription_without_arg[const.CMD_ON](dummy_event)
    assert const.STR_COMMAND + const.CMD_ON in device_proxy.activityMessage
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ON,
                                                                         any_method(with_name='on_cmd_ended_cb'))


def test_off_should_command_with_callback_method(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback(const.CMD_OFF)
    event_subscription_without_arg[const.CMD_OFF](dummy_event)
    assert const.STR_COMMAND + const.CMD_OFF in device_proxy.activityMessage
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_OFF,
                                                                         any_method(with_name='off_cmd_ended_cb'))


def test_end_sb_command_with_callback_method(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.EndSB()
    dummy_event = command_callback(const.CMD_RESET)
    event_subscription_without_arg[const.CMD_RESET](dummy_event)
    assert const.STR_COMMAND + const.CMD_RESET in device_proxy.activityMessage


def test_release_resources_command_with_callback_method(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.ReleaseAllResources()
    dummy_event = command_callback(const.CMD_RELEASE_RESOURCES)
    event_subscription_without_arg[const.CMD_RELEASE_RESOURCES](dummy_event)
    assert const.STR_COMMAND + const.CMD_RELEASE_RESOURCES in device_proxy.activityMessage


def test_assign_command_assignresources_ended_with_callback_method(mock_sdp_subarray,event_subscription_with_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.AssignResources(assign_input_str)
    dummy_event = command_callback(const.CMD_ASSIGN_RESOURCES)
    event_subscription_with_arg[const.CMD_ASSIGN_RESOURCES](dummy_event)
    assert const.STR_COMMAND + const.CMD_ASSIGN_RESOURCES in device_proxy.activityMessage


def test_on_should_command_with_callback_method_with_event_error(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    device_proxy.On()
    dummy_event = command_callback_with_event_error(const.CMD_ON)
    event_subscription_without_arg[const.CMD_ON](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_ON in device_proxy.activityMessage


def test_off_should_command_with_callback_method_with_event_error(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback_with_event_error(const.CMD_OFF)
    event_subscription_without_arg[const.CMD_OFF](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_OFF in device_proxy.activityMessage


def test_scan_command_with_callback_method(mock_sdp_subarray,event_subscription_with_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.Scan(scan_input_str)
    dummy_event = command_callback(const.CMD_SCAN)
    event_subscription_with_arg[const.CMD_SCAN](dummy_event)
    assert const.STR_COMMAND + const.CMD_SCAN in device_proxy.activityMessage


def test_configure_command_with_callback_method(mock_sdp_subarray,event_subscription_with_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.Configure(configure_str)
    dummy_event = command_callback(const.CMD_CONFIGURE)
    event_subscription_with_arg[const.CMD_CONFIGURE](dummy_event)
    assert const.STR_COMMAND + const.CMD_CONFIGURE in device_proxy.activityMessage


def test_end_scan_command_with_callback_method(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.EndScan()
    dummy_event = command_callback(const.CMD_ENDSCAN)
    event_subscription_without_arg[const.CMD_ENDSCAN](dummy_event)
    assert const.STR_COMMAND + const.CMD_ENDSCAN in device_proxy.activityMessage


def test_abort_command_with_callback_method(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.Abort()
    dummy_event = command_callback(const.CMD_ABORT)
    event_subscription_without_arg[const.CMD_ABORT](dummy_event)
    assert const.STR_COMMAND + const.CMD_ABORT in device_proxy.activityMessage


def test_restart_command_with_callback_method(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    device_proxy.Restart()
    dummy_event = command_callback(const.CMD_RESTART)
    event_subscription_without_arg[const.CMD_RESTART](dummy_event)
    assert const.STR_COMMAND + const.CMD_RESTART in device_proxy.activityMessage


def test_end_sb_command_with_callback_method_with_event_error(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.EndSB()
    dummy_event = command_callback_with_event_error(const.CMD_RESET)
    event_subscription_without_arg[const.CMD_RESET](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_RESET in device_proxy.activityMessage


def test_release_resource_command_with_callback_method_with_event_error(mock_sdp_subarray,
                                                                        event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.ReleaseAllResources()
    dummy_event = command_callback_with_event_error(const.CMD_RELEASE_RESOURCES)
    event_subscription_without_arg[const.CMD_RELEASE_RESOURCES](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_RELEASE_RESOURCES in device_proxy.activityMessage


def test_assign_command_assign_resources_ended_raises_exception_for_error_event(mock_sdp_subarray,
                                                                                event_subscription_with_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.AssignResources(assign_input_str)
    dummy_event = command_callback_with_event_error(const.CMD_ASSIGN_RESOURCES)
    with pytest.raises(tango.DevFailed) as df:
        event_subscription_with_arg[const.CMD_ASSIGN_RESOURCES](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_ASSIGN_RESOURCES in device_proxy.activityMessage


def test_scan_command_with_callback_method_with_event_error(mock_sdp_subarray,event_subscription_with_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.Scan(scan_input_str)
    dummy_event = command_callback_with_event_error(const.CMD_SCAN)
    event_subscription_with_arg[const.CMD_SCAN](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_SCAN in device_proxy.activityMessage


def test_end_scan_command_with_callback_method_with_event_error(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.EndScan()
    dummy_event = command_callback_with_event_error(const.CMD_ENDSCAN)
    event_subscription_without_arg[const.CMD_ENDSCAN](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_ENDSCAN in device_proxy.activityMessage

def test_configure_command_with_callback_method_with_event_error(mock_sdp_subarray,event_subscription_with_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.Configure(configure_str)
    dummy_event = command_callback_with_event_error(const.CMD_CONFIGURE)
    event_subscription_with_arg[const.CMD_CONFIGURE](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_CONFIGURE in device_proxy.activityMessage


def test_abort_command_with_callback_method_with_event_error(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.Abort()
    dummy_event = command_callback_with_event_error(const.CMD_ABORT)
    event_subscription_without_arg[const.CMD_ABORT](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_ABORT in device_proxy.activityMessage


def test_restart_command_with_callback_method_with_event_error(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    device_proxy.Restart()
    dummy_event = command_callback_with_event_error(const.CMD_RESTART)
    event_subscription_without_arg[const.CMD_RESTART](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_RESTART in device_proxy.activityMessage


def test_assign_command_with_callback_method_with_devfailed_error(mock_sdp_subarray,event_subscription_with_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
        dummy_event = command_callback_with_devfailed_exception()
        event_subscription_with_arg[const.CMD_ASSIGN_RESOURCES](dummy_event)
    assert const.ERR_CMD_FAILED in str(df.value)


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


def command_callback_with_command_exception():
    return Exception("Exception in Command callback")


def command_callback_with_devfailed_exception():
    tango.Except.throw_exception("SdpSubarrayLeafNode_Commandfailed in callback", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)

def raise_devfailed_exception_with_arg(cmd_name, input_str):
    tango.Except.throw_exception("SdpSubarrayLeafNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)

def raise_devfailed_exception_with_args(cmd_name, input_str, callback):
    tango.Except.throw_exception("SdpSubarrayLeafNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)

def test_start_scan_should_command_sdp_subarray_to_start_scan_when_it_is_ready(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.Scan(scan_input_str)
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SCAN, scan_input_str,
                                                                         any_method(with_name='scan_cmd_ended_cb'))


def test_start_scan_should_raise_devfailed_exception(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_args
    with pytest.raises(tango.DevFailed):
        device_proxy.Scan(scan_input_str)
    assert const.ERR_SCAN in device_proxy.activityMessage


def test_assign_resources_should_send_sdp_subarray_with_correct_processing_block_list(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ASSIGN_RESOURCES,
                                                                     assign_input_str,
                                                                     any_method(with_name='AssignResources_ended'))
    assert_activity_message(device_proxy, const.STR_ASSIGN_RESOURCES_SUCCESS)


def test_assign_resources_should_raise_devfailed_for_invalid_obstate(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    assert "SDP subarray is not in EMPTY obstate." in str(df)


def test_release_resources_when_sdp_subarray_is_idle(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.ReleaseAllResources()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RELEASE_RESOURCES,
                                                    any_method(with_name='releaseallresources_cmd_ended_cb'))
    assert_activity_message(device_proxy, const.STR_REL_RESOURCES)


def test_release_resources_should_raise_devfailed_exception(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed):
        device_proxy.ReleaseAllResources()
    assert const.ERR_RELEASE_RESOURCES in device_proxy.activityMessage


def test_configure_to_send_correct_configuration_data_when_sdp_subarray_is_idle(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.Configure(configure_str)
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_CONFIGURE,
                                                                         configure_str,
                                                                         any_method(with_name='configure_cmd_ended_cb'))


def test_configure_should_raise_devfailed_exception(mock_sdp_subarray,event_subscription_with_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_args
    with pytest.raises(tango.DevFailed):
        device_proxy.Configure(configure_str)
    assert const.ERR_CONFIGURE in device_proxy.activityMessage


def test_end_scan_should_command_sdp_subarray_to_end_scan_when_it_is_scanning(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.EndScan()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ENDSCAN,
                                                                         any_method(with_name='endscan_cmd_ended_cb'))


def test_end_scan_should_raise_devfailed_exception(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed):
        device_proxy.EndScan()
    assert const.ERR_ENDSCAN_INVOKING_CMD in device_proxy.activityMessage


def test_end_sb_should_command_sdp_subarray_to_reset_when_it_is_ready(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.EndSB()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RESET,
                                                                         any_method(with_name='endsb_cmd_ended_cb'))


def test_end_sb_should_raise_devfailed_exception(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed):
        device_proxy.EndSB()
    assert const.ERR_ENDSB_INVOKING_CMD in device_proxy.activityMessage


def test_abort_should_command_sdp_subarray_to_abort_when_it_is_ready(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.Abort()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                                     any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_command_sdp_subarray_to_abort_when_it_is_scanning(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.Abort()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                                     any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_command_sdp_subarray_to_abort_when_it_is_configuring(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.CONFIGURING
    device_proxy.Abort()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                                     any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_command_sdp_subarray_to_abort_when_it_is_idle(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.Abort()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                                     any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_command_sdp_subarray_to_abort_when_it_is_resetting(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.RESETTING
    device_proxy.Abort()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                                     any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_raise_devfailed_exception(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed):
        device_proxy.Abort()
    assert const.ERR_ABORT_INVOKING_CMD in device_proxy.activityMessage


def test_abort_should_failed_when_device_obsstate_is_resourcing(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.RESOURCING
    device_proxy.Abort()
    assert "Unable to invoke Abort command" in device_proxy.activityMessage


def test_abort_should_failed_when_device_obsstate_is_empty(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.Abort()
    assert "Unable to invoke Abort command" in device_proxy.activityMessage


def test_restart_should_command_sdp_subarray_to_restart_when_obsstate_is_aborted(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    device_proxy.Restart()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RESTART,
                                                                     any_method(with_name='restart_cmd_ended_cb'))


def test_restart_should_command_sdp_subarray_to_restart_when_obsstate_is_fault(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.FAULT
    device_proxy.Restart()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RESTART,
                                                                     any_method(with_name='restart_cmd_ended_cb'))


def test_restart_should_raise_devfailed_exception(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed):
        device_proxy.Restart()
    assert const.ERR_RESTART_INVOKING_CMD in device_proxy.activityMessage


def test_restart_should_failed_when_device_obsstate_is_resourcing(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.RESOURCING
    device_proxy.Restart()
    assert "Unable to invoke Restart command" in device_proxy.activityMessage


def test_restart_should_failed_when_device_obsstate_is_scanning(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.Restart()
    assert "Unable to invoke Restart command" in device_proxy.activityMessage


def test_restart_should_failed_when_device_obsstate_is_empty(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.Restart()
    assert "Unable to invoke Restart command" in device_proxy.activityMessage


def test_restart_should_failed_when_device_obsstate_is_configuring(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.CONFIGURING
    device_proxy.Restart()
    assert "Unable to invoke Restart command" in device_proxy.activityMessage


def test_restart_should_failed_when_device_obsstate_is_idle(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.Restart()
    assert "Unable to invoke Restart command" in device_proxy.activityMessage


def test_restart_should_failed_when_device_obsstate_is_ready(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.Restart()
    assert "Unable to invoke Restart command" in device_proxy.activityMessage


def test_obsreset_should_command_sdp_subarray_to_reset_when_obsstate_is_aborted(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    device_proxy.ObsReset()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_OBSRESET,
                                                                     any_method(with_name='obsreset_cmd_ended_cb'))


def test_obsreset_should_command_sdp_subarray_to_reset_when_obsstate_is_fault(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.FAULT
    device_proxy.ObsReset()
    sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_OBSRESET,
                                                                     any_method(with_name='obsreset_cmd_ended_cb'))


def test_obsreset_command_with_callback_method(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    device_proxy.ObsReset()
    dummy_event = command_callback(const.CMD_OBSRESET)
    event_subscription_without_arg[const.CMD_OBSRESET](dummy_event)
    assert const.STR_COMMAND + const.CMD_OBSRESET in device_proxy.activityMessage


def test_obsreset_command_with_callback_method_with_event_error(mock_sdp_subarray,event_subscription_without_arg):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    device_proxy.ObsReset()
    dummy_event = command_callback_with_event_error(const.CMD_OBSRESET)
    event_subscription_without_arg[const.CMD_OBSRESET](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_OBSRESET in device_proxy.activityMessage


def test_obsreset_should_raise_devfailed_exception(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.ObsReset()
    assert const.ERR_OBSRESET_INVOKING_CMD in str(df.value)


def test_obsreset_should_failed_when_device_obsstate_is_resourcing(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.RESOURCING
    device_proxy.ObsReset()
    assert "Unable to invoke ObsReset command" in device_proxy.activityMessage


def test_obsreset_should_failed_when_device_obsstate_is_scanning(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.ObsReset()
    assert "Unable to invoke ObsReset command" in device_proxy.activityMessage


def test_obsreset_should_failed_when_device_obsstate_is_empty(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.ObsReset()
    assert "Unable to invoke ObsReset command" in device_proxy.activityMessage


def test_obsreset_should_failed_when_device_obsstate_is_configuring(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.CONFIGURING
    device_proxy.ObsReset()
    assert "Unable to invoke ObsReset command" in device_proxy.activityMessage


def test_obsreset_should_failed_when_device_obsstate_is_idle(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.ObsReset()
    assert "Unable to invoke ObsReset command" in device_proxy.activityMessage


def test_obsreset_should_failed_when_device_obsstate_is_ready(mock_sdp_subarray):
    device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.ObsReset()
    assert "Unable to invoke ObsReset command" in device_proxy.activityMessage


def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def test_status():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.Status() != const.STR_INIT_SUCCESS


def test_logging_level():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_control_mode():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_test_mode():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_receive_addresses():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.receiveAddresses == ""


def test_activity_message():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.activityMessage == const.STR_SDPSALN_INIT_SUCCESS


def test_write_receive_addresses():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.receiveAddresses = "test"
        assert tango_context.device.receiveAddresses == "test"


def test_write_activity_message():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.activityMessage = "test"
        assert tango_context.device.activityMessage == "test"


def test_active_processing_blocks():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.activeProcessingBlocks == ""


def test_logging_targets():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))


def test_scan_device_not_ready():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.Scan(scan_input_str)
        assert const.ERR_DEVICE_NOT_READY in tango_context.device.activityMessage


def test_endsb_device_not_ready():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.EndSB()
        assert tango_context.device.activityMessage == const.ERR_DEVICE_NOT_READY


def test_endscan_invalid_state():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.EndScan()
        assert const.ERR_DEVICE_NOT_IN_SCAN in tango_context.device.activityMessage


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

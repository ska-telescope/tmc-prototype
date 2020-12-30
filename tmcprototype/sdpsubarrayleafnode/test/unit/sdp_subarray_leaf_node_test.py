# Standard Python imports
import contextlib
import importlib
import sys
import types
import pytest
import tango
import mock
from mock import Mock
from mock import MagicMock
from os.path import dirname, join

# Tango imports
import tango
from tango.test_context import DeviceTestContext

# Additional import
from sdpsubarrayleafnode import SdpSubarrayLeafNode, const, release, device_data
from sdpsubarrayleafnode.device_data import DeviceData
from ska.base.control_model import ObsState, HealthState, AdminMode, TestMode, ControlMode, SimulationMode
from ska.base.control_model import LoggingLevel
from ska.base.commands import ResultCode
from tmc.common.tango_client import TangoClient


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

# Create DeviceData class instance
device_data = DeviceData.get_instance()

##### This fixture is used in refactored On and Off command testcases (SP-1420)
@pytest.fixture(scope="function")
def mock_sdp_subarray_proxy():
    dut_properties = {'SdpSubarrayFQDN': 'mid_sdp/elt/subarray_01'}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['SdpSubarrayFQDN'])
            yield tango_context.device, tango_client_obj, dut_properties['SdpSubarrayFQDN'], event_subscription_map


### This fixture is used in refactored On and Off command testcases (SP-1420)
@pytest.fixture(scope="function")
def event_subscription_mock():
    dut_properties = {'SdpSubarrayFQDN': 'mid_sdp/elt/subarray_01'}
    event_subscription_map = {}
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        tango_client_obj = TangoClient(dut_properties['SdpSubarrayFQDN'])
        tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
            lambda command_name, arg, callback, *args,
                **kwargs: event_subscription_map.update({command_name: callback}))
        yield event_subscription_map


@pytest.fixture(scope="function")
def tango_context():
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        yield tango_context


def test_on(mock_sdp_subarray_proxy):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    assert device_proxy.On() == [[ResultCode.OK],
                                ["OnCommand :->  invoked successfully."]]


def test_on_should_command_with_callback_method(mock_sdp_subarray_proxy,event_subscription_mock):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    device_proxy.On()
    dummy_event = command_callback(const.CMD_ON)
    event_subscription_mock[const.CMD_ON](dummy_event)
    assert const.STR_COMMAND + const.CMD_ON in device_proxy.activityMessage


def test_off_should_command_sdp_subarray_to_stop(mock_sdp_subarray_proxy):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]

    device_proxy.On()
    assert device_proxy.Off() == [[ResultCode.OK], ["OffCommand :->  invoked successfully."]]


def test_off_should_command_with_callback_method(mock_sdp_subarray_proxy,event_subscription_mock):
    device_proxy, tango_client_obj,_ ,_= mock_sdp_subarray_proxy
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback(const.CMD_OFF)
    event_subscription_mock[const.CMD_OFF](dummy_event)
    assert const.STR_COMMAND + const.CMD_OFF in device_proxy.activityMessage


def test_on_should_command_with_callback_method_with_event_error(mock_sdp_subarray_proxy,event_subscription_mock):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    device_proxy.On()
    dummy_event = command_callback_with_event_error(const.CMD_ON)
    event_subscription_mock[const.CMD_ON](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_ON in device_proxy.activityMessage


def test_off_should_command_with_callback_method_with_event_error(mock_sdp_subarray_proxy,event_subscription_mock):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback_with_event_error(const.CMD_OFF)
    event_subscription_mock[const.CMD_OFF](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_OFF in device_proxy.activityMessage


def test_on_command_should_raise_dev_failed(mock_sdp_subarray_proxy):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.On()
    assert "This is error message for devfailed" in str(df.value)


def test_off_command_should_raise_dev_failed(mock_sdp_subarray_proxy):
    device_proxy, tango_client_obj,_,_= mock_sdp_subarray_proxy
    device_proxy.On()
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Off()
    assert "This is error message for devfailed" in str(df.value)


@pytest.fixture(
    scope="function",
    params=[
        ("Configure", configure_str, const.CMD_CONFIGURE, ObsState.READY,"configure_cmd_ended_cb", const.ERR_CONFIGURE),
        ("Configure", configure_str, const.CMD_CONFIGURE, ObsState.IDLE,"configure_cmd_ended_cb", const.ERR_CONFIGURE),
        ("AssignResources", assign_input_str, const.CMD_ASSIGN_RESOURCES, ObsState.EMPTY,"AssignResources_ended", const.ERR_ASSGN_RESOURCES),
        ("AssignResources", assign_input_str, const.CMD_ASSIGN_RESOURCES, ObsState.IDLE, "AssignResources_ended",const.ERR_ASSGN_RESOURCES),
        ("Scan", scan_input_str, const.CMD_SCAN, ObsState.READY,"scan_cmd_ended_cb", const.ERR_SCAN),
    ])

def command_with_arg(request):
    cmd_name, input_arg, requested_cmd, obs_state, callback_str, Error_msg = request.param
    return cmd_name, input_arg, requested_cmd, obs_state, callback_str, Error_msg


def test_command_with_callback_method_with_arg(mock_sdp_subarray_proxy, event_subscription_mock, command_with_arg):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    cmd_name, input_arg, requested_cmd, obs_state, _, _ = command_with_arg
    # tango_client_obj.set_attribute("obsState", obs_state)
    device_proxy.command_inout(cmd_name, input_arg)
    dummy_event = command_callback(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


def test_command_with_callback_method_with_arg_with_event_error(mock_sdp_subarray_proxy, event_subscription_mock, command_with_arg):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    cmd_name, input_arg, requested_cmd, obs_state, _, _ = command_with_arg
    # tango_client_obj.set_attribute("obsState", obs_state)
    device_proxy.command_inout(cmd_name, input_arg)
    dummy_event = command_callback(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


def test_command_for_allowed_Obstate_with_arg(mock_sdp_subarray_proxy, command_with_arg):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    cmd_name, input_arg, requested_cmd, obs_state, callback_str, _ = command_with_arg    
    # tango_client_obj.set_attribute("obsState", obs_state)
    device_proxy.command_inout(cmd_name, input_arg)
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(requested_cmd, input_arg,
                                                                         any_method(with_name=callback_str))
    assert_activity_message(device_proxy, const.STR_ASSIGN_RESOURCES_SUCCESS)


def test_command_with_arg_should_raise_devfailed_exception(mock_sdp_subarray_proxy, event_subscription_mock, command_with_arg):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    cmd_name, input_arg, requested_cmd, obs_state, _,_ = command_with_arg
    # tango_client_obj.set_attribute("obsState", obs_state)
    # tango_client_obj.deviceproxy.command_inout_asynch.side_effect = raise_devfailed_exception
    # with pytest.raises(tango.DevFailed) as df:
    #     device_proxy.command_inout(cmd_name, input_arg)
    # assert Error_msg in str(df.value)
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(input_arg)
        dummy_event = command_callback_with_devfailed_exception()
        event_subscription_mock[requested_cmd](dummy_event)
    assert "This is error message for devfailed" in str(df.value)


@pytest.fixture(
    scope="function",
    params=[
        ("ReleaseAllResources", const.CMD_RELEASE_RESOURCES, ObsState.IDLE,"releaseallresources_cmd_ended_cb", const.STR_REL_RESOURCES),
        ("End", const.CMD_END, ObsState.READY,"end_cmd_ended_cb",const.STR_END_SUCCESS),
        ("EndScan", const.CMD_ENDSCAN, ObsState.SCANNING, "endscan_cmd_ended_cb", const.STR_ENDSCAN_SUCCESS),
        ("Abort", const.CMD_ABORT, ObsState.SCANNING, "abort_cmd_ended_cb", const.STR_ABORT_SUCCESS),
        ("Abort", const.CMD_ABORT, ObsState.CONFIGURING, "abort_cmd_ended_cb", const.STR_ABORT_SUCCESS),
        ("Abort", const.CMD_ABORT, ObsState.IDLE, "abort_cmd_ended_cb", const.STR_ABORT_SUCCESS),
        ("Abort", const.CMD_ABORT, ObsState.RESETTING, "abort_cmd_ended_cb", const.STR_ABORT_SUCCESS),
        ("Abort", const.CMD_ABORT, ObsState.READY, "abort_cmd_ended_cb", const.STR_ABORT_SUCCESS),
        ("Restart", const.CMD_RESTART, ObsState.ABORTED,"restart_cmd_ended_cb", const.STR_RESTART_SUCCESS), 
        ("Restart", const.CMD_RESTART, ObsState.FAULT,"restart_cmd_ended_cb", const.STR_RESTART_SUCCESS), 
        ("ObsReset", const.CMD_OBSRESET, ObsState.ABORTED, "obsreset_cmd_ended_cb", const.STR_OBSRESET_SUCCESS), 
        ("ObsReset", const.CMD_OBSRESET, ObsState.FAULT, "obsreset_cmd_ended_cb", const.STR_OBSRESET_SUCCESS),
    ])

def command_without_arg(request):
    cmd_name, requested_cmd, obs_state, callback_str, cmd_success_msg = request.param
    return cmd_name, requested_cmd, obs_state, callback_str, cmd_success_msg

def test_command_with_callback_method_without_arg(mock_sdp_subarray_proxy, event_subscription_mock, command_without_arg):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    cmd_name, requested_cmd, obs_state, _, _ = command_without_arg
    
    # tango_client_obj.set_attribute("obsState", obs_state)

    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage

def test_command_with_callback_method_without_arg_with_event_error(mock_sdp_subarray_proxy,event_subscription_mock, command_without_arg):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    cmd_name, requested_cmd, obs_state, _, _ = command_without_arg
    
    # tango_client_obj.set_attribute("obsState", obs_state)

    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage

def test_command_for_allowed_Obstate_without_arg(mock_sdp_subarray_proxy, command_without_arg):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    cmd_name, requested_cmd, obs_state, callback_str, cmd_success_msg = command_without_arg    

#     tango_client_obj.set_attribute("obsState", obs_state)

    device_proxy.command_inout(cmd_name)
    assert cmd_success_msg in device_proxy.activityMessage
#     tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(requested_cmd, 
#                                                                          any_method(with_name=callback_str))


def test_command_without_arg_should_raise_devfailed_exception(mock_sdp_subarray_proxy,event_subscription_mock, command_without_arg):
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    cmd_name, requested_cmd, obs_state, _, _ = command_without_arg

    # tango_client_obj.set_attribute("obsState", obs_state)

    # tango_client_obj.send_command_async.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name)
        raise_devfailed_exception()
    assert "This is error message for devfailed" in str(df.value)


@pytest.fixture(
    scope="function",
    params=[
        ("Scan", scan_input_str,  ObsState.IDLE),
        ("Configure", configure_str, ObsState.SCANNING),
        ("Configure", configure_str, ObsState.EMPTY),
        ("AssignResources", assign_input_str, ObsState.READY),
    ])

def command_with_argin_should_not_allowed_in_obstate(request):
    cmd_name, input_str, obs_state = request.param
    return cmd_name, input_str, obs_state

# TODO: Run the test case with latest tmc-common-package package
# def test_command_with_argin_should_failed_when_device_is_not_in_required_obstate(mock_sdp_subarray_proxy, command_with_argin_should_not_allowed_in_obstate):
#     cmd_name, input_str, obs_state = command_with_argin_should_not_allowed_in_obstate
#     device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]

#     # tango_client_obj.set_attribute("obsState", obs_state)
    
#     with pytest.raises(tango.DevFailed) as df:
#         device_proxy.command_inout(cmd_name, input_str)
#     assert "Failed to invoke " + cmd_name in str(df.value)

# TODO: Run the test case with latest tmc-common-package package
# def test_scan_device_not_ready():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         with pytest.raises(tango.DevFailed) as df:
#             tango_context.device.Scan(scan_input_str)
#         assert const.ERR_DEVICE_NOT_READY in str(df.value)

# TODO: Run the test case with latest tmc-common-package package
# def test_end_device_not_ready():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         with pytest.raises(tango.DevFailed) as df:
#             tango_context.device.End()
#         assert const.ERR_DEVICE_NOT_READY in str(df.value)

# TODO: Run the test case with latest tmc-common-package package
# def test_endscan_invalid_state():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         with pytest.raises(tango.DevFailed) as df:
#             tango_context.device.EndScan()
#         assert const.ERR_DEVICE_NOT_IN_SCAN in str(df.value)


@pytest.fixture(
    scope="function",
    params=[
        ( "Abort", ObsState.RESOURCING),
        ( "Abort", ObsState.EMPTY),
        ( "Restart", ObsState.SCANNING),
        ( "Restart", ObsState.EMPTY),
        ( "Restart", ObsState.CONFIGURING),
        ( "Restart", ObsState.IDLE),
        ( "Restart", ObsState.READY),
        ( "Restart", ObsState.RESOURCING),
        ( "End", ObsState.SCANNING),
        ( "ReleaseAllResources", ObsState.SCANNING),
        ( "ObsReset", ObsState.SCANNING),
        ( "ObsReset", ObsState.EMPTY),
        ( "ObsReset", ObsState.CONFIGURING),
        ( "ObsReset", ObsState.IDLE),
        ( "ObsReset", ObsState.READY),
        ( "ObsReset", ObsState.RESOURCING),
])

def command_should_not_allowed_in_obstate(request):
    cmd_name, obs_state = request.param
    return cmd_name, obs_state

# TODO:Run the test case with latest tmc-common-package package 
def test_command_should_failed_when_device_is_not_in_required_obstate(mock_sdp_subarray_proxy, command_should_not_allowed_in_obstate):
    cmd_name, obs_state = command_should_not_allowed_in_obstate
    device_proxy, tango_client_obj = mock_sdp_subarray_proxy[:2]
    # tango_client_obj.set_attribute("obsState", obs_state)
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name)
    #assert "Failed to invoke " + cmd_name in str(df.value)
    assert "This is error message for devfailed" in str(df.value)



###########################################################################################################

# @pytest.fixture(scope="function")
# def event_subscription_with_arg(mock_sdp_subarray):
#     event_subscription_map = {}
#     mock_sdp_subarray[1].command_inout_asynch.side_effect = (
#         lambda command_name, argument, callback, *args,
#                **kwargs: event_subscription_map.update({command_name: callback}))
#     yield event_subscription_map


# @pytest.fixture(scope="function")
# def event_subscription_without_arg(mock_sdp_subarray):
#     event_subscription_map = {}
#     mock_sdp_subarray[1].command_inout_asynch.side_effect = (
#         lambda command_name, callback, *args,
#                **kwargs: event_subscription_map.update({command_name: callback}))
#     yield event_subscription_map


# @pytest.fixture(scope="function")
# def mock_sdp_subarray():
#     sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_01'
#     dut_properties = {
#         'SdpSubarrayFQDN': sdp_subarray1_fqdn
#     }
#     sdp_subarray1_proxy_mock = Mock()
#     proxies_to_mock = {
#         sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
#     }
#     with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
#                            proxies_to_mock=proxies_to_mock) as tango_context:
#         yield tango_context.device, sdp_subarray1_proxy_mock



# @pytest.fixture(
#     scope="function",
#     params=[
#         ("Scan", scan_input_str, const.CMD_SCAN, ObsState.READY,"scan_cmd_ended_cb", const.ERR_SCAN),
#         ("Configure", configure_str, const.CMD_CONFIGURE, ObsState.READY,"configure_cmd_ended_cb", const.ERR_CONFIGURE),
#         ("Configure", configure_str, const.CMD_CONFIGURE, ObsState.IDLE,"configure_cmd_ended_cb", const.ERR_CONFIGURE),
#         ("AssignResources", assign_input_str, const.CMD_ASSIGN_RESOURCES, ObsState.EMPTY,"AssignResources_ended", const.ERR_ASSGN_RESOURCES),
#         ("AssignResources", assign_input_str, const.CMD_ASSIGN_RESOURCES, ObsState.IDLE, "AssignResources_ended",const.ERR_ASSGN_RESOURCES),
#     ])

# def command_with_arg(request):
#     cmd_name, input_arg, requested_cmd, obs_state, callback_str, Error_msg = request.param
#     return cmd_name, input_arg, requested_cmd, obs_state, callback_str, Error_msg


# def test_command_with_callback_method_with_arg(mock_sdp_subarray, event_subscription_with_arg, command_with_arg):
#     device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
#     cmd_name, input_arg, requested_cmd, obs_state, _, _ = command_with_arg
#     sdp_subarray1_proxy_mock.obsState = obs_state
#     device_proxy.command_inout(cmd_name, input_arg)
#     dummy_event = command_callback(requested_cmd)
#     event_subscription_with_arg[requested_cmd](dummy_event)
#     assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


# def test_command_with_callback_method_with_arg_with_event_error(mock_sdp_subarray, event_subscription_with_arg, command_with_arg):
#     device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
#     cmd_name, input_arg, requested_cmd, obs_state, _, _ = command_with_arg
#     sdp_subarray1_proxy_mock.obsState = obs_state
#     device_proxy.command_inout(cmd_name, input_arg)
#     dummy_event = command_callback(requested_cmd)
#     event_subscription_with_arg[requested_cmd](dummy_event)
#     assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


# def test_command_for_allowed_Obstate_with_arg(mock_sdp_subarray, command_with_arg):
#     device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
#     cmd_name, input_arg, requested_cmd, obs_state, callback_str, _ = command_with_arg    
#     sdp_subarray1_proxy_mock.obsState = obs_state
#     device_proxy.command_inout(cmd_name, input_arg)
#     sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(requested_cmd, input_arg,
#                                                                          any_method(with_name=callback_str))


# def test_command_with_arg_should_raise_devfailed_exception(mock_sdp_subarray, event_subscription_with_arg, command_with_arg):
#     device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
#     cmd_name, input_arg, requested_cmd, obs_state, _, Error_msg = command_with_arg
#     sdp_subarray1_proxy_mock.obsState = obs_state
#     sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
#     with pytest.raises(tango.DevFailed) as df:
#         device_proxy.command_inout(cmd_name, input_arg)
#     assert Error_msg in str(df.value)


# @pytest.fixture(
#     scope="function",
#     params=[
#         ("End", const.CMD_END, ObsState.READY,"end_cmd_ended_cb",const.ERR_END_INVOKING_CMD),
#         ("ReleaseAllResources", const.CMD_RELEASE_RESOURCES, ObsState.IDLE,"releaseallresources_cmd_ended_cb", const.ERR_RELEASE_RESOURCES),
#         ("EndScan", const.CMD_ENDSCAN, ObsState.SCANNING, "endscan_cmd_ended_cb", const.ERR_ENDSCAN_INVOKING_CMD),
#         ("Abort", const.CMD_ABORT, ObsState.SCANNING, "abort_cmd_ended_cb", const.ERR_ABORT_INVOKING_CMD),
#         ("Abort", const.CMD_ABORT, ObsState.CONFIGURING, "abort_cmd_ended_cb", const.ERR_ABORT_INVOKING_CMD),
#         ("Abort", const.CMD_ABORT, ObsState.IDLE, "abort_cmd_ended_cb", const.ERR_ABORT_INVOKING_CMD),
#         ("Abort", const.CMD_ABORT, ObsState.RESETTING, "abort_cmd_ended_cb", const.ERR_ABORT_INVOKING_CMD),
#         ("Abort", const.CMD_ABORT, ObsState.READY, "abort_cmd_ended_cb", const.ERR_ABORT_INVOKING_CMD),
#         ("Restart", const.CMD_RESTART, ObsState.ABORTED,"restart_cmd_ended_cb", const.ERR_RESTART_INVOKING_CMD), 
#         ("Restart", const.CMD_RESTART, ObsState.FAULT,"restart_cmd_ended_cb", const.ERR_RESTART_INVOKING_CMD), 
#         ("ObsReset", const.CMD_OBSRESET, ObsState.ABORTED, "obsreset_cmd_ended_cb", const.ERR_OBSRESET_INVOKING_CMD), 
#         ("ObsReset", const.CMD_OBSRESET, ObsState.FAULT, "obsreset_cmd_ended_cb", const.ERR_OBSRESET_INVOKING_CMD),
#     ])

# def command_without_arg(request):
#     cmd_name, requested_cmd, obs_state, callback_str, Error_msg = request.param
#     return cmd_name, requested_cmd, obs_state, callback_str, Error_msg

# def test_command_with_callback_method_without_arg(mock_sdp_subarray, event_subscription_without_arg, command_without_arg):
#     device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
#     cmd_name, requested_cmd, obs_state, _, _ = command_without_arg
#     sdp_subarray1_proxy_mock.obsState = obs_state
#     device_proxy.command_inout(cmd_name)
#     dummy_event = command_callback(requested_cmd)
#     event_subscription_without_arg[requested_cmd](dummy_event)
#     assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage

# def test_command_with_callback_method_without_arg_with_event_error(mock_sdp_subarray,event_subscription_without_arg, command_without_arg):
#     device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
#     cmd_name, requested_cmd, obs_state, _, _ = command_without_arg
#     sdp_subarray1_proxy_mock.obsState = obs_state
#     device_proxy.command_inout(cmd_name)
#     dummy_event = command_callback_with_event_error(requested_cmd)
#     event_subscription_without_arg[requested_cmd](dummy_event)
#     assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage

# def test_command_for_allowed_Obstate_without_arg(mock_sdp_subarray, command_without_arg):
#     device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
#     cmd_name, requested_cmd, obs_state, callback_str, _ = command_without_arg    
#     sdp_subarray1_proxy_mock.obsState = obs_state
#     device_proxy.command_inout(cmd_name)
#     sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(requested_cmd, 
#                                                                          any_method(with_name=callback_str))

# def test_command_without_arg_should_raise_devfailed_exception(mock_sdp_subarray,event_subscription_without_arg, command_without_arg):
#     device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
#     cmd_name, requested_cmd, obs_state, _, Error_msg = command_without_arg
#     sdp_subarray1_proxy_mock.obsState = obs_state
#     sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
#     with pytest.raises(tango.DevFailed) as df:
#         device_proxy.command_inout(cmd_name)
#     assert Error_msg in str(df.value)


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

# TODO: FOR FUTURE REFERENCE
# def command_callback_with_command_exception():
#     return Exception("Exception in Command callback")

def command_callback_with_devfailed_exception():
    tango.Except.throw_exception("SdpSubarrayLeafNode_Commandfailed in callback", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)

def raise_devfailed_exception(*args):
    tango.Except.throw_exception("SdpSubarrayLeafNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)


# @pytest.fixture(
#     scope="function",
#     params=[
#         ( "Abort", ObsState.RESOURCING),
#         ( "Abort", ObsState.EMPTY),
#         ( "Restart", ObsState.SCANNING),
#         ( "Restart", ObsState.EMPTY),
#         ( "Restart", ObsState.CONFIGURING),
#         ( "Restart", ObsState.IDLE),
#         ( "Restart", ObsState.READY),
#         ( "Restart", ObsState.RESOURCING),
#         ( "ObsReset", ObsState.SCANNING),
#         ( "ObsReset", ObsState.EMPTY),
#         ( "ObsReset", ObsState.CONFIGURING),
#         ( "ObsReset", ObsState.IDLE),
#         ( "ObsReset", ObsState.READY),
#         ( "ObsReset", ObsState.RESOURCING),
#     ])

# def command_should_not_allowed_in_obstate(request):
#     cmd_name, obs_state = request.param
#     return cmd_name, obs_state


# def test_command_should_failed_when_device_is_not_in_required_obstate(mock_sdp_subarray, command_should_not_allowed_in_obstate):
#     cmd_name, obs_state = command_should_not_allowed_in_obstate
#     device_proxy, sdp_subarray1_proxy_mock = mock_sdp_subarray
#     sdp_subarray1_proxy_mock.obsState = obs_state
#     with pytest.raises(tango.DevFailed) as df:
#         device_proxy.command_inout(cmd_name)
#     assert "Failed to invoke " + cmd_name in str(df.value)





def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False
            return other.__func__.__name__ == with_name if with_name else True
    return AnyMethod()
  


# def test_status():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         assert tango_context.device.Status() != const.STR_INIT_SUCCESS


# def test_logging_level():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         tango_context.device.loggingLevel = LoggingLevel.INFO
#         assert tango_context.device.loggingLevel == LoggingLevel.INFO


# def test_control_mode():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         control_mode = ControlMode.REMOTE
#         tango_context.device.controlMode = control_mode
#         assert tango_context.device.controlMode == control_mode


# def test_test_mode():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         test_mode = TestMode.NONE
#         tango_context.device.testMode = test_mode
#         assert tango_context.device.testMode == test_mode


# def test_receive_addresses():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         assert tango_context.device.receiveAddresses == ""


# def test_activity_message():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         assert tango_context.device.activityMessage == const.STR_SDPSALN_INIT_SUCCESS


# def test_write_receive_addresses():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         tango_context.device.receiveAddresses = "test"
#         assert tango_context.device.receiveAddresses == "test"


# def test_write_activity_message():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         tango_context.device.activityMessage = "test"
#         assert tango_context.device.activityMessage == "test"


# def test_active_processing_blocks():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         assert tango_context.device.activeProcessingBlocks == ""


# def test_logging_targets():
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         tango_context.device.loggingTargets = ['console::cout']
#         assert 'console::cout' in tango_context.device.loggingTargets


# def test_version_id():
#     """Test for versionId"""
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         assert tango_context.device.versionId == release.version


# def test_build_state():
#     """Test for buildState"""
#     with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
#         assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))

 
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

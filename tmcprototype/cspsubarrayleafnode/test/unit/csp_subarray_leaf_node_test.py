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
from cspsubarrayleafnode import CspSubarrayLeafNode, const, release
from ska.base.control_model import HealthState, ObsState, LoggingLevel

assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

scan_input_file = 'command_Scan.json'
path = join(dirname(__file__), 'data', scan_input_file)
with open(path, 'r') as f:
    scan_input_str = f.read()

configure_input_file = 'command_Configure.json'
path = join(dirname(__file__), 'data', configure_input_file)
with open(path, 'r') as f:
    configure_str = f.read()

invalid_json_assign_config_file = 'invalid_json_Assign_Resources_Configure.json'
path = join(dirname(__file__), 'data', invalid_json_assign_config_file)
with open(path, 'r') as f:
    invalid_key_str = f.read()

assign_invalid_key_file = 'invalid_key_AssignResources.json'
path = join(dirname(__file__), 'data', assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key = f.read()


@pytest.fixture(scope="function")
def event_subscription(mock_csp_subarray):
    event_subscription_map = {}
    mock_csp_subarray[1].command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def event_subscription_without_arg(mock_csp_subarray):
    event_subscription_map = {}
    mock_csp_subarray[1].command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def mock_csp_subarray():
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }
    csp_subarray1_proxy_mock = Mock()
    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }
    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, csp_subarray1_proxy_mock


@pytest.fixture(
    scope="function",
    params=[
        ("Configure", configure_str, const.CMD_CONFIGURE, ObsState.READY, const.ERR_DEVFAILED_MSG),
        ("StartScan", scan_input_str, const.CMD_STARTSCAN, ObsState.READY, const.ERR_STARTSCAN_RESOURCES),
        ("AssignResources", assign_input_str, const.CMD_ADD_RECEPTORS, ObsState.EMPTY, const.ERR_DEVFAILED_MSG),
    ])
def command_with_arg(request):
    cmd_name, input_arg, requested_cmd, obs_state, error_msg = request.param
    return cmd_name, input_arg, requested_cmd, obs_state, error_msg


def test_command_cb_is_invoked_when_command_with_arg_is_called_async(mock_csp_subarray, event_subscription, command_with_arg):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    cmd_name, input_arg, requested_cmd, obs_state, _ = command_with_arg
    csp_subarray1_proxy_mock.obsState = obs_state
    device_proxy.command_inout(cmd_name, input_arg)
    dummy_event = command_callback(requested_cmd)
    event_subscription[requested_cmd](dummy_event)
    assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


@pytest.fixture(
    scope="function",
    params=[
        ("EndScan", ObsState.SCANNING, const.ERR_ENDSCAN_INVOKING_CMD),
        ("GoToIdle", ObsState.READY, const.ERR_GOTOIDLE_INVOKING_CMD),
        ("Abort", ObsState.SCANNING, const.ERR_ABORT_INVOKING_CMD),
        ("Restart", ObsState.ABORTED, const.ERR_RESTART_INVOKING_CMD),
        ("ObsReset", ObsState.ABORTED, const.ERR_OBSRESET_INVOKING_CMD),
    ])
def command_without_arg(request):
    cmd_name, obs_state, error_msg = request.param
    return cmd_name, obs_state, error_msg


def test_command_cb_is_invoked_when_command_without_arg_is_called_async(mock_csp_subarray, event_subscription_without_arg, command_without_arg):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    cmd_name, obs_state, _ = command_without_arg
    csp_subarray1_proxy_mock.obsState = obs_state
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback(cmd_name)
    event_subscription_without_arg[cmd_name](dummy_event)
    assert const.STR_COMMAND + cmd_name in device_proxy.activityMessage


def test_command_cb_is_invoked_when_releaseresources_is_called_async(mock_csp_subarray, event_subscription_without_arg):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.ReleaseAllResources()
    dummy_event = command_callback(const.CMD_REMOVE_ALL_RECEPTORS)
    event_subscription_without_arg[const.CMD_REMOVE_ALL_RECEPTORS](dummy_event)
    assert const.STR_COMMAND + const.CMD_REMOVE_ALL_RECEPTORS in device_proxy.activityMessage


def test_command_cb_is_invoked_when_command_with_event_error_is_called_async(mock_csp_subarray, event_subscription, command_with_arg):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    cmd_name, input_str, requested_cmd, obs_state, _ = command_with_arg
    csp_subarray1_proxy_mock.obsState = obs_state
    device_proxy.command_inout(cmd_name, input_str)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription[requested_cmd](dummy_event)
    assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage


def test_command_cb_is_invoked_when_command_with_event_error_without_arg_is_called_async(mock_csp_subarray, event_subscription_without_arg, command_without_arg):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    cmd_name, obs_state, _ = command_without_arg
    csp_subarray1_proxy_mock.obsState = obs_state
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback_with_event_error(cmd_name)
    event_subscription_without_arg[cmd_name](dummy_event)
    assert const.ERR_INVOKING_CMD + cmd_name in device_proxy.activityMessage


def test_command_cb_is_invoked_releaseresources_when_command_with_event_error_async(mock_csp_subarray, event_subscription_without_arg):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.ReleaseAllResources()
    dummy_event = command_callback_with_event_error(const.CMD_REMOVE_ALL_RECEPTORS)
    event_subscription_without_arg[const.CMD_REMOVE_ALL_RECEPTORS](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_REMOVE_ALL_RECEPTORS in device_proxy.activityMessage


def test_command_with_arg_devfailed(mock_csp_subarray, event_subscription, command_with_arg):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    cmd_name, input_str, requested_cmd, obs_state, error_msg = command_with_arg
    csp_subarray1_proxy_mock.obsState = obs_state
    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_with_arg
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name, input_str)
    assert error_msg in str(df.value)


def test_command_without_arg_devfailed(mock_csp_subarray, event_subscription, command_without_arg):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    cmd_name, obs_state, error_msg = command_without_arg
    csp_subarray1_proxy_mock.obsState = obs_state
    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name)
    assert error_msg in str(df.value)


def test_command_releaseresources_devfailed(mock_csp_subarray, event_subscription):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.ReleaseAllResources()
    assert const.ERR_RELEASE_ALL_RESOURCES in str(df.value)


@pytest.fixture(
    scope="function",
    params=[
        ("EndScan", ObsState.SCANNING, "endscan_cmd_ended_cb", const.STR_ENDSCAN_SUCCESS),
        ("GoToIdle", ObsState.READY, "gotoidle_cmd_ended_cb", const.STR_GOTOIDLE_SUCCESS),
        ("Abort", ObsState.SCANNING, "abort_cmd_ended_cb" ,const.STR_ABORT_SUCCESS),
        ("Abort", ObsState.RESETTING, "abort_cmd_ended_cb", const.STR_ABORT_SUCCESS),
        ("Abort", ObsState.IDLE, "abort_cmd_ended_cb", const.STR_ABORT_SUCCESS),
        ("Abort", ObsState.CONFIGURING, "abort_cmd_ended_cb", const.STR_ABORT_SUCCESS),
        ("Abort", ObsState.READY, "abort_cmd_ended_cb", const.STR_ABORT_SUCCESS),
        ("Restart", ObsState.FAULT, "restart_cmd_ended_cb", const.STR_RESTART_SUCCESS),
        ("Restart", ObsState.ABORTED, "restart_cmd_ended_cb" ,const.STR_RESTART_SUCCESS),
        ("ObsReset", ObsState.ABORTED, "obsreset_cmd_ended_cb", const.STR_OBSRESET_SUCCESS),
        ("ObsReset", ObsState.FAULT, "obsreset_cmd_ended_cb", const.STR_OBSRESET_SUCCESS),
    ])
def command_with_correct_obsstate(request):
    cmd_name, obs_state, cmd_callback, activity_msg = request.param
    return cmd_name, obs_state, cmd_callback, activity_msg


def test_command_correct_obsstate(mock_csp_subarray, command_with_correct_obsstate):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    cmd_name, obs_state, cmd_callback, activity_msg = command_with_correct_obsstate
    csp_subarray1_proxy_mock.obsState = obs_state
    device_proxy.command_inout(cmd_name)
    csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with (cmd_name, any_method(with_name=cmd_callback))
    assert_activity_message(device_proxy, activity_msg)


@pytest.fixture(
    scope="function",
    params=[
        ("EndScan", ObsState.READY, const.ERR_DEVICE_NOT_IN_SCAN),
        ("GoToIdle", ObsState.IDLE, const.ERR_DEVICE_NOT_READY),
        ("Abort", ObsState.RESOURCING, const.ERR_UNABLE_ABORT_CMD),
        ("Abort", ObsState.EMPTY, const.ERR_UNABLE_ABORT_CMD),
        ("Restart", ObsState.EMPTY, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.RESOURCING, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.IDLE, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.CONFIGURING, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.SCANNING, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.READY, const.ERR_UNABLE_RESTART_CMD),
        ("ObsReset", ObsState.EMPTY, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.RESOURCING, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.IDLE, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.CONFIGURING, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.SCANNING, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.READY, const.ERR_UNABLE_OBSRESET_CMD),
    ])
def command_with_incorrect_obsstate(request):
    cmd_name, obs_state, activity_msg = request.param
    return cmd_name, obs_state, activity_msg


def test_command_fails_when_device_in_invalid_obstate(mock_csp_subarray, command_with_incorrect_obsstate):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    cmd_name, obs_state, activity_msg = command_with_incorrect_obsstate
    csp_subarray1_proxy_mock.obsState = obs_state
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name)
    assert activity_msg in str(df.value)


def test_assign_resources_should_send_csp_subarray_with_correct_receptor_id_list(mock_csp_subarray):
    #arrange
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    json_argument = json.loads(assign_input_str)
    receptorIDList_str = json_argument[const.STR_DISH][const.STR_RECEPTORID_LIST]
    # convert receptorIDList from list of string to list of int
    receptorIDList = [int(receptor_id) for receptor_id in receptorIDList_str]
    csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ADD_RECEPTORS,
                                                                     receptorIDList,
                                                                     any_method(with_name='add_receptors_ended'))
    assert_activity_message(device_proxy, const.STR_ADD_RECEPTORS_SUCCESS)


def test_assign_command_with_callback_method_with_devfailed_error(mock_csp_subarray, event_subscription):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
        dummy_event = command_callback_with_devfailed_exception()
        event_subscription[const.CMD_ADD_RECEPTORS](dummy_event)
    assert const.ERR_CALLBACK_CMD_FAILED in str(df.value)


def test_release_resource_should_command_csp_subarray_to_release_all_resources(mock_csp_subarray):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.ReleaseAllResources()
    csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_REMOVE_ALL_RECEPTORS,
                                                            any_method(with_name = 'releaseallresources_cmd_ended_cb'))
    assert_activity_message(device_proxy, const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)


def test_release_resource_should_raise_exception_when_not_idle_obsstate(mock_csp_subarray):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.ReleaseAllResources()
    assert const.ERR_DEVICE_NOT_IDLE in str(df.value)


def test_configure_to_send_correct_configuration_data_when_csp_subarray_is_idle(mock_csp_subarray):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.Configure(configure_str)
    argin_json = json.loads(configure_str)
    cspConfiguration = argin_json.copy()
    if "pointing" in cspConfiguration:
        del cspConfiguration["pointing"]
    csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_CONFIGURE,
                                json.dumps(cspConfiguration), any_method(with_name='configure_cmd_ended_cb'))


def test_configure_should_raise_exception_when_called_invalid_json(mock_csp_subarray):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Configure(invalid_key_str)
    assert const.ERR_INVALID_JSON_CONFIG in str(df.value)

def test_configure_should_raise_assertion_exception_when_called_invalid_obsstate(mock_csp_subarray):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Configure(configure_str)
    assert const.ERR_DEVICE_NOT_READY_OR_IDLE in str(df.value)


def test_start_scan_should_command_csp_subarray_to_start_its_scan_when_it_is_ready(mock_csp_subarray):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.StartScan(scan_input_str)
    csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STARTSCAN, '0',
                                                                    any_method(with_name='startscan_cmd_ended_cb'))


def test_start_scan_should_not_command_csp_subarray_to_start_scan_when_it_is_idle(mock_csp_subarray):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.StartScan(scan_input_str)
    assert_activity_message(device_proxy , const.ERR_DEVICE_NOT_READY)
    assert const.ERR_DEVICE_NOT_READY in str(df.value)


def test_add_receptors_ended_should_raise_dev_failed_exception_for_invalid_obs_state(mock_csp_subarray, event_subscription):
    device_proxy, csp_subarray1_proxy_mock = mock_csp_subarray
    csp_subarray1_proxy_mock.obsState = ObsState.READY
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(json.dumps(assign_input_file))
    assert const.ERR_RAISED_EXCEPTION in str(df.value)


def test_assign_resource_should_raise_exception_when_key_not_found():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.AssignResources(assign_invalid_key)
        assert const.ERR_RAISED_EXCEPTION in str(df)


def create_dummy_event_state(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    fake_event.device = proxy_mock
    return fake_event


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


def command_callback_with_devfailed_exception():
    # "This function is called when command is failed with DevFailed exception."
    tango.Except.throw_exception(const.ERR_DEVFAILED_MSG,
                                 const.ERR_CALLBACK_CMD_FAILED, " ", tango.ErrSeverity.ERR)


def raise_devfailed_with_arg(cmd_name, input_arg1, input_arg2):
    # "This function is called to raise DevFailed exception with arguments."
    tango.Except.throw_exception(const.STR_CMD_FAILED, const.ERR_DEVFAILED_MSG,
                                 cmd_name, tango.ErrSeverity.ERR)


def command_callback_with_command_exception():
    # "This function is called when there is exception in command calling."
    return Exception("Exception in command callback")


def raise_devfailed_exception(cmd_name, inp_str):
    # "This function is called to raise DevFailed exception."
    tango.Except.throw_exception("CspSubarrayLeafNode_CommandFailed", const.ERR_DEVFAILED_MSG,
                                 " ", tango.ErrSeverity.ERR)


def raise_devfailed_exception_for_scan(cmd_name, inp_str, cmd_cb):
    # "This function is called to raise DevFailed exception."
    tango.Except.throw_exception("CspSubarrayLeafNode_CommandFailed", const.ERR_DEVFAILED_MSG,
                                 " ", tango.ErrSeverity.ERR)


def test_status():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.Status() != const.STR_CSPSALN_INIT_SUCCESS


def test_read_delay_model():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.delayModel == " "


def test_write_delay_model():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.delayModel = " "
        assert tango_context.device.delayModel == " "


def test_health_state():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


def test_read_activity_message():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.activityMessage == " "


def test_write_activity_message():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.activityMessage = "test"
        assert tango_context.device.activityMessage == "test"


def test_logging_level():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_read_version_info():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.versionInfo == " "


def test_logging_targets():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False
            return other.__func__.__name__ == with_name if with_name else True
    return AnyMethod()


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

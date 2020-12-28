# Standard Python imports
import contextlib
import importlib
import sys
import types
import json
import pytest
import mock
from mock import MagicMock
from mock import Mock
from os.path import dirname, join

# Tango imports
import tango
from tango import DevState
from tango.test_context import DeviceTestContext
from tmc.common.tango_client import TangoClient
from centralnode.device_data import DeviceData

# Additional import
from centralnode import CentralNode, const, release
from centralnode.const import CMD_SET_STOW_MODE, STR_ON_CMD_ISSUED, STR_STOW_CMD_ISSUED_CN, STR_STANDBY_CMD_ISSUED
from ska.base.control_model import HealthState, AdminMode, SimulationMode, ControlMode, TestMode
from ska.base.control_model import LoggingLevel
from ska.base.commands import ResultCode

assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

release_input_file='command_ReleaseResources.json'
path= join(dirname(__file__), 'data' , release_input_file)
with open(path, 'r') as f:
    release_input_str= f.read()

invalid_json_Assign_Release_file='invalid_json_Assign_Release_Resources.json'
path= join(dirname(__file__), 'data', invalid_json_Assign_Release_file)
with open(path, 'r') as f:
    assign_release_invalid_str= f.read()

assign_invalid_key_file='invalid_key_AssignResources.json'
path= join(dirname(__file__), 'data', assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key=f.read()

release_invalid_key_file='invalid_key_ReleaseResources.json'
path= join(dirname(__file__), 'data', release_invalid_key_file)
with open(path, 'r') as f:
    release_invalid_key=f.read()


@pytest.fixture(scope = 'function')
def mock_subarraynode_device():
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dut_properties = {
        'TMMidSubarrayNodes': 'ska_mid/tm_subarray_node/1'
    }

    event_subscription_map = {}
    subarray1_device_proxy_mock = Mock()
    Mock().subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['TMMidSubarrayNodes'])
            yield tango_context.device, tango_client_obj, dut_properties['TMMidSubarrayNodes'], event_subscription_map

@pytest.fixture(
    scope="function",
    params=[
        HealthState.UNKNOWN
    ])
def health_state(request):
    return request.param

def dummy_subscriber(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"ska_mid/tm_leaf_node/csp_master/{attribute}"
    fake_event.attr_value.value =  HealthState.UNKNOWN 
    print("Inside dummy subscriber ...........................")
    print( fake_event.attr_value.value )

    callback_method(fake_event)
    return 10


@pytest.fixture( scope="function",
    params=[HealthState.DEGRADED, HealthState.OK, HealthState.UNKNOWN, HealthState.FAILED])
def central_node_test_info(request):
    device_under_test = CentralNode
    csp_master_ln_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    csp_master_ln_health_attribute = 'cspHealthState'

    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_ln_fqdn
    }

    event_subscription_map = {}
    csp_master_ln_proxy_mock = Mock()
    csp_master_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs:
        event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_ln_fqdn: csp_master_ln_proxy_mock
    }

    test_info = {
        'csp_master_ln_health_attribute': csp_master_ln_health_attribute,
        'initial_dut_properties': initial_dut_properties,
        'proxies_to_mock': proxies_to_mock,
        'csp_master_ln_health_state': request.param,
        'event_subscription_map': event_subscription_map,
        'csp_master_ln_fqdn': csp_master_ln_fqdn,
    }
    return test_info

def test_startup(mock_subarray):
    device_proxy, tango_client_obj = mock_subarray
    assert device_proxy.StartUpTelescope() == [[ResultCode.OK], ['STARTUPTELESCOPE (ON) command invoked from Central node']]
    assert device_proxy.state() == DevState.ON

def test_standby(mock_subarray):
    device_proxy, tango_client_obj = mock_subarray
    # device_proxy.StartUpTelescope()
    # assert device_proxy.state() == DevState.ON
    device_proxy.StartUpTelescope()
    assert device_proxy.StandByTelescope() == [[ResultCode.OK], ["STANDBYTELESCOPE command invoked from Central node"]]
    assert device_proxy.state() == DevState.OFF

# # Mocking AssignResources command success response from SubarrayNode
def mock_subarray_call_assign_resources_success(arg1, arg2):
    arg = json.loads(assign_input_str)
    argout = [str(arg["dish"]["receptorIDList"])]
    return [ResultCode.STARTED, argout]

# Mocking ReleaseResources command success response from SubarrayNode
def mock_subarray_call_release_resources_success(arg1, arg2):
    argout = ["[]"]
    return [ResultCode.STARTED, argout]

@pytest.fixture(scope='function')
def mock_subarray():
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    tm_subarrays = []
    tm_subarrays.append(subarray1_fqdn)
    dut_properties = {
        'TMMidSubarrayNodes': tm_subarrays,
        'NumDishes': 4
    }
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=MagicMock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['TMMidSubarrayNodes'])
            yield tango_context.device, tango_client_obj


def test_assign_resources(mock_subarray):
    device_proxy,tango_client_obj=mock_subarray
    # mocking subarray device state as ON as per new state model
    tango_client_obj.DevState = DevState.ON
    receptorIDList_success = []
    receptorIDList_success.append("0001")
    dish = {}
    dish["receptorIDList_success"] = receptorIDList_success
    success_response = {}
    success_response["dish"] = dish
    tango_client_obj.deviceproxy.command_inout.side_effect = mock_subarray_call_assign_resources_success
    message = device_proxy.AssignResources(assign_input_str)
    assert json.loads(message) == success_response


def test_assign_resources_should_raise_devfailed_exception_when_subarray_node_throws_devfailed_exception(mock_subarray):
    device_proxy,tango_client_obj=mock_subarray
    tango_client_obj.DevState = DevState.OFF
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    assert "Error occurred while assigning resources to the Subarray" in str(df)


def test_assign_resources_invalid_json_value():
    with fake_tango_system(CentralNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.AssignResources(assign_release_invalid_str)
        assert const.STR_RESOURCE_ALLOCATION_FAILED in str(df.value)


def test_assign_resources_invalid_key():
    with fake_tango_system(CentralNode) \
            as tango_context:
        result = 'test'
        with pytest.raises(tango.DevFailed):
            result = tango_context.device.AssignResources(assign_invalid_key)
        assert 'test' in result


def test_assign_resources_raise_devfailed_when_reseource_reallocation():
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    subarray2_fqdn = 'ska_mid/tm_subarray_node/2'
    tm_subarrays = []
    tm_subarrays.append(subarray1_fqdn)
    tm_subarrays.append(subarray2_fqdn)
    dut_properties = {
        'TMMidSubarrayNodes': tm_subarrays,
        'NumDishes' : 4
    }

    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties) as tango_context:
        device_proxy=tango_context.device
        receptorIDList_success = []
        receptorIDList_success.append("0001")
        dish = {}
        dish["receptorIDList_success"] = receptorIDList_success
        success_response = {}
        success_response["dish"] = dish
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=MagicMock()) as mock_obj:
            tango_client_obj = TangoClient(subarray1_fqdn)
            # subarray1_proxy_mock.command_inout.side_effect = mock_subarray_call_assign_resources_success
            tango_client_obj.deviceproxy.command_inout.side_effect = mock_subarray_call_assign_resources_success
            message = device_proxy.AssignResources(assign_input_str)
            assert json.loads(message) == success_response
            reallocation_request = json.loads(assign_input_str)
            reallocation_request["subarrayID"] = 2
            with pytest.raises(tango.DevFailed) as df:
                device_proxy.AssignResources(json.dumps(reallocation_request))
            assert const.ERR_RECEPTOR_ID_REALLOCATION in str(df.value)

# Test cases for Attributes
def test_telescope_health_state():
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.telescopeHealthState == HealthState.UNKNOWN

def test_activity_message():
    with fake_tango_system(CentralNode) as tango_context:
        tango_context.device.activityMessage = ''
        assert tango_context.device.activityMessage == ''


def test_logging_level():
    with fake_tango_system(CentralNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets():
    with fake_tango_system(CentralNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_test_mode():
    with fake_tango_system(CentralNode) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_simulation_mode():
    with fake_tango_system(CentralNode) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode


def test_control_mode():
    with fake_tango_system(CentralNode) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_health_state():
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK

# # Test cases for commands
def test_stow_antennas_should_set_stow_mode_on_leaf_nodes():
    dish_device_ids = [str(i).zfill(4) for i in range(1, 4)]
    fqdn_prefix = "ska_mid/tm_leaf_node/d"
    initial_dut_properties = {
        'DishLeafNodePrefix': fqdn_prefix,
        'NumDishes': len(dish_device_ids)
    }
    # proxies_to_mock = { fqdn_prefix + device_id : Mock() for device_id in dish_device_ids }

    with fake_tango_system(CentralNode, initial_dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(initial_dut_properties['DishLeafNodePrefix'] + dish_device_ids[0])
            tango_context.device.StowAntennas(dish_device_ids)
            # for proxy_mock in proxies_to_mock.values():
            tango_client_obj.deviceproxy.command_inout.assert_called_with(CMD_SET_STOW_MODE, None)

def test_stow_antennas_should_raise_devfailed_exception():
    dish_device_ids = [str(i).zfill(4) for i in range(1, 4)]
    fqdn_prefix = "ska_mid/tm_leaf_node/d"
    initial_dut_properties = {
        'DishLeafNodePrefix': fqdn_prefix,
        'NumDishes': len(dish_device_ids)
    }

    with fake_tango_system(CentralNode, initial_dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(initial_dut_properties['DishLeafNodePrefix'] + dish_device_ids[0])
            tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
            with pytest.raises(tango.DevFailed) as df:
                tango_context.device.StowAntennas(dish_device_ids)
            assert const.ERR_EXE_STOW_CMD in str(df.value)

def test_stow_antennas_invalid_value():
#     """Negative Test for StowAntennas"""
    with fake_tango_system(CentralNode) \
            as tango_context:
        argin = ["invalid_antenna", ]
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.StowAntennas(argin)

        assert const.ERR_STOW_ARGIN in str(df.value)


def test_release_resources(mock_subarray):
    device_proxy,tango_client_obj=mock_subarray

    release_all_success = {"ReleaseAll": True, "receptorIDList": []}
    tango_client_obj.deviceproxy.command_inout.side_effect = mock_subarray_call_release_resources_success
    message = device_proxy.ReleaseResources(release_input_str)
    assert json.dumps(release_all_success) in message


def test_release_resources_should_raise_devfailed_exception():
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dut_properties = {
        'TMMidSubarrayNodes': subarray1_fqdn
    }
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['TMMidSubarrayNodes'])
            tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
            with pytest.raises(tango.DevFailed) as df:
                tango_context.device.ReleaseResources(release_input_str)
            assert const.ERR_DEVFAILED_MSG in str(df.value)


def test_release_resources_invalid_json_value():
    with fake_tango_system(CentralNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.ReleaseResources(assign_release_invalid_str)
        assert const.ERR_INVALID_JSON in str(df.value)


def test_release_resources_invalid_key():
    with fake_tango_system(CentralNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.ReleaseResources(release_invalid_key)
        assert const.ERR_JSON_KEY_NOT_FOUND in str(df.value)

@pytest.fixture(
    scope="function",
    params=[
        ("StandByTelescope"),
        ("StartUpTelescope")
    ])
def command_without_arg_devfailed(request):
    cmd_name = request.param
    return cmd_name

def test_command_without_arg_should_raise_devfailed_exception(mock_subarray, command_without_arg_devfailed):
    device_proxy, tango_client = mock_subarray
    cmd_name = command_without_arg_devfailed
    tango_client.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed):
        device_proxy.command_inout(cmd_name)
    assert device_proxy.state() == DevState.FAULT

# # Test cases for Telescope Health State

@pytest.fixture(scope="function")
def mock_csp_master_proxy():
    dut_properties = {'CspMasterFQDN': 'mid_csp/elt/master'}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['CspMasterFQDN'])
            yield tango_context.device, tango_client_obj, dut_properties['CspMasterFQDN'], event_subscription_map


def test_telescope_health_state_matches_csp_master_leaf_node_health_state_after_start(mock_csp_master_proxy, health_state):
    device_proxy, tango_client_obj, csp_master_fqdn, event_subscription_map = mock_csp_master_proxy
    device_data = DeviceData.get_instance()
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect = dummy_subscriber):
            # updator = HealthStateAggreegator()
            tango_client_obj = TangoClient('ska_mid/tm_leaf_node/csp_master')
            device_proxy.StartUpTelescope()    
    assert device_data._telescope_health_state == health_state


@pytest.fixture(scope="function")
def mock_sdp_master_proxy():
    dut_properties = {'SdpMasterFQDN': 'mid_sdp/elt/master'}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['SdpMasterFQDN'])
            yield tango_context.device, tango_client_obj, dut_properties['SdpMasterFQDN'], event_subscription_map


def test_telescope_health_state_is_ok_when_sdp_master_leaf_node_is_ok_after_start(mock_sdp_master_proxy, health_state):
    device_proxy, tango_client_obj, csp_master_fqdn, event_subscription_map = mock_sdp_master_proxy
    device_data = DeviceData.get_instance()
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect = dummy_subscriber):
            tango_client_obj = TangoClient('ska_mid/tm_leaf_node/sdp_master')
            device_proxy.StartUpTelescope()
    assert device_data._telescope_health_state == health_state


@pytest.fixture(scope = 'function')
def mock_subarraynode2_proxy():
    dut_properties = {'subarray2_fqdn': 'ska_mid/tm_subarray_node/2'}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['subarray2_fqdn'])
            yield  tango_context.device ,tango_client_obj , dut_properties['subarray2_fqdn'], event_subscription_map

def test_telescope_health_state_is_ok_when_subarray1_is_ok_after_start(mock_subarraynode_device, health_state):
    device_proxy , tango_client_obj, subarray1_fqdn, event_subscription_map = mock_subarraynode_device
    device_data = DeviceData.get_instance()
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect = dummy_subscriber):
            # updator = HealthStateAggreegator()
            tango_client_obj = TangoClient('ska_mid/tm_subarray_node/1')
            device_proxy.StartUpTelescope()
    assert device_data._telescope_health_state == health_state

def test_telescope_health_state_is_ok_when_subarray2_is_ok_after_start(mock_subarraynode2_proxy, health_state):
    device_proxy , tango_client_obj, subarray2_fqdn, event_subscription_map = mock_subarraynode2_proxy
    device_data = DeviceData.get_instance()
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect = dummy_subscriber):
            tango_client_obj = TangoClient('ska_mid/tm_subarray_node/2')
            device_proxy.StartUpTelescope()
    assert device_data._telescope_health_state == health_state

@pytest.fixture(scope = 'function')
def mock_subarraynode3_proxy():
    dut_properties = {'subarray3_fqdn': 'ska_mid/tm_subarray_node/3'}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['subarray3_fqdn'])
            yield  tango_context.device ,tango_client_obj , dut_properties['subarray3_fqdn'], event_subscription_map

def test_telescope_health_state_is_ok_when_subarray3_is_ok_after_start(mock_subarraynode3_proxy, health_state):
    device_proxy , tango_client_obj, subarray3_fqdn, event_subscription_map = mock_subarraynode3_proxy
    device_data = DeviceData.get_instance()
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect = dummy_subscriber):
            tango_client_obj = TangoClient('ska_mid/tm_subarray_node/3')
            device_proxy.StartUpTelescope()
    assert device_data._telescope_health_state == health_state


# # Throw Devfailed exception for command with argument
def raise_devfailed_exception(*args):
    tango.Except.throw_exception("CentralNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)
#

def test_version_id():
    """Test for versionId"""
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False
            return other.__func__.__name__ == with_name if with_name else True
    return AnyMethod()


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

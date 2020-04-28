import contextlib
import importlib
import sys
import mock
import types
import json
import pytest
from tango import DevState
from tango.test_context import DeviceTestContext
from mock import MagicMock
from mock import Mock
from centralnode import CentralNode,const
from centralnode.const import CMD_SET_STOW_MODE, STR_STARTUP_CMD_ISSUED, \
    STR_STOW_CMD_ISSUED_CN, STR_STANDBY_CMD_ISSUED
from ska.base.control_model import HealthState, AdminMode, SimulationMode, ControlMode, TestMode
from ska.base.control_model import LoggingLevel


def create_dummy_event_for_degraded(csp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.DEGRADED
    return fake_event

def create_dummy_event_for_ok(csp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.OK
    return fake_event

def create_dummy_event_for_unknown(csp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.UNKNOWN
    return fake_event

def create_dummy_event_for_failed(csp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.FAILED
    return fake_event


def create1_dummy_event_for_ok(sdp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{sdp_master_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.OK
    return fake_event

def create_subarray_dummy_event_for_unknown(subarray_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{subarray_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.UNKNOWN
    return fake_event

def create_subarray_dummy_event_for_failed(subarray_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{subarray_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.FAILED
    return fake_event

def create_subarray_dummy_event_for_degraded(subarray_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{subarray_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.DEGRADED
    return fake_event

def create_subarray_dummy_event_for_ok(subarray_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{subarray_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.OK
    return fake_event

def test_telescope_health_state_is_degraded_when_csp_master_leaf_node_is_degraded_after_start():
    # arrange:
    device_under_test = CentralNode
    csp_master_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    csp_master_health_attribute = 'cspHealthState'
    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event_for_degraded(csp_master_fqdn)
        event_subscription_map[csp_master_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.DEGRADED

def test_telescope_health_state_is_OK_when_csp_master_leaf_node_is_OK_after_start():
    # arrange:
    device_under_test = CentralNode
    csp_master_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    csp_master_health_attribute = 'cspHealthState'
    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event_for_ok(csp_master_fqdn)
        event_subscription_map[csp_master_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.OK

def test_telescope_health_state_is_UNKNOWN_when_csp_master_leaf_node_is_UNKNOWN_after_start():
    # arrange:
    device_under_test = CentralNode
    csp_master_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    csp_master_health_attribute = 'cspHealthState'
    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event_for_unknown(csp_master_fqdn)
        event_subscription_map[csp_master_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.UNKNOWN

def test_telescope_health_state_is_FAILED_when_csp_master_leaf_node_is_FAILED_after_start():
    # arrange:
    device_under_test = CentralNode
    csp_master_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    csp_master_health_attribute = 'cspHealthState'
    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event_for_failed(csp_master_fqdn)
        print('dummy_event in csp failed',dummy_event)
        event_subscription_map[csp_master_health_attribute](dummy_event)
        print('tango_context.device.telescopeHealthState in csp failed:',
              tango_context.device.telescopeHealthState)
        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.FAILED


def test_telescope_health_state_is_ok_when_sdp_master_leaf_node_is_ok_after_start():
    # arrange:
    device_under_test = CentralNode
    sdp_master_fqdn = 'ska_mid/tm_leaf_node/sdp_master'
    sdp_master_health_attribute = 'sdpHealthState'
    initial_dut_properties = {
        'SdpMasterLeafNodeFQDN': sdp_master_fqdn
    }

    event_subscription_map = {}

    sdp_master_device_proxy_mock = Mock()
    sdp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        sdp_master_fqdn: sdp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create1_dummy_event_for_ok(sdp_master_fqdn)
        event_subscription_map[sdp_master_health_attribute](dummy_event)
        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.OK


def test_telescope_health_state_is_degraded_when_subarray_leaf_node_is_degraded_after_start():
    # arrange:
    device_under_test = CentralNode
    subarray_fqdn = 'ska_mid/tm_subarray_node/1'
    subarray_health_attribute = 'healthState'
    initial_dut_properties = {
        'TMMidSubarrayNodes': subarray_fqdn
    }

    event_subscription_map = {}

    subarray_device_proxy_mock = Mock()
    subarray_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        subarray_fqdn: subarray_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_subarray_dummy_event_for_degraded(subarray_fqdn)
        event_subscription_map[subarray_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.DEGRADED


def test_telescope_health_state_is_ok_when_subarray_leaf_node_is_ok_after_start():
    # arrange:
    device_under_test = CentralNode
    subarray_fqdn = 'ska_mid/tm_subarray_node/1'
    subarray_health_attribute = 'healthState'
    initial_dut_properties = {
        'TMMidSubarrayNodes': subarray_fqdn
    }

    event_subscription_map = {}

    subarray_device_proxy_mock = Mock()
    subarray_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        subarray_fqdn: subarray_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_subarray_dummy_event_for_ok(subarray_fqdn)
        event_subscription_map[subarray_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.OK


def test_telescope_health_state_is_unknown_when_subarray_leaf_node_is_unknown_after_start():
    # arrange:
    device_under_test = CentralNode
    subarray_fqdn = 'ska_mid/tm_subarray_node/1'
    subarray_health_attribute = 'healthState'
    initial_dut_properties = {
        'TMMidSubarrayNodes': subarray_fqdn
    }

    event_subscription_map = {}

    subarray_device_proxy_mock = Mock()
    subarray_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        subarray_fqdn: subarray_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_subarray_dummy_event_for_unknown(subarray_fqdn)
        event_subscription_map[subarray_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.UNKNOWN


def test_telescope_health_state_is_failed_when_subarray_leaf_node_is_failed_after_start():
    # arrange:
    device_under_test = CentralNode
    subarray_fqdn = 'ska_mid/tm_subarray_node/1'
    subarray_health_attribute = 'healthState'
    initial_dut_properties = {
        'TMMidSubarrayNodes': subarray_fqdn
    }

    event_subscription_map = {}

    subarray_device_proxy_mock = Mock()
    subarray_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        subarray_fqdn: subarray_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_subarray_dummy_event_for_failed(subarray_fqdn)
        event_subscription_map[subarray_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.FAILED

def test_stow_antennas_should_set_stow_mode_on_leaf_nodes():
    # arrange:
    device_under_test = CentralNode
    dish_device_ids = [str(i).zfill(4) for i in range(1,10)]
    fqdn_prefix = "ska_mid/tm_leaf_node/d"
    initial_dut_properties = {
        'DishLeafNodePrefix': fqdn_prefix,
        'NumDishes': len(dish_device_ids)
    }
    proxies_to_mock = { fqdn_prefix + device_id : Mock() for device_id in dish_device_ids }

    # act:
    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        tango_context.device.StowAntennas(dish_device_ids)

    # assert:
    for proxy_mock in proxies_to_mock.values():
        proxy_mock.command_inout.assert_called_with(CMD_SET_STOW_MODE)


def test_activity_message_attribute_captures_the_last_received_command():
    # arrange:
    device_under_test = CentralNode

    # act & assert:
    with fake_tango_system(device_under_test)as tango_context:
        dut = tango_context.device
        dut.StartUpTelescope()
        assert_activity_message(dut, STR_STARTUP_CMD_ISSUED)

        dut.StandByTelescope()
        assert_activity_message(dut, STR_STANDBY_CMD_ISSUED)

def test_telescopeHealthState():
    # arrange:
    device_under_test = CentralNode

    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.telescopeHealthState == HealthState.OK

def test_subarray1HealthState():
    # arrange:
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.subarray1HealthState == HealthState.OK

def test_subarray2HealthState():
    # arrange:
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.subarray2HealthState == HealthState.OK

def test_subarray3HealthState():
    # arrange:
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.subarray3HealthState == HealthState.OK

def test_activityMessage():
    # arrange:
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.activityMessage = 'test'
        assert tango_context.device.activityMessage == "test"

def test_State():
    #arrange
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.State() == DevState.ON

def test_Status():
    # arrange
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.Status() == const.STR_INIT_SUCCESS

def test_loggingLevel():
    # arrange
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO

def test_loggingTargets():
    # arrange
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets

def test_testMode():
    # arrange
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode

def test_simulationMode():
    # arrange
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode

def test_controlMode():
    # arrange
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode

def test_adminMode():
    # arrange
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.adminMode == AdminMode.ONLINE

def test_healthState():
    # arrange
    device_under_test = CentralNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.healthState == HealthState.OK

def assert_activity_message(dut, expected_message):
    assert dut.activityMessage == expected_message # reads tango attribute


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def test_assign_resources_should_send_json_to_subarraynode():
    # arrange:
    device_under_test = CentralNode
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dut_properties = {
        'TMMidSubarrayNodes': subarray1_fqdn
    }

    subarray1_proxy_mock = MagicMock()
    subarray1_proxy_mock.DevState = DevState.OFF
    proxies_to_mock = {
        subarray1_fqdn: subarray1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        assign_command = '{"subarrayID":1,"dish":{"receptorIDList":["0001"]}}'
        device_proxy=tango_context.device
        device_proxy.AssignResources(assign_command)

        # assert:
        jsonArgument = json.loads(assign_command)
        subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES,
                                                             jsonArgument["dish"]["receptorIDList"])

        assert_activity_message(tango_context.device, const.STR_ASSIGN_RESOURCES_SUCCESS)

@pytest.mark.xfail
def test_release_resources_when_subarray_is_idle():
    # arrange:
    device_under_test = CentralNode
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dut_properties = {
        'TMMidSubarrayNodes': subarray1_fqdn
    }

    subarray1_proxy_mock = MagicMock()
    subarray1_proxy_mock.DevState = DevState.ON
    subarray1_proxy_mock.receptorIDList = [1]
    proxies_to_mock = {
        subarray1_fqdn: subarray1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        release_input= '{"subarrayID":1,"releaseALL":true,"receptorIDList":[]}'
        tango_context.device.ReleaseResources(release_input)

        # assert:
        jsonArgument = json.loads(release_input)
        if jsonArgument['releaseALL'] == True:
            subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_RESOURCES)


def test_standby():
    # arrange:
    device_under_test = CentralNode
    csp_master_ln_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    sdp_master_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_master'
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dish_device_ids = [str(i).zfill(1) for i in range(1,4)]
    dish_leaf_fqdn_prefix = "ska_mid/tm_leaf_node/d"

    dut_properties = {
        'DishLeafNodePrefix': dish_leaf_fqdn_prefix,
        'SdpMasterLeafNodeFQDN': sdp_master_ln_fqdn,
        'CspMasterLeafNodeFQDN': csp_master_ln_fqdn,
        'TMMidSubarrayNodes': subarray1_fqdn,
        'NumDishes': len(dish_device_ids)
    }
    dish_ln1_proxy_mock = MagicMock()
    csp_master_ln_proxy_mock = Mock()
    sdp_master_ln_proxy_mock = Mock()
    subarray1_proxy_mock = MagicMock()
    proxies_to_mock = {
        dish_leaf_fqdn_prefix + "0001": dish_ln1_proxy_mock,
        csp_master_ln_fqdn: csp_master_ln_proxy_mock,
        sdp_master_ln_fqdn: sdp_master_ln_proxy_mock,
        subarray1_fqdn: subarray1_proxy_mock
    }
    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.StandByTelescope()

        # assert:
        dish_ln1_proxy_mock.command_inout.assert_called_with(const.CMD_SET_STANDBY_MODE)
        csp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STANDBY, [])
        sdp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STANDBY)
        subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_STANDBY)
        assert_activity_message(tango_context.device, const.STR_STANDBY_CMD_ISSUED)

def test_startup():
    # arrange:
    device_under_test = CentralNode
    csp_master_ln_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    sdp_master_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_master'
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dish_device_ids = [str(i).zfill(1) for i in range(1,4)]
    dish_leaf_fqdn_prefix = "ska_mid/tm_leaf_node/d"

    dut_properties = {
        'DishLeafNodePrefix': dish_leaf_fqdn_prefix,
        'SdpMasterLeafNodeFQDN': sdp_master_ln_fqdn,
        'CspMasterLeafNodeFQDN': csp_master_ln_fqdn,
        'TMMidSubarrayNodes': subarray1_fqdn,
        'NumDishes': len(dish_device_ids)
    }
    dish_ln1_proxy_mock = MagicMock()
    csp_master_ln_proxy_mock = Mock()
    sdp_master_ln_proxy_mock = Mock()
    subarray1_proxy_mock = MagicMock()
    proxies_to_mock = {
        dish_leaf_fqdn_prefix + "0001": dish_ln1_proxy_mock,
        csp_master_ln_fqdn: csp_master_ln_proxy_mock,
        sdp_master_ln_fqdn: sdp_master_ln_proxy_mock,
        subarray1_fqdn: subarray1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.StartUpTelescope()

        # assert:
        dish_ln1_proxy_mock.command_inout.assert_called_with(const.CMD_SET_OPERATE_MODE)
        csp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STARTUP, [])
        sdp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STARTUP)
        subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_STARTUP)
        assert_activity_message(tango_context.device, const.STR_STARTUP_CMD_ISSUED)


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
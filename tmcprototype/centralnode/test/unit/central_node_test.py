import contextlib
import importlib
import sys
import mock
from mock import Mock
from centralnode import CentralNode
from centralnode.const import CMD_SET_STOW_MODE, STR_STARTUP_CMD_ISSUED, STR_STOW_CMD_ISSUED_CN, STR_STANDBY_CMD_ISSUED
from tango.test_context import DeviceTestContext
from ska.base.control_model import HealthState, AdminMode, SimulationMode, ControlMode, TestMode, LoggingLevel

def test_telescope_health_state_is_degraded_when_csp_master_leaf_node_is_degraded_after_start():
    # arrange:
    device_under_test = CentralNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_master_health_attribute = 'cspHealthState'
    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event(csp_master_fqdn)
        event_subscription_map[csp_master_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.DEGRADED


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


def create_dummy_event(csp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.DEGRADED
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

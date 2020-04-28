import contextlib
import importlib
import sys
import json
import types
import mock
from mock import Mock
import tango
from tango import DevState
from tango.test_context import DeviceTestContext
from cspmasterleafnode import CspMasterLeafNode, const
from ska.base.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
from ska.base.control_model import LoggingLevel
import pytest
import time

def test_on_should_command_csp_master_leaf_node_to_start():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid_csp/elt/master'

    dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    csp_proxy_mock = Mock()

    proxies_to_mock = {
        csp_master_fqdn: csp_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        on_config = []
        # act:
        tango_context.device.On(on_config)

        # assert:
        csp_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ON, on_config,
                                                                    any_method(with_name='commandCallback'))

def test_off_should_command_csp_master_leaf_node_to_stop():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid_csp/elt/master'

    dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    csp_proxy_mock = Mock()

    proxies_to_mock = {
        csp_master_fqdn: csp_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        off_config = []
        # act:
        tango_context.device.Off(off_config)

        # assert:
        csp_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_OFF, off_config,
                                                                    any_method(with_name='commandCallback'))


def test_standby_should_command_csp_master_leaf_node_to_standby():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid_csp/elt/master'

    dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    csp_proxy_mock = Mock()

    proxies_to_mock = {
        csp_master_fqdn: csp_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        standby_config = []
        # act:
        tango_context.device.Standby(standby_config)

        # assert:
        csp_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STANDBY, standby_config,
                                                                    any_method(with_name='commandCallback'))


def test_attribute_cspCbfHealthState_of_csp_master_is_equal_to_OK():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_master_health_attribute = 'cspCbfHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
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
        dummy_event = create_dummy_event_for_cspCbfHealthState_OK(csp_master_fqdn)
        event_subscription_map[csp_master_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_CBF_HEALTH_OK

def create_dummy_event_for_cspCbfHealthState_OK(csp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_fqdn}/cspCbfHealthState"
    fake_event.attr_value.value = HealthState.OK
    return fake_event

# def test_attribute_cspCbfHealthState_of_csp_master_is_equal_to_DEGRADED():
#     # arrange:
#     device_under_test = CspMasterLeafNode
#     csp_master_fqdn = 'mid/csp_elt/master'
#     csp_master_health_attribute = 'cspCbfHealthState'
#     initial_dut_properties = {
#         'CspMasterFQDN': csp_master_fqdn
#     }
#
#     event_subscription_map = {}
#
#     csp_master_device_proxy_mock = Mock()
#     csp_master_device_proxy_mock.subscribe_event.side_effect = (
#         lambda attr_name, event_type, callback, *args,
#                **kwargs: event_subscription_map.update({attr_name: callback}))
#
#     proxies_to_mock = {
#         csp_master_fqdn: csp_master_device_proxy_mock
#     }
#
#     with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
#         # act:
#         dummy_event = create_dummy_event_for_cspCbfHealthState_DEGRADED(csp_master_fqdn)
#         event_subscription_map[csp_master_health_attribute](dummy_event)
#
#         # assert:
#         assert tango_context.device.cspCbfHealthState == HealthState.DEGRADED
#
# def create_dummy_event_for_cspCbfHealthState_DEGRADED(csp_master_fqdn):
#     fake_event = Mock()
#     fake_event.err = False
#     fake_event.attr_name = f"{csp_master_fqdn}/cspCbfHealthState"
#     fake_event.attr_value.value = HealthState.DEGRADED
#     return fake_event
#
# def test_attribute_cspCbfHealthState_of_csp_master_is_equal_to_FAILED():
#     # arrange:
#     device_under_test = CspMasterLeafNode
#     csp_master_fqdn = 'mid/csp_elt/master'
#     csp_master_health_attribute = 'cspCbfHealthState'
#     initial_dut_properties = {
#         'CspMasterFQDN': csp_master_fqdn
#     }
#
#     event_subscription_map = {}
#
#     csp_master_device_proxy_mock = Mock()
#     csp_master_device_proxy_mock.subscribe_event.side_effect = (
#         lambda attr_name, event_type, callback, *args,
#                **kwargs: event_subscription_map.update({attr_name: callback}))
#
#     proxies_to_mock = {
#         csp_master_fqdn: csp_master_device_proxy_mock
#     }
#
#     with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
#         # act:
#         dummy_event = create_dummy_event_for_cspCbfHealthState_FAILED(csp_master_fqdn)
#         event_subscription_map[csp_master_health_attribute](dummy_event)
#
#         # assert:
#         assert tango_context.device.cspCbfHealthState == HealthState.FAILED
#
# def create_dummy_event_for_cspCbfHealthState_FAILED(csp_master_fqdn):
#     fake_event = Mock()
#     fake_event.err = False
#     fake_event.attr_name = f"{csp_master_fqdn}/cspCbfHealthState"
#     fake_event.attr_value.value = HealthState.FAILED
#     return fake_event
#
# def test_attribute_cspCbfHealthState_of_csp_master_is_equal_to_UNKNOWN():
#     # arrange:
#     device_under_test = CspMasterLeafNode
#     csp_master_fqdn = 'mid/csp_elt/master'
#     csp_master_health_attribute = 'cspCbfHealthState'
#     initial_dut_properties = {
#         'CspMasterFQDN': csp_master_fqdn
#     }
#
#     event_subscription_map = {}
#
#     csp_master_device_proxy_mock = Mock()
#     csp_master_device_proxy_mock.subscribe_event.side_effect = (
#         lambda attr_name, event_type, callback, *args,
#                **kwargs: event_subscription_map.update({attr_name: callback}))
#
#     proxies_to_mock = {
#         csp_master_fqdn: csp_master_device_proxy_mock
#     }
#
#     with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
#         # act:
#         dummy_event = create_dummy_event_for_cspCbfHealthState_UNKNOWN(csp_master_fqdn)
#         event_subscription_map[csp_master_health_attribute](dummy_event)
#
#         # assert:
#         assert tango_context.device.cspCbfHealthState == HealthState.UNKNOWN
#
# def create_dummy_event_for_cspCbfHealthState_UNKNOWN(csp_master_fqdn):
#     fake_event = Mock()
#     fake_event.err = False
#     fake_event.attr_name = f"{csp_master_fqdn}/cspCbfHealthState"
#     fake_event.attr_value.value = HealthState.UNKNOWN
#     return fake_event

def test_attribute_cspPssHealthCallback_of_csp_master_is_equal_to_OK():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_master_health_attribute = 'cspPssHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
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
        dummy_event = create_dummy_event_for_cspPssHealthCallback_OK(csp_master_fqdn)
        event_subscription_map[csp_master_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PSS_HEALTH_OK

def create_dummy_event_for_cspPssHealthCallback_OK(csp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_fqdn}/cspPssHealthState"
    fake_event.attr_value.value = HealthState.OK
    return fake_event

def test_attribute_cspPstHealthCallback_of_csp_master_is_equal_to_OK():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_master_health_attribute = 'cspPstHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
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
        dummy_event = create_dummy_event_for_cspPssHealthCallback_OK(csp_master_fqdn)
        event_subscription_map[csp_master_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PST_HEALTH_OK

def create_dummy_event_for_cspPstHealthCallback_OK(csp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_fqdn}/cspPstHealthState"
    fake_event.attr_value.value = HealthState.OK
    return fake_event


def test_activityMessage():
    # arrange:
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.activityMessage = "text"
        assert tango_context.device.activityMessage == "text"

def test_State():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.State() == DevState.ALARM

def test_Status():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert const.STR_DEV_ALARM in tango_context.device.Status()

def test_loggingLevel():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO

def test_loggingTargets():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets

def test_testMode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode

def test_simulationMode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode

def test_controlMode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode

def test_adminMode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.adminMode == AdminMode.ONLINE

def test_healthState():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.healthState == HealthState.OK

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
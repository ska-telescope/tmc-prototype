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
    #dish_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        csp_master_fqdn: csp_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        on_config = "0"
        # act:
        tango_context.device.On(on_config)

        # assert:
        if type(list(on_config)) == list:
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
    #dish_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        csp_master_fqdn: csp_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        off_config = "0"
        # act:
        tango_context.device.Off(off_config)

        # assert:
        if type(list(off_config)) == list:
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
    #dish_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        csp_master_fqdn: csp_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        standby_config = "0"
        # act:
        tango_context.device.Standby(standby_config)

        # assert:
        if type(list(standby_config)) == list:
            csp_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STANDBY, standby_config,
                                                                    any_method(with_name='commandCallback'))

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
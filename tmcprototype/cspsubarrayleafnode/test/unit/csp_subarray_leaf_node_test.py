import contextlib
import importlib
import sys
import json
import mock
import types
import pytest
import tango

from mock import Mock
from tango import DevState
from cspsubarrayleafnode import CspSubarrayLeafNode, const
from tango.test_context import DeviceTestContext
from ska.base.control_model import HealthState, ObsState, TestMode, SimulationMode, ControlMode, AdminMode, LoggingLevel

def test_start_scan_should_command_csp_subarray_master_to_start_its_scan_when_it_is_ready():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray_fqdn
    }

    csp_subarray_proxy_mock = Mock()
    csp_subarray_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        csp_subarray_fqdn: csp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        scan_config = { 'scanDuration': 10.0 }
        # act:
        tango_context.device.StartScan([json.dumps(scan_config)])

        # assert:
        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STARTSCAN, '0', any_method(with_name='commandCallback'))


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()




def test_assign_resource_should_raise_exception_when_called_invalid_json():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act
    with fake_tango_system(device_under_test) \
            as tango_context:
        assignresources_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(assignresources_input)
        # assert:
        assert const.ERR_INVALID_JSON_ASSIGN_RES in tango_context.device.activityMessage


def test_assign_resource_should_raise_exception_when_key_not_found():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act
    with fake_tango_system(device_under_test) \
            as tango_context:
        assignresources_input = []
        assignresources_input.append('{"dis":{"receptorIDList":["0001","0002"]}}')
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(assignresources_input)
        # assert:
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage

@pytest.mark.xfail
def test_Configure_should_raise_exception_when_called_invalid_json():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act
    with fake_tango_system(device_under_test) \
            as tango_context:
        configure_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(configure_input)
        # assert:
        assert const.ERR_INVALID_JSON_CONFIG in tango_context.device.activityMessage

def test_StartScan_should_raise_generic_exception():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act
    with fake_tango_system(device_under_test) \
            as tango_context:
        StartScan_input = '[123]'
        with pytest.raises(tango.DevFailed):
            tango_context.device.StartScan(StartScan_input)
        # assert:
        assert const.ERR_STARTSCAN_RESOURCES in tango_context.device.activityMessage



def test_State():   #from tango import DevState?
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.State() == DevState.ALARM

def test_Status():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.Status() != const.STR_CSPSALN_INIT_SUCCESS

def test_delayModel():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.delayModel == " "

def test_healthState():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.healthState == HealthState.OK

def test_adminMode():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.adminMode == AdminMode.ONLINE

def test_controlMode():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode

def test_simulationMode():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode

def test_testMode():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode

def test_visDestinationAddress():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.visDestinationAddress = "test"
        assert tango_context.device.visDestinationAddress == "test"

def test_activityMessage():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.activityMessage = 'text'
        assert tango_context.device.activityMessage == 'text'

def test_loggingLevel():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO

def test_loggingTargets():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets

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

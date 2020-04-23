import contextlib
import importlib
import sys
import json
import mock
import types

from mock import Mock
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

def test_State():
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
        assert_flag = True
        delay_model_json = json.loads(tango_context.device.delayModel)
        for delayModel in (delay_model_json['delayModel']):
            for delayDetails in delayModel['delayDetails']:
                for receptorDelayDetails in delayDetails['receptorDelayDetails']:
                    # Check if length of delay coefficients array is 6 and all the elements in array are float
                    delay_coeff_list = receptorDelayDetails['delayCoeff']
                    fsid = receptorDelayDetails['fsid']
                    if len(delay_coeff_list) == 6:
                        for i in range(0, 6):
                            if not isinstance(delay_coeff_list[i], float):
                                _assert_flag = False
                                assert 0
                                break
                    else:
                        _assert_flag = False
                        assert 0
                        break

                    if not fsid in range(1, 27):
                        _assert_flag = False
                        assert 0
                        break

                # Check if receptor id is in the range 1 to 197
                if _assert_flag == False:
                    break
                elif not int(delayDetails['receptor']) in range(1, 198):
                    _assert_flag = False
                    assert 0
                    break

            # Check if epoch is empty and is float
            epoch = delayModel['epoch']
            if _assert_flag == False:
                break
            elif not (epoch) or not isinstance(float(epoch), float):
                _assert_flag = False
                assert 0
                break
            else:
                pass

        if _assert_flag == True:
            assert 1

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








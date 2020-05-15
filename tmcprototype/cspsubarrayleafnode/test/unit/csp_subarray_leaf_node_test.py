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
from ska.base.control_model import HealthState, ObsState, TestMode, SimulationMode, ControlMode, AdminMode, \
    LoggingLevel

def test_start_scan_should_command_csp_subarray_to_start_its_scan_when_it_is_ready():
    # arrange:
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }

    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }

    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        scan_input = {'id':1}
        # act:
        tango_context.device.StartScan([json.dumps(scan_input)])

        # assert:
        csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STARTSCAN, '0',
                                                             any_method(with_name='commandCallback'))


def test_assign_resources_should_send_csp_subarray_with_correct_receptor_id_list():
    # arrange:
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }

    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE

    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }

    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        assign_input='{"dish":{"receptorIDList":["0001","0002"]}}'
        assign_resources_input = []
        assign_resources_input.append(assign_input)
        device_proxy=tango_context.device
        ##act
        device_proxy.AssignResources(assign_resources_input)
        #assert
        receptorIDList = []
        jsonArgument = json.loads(assign_resources_input[0])
        receptorIDList_str = jsonArgument[const.STR_DISH][const.STR_RECEPTORID_LIST]
        # convert receptorIDList from list of string to list of int
        for i in range(0, len(receptorIDList_str)):
            receptorIDList.append(int(receptorIDList_str[i]))
        csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ADD_RECEPTORS,
                                                receptorIDList, any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_ADD_RECEPTORS_SUCCESS)


def test_release_resource_should_command_csp_subarray_to_release_all_resources():
    # arrange:
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }

    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE

    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }

    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        device_proxy = tango_context.device
        assign_input='{"dish":{"receptorIDList":["0001","0002"]}}'
        assign_resources_input = []
        assign_resources_input.append(assign_input)
        # act:
        device_proxy.AssignResources(assign_resources_input)
        device_proxy.ReleaseAllResources()

        # assert:
        csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_REMOVE_ALL_RECEPTORS,
                                                               any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)


def test_end_scan_should_command_csp_subarray_to_end_scan_when_it_is_scanning():
    # arrange:
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }

    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.SCANNING

    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }

    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        tango_context.device.EndScan()
        csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ENDSCAN,
                                                        any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_ENDSCAN_SUCCESS)


def test_configure_to_send_correct_configuration_data_when_csp_subarray_is_idle():
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }

    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE

    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }

    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        csp_config = '{"frequencyBand": "1", "fsp": [{"fspID": 1, "functionMode": "CORR", ' \
                              '"frequencySliceID": 1, "integrationTime": 1400, "corrBandwidth": 0}], ' \
                              '"delayModelSubscriptionPoint": "ska_mid/tm_leaf_node/csp_subarray01/' \
                     'delayModel", ' \
                              '"visDestinationAddressSubscriptionPoint": "ska_mid/tm_leaf_node/' \
                     'sdp_subarray01/receiveAddresses", ' \
                              '"pointing": {"target": {"system": "ICRS", "name": "Polaris", ' \
                     '"RA": "21:08:47.92", ' \
                              '"dec": "-88:5.7:22.9"}}, "scanID": "1"}'
        assign_input='{"dish":{"receptorIDList":["0001","0002"]}}'
        assign_resources_input = []
        assign_resources_input.append(assign_input)

        # act
        device_proxy.AssignResources(assign_resources_input)
        device_proxy.Configure(csp_config)
        # Assert
        argin_json = json.loads(csp_config)
        cspConfiguration = argin_json.copy()
        if "pointing" in cspConfiguration:
            del cspConfiguration["pointing"]
        csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_CONFIGURE,
                                    json.dumps(cspConfiguration), any_method(with_name='commandCallback'))


def test_goto_idle_should_command_csp_subarray_to_end_sb_when_it_is_ready():
    # arrange:
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }

    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }

    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        tango_context.device.GoToIdle()

        csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_GOTOIDLE,
                                                            any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_GOTOIDLE_SUCCESS)


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def test_assign_resource_should_raise_exception_when_called_invalid_json():
    # act
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assignresources_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(assignresources_input)
        # assert:
        assert const.ERR_INVALID_JSON_ASSIGN_RES in tango_context.device.activityMessage


def test_assign_resource_should_raise_exception_when_key_not_found():
    # act
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assignresources_input = []
        assignresources_input.append('{"dis":{"receptorIDList":["0001","0002"]}}')
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(assignresources_input)
        # assert:
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage


@pytest.mark.xfail
def test_configure_should_raise_exception_when_called_invalid_json():
    # act
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        configure_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(configure_input)
        # assert:
        assert const.ERR_INVALID_JSON_CONFIG in tango_context.device.activityMessage


def test_state():   #from tango import DevState?
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.State() == DevState.ALARM


def test_status():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.Status() != const.STR_CSPSALN_INIT_SUCCESS


def test_delay_model():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.delayModel == " "


def test_health_state():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


def test_admin_mode():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.adminMode == AdminMode.ONLINE


def test_control_mode():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_simulation_mode():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode


def test_test_mode():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_visdestination_address():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.visDestinationAddress = "test"
        assert tango_context.device.visDestinationAddress == "test"


def test_activity_message():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.activityMessage == " "


def test_logging_level():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


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
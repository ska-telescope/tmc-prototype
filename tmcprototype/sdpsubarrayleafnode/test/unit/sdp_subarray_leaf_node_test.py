import contextlib
import importlib
import sys
import json
import mock
import types
import pytest
import time
import tango
from mock import Mock
from tango import DevState
from sdpsubarrayleafnode import SdpSubarrayLeafNode, const
from tango.test_context import DeviceTestContext
from ska.base.control_model import ObsState, HealthState, AdminMode, TestMode, ControlMode, SimulationMode
from ska.base.control_model import LoggingLevel


def test_start_scan_should_command_sdp_subarray_to_start_scan_when_it_is_ready():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    sdp_subarray_proxy_mock = Mock()
    sdp_subarray_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        sdp_subarray_fqdn: sdp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        scan_config = '{"id":1}'
        # act:
        tango_context.device.Scan(scan_config)

        # assert:
        sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SCAN, scan_config,
                                                                        any_method(with_name='commandCallback'))


def test_assign_resources_should_send_sdp_subarray_with_correct_processing_block_list():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    sdp_subarray_proxy_mock = Mock()
    sdp_subarray_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {
        sdp_subarray_fqdn: sdp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        assign_config = '{"id":"sbi-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id":"calibration_B","coordinate_system":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598","subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":["calibration"]}]}]}'
        device_proxy = tango_context.device
        # act:
        device_proxy.AssignResources(assign_config)

        # assert:
        sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ASSIGN_RESOURCES, assign_config,
                                                                        any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_ASSIGN_RESOURCES_SUCCESS)


def test_release_resources_with_dummy_data_when_sdp_subarray_is_idle():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    sdp_subarray_proxy_mock = Mock()
    sdp_subarray_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {
        sdp_subarray_fqdn: sdp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        device_proxy = tango_context.device
        # act:
        device_proxy.ReleaseAllResources()

        # assert:
        sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RELEASE_RESOURCES,
                                                                        any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_REL_RESOURCES)


def test_configure_to_send_correct_configuration_data_when_sdp_subarray_is_idle():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    sdp_subarray_proxy_mock = Mock()
    sdp_subarray_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {
        sdp_subarray_fqdn: sdp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        sdp_config = '{"sdp":{ "scan_type": "science_A" }}'
        # act:
        tango_context.device.Configure(sdp_config)

        # assert:
        json_argument = json.loads(sdp_config)
        sdp_arg = json_argument["sdp"]
        sdp_configuration = sdp_arg.copy()
        sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_CONFIGURE,
                                                                        json.dumps(sdp_configuration),
                                                                        any_method(with_name='commandCallback'))


def test_end_scan_should_command_sdp_subarray_to_end_scan_when_it_is_scanning():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    sdp_subarray_proxy_mock = Mock()
    sdp_subarray_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {
        sdp_subarray_fqdn: sdp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.EndScan()

        # assert:
        sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ENDSCAN,
                                                                        any_method(with_name='commandCallback'))


def test_end_sb_should_command_sdp_subarray_to_end_sb_when_it_is_ready():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    sdp_subarray_proxy_mock = Mock()
    sdp_subarray_proxy_mock.obsState = ObsState.READY
    proxies_to_mock = {
        sdp_subarray_fqdn: sdp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.EndSB()

        # assert:
        sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RESET,
                                                                        any_method(with_name='commandCallback'))


def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute


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
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.State() == DevState.ALARM

def test_Status():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.Status() != const.STR_INIT_SUCCESS

def test_loggingLevel():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO

def test_healthState():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.healthState == HealthState.OK

def test_adminMode():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.adminMode == AdminMode.ONLINE

def test_controlMode():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode

def test_simulationMode():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode

def test_testMode():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode

def test_receiveAddresses():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.receiveAddresses == ""

def test_activityMessage():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.activityMessage = "test"
        assert tango_context.device.activityMessage == "test"

def test_activeProcessingBlocks():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.activeProcessingBlocks == ""

def test_loggingTargets():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets

def test_Configure_invalid_key():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_input = '{"":{"":{"id":"realtime-20190627-0001","sbiId":"20190627-0001",' \
                     '"workflow":{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":' \
                     '{"numStations":4,"numChanels":372,"numPolarisations":4,"freqStartHz":0.35e9,' \
                     '"freqEndHz":1.05e9,"fields":{"0":{"system":"ICRS","name":"NGC6251","ra":1.0,"dec"' \
                     ':1.0}}},"scanParameters":{"12345":{"fieldId":0,"intervalMs":1400}}},"configureScan"' \
                     ':{"scanParameters":{"12346":{"fieldId":0,"intervalMs":2800}}}}}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage

def test_Configure_invalid_format():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_input = '{"abc"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert const.ERR_INVALID_JSON_CONFIG in tango_context.device.activityMessage

def test_Configure_generic_exception():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_input = '[123]'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert const.ERR_CONFIGURE in tango_context.device.activityMessage

def test_Scan_device_not_ready():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_input = '{"scanDuration":0}'
        tango_context.device.Scan(test_input)
        time.sleep(1)
        assert const.ERR_DEVICE_NOT_READY in tango_context.device.activityMessage

def test_EndSB_device_not_ready():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.EndSB()
        time.sleep(2)
        assert tango_context.device.activityMessage == const.ERR_DEVICE_NOT_READY

def test_EndScan_Invalid_State():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.EndScan()
        time.sleep(2)
        assert const.ERR_DEVICE_NOT_IN_SCAN in tango_context.device.activityMessage







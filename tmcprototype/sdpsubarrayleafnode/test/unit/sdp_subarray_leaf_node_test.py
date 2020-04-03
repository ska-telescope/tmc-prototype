import contextlib
import importlib
import sys
import json
import mock
import types

from mock import Mock
from sdpsubarrayleafnode import SdpSubarrayLeafNode, CONST
from tango.test_context import DeviceTestContext
from ska.base.control_model import ObsState

def test_start_scan_should_command_sdp_subarray_master_to_start_its_scan_when_it_is_ready():
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

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        scan_config = '{"scanDuration":10}'
        # act:
        tango_context.device.Scan(scan_config)

        # assert:
        sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(CONST.CMD_SCAN, any_method(with_name='commandCallback'))


def test_assign_resources():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    sdp_subarray_proxy_mock = Mock()
    proxies_to_mock = {
        sdp_subarray_fqdn: sdp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        assign_config = '{"processingBlockIdList": ["0001", "0002"]}'
        dut = tango_context.device
        # act:
        dut.AssignResources(assign_config)

        # assert:
        # sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(CONST.CMD_ASSIGN_RESOURCES,'0', any_method(with_name='commandCallback'))
        assert_activity_message(dut, CONST.STR_ASSIGN_RESOURCES_SUCCESS)

def test_release_resources():
    # arrange:
    device_under_test = SdpSubarrayLeafNode
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    sdp_subarray_proxy_mock = Mock()
    proxies_to_mock = {
        sdp_subarray_fqdn: sdp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        dut = tango_context.device
        # act:
        dut.ReleaseAllResources()

        # assert:
        # sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(CONST.CMD_ASSIGN_RESOURCES,'0', any_method(with_name='commandCallback'))
        assert_activity_message(dut, CONST.STR_REL_RESOURCES)

def test_configure():
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

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        sdp_config = '{"sdp":{"configure":{"id":"realtime-20190627-0001","sbiId":"20190627-0001",' \
                     '"workflow":{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":' \
                     '{"numStations":4,"numChanels":372,"numPolarisations":4,"freqStartHz":0.35e9,' \
                     '"freqEndHz":1.05e9,"fields":{"0":{"system":"ICRS","name":"NGC6251","ra":1.0,"dec"' \
                     ':1.0}}},"scanParameters":{"12345":{"fieldId":0,"intervalMs":1400}}},"configureScan"' \
                     ':{"scanParameters":{"12346":{"fieldId":0,"intervalMs":2800}}}}}'
        dut = tango_context.device
        # act:
        dut.Configure(sdp_config)

        # assert:
        sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(CONST.CMD_CONFIGURE, json.dumps(sdp_config), any_method(with_name='commandCallback'))
        # assert_activity_message(dut, CONST.STR_REL_RESOURCES)
        # assert sdp_subarray_proxy_mock.obsState == ObsState.READY

def assert_activity_message(dut, expected_message):
    assert dut.activityMessage == expected_message # reads tango attribute

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

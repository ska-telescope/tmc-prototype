import contextlib
import importlib
import sys
import json
import mock
import types

from mock import Mock
from sdpsubarrayleafnode import SdpSubarrayLeafNode
from sdpsubarrayleafnode.CONST import CMD_SCAN
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
        sdp_subarray_proxy_mock.command_inout_asynch.assert_called_with(CONST.CMD_SCAN, '0', any_method(with_name='commandCallback'))


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

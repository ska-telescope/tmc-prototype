import contextlib
import importlib
import sys
import json
import mock

from mock import Mock

from tango.test_context import DeviceTestContext
from CspSubarrayLeafNode import CspSubarrayLeafNode
from CONST import CMD_STARTSCAN, ENUM_READY


def test_start_scan_should_command_csp_subarray_master_to_start_its_scan_when_it_is_ready():
    # arrange:
    device_under_test = CspSubArrayLeafNode
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    initial_dut_properties = {
        'CspSubarrayFQDN': csp_subarray_fqdn
    }

    csp_subarray_proxy_mock = Mock()
    csp_subarray_proxy_mock.obsState = ENUM_READY

    proxies_to_mock = {
        csp_subarray_fqdn: csp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=initial_dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        scan_config = { 'scandDuration': 10.0 }
        # act:
        tango_context.device.StartScan([json.dumps(scan_config)])

        # assert:
        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(CMD_STARTSCAN)

    

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

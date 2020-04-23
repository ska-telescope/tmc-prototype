import contextlib
import importlib
import sys
import os
import json
import mock
import types
import subprocess as sp

from mock import Mock, mock_open
from cspsubarrayleafnode import CspSubarrayLeafNode, const
from tango.test_context import DeviceTestContext
from ska.base.control_model import ObsState

file_path = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT_DIR = "/app"
TMC_ROOT_DIR = SRC_ROOT_DIR + "/tmcprototype"
ska_antennas_path = TMC_ROOT_DIR + "/ska_antennas.txt"


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

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,proxies_to_mock=proxies_to_mock) as tango_context:
        scan_config = { 'scanDuration': 10.0 }
        # act:
        tango_context.device.StartScan([json.dumps(scan_config)])

        # assert:
        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STARTSCAN, '0', any_method(with_name='commandCallback'))


def test_assign_resources_should_send_csp_subarray_with_correct_receptor_id_list():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray_fqdn
    }

    csp_subarray_proxy_mock = Mock()
    csp_subarray_proxy_mock.obsState = ObsState.IDLE

    proxies_to_mock = {
        csp_subarray_fqdn: csp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock)\
            as tango_context:
        assign_config = []
        assign_config.append('{"dish":{"receptorIDList":["0001","0002"]}}')
        device_proxy=tango_context.device
        # out = sp.check_output("find / -name 'ska_antennas.txt'", shell=True)
        # print("Path: ", out)
        print ("SKA path in test file is           :", ska_antennas_path)

        #act
        device_proxy.AssignResources(assign_config)

        #assert
        receptorIDList = []
        jsonArgument = json.loads(assign_config)
        receptorIDList_str = jsonArgument[const.STR_DISH][const.STR_RECEPTORID_LIST]
        # convert receptorIDList from list of string to list of int
        for i in range(0, len(receptorIDList_str)):
            receptorIDList.append(int(receptorIDList_str[i]))
        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ADD_RECEPTORS, receptorIDList,
                                                                        any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_ADD_RECEPTORS_SUCCESS)


def test_release_resources_RemoveAllReceptors_when_csp_subarray_is_idle():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray_fqdn
    }

    csp_subarray_proxy_mock = Mock()
    csp_subarray_proxy_mock.obsState = ObsState.IDLE

    proxies_to_mock = {
        csp_subarray_fqdn: csp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        device_proxy = tango_context.device
        # act:
        device_proxy.ReleaseAllResources()

        # assert:
        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_REMOVE_ALL_RECEPTORS,
                                                                        any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)

def test_end_scan_should_command_csp_subarray_to_end_scan_when_it_is_scanning():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray_fqdn
    }

    csp_subarray_proxy_mock = Mock()
    csp_subarray_proxy_mock.obsState = ObsState.SCANNING

    proxies_to_mock = {
        csp_subarray_fqdn: csp_subarray_proxy_mock
    }


    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        device_proxy = tango_context.device
        tango_context.device.EndScan()
        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ENDSCAN,
                                                                        any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_ENDSCAN_SUCCESS)


def test_configure_to_send_correct_configuration_data_when_csp_subarray_is_idle():
    device_under_test = CspSubarrayLeafNode
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray_fqdn
    }

    csp_subarray_proxy_mock = Mock()
    csp_subarray_proxy_mock.obsState = ObsState.IDLE

    proxies_to_mock = {
        csp_subarray_fqdn: csp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        device_proxy = tango_context.device
        csp_config = '{"frequencyBand": "1", "fsp": [{"fspID": 1, "functionMode": "CORR", ' \
                          '"frequencySliceID": 1, "integrationTime": 1400, "corrBandwidth": 0}], ' \
                          '"delayModelSubscriptionPoint": "ska_mid/tm_leaf_node/csp_subarray01/delayModel", ' \
                          '"visDestinationAddressSubscriptionPoint": "ska_mid/tm_leaf_node/sdp_subarray01/receiveAddresses", ' \
                          '"pointing": {"target": {"system": "ICRS", "name": "Polaris", "RA": "20:21:10.31", ' \
                          '"dec": "-30:52:17.3"}}, "scanID": "123"}'
        tango_context.device.Configure(csp_config)
        argin_json = json.loads(argin)
        cspConfiguration = argin_json.copy()
        if "pointing" in cspConfiguration:
            del cspConfiguration["pointing"]
        cmdData = tango.DeviceData()
        cmdData.insert(tango.DevString, json.dumps(cspConfiguration))
        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_CONFIGURE, cmdData,
                                                                        any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_CONFIGURE_SUCCESS)


def test_goto_idle_should_command_csp_subarray_to_end_sb_when_it_is_ready():
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


    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        device_proxy = tango_context.device
        tango_context.device.GoToIdle()

        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_GOTOIDLE,
                                                                        any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_GOTOIDLE_SUCCESS)






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

def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute

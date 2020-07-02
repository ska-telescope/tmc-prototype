# Standard Python imports
import contextlib
import importlib
import sys
import json
import types
import pytest
import tango
import mock
from mock import Mock
from mock import MagicMock
from os.path import dirname, join

# Tango imports
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from cspsubarrayleafnode import CspSubarrayLeafNode, const
from ska.base.control_model import HealthState, ObsState, TestMode, SimulationMode, ControlMode, AdminMode, \
    LoggingLevel


assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

scan_input_file='command_Scan.json'
path= join(dirname(__file__), 'data' ,scan_input_file)
with open(path, 'r') as f:
    scan_input_str=f.read()

configure_input_file= 'command_Configure.json'
path= join(dirname(__file__), 'data' , configure_input_file)
with open(path, 'r') as f:
    configure_str=f.read()

invalid_json_assign_config_file='invalid_json_Assign_Resources_Configure.json'
path= join(dirname(__file__), 'data' ,invalid_json_assign_config_file)
with open(path, 'r') as f:
    assign_config_invalid_str=f.read()

assign_invalid_key_file='invalid_key_AssignResources.json'
path= join(dirname(__file__), 'data' , assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key=f.read()

#
# def test_on_command_should_change_cspsubarrayleafnode_device_state_to_on():
#     with fake_tango_system(CspSubarrayLeafNode) as tango_context:
#         # act:
#         tango_context.device.On()
#         # assert:
#         assert tango_context.device.state() == DevState.ON
#         # Due to forwarded attribute is not set in the unit test cases device state remains in ALARM
#         # assert tango_context.device.state() == DevState.ALARM
#         # assert tango_context.device.obsState == ObsState.EMPTY


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
        assign_resources_input = []
        assign_resources_input.append(assign_input_str)
        device_proxy=tango_context.device
        # device_proxy.on()
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
                                                receptorIDList, any_method(with_name='cmd_ended_cb'))
        assert_activity_message(device_proxy, const.STR_ADD_RECEPTORS_SUCCESS)


# def test_assign_resources_should_raise_devfailed_exception():
#     # arrange:
#     csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
#     dut_properties = {
#         'CspSubarrayFQDN': csp_subarray1_fqdn
#     }
#
#     csp_subarray1_proxy_mock = Mock()
#     csp_subarray1_proxy_mock.obsState = ObsState.IDLE
#
#     proxies_to_mock = {
#         csp_subarray1_fqdn: csp_subarray1_proxy_mock
#     }
#     csp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
#     with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
#                            proxies_to_mock=proxies_to_mock) as tango_context:
#         assign_resources_input = []
#         assign_resources_input.append(assign_input_str)
#         device_proxy=tango_context.device
#         device_proxy.On()
#         ##act
#         with pytest.raises(tango.DevFailed):
#             device_proxy.AssignResources(assign_input_str)
#         #assert
#
#         assert const.ERR_ASSGN_RESOURCES in tango_context.device.activityMessage


def test_assign_command_with_callback_method():
    # arrange:
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {   'CspSubarrayFQDN': csp_subarray1_fqdn}
    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {csp_subarray1_fqdn: csp_subarray1_proxy_mock}
    event_subscription_map = {}

    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        assign_resources_input = []
        assign_resources_input.append(assign_input_str)
        device_proxy = tango_context.device
        # act
        device_proxy.AssignResources(assign_resources_input)
        dummy_event = command_callback(const.CMD_ADD_RECEPTORS)
        event_subscription_map[const.CMD_ADD_RECEPTORS](dummy_event)
        # assert:
        assert const.STR_INVOKE_SUCCESS in tango_context.device.activityMessage


def test_assign_command_with_callback_method_with_event_error():
    # arrange:
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {'CspSubarrayFQDN': csp_subarray1_fqdn}
    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {csp_subarray1_fqdn: csp_subarray1_proxy_mock}
    event_subscription_map = {}

    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:

        assign_resources_input = []
        assign_resources_input.append(assign_input_str)
        device_proxy = tango_context.device
        # act
        device_proxy.AssignResources(assign_resources_input)
        dummy_event = command_callback_with_event_error(const.CMD_ADD_RECEPTORS)
        event_subscription_map[const.CMD_ADD_RECEPTORS](dummy_event)
        # assert:
        assert const.ERR_INVOKING_CMD in tango_context.device.activityMessage


def test_assign_command_with_callback_method_with_command_error():
    # arrange:
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {'CspSubarrayFQDN': csp_subarray1_fqdn}
    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {csp_subarray1_fqdn: csp_subarray1_proxy_mock}
    event_subscription_map = {}

    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:

        assign_resources_input = []
        assign_resources_input.append(assign_input_str)
        device_proxy = tango_context.device
        # act:

        with pytest.raises(Exception):
            device_proxy.AssignResources(assign_resources_input)
            dummy_event = command_callback_with_command_exception()
            event_subscription_map[const.CMD_ADD_RECEPTORS](dummy_event)
        # assert:
        assert const.ERR_EXCEPT_CMD_CB in tango_context.device.activityMessage

#
# def test_assign_resource_should_raise_exception_when_called_invalid_json():
#     # act
#     with fake_tango_system(CspSubarrayLeafNode) as tango_context:
#         tango_context.device.On()
#         with pytest.raises(tango.DevFailed):
#             tango_context.device.AssignResources(assign_config_invalid_str)
#         # assert:
#         assert const.ERR_INVALID_JSON_ASSIGN_RES in tango_context.device.activityMessage

#
# def test_assign_resource_should_raise_exception_when_key_not_found():
#     # act
#     with fake_tango_system(CspSubarrayLeafNode) as tango_context:
#         tango_context.device.On()
#         assignresources_input = []
#         assignresources_input.append(assign_invalid_key)
#         with pytest.raises(tango.DevFailed):
#             tango_context.device.AssignResources(assignresources_input)
#         # assert:
#         assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage


# def test_release_resource_should_command_csp_subarray_to_release_all_resources():
#     # arrange:
#     csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
#     dut_properties = {
#         'CspSubarrayFQDN': csp_subarray1_fqdn
#     }
#
#     csp_subarray1_proxy_mock = Mock()
#     csp_subarray1_proxy_mock.obsState = ObsState.IDLE
#
#     proxies_to_mock = {
#         csp_subarray1_fqdn: csp_subarray1_proxy_mock
#     }
#
#     with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
#                            proxies_to_mock=proxies_to_mock) \
#             as tango_context:
#         device_proxy = tango_context.device
#         # assign_resources_input = []
#         # assign_resources_input.append(assign_input_str)
#         device_proxy.On()
#         # act:
#         device_proxy.AssignResources(assign_input_str)
#         device_proxy.ReleaseAllResources()
#         # assert:
#         csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_REMOVE_ALL_RECEPTORS,
#                                                                any_method(with_name='cmd_ended_cb'))
#         assert_activity_message(device_proxy, const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)
#
# #
# # def test_configure_to_send_correct_configuration_data_when_csp_subarray_is_idle():
#     csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
#     dut_properties = {
#         'CspSubarrayFQDN': csp_subarray1_fqdn
#     }
#
#     csp_subarray1_proxy_mock = Mock()
#     csp_subarray1_proxy_mock.obsState = ObsState.IDLE
#
#     proxies_to_mock = {
#         csp_subarray1_fqdn: csp_subarray1_proxy_mock
#     }
#
#     with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
#                            proxies_to_mock=proxies_to_mock) as tango_context:
#         device_proxy = tango_context.device
#         device_proxy.On()
#         csp_config = configure_str
#         # assign_resources_input = []
#         # assign_resources_input.append(assign_input_str)
#
#         # act
#         device_proxy.AssignResources(assign_input_str)
#         device_proxy.Configure(csp_config)
#         # Assert
#         argin_json = json.loads(csp_config)
#         cspConfiguration = argin_json.copy()
#         if "pointing" in cspConfiguration:
#             del cspConfiguration["pointing"]
#         csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_CONFIGURE,
#                                     json.dumps(cspConfiguration), any_method(with_name='cmd_ended_cb'))

def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_event_error(command_name):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Event error in Command Callback'
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_command_exception():
    return Exception("Exception in command callback")


def raise_devfailed_exception(cmd_name):
    tango.Except.throw_exception("CspSubarrayLeafNode_CommandFailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)

'''
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
        # act:
        tango_context.device.StartScan(scan_input_str)

        # assert:
        csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STARTSCAN, '0',
                                                             any_method(with_name='cmd_ended_cb'))


def test_start_scan_should_raise_devfailed_exception():
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
    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        with pytest.raises(tango.DevFailed):
            tango_context.device.StartScan(scan_input_str)

        # assert:
        assert const.ERR_STARTSCAN_RESOURCES in tango_context.device.activityMessage


def test_start_scan_should_not_command_csp_subarray_to_start_its_scan_when_it_is_idle():
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
        # act:
        tango_context.device.StartScan(scan_input_str)

        # assert:
        assert_activity_message(tango_context.device, const.ERR_DEVICE_NOT_READY)




def test_release_resource_should_command_csp_subarray_to_release_all_resources_raise_devfail():
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
    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        device_proxy = tango_context.device
        with pytest.raises(tango.DevFailed):
            device_proxy.ReleaseAllResources()

        # assert:
        assert const.ERR_RELEASE_ALL_RESOURCES in tango_context.device.activityMessage


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
                                                        any_method(with_name='cmd_ended_cb'))
        assert_activity_message(device_proxy, const.STR_ENDSCAN_SUCCESS)


def test_end_scan_should_raise_devfailed_exception():
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
    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        with pytest.raises(tango.DevFailed):
            tango_context.device.EndScan()

        assert const.ERR_ENDSCAN_INVOKING_CMD in tango_context.device.activityMessage


def test_end_scan_should_not_command_csp_subarray_to_end_scan_when_it_is_not_scanning():
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
        tango_context.device.EndScan()
        assert_activity_message(device_proxy, const.ERR_DEVICE_NOT_IN_SCAN)


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
        csp_config = configure_str
        assign_resources_input = []
        assign_resources_input.append(assign_input_str)

        # act
        device_proxy.AssignResources(assign_resources_input)
        device_proxy.Configure(csp_config)
        # Assert
        argin_json = json.loads(csp_config)
        cspConfiguration = argin_json.copy()
        if "pointing" in cspConfiguration:
            del cspConfiguration["pointing"]
        csp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_CONFIGURE,
                                    json.dumps(cspConfiguration), any_method(with_name='cmd_ended_cb'))


def test_configure_to_raise_devfailed_exception():
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }

    csp_subarray1_proxy_mock = Mock()
    csp_subarray1_proxy_mock.obsState = ObsState.IDLE

    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }

    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        csp_config = configure_str

        with pytest.raises(tango.DevFailed):
            device_proxy.Configure(csp_config)
        # Assert
        assert const.ERR_CONFIGURE_INVOKING_CMD in tango_context.device.activityMessage


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
                                                            any_method(with_name='cmd_ended_cb'))
        assert_activity_message(device_proxy, const.STR_GOTOIDLE_SUCCESS)


def test_goto_idle_should_raise_devfailed_exception():
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
    csp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(CspSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        with pytest.raises(tango.DevFailed):
            tango_context.device.GoToIdle()

        assert const.ERR_GOTOIDLE_INVOKING_CMD in tango_context.device.activityMessage


def test_goto_idle_should_not_command_csp_subarray_to_end_sb_when_it_is_idle():
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
        device_proxy = tango_context.device
        tango_context.device.GoToIdle()
        assert_activity_message(device_proxy, const.ERR_DEVICE_NOT_READY)


def test_configure_should_raise_exception_when_called_invalid_json():
    # act
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(assign_config_invalid_str)
        # assert:
        assert const.ERR_INVALID_JSON_CONFIG in tango_context.device.activityMessage



def test_status():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.Status() != const.STR_CSPSALN_INIT_SUCCESS


def test_read_delay_model():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.delayModel == " "


def test_write_delay_model():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.delayModel = " "
        assert tango_context.device.delayModel == " "


def test_health_state():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK

def test_read_activity_message():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.activityMessage == " "


def test_write_activity_message():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.activityMessage = "test"
        assert tango_context.device.activityMessage == "test"


def test_logging_level():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_read_version_info():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.versionInfo == " "


def test_logging_targets():
    # act & assert:
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets
'''


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()

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
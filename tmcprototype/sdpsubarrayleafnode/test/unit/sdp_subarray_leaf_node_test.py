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
from sdpsubarrayleafnode import SdpSubarrayLeafNode, const
from ska.base.control_model import ObsState, HealthState, AdminMode, TestMode, ControlMode, SimulationMode
from ska.base.control_model import LoggingLevel

assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

scan_input_file= 'command_Scan.json'
path= join(dirname(__file__), 'data', scan_input_file)
with open(path, 'r') as f:
    scan_input_str=f.read()

configure_input_file= 'command_Configure.json'
path= join(dirname(__file__), 'data' , configure_input_file)
with open(path, 'r') as f:
    configure_str=f.read()

configure_invalid_key_file='invalid_key_Configure.json'
path= join(dirname(__file__), 'data' , configure_invalid_key_file)
with open(path, 'r') as f:
    configure_invalid_key=f.read()

configure_invalid_format_file='invalid_format_Configure.json'
path= join(dirname(__file__), 'data' , configure_invalid_format_file)
with open(path, 'r') as f:
    configure_invalid_format =f.read()


def test_end_sb_command_with_callback_method():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act
        tango_context.device.EndSB()
        dummy_event = command_callback(const.CMD_RESET)
        event_subscription_map[const.CMD_RESET](dummy_event)
        # assert:
        assert const.STR_INVOKE_SUCCESS in tango_context.device.activityMessage


def test_end_sb_command_with_callback_method_with_event_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act
        tango_context.device.EndSB()
        dummy_event = command_callback_with_event_error(const.CMD_RESET)
        event_subscription_map[const.CMD_RESET](dummy_event)
        # assert:
        assert const.ERR_INVOKING_CMD in tango_context.device.activityMessage


def test_assign_command_with_callback_method_with_devfailed_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        with pytest.raises(tango.DevFailed) as df:
        #arrange:
            tango_context.device.On()
            tango_context.device.AssignResources(assign_input_str)
            dummy_event = command_callback_with_devfailed_exception()
            event_subscription_map[const.CMD_ASSIGN_RESOURCES](dummy_event)
        # assert:
        assert "SdpSubarrayLeafNode_Commandfailed in callback" in str(df.value)


def test_assign_command_assignresources_ended_with_callback_method():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.AssignResources(assign_input_str)
        dummy_event = command_callback(const.CMD_ASSIGN_RESOURCES)
        event_subscription_map[const.CMD_ASSIGN_RESOURCES](dummy_event)
        # assert:
        assert const.STR_COMMAND in tango_context.device.activityMessage


def test_assign_command_assignresources_ended_raises_exception_for_error_event():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.AssignResources(assign_input_str)
        dummy_event = command_callback_with_event_error(const.CMD_ASSIGN_RESOURCES)
        
        with pytest.raises(tango.DevFailed) as df:
            event_subscription_map[const.CMD_ASSIGN_RESOURCES](dummy_event)
        # assert:
        assert "Event error in Command Callback" in str(df)
        # assert const.ERR_INVOKING_CMD in tango_context.device.activityMessage

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
    return Exception("Exception in Command callback")


def command_callback_with_devfailed_exception():
    tango.Except.throw_exception("SdpSubarrayLeafNode_Commandfailed in callback", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)


def raise_devfailed_exception(cmd_name):
    tango.Except.throw_exception("SdpSubarrayLeafNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)


def test_start_scan_should_command_sdp_subarray_to_start_scan_when_it_is_ready():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Scan(scan_input_str)

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SCAN, scan_input_str,
                                                                 any_method(with_name='cmd_ended_cb'))


def test_start_scan_should_raise_devfailed_exception():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        with pytest.raises(tango.DevFailed):
            
            tango_context.device.Scan(scan_input_str)
            tango_context.device.Scan(scan_input_str)

        # assert:
        assert const.ERR_SCAN in tango_context.device.activityMessage


def test_assign_resources_should_send_sdp_subarray_with_correct_processing_block_list():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.EMPTY
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        device_proxy = tango_context.device
        device_proxy.On()
        # act:
        device_proxy.AssignResources(assign_input_str)
        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ASSIGN_RESOURCES,
                                                            assign_input_str,
                                                            any_method(with_name='AssignResources_ended'))
        assert_activity_message(device_proxy, const.STR_ASSIGN_RESOURCES_SUCCESS)


def test_assign_resources_should_raise_devfailed_for_invalid_obstate():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
                **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        device_proxy.On()
        # act:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.AssignResources(assign_input_str)

    # assert:
        assert "SDP subarray is not in EMPTY obstate." in str(df)


def test_release_resources_when_sdp_subarray_is_idle():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        # act:
        device_proxy.ReleaseAllResources()

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RELEASE_RESOURCES,
                                                                 any_method(with_name='cmd_ended_cb'))
        assert_activity_message(device_proxy, const.STR_REL_RESOURCES)


def test_release_resources_should_raise_devfailed_exception():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        # act:
        with pytest.raises(tango.DevFailed):
            device_proxy.ReleaseAllResources()

        # assert:
        assert const.ERR_RELEASE_RESOURCES in tango_context.device.activityMessage


def test_configure_to_send_correct_configuration_data_when_sdp_subarray_is_idle():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Configure(configure_str)

        # assert:
        json_argument = json.loads(configure_str)
        sdp_arg = json_argument["sdp"]
        sdp_configuration = sdp_arg.copy()
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_CONFIGURE,
                                                                        json.dumps(sdp_configuration),
                                                                     any_method(with_name='cmd_ended_cb'))


def test_configure_should_raise_devfailed_exception():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(configure_str)

        # assert:
        assert const.ERR_CONFIGURE in tango_context.device.activityMessage


def test_end_scan_should_command_sdp_subarray_to_end_scan_when_it_is_scanning():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.EndScan()

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ENDSCAN,
                                                                     any_method(with_name='cmd_ended_cb'))


def test_end_scan_should_raise_devfailed_exception():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        with pytest.raises(tango.DevFailed):
            tango_context.device.EndScan()

        # assert:
        assert const.ERR_ENDSCAN_INVOKING_CMD in tango_context.device.activityMessage


def test_end_sb_should_command_sdp_subarray_to_reset_when_it_is_ready():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.EndSB()

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RESET,
                                                                     any_method(with_name='cmd_ended_cb'))


def test_end_sb_should_raise_devfailed_exception():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.READY
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        with pytest.raises(tango.DevFailed):
            tango_context.device.EndSB()

        # assert:
        assert const.ERR_ENDSB_INVOKING_CMD in tango_context.device.activityMessage


def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def test_status():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.Status() != const.STR_INIT_SUCCESS


def test_logging_level():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_control_mode():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_test_mode():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_receive_addresses():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.receiveAddresses == ""


def test_activity_message():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.activityMessage == const.STR_SDPSALN_INIT_SUCCESS


def test_write_receive_addresses():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.receiveAddresses = "test"
        assert tango_context.device.receiveAddresses == "test"


def test_write_activity_message():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.activityMessage = "test"
        assert tango_context.device.activityMessage == "test"


def test_active_processing_blocks():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.activeProcessingBlocks == ""


def test_logging_targets():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_configure_invalid_key():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(configure_invalid_key)
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage


def test_configure_invalid_format():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        test_input = configure_invalid_format
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert const.ERR_INVALID_JSON_CONFIG in tango_context.device.activityMessage


def test_configure_generic_exception():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        test_input = '[123]'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert const.ERR_CONFIGURE in tango_context.device.activityMessage


def test_scan_device_not_ready():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.Scan(scan_input_str)
        assert const.ERR_DEVICE_NOT_READY in tango_context.device.activityMessage


def test_endsb_device_not_ready():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.EndSB()
        assert tango_context.device.activityMessage == const.ERR_DEVICE_NOT_READY


def test_endscan_invalid_state():
    # act & assert:
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        tango_context.device.EndScan()
        assert const.ERR_DEVICE_NOT_IN_SCAN in tango_context.device.activityMessage


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
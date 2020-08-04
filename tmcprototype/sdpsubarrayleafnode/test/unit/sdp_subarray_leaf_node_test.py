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
from sdpsubarrayleafnode import SdpSubarrayLeafNode, const, release
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
        assert const.STR_COMMAND + const.CMD_RESET in tango_context.device.activityMessage

def test_release_resources_command_with_callback_method():
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
        tango_context.device.ReleaseAllResources()
        dummy_event = command_callback(const.CMD_RELEASE_RESOURCES)
        event_subscription_map[const.CMD_RELEASE_RESOURCES](dummy_event)
        # assert:
        assert const.STR_COMMAND + const.CMD_RELEASE_RESOURCES in tango_context.device.activityMessage

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
        assert const.STR_COMMAND + const.CMD_ASSIGN_RESOURCES in tango_context.device.activityMessage


def test_scan_command_with_callback_method():
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
        # act
        tango_context.device.Scan(scan_input_str)
        dummy_event = command_callback(const.CMD_SCAN)
        event_subscription_map[const.CMD_SCAN](dummy_event)
        # assert:
        assert const.STR_COMMAND + const.CMD_SCAN in tango_context.device.activityMessage

def test_configure_command_with_callback_method():
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
        # act
        tango_context.device.Configure(configure_str)
        dummy_event = command_callback(const.CMD_CONFIGURE)
        event_subscription_map[const.CMD_CONFIGURE](dummy_event)
        # assert:
        assert const.STR_COMMAND + const.CMD_CONFIGURE in tango_context.device.activityMessage

def test_end_scan_command_with_callback_method():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act
        tango_context.device.EndScan()
        dummy_event = command_callback(const.CMD_ENDSCAN)
        event_subscription_map[const.CMD_ENDSCAN](dummy_event)
        # assert:
        assert const.STR_COMMAND + const.CMD_ENDSCAN in tango_context.device.activityMessage

def test_abort_command_with_callback_method():
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
        tango_context.device.Abort()
        dummy_event = command_callback(const.CMD_ABORT)
        event_subscription_map[const.CMD_ABORT](dummy_event)
        # assert:
        assert const.STR_COMMAND + const.CMD_ABORT in tango_context.device.activityMessage

def test_restart_command_with_callback_method():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act
        tango_context.device.Restart()
        dummy_event = command_callback(const.CMD_RESTART)
        event_subscription_map[const.CMD_RESTART](dummy_event)
        # assert:
        assert const.STR_COMMAND + const.CMD_RESTART in tango_context.device.activityMessage

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
        assert const.ERR_INVOKING_CMD + const.CMD_RESET in tango_context.device.activityMessage

def test_release_resource_command_with_callback_method_with_event_error():
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
        tango_context.device.ReleaseAllResources()
        dummy_event = command_callback_with_event_error(const.CMD_RELEASE_RESOURCES)
        event_subscription_map[const.CMD_RELEASE_RESOURCES](dummy_event)
        # assert:
        assert const.ERR_INVOKING_CMD + const.CMD_RELEASE_RESOURCES in tango_context.device.activityMessage

def test_assign_command_assign_resources_ended_raises_exception_for_error_event():
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
        assert const.ERR_INVOKING_CMD + const.CMD_ASSIGN_RESOURCES in tango_context.device.activityMessage

def test_scan_command_with_callback_method_with_event_error():
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
        # act
        tango_context.device.Scan(scan_input_str)
        dummy_event = command_callback_with_event_error(const.CMD_SCAN)
        event_subscription_map[const.CMD_SCAN](dummy_event)
        # assert:
        assert const.ERR_INVOKING_CMD + const.CMD_SCAN in tango_context.device.activityMessage

def test_end_scan_command_with_callback_method_with_event_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act
        tango_context.device.EndScan()
        dummy_event = command_callback_with_event_error(const.CMD_ENDSCAN)
        event_subscription_map[const.CMD_ENDSCAN](dummy_event)
        # assert:
        assert const.ERR_INVOKING_CMD + const.CMD_ENDSCAN in tango_context.device.activityMessage

def test_configure_command_with_callback_method_with_event_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act
        tango_context.device.Configure(configure_str)
        dummy_event = command_callback_with_event_error(const.CMD_CONFIGURE)
        event_subscription_map[const.CMD_CONFIGURE](dummy_event)
        # assert:
        assert const.ERR_INVOKING_CMD + const.CMD_CONFIGURE in tango_context.device.activityMessage

def test_abort_command_with_callback_method_with_event_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act
        tango_context.device.Abort()
        dummy_event = command_callback_with_event_error(const.CMD_ABORT)
        event_subscription_map[const.CMD_ABORT](dummy_event)
        # assert:
        assert const.ERR_INVOKING_CMD + const.CMD_ABORT in tango_context.device.activityMessage


def test_restart_command_with_callback_method_with_event_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}
    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act
        tango_context.device.Restart()
        dummy_event = command_callback_with_event_error(const.CMD_RESTART)
        event_subscription_map[const.CMD_RESTART](dummy_event)
        # assert:
        assert const.ERR_INVOKING_CMD + const.CMD_RESTART in tango_context.device.activityMessage

def test_release_resources_command_with_callback_method_with_command_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}

    sdp_subarray1_proxy_mock = Mock()
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}

    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device

        # act
        with pytest.raises(Exception):
            device_proxy.ReleaseAllResources()
            dummy_event = command_callback_with_command_exception()
            event_subscription_map[const.CMD_RELEASE_RESOURCES](dummy_event)

        # assert:
        assert const.ERR_EXCEPT_RELEASE_ALL_RESOURCES_CMD_CB in tango_context.device.activityMessage

def test_end_sb_command_with_callback_method_with_command_error():
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
        device_proxy = tango_context.device

        # act
        with pytest.raises(Exception):
            device_proxy.EndSB()
            dummy_event = command_callback_with_command_exception()
            event_subscription_map[const.CMD_RESET](dummy_event)

        # assert:
        assert const.ERR_EXCEPT_END_SB_CMD_CB in tango_context.device.activityMessage

def test_configure_command_with_callback_method_with_command_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}

    sdp_subarray1_proxy_mock = Mock()
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}

    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device

        # act
        with pytest.raises(Exception):
            device_proxy.Configure(configure_str)
            dummy_event = command_callback_with_command_exception()
            event_subscription_map[const.CMD_CONFIGURE](dummy_event)

        # assert:
        assert const.ERR_EXCEPT_CONFIGURE_CMD_CB in tango_context.device.activityMessage

def test_scan_command_with_callback_method_with_command_error():
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
        scan_input_str = "0"
        # act
        with pytest.raises(Exception):
            device_proxy.Scan(scan_input_str)
            dummy_event = command_callback_with_command_exception()
            event_subscription_map[const.CMD_SCAN](dummy_event)

        # assert:
        assert const.ERR_EXCEPT_SCAN_CMD_CB in tango_context.device.activityMessage


def test_end_scan_command_with_callback_method_with_command_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}

    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device

        # act
        with pytest.raises(Exception):
            device_proxy.EndScan()
            dummy_event = command_callback_with_command_exception()
            event_subscription_map[const.CMD_ENDSCAN](dummy_event)

        # assert:
        assert const.ERR_EXCEPT_END_SCAN_CMD_CB in tango_context.device.activityMessage


def test_abort_command_with_callback_method_with_command_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}

    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device

        # act
        with pytest.raises(Exception):
            device_proxy.Abort()
            dummy_event = command_callback_with_command_exception()
            event_subscription_map[const.CMD_ABORT](dummy_event)

        # assert:
        assert const.ERR_EXCEPT_ABORT_CMD_CB in tango_context.device.activityMessage

def test_restart_command_with_callback_method_with_command_error():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {'SdpSubarrayFQDN': sdp_subarray1_fqdn}

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    proxies_to_mock = {sdp_subarray1_fqdn: sdp_subarray1_proxy_mock}
    event_subscription_map = {}

    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device

        # act
        with pytest.raises(Exception):
            device_proxy.Restart()
            dummy_event = command_callback_with_command_exception()
            event_subscription_map[const.CMD_RESTART](dummy_event)

        # assert:
        assert const.ERR_EXCEPT_RESTART_CMD_CB in tango_context.device.activityMessage


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
        # tango_context.device.On()
        # act:
        with pytest.raises(tango.DevFailed) as df:
            # arrange:
            tango_context.device.AssignResources(assign_input_str)
            dummy_event = command_callback_with_devfailed_exception()
            event_subscription_map[const.CMD_ASSIGN_RESOURCES](dummy_event)
        # assert:
        assert const.ERR_CMD_FAILED in str(df.value)


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
                                                                         any_method(with_name='scan_cmd_ended_cb'))


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
        # device_proxy.On()
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
                                                        any_method(with_name='releaseallresources_cmd_ended_cb'))
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
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_CONFIGURE,
                                                                         json.dumps(configure_str),
                                                                         any_method(with_name='configure_cmd_ended_cb'))


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
                                                                         any_method(with_name='endscan_cmd_ended_cb'))


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
                                                                         any_method(with_name='endsb_cmd_ended_cb'))


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


def test_abort_should_command_sdp_subarray_to_abort_when_it_is_ready():
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
        tango_context.device.Abort()

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                                     any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_command_sdp_subarray_to_abort_when_it_is_scanning():
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
        tango_context.device.Abort()

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                                     any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_command_sdp_subarray_to_abort_when_it_is_configuring():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.CONFIGURING
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Abort()

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                                     any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_command_sdp_subarray_to_abort_when_it_is_idle():
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
        tango_context.device.Abort()

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                                     any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_raise_devfailed_exception():
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
            tango_context.device.Abort()

        # assert:
        assert const.ERR_ABORT_INVOKING_CMD in tango_context.device.activityMessage


def test_abort_should_failed_when_device_obsstate_is_resourcing():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.RESOURCING
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Abort()

        # assert:
        assert "Unable to invoke Abort command." in tango_context.device.activityMessage


def test_abort_should_failed_when_device_obsstate_is_empty():
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
        # act:
        tango_context.device.Abort()

        # assert:
        assert "Unable to invoke Abort command." in tango_context.device.activityMessage


def test_restart_should_command_sdp_subarray_to_restart_when_obsstate_is_aborted():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Restart()

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RESTART,
                                                                     any_method(with_name='restart_cmd_ended_cb'))


def test_restart_should_command_sdp_subarray_to_restart_when_obsstate_is_fault():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.FAULT
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Restart()

        # assert:
        sdp_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RESTART,
                                                                     any_method(with_name='restart_cmd_ended_cb'))


def test_restart_should_raise_devfailed_exception():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.ABORTED
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }
    sdp_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Restart()

        # assert:
        assert const.ERR_RESTART_INVOKING_CMD in tango_context.device.activityMessage


def test_restart_should_failed_when_device_obsstate_is_resourcing():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.RESOURCING
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Restart()

        # assert:
        assert "Unable to invoke Restart command" in tango_context.device.activityMessage


def test_restart_should_failed_when_device_obsstate_is_scanning():
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
        tango_context.device.Restart()

        # assert:
        assert "Unable to invoke Restart command" in tango_context.device.activityMessage


def test_restart_should_failed_when_device_obsstate_is_empty():
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
        # act:
        tango_context.device.Restart()

        # assert:
        assert "Unable to invoke Restart command" in tango_context.device.activityMessage


def test_restart_should_failed_when_device_obsstate_is_configuring():
    # arrange:
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dut_properties = {
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    sdp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock.obsState = ObsState.CONFIGURING
    proxies_to_mock = {
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    with fake_tango_system(SdpSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Restart()

        # assert:
        assert "Unable to invoke Restart command" in tango_context.device.activityMessage


def test_restart_should_failed_when_device_obsstate_is_idle():
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
        tango_context.device.Restart()

        # assert:
        assert "Unable to invoke Restart command" in tango_context.device.activityMessage


def test_restart_should_failed_when_device_obsstate_is_ready():
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
        tango_context.device.Restart()

        # assert:
        assert "Unable to invoke Restart command" in tango_context.device.activityMessage


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


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(SdpSubarrayLeafNode) as tango_context:
        assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))


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
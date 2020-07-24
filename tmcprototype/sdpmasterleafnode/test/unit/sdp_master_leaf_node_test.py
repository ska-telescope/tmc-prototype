# Standard Python imports
import contextlib
import importlib
import sys
import types
import mock
import pytest
from mock import Mock, MagicMock

# Tango imports
import tango
from tango.test_context import DeviceTestContext
from tango import DevState, DevFailed

# Additional import
from sdpmasterleafnode import SdpMasterLeafNode, const
from ska.base.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
from ska.base.control_model import LoggingLevel


def test_on_should_command_sdp_master_leaf_node_to_start():
    # arrange:
    sdp_master_fqdn = 'mid_sdp/elt/master'

    dut_properties = {'SdpMasterFQDN': sdp_master_fqdn}

    sdp_proxy_mock = Mock()

    proxies_to_mock = {sdp_master_fqdn: sdp_proxy_mock}

    with fake_tango_system(SdpMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.On()

        # assert:
        sdp_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ON,
                                                               any_method(with_name='on_cmd_ended_cb'))


def test_off_should_command_sdp_master_leaf_node_to_stop():
    # arrange:
    sdp_master_fqdn = 'mid_sdp/elt/master'

    dut_properties = {'SdpMasterFQDN': sdp_master_fqdn}

    sdp_proxy_mock = Mock()

    proxies_to_mock = {sdp_master_fqdn: sdp_proxy_mock}

    with fake_tango_system(SdpMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        tango_context.device.On()
        # act:
        tango_context.device.Off()
        # assert:
        assert tango_context.device.activityMessage in const.STR_OFF_CMD_SUCCESS
        sdp_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_OFF,
                                                               any_method(with_name='off_cmd_ended_cb'))


def test_standby_should_command_sdp_master_leaf_node_to_standby():
    # arrange:
    sdp_master_fqdn = 'mid_sdp/elt/master'

    dut_properties = {'SdpMasterFQDN': sdp_master_fqdn}

    sdp_proxy_mock = Mock()

    proxies_to_mock = {sdp_master_fqdn: sdp_proxy_mock}

    with fake_tango_system(SdpMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.Standby()

        # assert:
        sdp_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STANDBY,
                                                               any_method(with_name='standby_cmd_ended_cb'))


def test_disable_should_command_sdp_master_leaf_node_to_disable():
    # arrange:
    sdp_master_fqdn = 'mid_sdp/elt/master'

    dut_properties = {
        'SdpMasterFQDN': sdp_master_fqdn
    }

    sdp_proxy_mock = Mock()

    proxies_to_mock = {
        sdp_master_fqdn: sdp_proxy_mock
    }

    with fake_tango_system(SdpMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.Disable()

        # assert:
        assert tango_context.device.activityMessage in const.STR_DISABLE_CMS_SUCCESS
        sdp_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_Disable,
                                                               any_method(with_name='disable_cmd_ended_cb'))



def test_disable_should_command_sdp_master_leaf_node_to_disable_devfailed():
    # arrange:
    sdp_master_fqdn = 'mid_sdp/elt/master'

    dut_properties = {
        'SdpMasterFQDN': sdp_master_fqdn
    }

    sdp_proxy_mock = Mock()

    proxies_to_mock = {
        sdp_master_fqdn: sdp_proxy_mock
    }

    with fake_tango_system(SdpMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:

        tango_context.device.On()
        tango_context.device.DevState = DevState.FAULT
        # act:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.Disable()

        # assert:
        assert "Failed to invoke Disable command on SdpMasterLeafNode." in str(df)


def test_standby_should_command_with_callback_method():
    # arrange:
    sdp_master_fqdn = 'mid_sdp/elt/master'

    dut_properties = {'SdpMasterFQDN': sdp_master_fqdn}

    sdp_master_proxy_mock = Mock()
    event_subscription_map = {}
    proxies_to_mock = {sdp_master_fqdn: sdp_master_proxy_mock}
    sdp_master_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.Standby()
        dummy_event = command_callback(const.CMD_STANDBY)
        event_subscription_map[const.CMD_STANDBY](dummy_event)
        # assert:
        assert const.STR_INVOKE_SUCCESS in tango_context.device.activityMessage


def test_standby_should_command_with_callback_method_with_event_error():
    # arrange:
    sdp_master_fqdn = 'mid_sdp/elt/master'

    dut_properties = {'SdpMasterFQDN': sdp_master_fqdn}

    sdp_master_proxy_mock = Mock()
    event_subscription_map = {}
    proxies_to_mock = {sdp_master_fqdn: sdp_master_proxy_mock}
    sdp_master_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.Standby()
        dummy_event = command_callback_with_event_error(const.CMD_STANDBY)
        event_subscription_map[const.CMD_STANDBY](dummy_event)
        # assert:
        assert const.ERR_INVOKING_CMD in tango_context.device.activityMessage


def test_standby_should_command_with_callback_method_with_command_error():
    # arrange:
    sdp_master_fqdn = 'mid_sdp/elt/master'

    dut_properties = {'SdpMasterFQDN': sdp_master_fqdn}

    sdp_master_proxy_mock = Mock()
    event_subscription_map = {}
    proxies_to_mock = {sdp_master_fqdn: sdp_master_proxy_mock}
    sdp_master_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    with fake_tango_system(SdpMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        with pytest.raises(Exception) :
            tango_context.device.Standby()
            dummy_event = command_callback_with_command_exception()
            event_subscription_map[const.CMD_STANDBY](dummy_event)
        # assert:
        assert const.ERR_EXCEPT_STANDBY_CMD_CB in tango_context.device.activityMessage


def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_event_error(command_name):
    fake_event = MagicMock()
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Event error in Command Callback'
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_command_exception():
    return Exception("Exception in Command callback")


def test_activity_message():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        tango_context.device.activityMessage = "text"
        assert tango_context.device.activityMessage == "text"


def test_version_info():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        assert tango_context.device.versionInfo == '1.0'


def test_processing_block_list():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        assert tango_context.device.ProcessingBlockList


def test_status():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        assert tango_context.device.Status() != const.STR_INIT_SUCCESS


def test_logging_level():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_test_mode():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_simulation_mode():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode


def test_control_mode():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_health_state():
    # act & assert:
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


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
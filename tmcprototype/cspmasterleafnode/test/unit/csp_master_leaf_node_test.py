# Standard Python imports
import contextlib
import importlib
import types
import sys
import mock
from mock import Mock

# Tango imports
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from cspmasterleafnode import CspMasterLeafNode, const
from ska.base.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
from ska.base.control_model import LoggingLevel


def test_on_should_command_csp_master_leaf_node_to_start():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid_csp/elt/master'

    dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    csp_master_proxy_mock = Mock()

    proxies_to_mock = {
        csp_master_fqdn: csp_master_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        on_input = []
        # act:
        tango_context.device.On(on_input)

        # assert:
        csp_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ON, on_input,
                                                                    any_method(with_name='commandCallback'))


def test_off_should_command_csp_master_leaf_node_to_stop():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid_csp/elt/master'

    dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    csp_master_proxy_mock = Mock()

    proxies_to_mock = {
        csp_master_fqdn: csp_master_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        off_input = []
        # act:
        tango_context.device.Off(off_input)

        # assert:
        csp_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_OFF, off_input,
                                                                    any_method(with_name='commandCallback'))


def test_standby_should_command_csp_master_leaf_node_to_standby():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid_csp/elt/master'

    dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    csp_master_proxy_mock = Mock()

    proxies_to_mock = {
        csp_master_fqdn: csp_master_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        standby_input = []
        # act:
        tango_context.device.Standby(standby_input)

        # assert:
        csp_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STANDBY, standby_input,
                                                                    any_method(with_name='commandCallback'))


def test_attribute_csp_cbf_health_state_of_csp_master_is_ok():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_cbf_health_state_attribute = 'cspCbfHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.OK
        dummy_event = \
            create_dummy_event_for_health_state\
                (csp_master_fqdn,health_state_value,csp_cbf_health_state_attribute)
        event_subscription_map[csp_cbf_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_CBF_HEALTH_OK


def test_attribute_csp_cbf_health_state_of_csp_master_is_degraded():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_cbf_health_state_attribute = 'cspCbfHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.DEGRADED
        dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                               csp_cbf_health_state_attribute)
        event_subscription_map[csp_cbf_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_CBF_HEALTH_DEGRADED


def test_attribute_csp_cbf_health_state_of_csp_master_is_failed():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_cbf_health_state_attribute = 'cspCbfHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.FAILED
        dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                               csp_cbf_health_state_attribute)
        event_subscription_map[csp_cbf_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_CBF_HEALTH_FAILED


def test_attribute_csp_cbf_health_state_of_csp_master_is_unknown():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_cbf_health_state_attribute = 'cspCbfHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.UNKNOWN
        dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                               csp_cbf_health_state_attribute)
        event_subscription_map[csp_cbf_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_CBF_HEALTH_UNKNOWN


def test_attribute_csp_pss_health_callback_of_csp_master_is_ok():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_pss_health_state_attribute = 'cspPssHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.OK
        dummy_event = \
            create_dummy_event_for_health_state\
                (csp_master_fqdn,health_state_value,csp_pss_health_state_attribute)
        event_subscription_map[csp_pss_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PSS_HEALTH_OK


def test_attribute_csp_pss_health_callback_of_csp_master_is_degraded():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_pss_health_state_attribute = 'cspPssHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.DEGRADED
        dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                               csp_pss_health_state_attribute)
        event_subscription_map[csp_pss_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PSS_HEALTH_DEGRADED


def test_attribute_csp_pss_health_callback_of_csp_master_is_failed():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_pss_health_state_attribute = 'cspPssHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.FAILED
        dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                               csp_pss_health_state_attribute)
        event_subscription_map[csp_pss_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PSS_HEALTH_FAILED


def test_attribute_csp_pss_health_callback_of_csp_master_is_unknown():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_pss_health_state_attribute = 'cspPssHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.UNKNOWN
        dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                               csp_pss_health_state_attribute)
        event_subscription_map[csp_pss_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PSS_HEALTH_UNKNOWN


def test_attribute_csp_pst_health_callback_of_csp_master_is_ok():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_pst_health_state_attribute = 'cspPstHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.OK
        dummy_event = \
            create_dummy_event_for_health_state\
                (csp_master_fqdn,health_state_value,csp_pst_health_state_attribute)
        event_subscription_map[csp_pst_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PST_HEALTH_OK


def test_attribute_csp_pst_health_callback_of_csp_master_is_degraded():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_pst_health_state_attribute = 'cspPstHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.DEGRADED
        dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                               csp_pst_health_state_attribute)
        event_subscription_map[csp_pst_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PST_HEALTH_DEGRADED


def test_attribute_csp_pst_health_callback_of_csp_master_is_failed():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_pst_health_state_attribute = 'cspPstHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.FAILED
        dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                               csp_pst_health_state_attribute)
        event_subscription_map[csp_pst_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PST_HEALTH_FAILED


def test_attribute_csp_pst_health_callback_of_csp_master_is_unknown():
    # arrange:
    device_under_test = CspMasterLeafNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_pst_health_state_attribute = 'cspPstHealthState'
    initial_dut_properties = {
        'CspMasterFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.UNKNOWN
        dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                               csp_pst_health_state_attribute)
        event_subscription_map[csp_pst_health_state_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_CSP_PST_HEALTH_UNKNOWN


def create_dummy_event_for_health_state(device_fqdn,health_state_value,attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = health_state_value
    return fake_event


def test_activity_message():
    # arrange:
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.activityMessage = "text"
        assert tango_context.device.activityMessage == "text"


def test_state():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.State() == DevState.ALARM


def test_status():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert const.STR_DEV_ALARM in tango_context.device.Status()


def test_logging_level():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_test_mode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_simulation_mode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode


def test_control_mode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_admin_mode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.adminMode == AdminMode.ONLINE


def test_health_state():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
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
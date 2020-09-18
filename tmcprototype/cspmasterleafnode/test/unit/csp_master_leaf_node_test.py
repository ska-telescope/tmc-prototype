# PROTECTED REGION ID(CspMasterLeafNode.import) ENABLED START #

# Standard Python imports
import contextlib
import importlib
import types
import sys
import mock
from mock import Mock, MagicMock

# Tango imports
import pytest
import tango
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from cspmasterleafnode import CspMasterLeafNode, const, release
from ska.base.control_model import HealthState
from ska.base.control_model import LoggingLevel

# PROTECTED REGION END #    //  CspMasterLeafNode imports

@pytest.fixture(scope="function")
def mock_csp_master():
    csp_master_fqdn = 'mid_csp/elt/master'
    dut_properties = {'CspMasterFQDN': csp_master_fqdn}
    event_subscription_map = {}
    csp_master_proxy_mock = Mock()
    csp_master_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))
    proxies_to_mock = {csp_master_fqdn: csp_master_proxy_mock}
    with fake_tango_system(CspMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield csp_master_proxy_mock, tango_context.device, csp_master_fqdn, event_subscription_map

@pytest.fixture(scope="function")
def event_subscription(mock_csp_master):
    event_subscription_map = {}
    mock_csp_master[0].command_inout_asynch.side_effect = (
        lambda command_name, arg, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map

@pytest.fixture(scope="function")
def tango_context():
    with fake_tango_system(CspMasterLeafNode) as tango_context:
        yield tango_context

@pytest.mark.forked
def test_on_should_command_csp_master_leaf_node_to_start(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master

    # act:
    device_proxy.On()
    # assert:
    csp_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ON, [],
                                                                  any_method(with_name='on_cmd_ended_cb'))

@pytest.mark.forked
def test_off_should_command_csp_master_leaf_node_to_stop(mock_csp_master):
    # arrange:
    device_proxy=mock_csp_master[1]

    # act:
    device_proxy.On()
    device_proxy.Off()
    # assert:
    assert device_proxy.activityMessage in const.STR_OFF_CMD_ISSUED

@pytest.mark.forked
def test_standby_should_command_to_standby_with_callback_method(mock_csp_master, event_subscription):
    # arrange:
    device_proxy=mock_csp_master[1]

    # act:
    device_proxy.Standby([])
    dummy_event = command_callback(const.CMD_STANDBY)
    event_subscription[const.CMD_STANDBY](dummy_event)
    # assert:
    assert const.STR_COMMAND + const.CMD_STANDBY in device_proxy.activityMessage

@pytest.mark.forked
def test_on_should_command_to_on_with_callback_method(mock_csp_master, event_subscription):
    # arrange:
    device_proxy=mock_csp_master[1]

    # act:
    device_proxy.On()
    dummy_event = command_callback(const.CMD_ON)
    event_subscription[const.CMD_ON](dummy_event)
    # assert:
    assert const.STR_COMMAND + const.CMD_ON in device_proxy.activityMessage

@pytest.mark.forked
def test_off_should_command_to_off_with_callback_method(mock_csp_master):
    # arrange:
    device_proxy=mock_csp_master[1]

    # act:
    device_proxy.On()
    device_proxy.Off()
    #"Off command is not generating event error in current implementation. Will be updated later."
    #TODO:FOR FUTURE USE
    # dummy_event = command_callback(const.CMD_OFF)
    # event_subscription_map[const.CMD_OFF](dummy_event)
    # assert const.STR_COMMAND + const.CMD_OFF in tango_context.device.activityMessage
    # assert:
    assert device_proxy.activityMessage in const.STR_OFF_CMD_ISSUED

@pytest.mark.forked
def test_standby_should_command_with_callback_method_with_event_error(mock_csp_master, event_subscription):
    # arrange:
    device_proxy=mock_csp_master[1]

    # act:
    device_proxy.Standby([])
    dummy_event = command_callback_with_event_error(const.CMD_STANDBY)
    event_subscription[const.CMD_STANDBY](dummy_event)
    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_STANDBY in device_proxy.activityMessage

@pytest.mark.forked
def test_on_should_command_with_callback_method_with_event_error(mock_csp_master, event_subscription ):
    # arrange:
    device_proxy=mock_csp_master[1]

   #act
    device_proxy.On()
    dummy_event = command_callback_with_event_error(const.CMD_ON)
    event_subscription[const.CMD_ON](dummy_event)
    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_ON in device_proxy.activityMessage


#TODO: FOR FUTURE USE
@pytest.mark.xfail(reason="Off command is not generating event error in current implementation. "
                          "Will be updated later.")
def test_off_should_command_with_callback_method_with_event_error(mock_csp_master ,event_subscription):
    # arrange:
    device_proxy=mock_csp_master[1]

    # act:
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback_with_event_error(const.CMD_OFF)
    event_subscription[const.CMD_OFF](dummy_event)
    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_OFF in device_proxy.activityMessage


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
    return Exception("Exception in Command Callback")

@pytest.mark.forked
def test_attribute_csp_cbf_health_state_of_csp_master_is_ok(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_cbf_health_state_attribute = 'cspCbfHealthState'

    # act:
    health_state_value = HealthState.OK
    dummy_event = \
        create_dummy_event_for_health_state \
            (csp_master_fqdn, health_state_value, csp_cbf_health_state_attribute)
    event_subscription_map[csp_cbf_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_CBF_HEALTH_OK

@pytest.mark.forked
def test_attribute_csp_cbf_health_state_of_csp_master_is_degraded(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_cbf_health_state_attribute = 'cspCbfHealthState'

    # act:
    health_state_value = HealthState.DEGRADED
    dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                      csp_cbf_health_state_attribute)
    event_subscription_map[csp_cbf_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_CBF_HEALTH_DEGRADED

@pytest.mark.forked
def test_attribute_csp_cbf_health_state_of_csp_master_is_failed(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_cbf_health_state_attribute = 'cspCbfHealthState'

    # act:
    health_state_value = HealthState.FAILED
    dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                      csp_cbf_health_state_attribute)
    event_subscription_map[csp_cbf_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_CBF_HEALTH_FAILED

@pytest.mark.forked
def test_attribute_csp_cbf_health_state_of_csp_master_is_unknown(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_cbf_health_state_attribute = 'cspCbfHealthState'

    # act:
    health_state_value = HealthState.UNKNOWN
    dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                      csp_cbf_health_state_attribute)
    event_subscription_map[csp_cbf_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_CBF_HEALTH_UNKNOWN

@pytest.mark.forked
def test_attribute_csp_cbf_health_state_of_csp_master_with_error_event(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_cbf_health_state_attribute = 'cspCbfHealthState'

    # act:
    health_state_value = HealthState.UNKNOWN
    dummy_event = create_dummy_event_for_health_state_with_error(csp_master_fqdn, health_state_value,
                                                                 csp_cbf_health_state_attribute)
    event_subscription_map[csp_cbf_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.ERR_ON_SUBS_CSP_CBF_HEALTH + str(
        dummy_event.errors)

@pytest.mark.forked
def test_attribute_csp_pss_health_callback_of_csp_master_is_ok(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pss_health_state_attribute = 'cspPssHealthState'
    # act:
    health_state_value = HealthState.OK
    dummy_event = \
        create_dummy_event_for_health_state \
            (csp_master_fqdn, health_state_value, csp_pss_health_state_attribute)
    event_subscription_map[csp_pss_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage ==  const.STR_CSP_PSS_HEALTH_OK

@pytest.mark.forked
def test_attribute_csp_pss_health_callback_of_csp_master_is_degraded(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pss_health_state_attribute = 'cspPssHealthState'

    # act:
    health_state_value = HealthState.DEGRADED
    dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                      csp_pss_health_state_attribute)
    event_subscription_map[csp_pss_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_PSS_HEALTH_DEGRADED

@pytest.mark.forked
def test_attribute_csp_pss_health_callback_of_csp_master_is_failed(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pss_health_state_attribute = 'cspPssHealthState'
    # act:
    health_state_value = HealthState.FAILED
    dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                      csp_pss_health_state_attribute)
    event_subscription_map[csp_pss_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_PSS_HEALTH_FAILED

@pytest.mark.forked
def test_attribute_csp_pss_health_callback_of_csp_master_is_unknown(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pss_health_state_attribute = 'cspPssHealthState'

    # act:
    health_state_value = HealthState.UNKNOWN
    dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                      csp_pss_health_state_attribute)
    event_subscription_map[csp_pss_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_PSS_HEALTH_UNKNOWN

@pytest.mark.forked
def test_attribute_csp_pss_health_callback_of_csp_master_with_error_event(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pss_health_state_attribute = 'cspPssHealthState'

    # act:
    health_state_value = HealthState.UNKNOWN
    dummy_event = create_dummy_event_for_health_state_with_error(csp_master_fqdn, health_state_value,
                                                                 csp_pss_health_state_attribute)
    event_subscription_map[csp_pss_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.ERR_ON_SUBS_CSP_PSS_HEALTH + str(
        dummy_event.errors)

@pytest.mark.forked
def test_attribute_csp_pst_health_callback_of_csp_master_is_ok(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pst_health_state_attribute = 'cspPstHealthState'

    # act:
    health_state_value = HealthState.OK
    dummy_event = \
        create_dummy_event_for_health_state \
            (csp_master_fqdn, health_state_value, csp_pst_health_state_attribute)
    event_subscription_map[csp_pst_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_PST_HEALTH_OK

@pytest.mark.forked
def test_attribute_csp_pst_health_callback_of_csp_master_is_degraded(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pst_health_state_attribute = 'cspPstHealthState'

    # act:
    health_state_value = HealthState.DEGRADED
    dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                      csp_pst_health_state_attribute)
    event_subscription_map[csp_pst_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_PST_HEALTH_DEGRADED

@pytest.mark.forked
def test_attribute_csp_pst_health_callback_of_csp_master_is_failed(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pst_health_state_attribute = 'cspPstHealthState'

    # act:
    health_state_value = HealthState.FAILED
    dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                      csp_pst_health_state_attribute)
    event_subscription_map[csp_pst_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_PST_HEALTH_FAILED

@pytest.mark.forked
def test_attribute_csp_pst_health_callback_of_csp_master_is_unknown(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pst_health_state_attribute = 'cspPstHealthState'

    # act:
    health_state_value = HealthState.UNKNOWN
    dummy_event = create_dummy_event_for_health_state(csp_master_fqdn, health_state_value,
                                                      csp_pst_health_state_attribute)
    event_subscription_map[csp_pst_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.STR_CSP_PST_HEALTH_UNKNOWN

@pytest.mark.forked
def test_attribute_csp_pst_health_callback_of_csp_master_with_error_event(mock_csp_master):
    # arrange:
    csp_proxy_mock, device_proxy, csp_master_fqdn, event_subscription_map = mock_csp_master
    csp_pst_health_state_attribute = 'cspPstHealthState'

    # act:
    health_state_value = HealthState.UNKNOWN
    dummy_event = create_dummy_event_for_health_state_with_error(csp_master_fqdn, health_state_value,
                                                                 csp_pst_health_state_attribute)
    event_subscription_map[csp_pst_health_state_attribute](dummy_event)
    # assert:
    assert device_proxy.activityMessage == const.ERR_ON_SUBS_CSP_PST_HEALTH + str(
        dummy_event.errors)


def create_dummy_event_for_health_state(device_fqdn, health_state_value, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = health_state_value
    return fake_event


def create_dummy_event_for_health_state_with_error(device_fqdn, health_state_value, attribute):
    fake_event = Mock()
    fake_event.err = True
    fake_event.errors = 'Event error in attribute callback'
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = health_state_value
    return fake_event

@pytest.mark.forked
def test_read_activity_message(tango_context):
    # act & assert:
    tango_context.device.activityMessage = 'test'
    assert tango_context.device.activityMessage == 'test'

@pytest.mark.forked
def test_write_activity_message(tango_context):
    # act & assert:
    tango_context.device.activityMessage = 'test'
    assert tango_context.device.activityMessage == 'test'

@pytest.mark.forked
def test_status(tango_context):
    # act & assert:
    assert const.STR_DEV_ALARM in tango_context.device.Status()

@pytest.mark.forked
def test_logging_level(tango_context):
    # act & assert:
    tango_context.device.loggingLevel = LoggingLevel.INFO
    assert tango_context.device.loggingLevel == LoggingLevel.INFO

@pytest.mark.forked
def test_logging_targets(tango_context):
    # act & assert:
    tango_context.device.loggingTargets = ['console::cout']
    assert 'console::cout' in tango_context.device.loggingTargets

@pytest.mark.forked
def test_health_state(tango_context):
    # act & assert:
    assert tango_context.device.healthState == HealthState.OK

@pytest.mark.forked
def test_version_id(tango_context):
    """Test for versionId"""
    assert tango_context.device.versionId == release.version

@pytest.mark.forked
def test_build_state(tango_context):
    """Test for buildState"""
    assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))


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
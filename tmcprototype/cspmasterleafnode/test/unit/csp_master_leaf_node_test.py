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
from tango.test_context import DeviceTestContext

# Additional import
from ska.base.control_model import HealthState
from ska.base.control_model import LoggingLevel
from ska.base.commands import ResultCode
from cspmasterleafnode import CspMasterLeafNode, const, release
from cspmasterleafnode.device_data import DeviceData
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

# PROTECTED REGION END #    //  CspMasterLeafNode imports


@pytest.fixture(scope="function")
def mock_csp_master_proxy():
    dut_properties = {"CspMasterFQDN": "mid_csp/elt/master"}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update(
        {attr_name: callback}
    )
    with fake_tango_system(
        CspMasterLeafNode, initial_dut_properties=dut_properties
    ) as tango_context:
        with mock.patch.object(
            TangoClient, "_get_deviceproxy", return_value=Mock()
        ) as mock_obj:
            tango_client_obj = TangoClient(dut_properties["CspMasterFQDN"])
            yield tango_context.device, tango_client_obj, dut_properties[
                "CspMasterFQDN"
            ], event_subscription_map


@pytest.fixture(scope="function")
def event_subscription_mock(mock_csp_master_proxy):
    event_subscription_map = {}
    mock_csp_master_proxy[
        1
    ].deviceproxy.command_inout_asynch.side_effect = lambda command_name, arg, callback, *args, **kwargs: event_subscription_map.update(
        {command_name: callback}
    )
    yield event_subscription_map


@pytest.fixture(scope="function")
def tango_context():
    with fake_tango_system(CspMasterLeafNode) as tango_context:
        yield tango_context

@pytest.fixture(scope="function")
def mock_tango_server_helper():
    csp_master_fqdn = "mid_csp/elt/master"
    tango_server_obj = TangoServerHelper.get_instance()
    tango_server_obj.read_property = Mock(return_value = csp_master_fqdn)
    yield tango_server_obj

def test_on(mock_csp_master_proxy, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_csp_master_proxy[:2]
    assert device_proxy.On() == [
        [ResultCode.OK],
        ["ON command invoked successfully from CSP Master leaf node."],
    ]
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_ON, [], any_method(with_name="on_cmd_ended_cb")
    )


def test_off_should_command_csp_master_leaf_node_to_stop(mock_csp_master_proxy, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_csp_master_proxy[:2]

    device_proxy.On()
    assert device_proxy.Off() == [
        [ResultCode.OK],
        ["OFF command invoked successfully from CSP Master leaf node."],
    ]


def test_standby_should_command_to_standby_with_callback_method(
    mock_csp_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_master_proxy[:2]
    device_proxy.Standby([])
    dummy_event = command_callback(const.CMD_STANDBY)
    event_subscription_mock[const.CMD_STANDBY](dummy_event)
    assert const.STR_COMMAND + const.CMD_STANDBY in device_proxy.activityMessage


def test_on_should_command_to_on_with_callback_method(
    mock_csp_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_master_proxy[:2]
    device_proxy.On()
    dummy_event = command_callback(const.CMD_ON)
    event_subscription_mock[const.CMD_ON](dummy_event)
    assert const.STR_COMMAND + const.CMD_ON in device_proxy.activityMessage


def test_off_should_command_to_off(mock_csp_master_proxy, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_csp_master_proxy[:2]
    device_proxy.On()
    device_proxy.Off()
    assert const.STR_OFF_CMD_ISSUED in device_proxy.activityMessage


def test_standby_should_command_with_callback_method_with_event_error(
    mock_csp_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_master_proxy[:2]
    device_proxy.Standby([])
    dummy_event = command_callback_with_event_error(const.CMD_STANDBY)
    event_subscription_mock[const.CMD_STANDBY](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_STANDBY in device_proxy.activityMessage


def test_on_should_command_with_callback_method_with_event_error(
    mock_csp_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_master_proxy[:2]
    device_proxy.On()
    dummy_event = command_callback_with_event_error(const.CMD_ON)
    event_subscription_mock[const.CMD_ON](dummy_event)

    assert const.ERR_INVOKING_CMD + const.CMD_ON in device_proxy.activityMessage


def test_on_command_should_raise_dev_failed(mock_csp_master_proxy, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_csp_master_proxy[:2]
    
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
        raise_devfailed_exception
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.On()
    assert const.ERR_DEVFAILED_MSG in str(df.value)


def test_standby_command_should_raise_dev_failed(mock_csp_master_proxy, mock_tango_server_helper ):
    device_proxy, tango_client_obj = mock_csp_master_proxy[:2]
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
        raise_devfailed_exception
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.standby([])
    assert const.ERR_DEVFAILED_MSG in str(df.value)


def raise_devfailed_exception(*args):
    # "This function is called to raise DevFailed exception with arguments."
    tango.Except.throw_exception(
        const.STR_CMD_FAILED, const.ERR_DEVFAILED_MSG, "", tango.ErrSeverity.ERR
    )


def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_event_error(command_name):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = "Event error in Command Callback"
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_command_exception():
    return Exception("Exception in Command Callback")


# TODO: Use parametrize approach for commented Healthstate callback parameters.
@pytest.fixture(
    scope="function",
    params=[
        HealthState.OK,
        # HealthState.DEGRADED,
        # HealthState.FAILED,
        # HealthState.UNKNOWN
    ],
)
def health_state(request):
    return request.param


def test_activity_message_attribute_reports_correct_csp_health_state_callbacks(
    mock_csp_master_proxy, health_state, mock_tango_server_helper
):
    (
        device_proxy,
        tango_client_obj,
        csp_master_fqdn,
        event_subscription_map,
    ) = mock_csp_master_proxy
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ) as mock_obj:
        with mock.patch.object(
            TangoClient, "subscribe_attribute", side_effect=dummy_subscriber
        ):
            tango_client_obj = TangoClient("mid_csp/elt/master")
            device_proxy.On()
    device_data = DeviceData.get_instance()
    assert (
        device_data._csp_cbf_health_state_log
        == f"CSP CBF health is {health_state.name}"
    )
    assert (
        device_data._csp_pst_health_state_log
        == f"CSP PST health is {health_state.name}."
    )
    assert (
        device_data._csp_pss_health_state_log
        == f"CSP PSS health is {health_state.name}."
    )


# TODO: Use parametrize approach for Healthstate callbacks
# @pytest.mark.parametrize(
#     "attribute_name,error_message",
#     [
#         ("cspCbfHealthState", const.ERR_ON_SUBS_CSP_CBF_HEALTH),
#         ("cspPssHealthState", const.ERR_ON_SUBS_CSP_PSS_HEALTH),
#         ("cspPstHealthState", const.ERR_ON_SUBS_CSP_PST_HEALTH )
#     ]
# )
def test_activity_message_reports_correct_health_state_when_attribute_event_has_error(
    mock_csp_master_proxy, mock_tango_server_helper
):
    (
        device_proxy,
        tango_client_obj,
        csp_master_fqdn,
        event_subscription_map,
    ) = mock_csp_master_proxy
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ) as mock_obj:
        with mock.patch.object(
            TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_with_error
        ):
            tango_client_obj = TangoClient("mid_csp/elt/master")
            device_proxy.On()
    device_data = DeviceData.get_instance()
    assert const.ERR_ON_SUBS_CSP_CBF_HEALTH in device_data._csp_cbf_health_state_log
    assert const.ERR_ON_SUBS_CSP_PSS_HEALTH in device_data._csp_pss_health_state_log
    assert const.ERR_ON_SUBS_CSP_PST_HEALTH in device_data._csp_pst_health_state_log


def dummy_subscriber(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"mid_csp/elt/master/{attribute}"
    fake_event.attr_value.value = HealthState.OK
    callback_method(fake_event)
    return 10


def dummy_subscriber_with_error(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = True
    fake_event.errors = "Event error in attribute callback"
    fake_event.attr_name = f"mid_csp/elt/master/{attribute}"
    fake_event.attr_value.value = HealthState.OK
    callback_method(fake_event)
    return 10


def test_read_activity_message(tango_context, mock_tango_server_helper):
    tango_context.device.activityMessage = "test"
    assert tango_context.device.activityMessage == "test"


def test_status(tango_context, mock_tango_server_helper):
    tango_server_obj = mock_tango_server_helper
    assert const.STR_DEV_OFF in tango_server_obj.get_status()


def test_logging_level(tango_context):
    tango_context.device.loggingLevel = LoggingLevel.INFO
    assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets(tango_context):
    tango_context.device.loggingTargets = ["console::cout"]
    assert "console::cout" in tango_context.device.loggingTargets


def test_health_state(tango_context, mock_tango_server_helper):
    tango_server_obj = mock_tango_server_helper
    assert tango_server_obj.read_attr("healthState") == HealthState.OK


def test_version_id(tango_context, mock_tango_server_helper):
    """Test for versionId"""
    tango_server_obj = mock_tango_server_helper
    assert tango_server_obj.read_attr("versionId") == release.version


def test_build_state(tango_context, mock_tango_server_helper):
    """Test for buildState"""
    tango_server_obj = mock_tango_server_helper
    assert tango_server_obj.read_attr("buildState") == (
        "{},{},{}".format(release.name, release.version, release.description))


def any_method(with_name=None):
    class AnyMethod:
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


@contextlib.contextmanager
def fake_tango_system(
    device_under_test,
    initial_dut_properties={},
    proxies_to_mock={},
    device_proxy_import_path="tango.DeviceProxy",
):
    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(
            device_fqdn, Mock()
        )
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(
        device_under_test, properties=initial_dut_properties
    )
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()

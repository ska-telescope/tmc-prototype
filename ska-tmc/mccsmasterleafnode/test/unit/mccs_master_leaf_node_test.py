# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #

# Standard Python imports
import contextlib
import importlib
import types
import sys
import mock
from mock import Mock, MagicMock
from os.path import dirname, join

# Tango imports
import pytest
import tango
from tango.test_context import DeviceTestContext

# Additional import
from mccsmasterleafnode import MccsMasterLeafNode, const, release
from ska.base.control_model import HealthState, ObsState
from ska.base.commands import ResultCode
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from mccsmasterleafnode import MccsMasterLeafNode, const, release, device_data
from mccsmasterleafnode.device_data import DeviceData


# PROTECTED REGION END #    //  MccsMasterLeafNode imports
assign_input_file = "command_AssignResources.json"
path = join(dirname(__file__), "data", assign_input_file)
with open(path, "r") as f:
    assign_input_str = f.read()

release_input_file = "command_ReleaseResources.json"
path = join(dirname(__file__), "data", release_input_file)
with open(path, "r") as f:
    release_input_str = f.read()


# Create DeviceData class instance
device_data = DeviceData.get_instance()

@pytest.fixture(scope="function")
def mock_tango_server_helper():
    mccs_master_fqdn = "low-mccs/control/control"
    tango_server_obj = TangoServerHelper.get_instance()
    tango_server_obj.read_property = Mock(return_value = mccs_master_fqdn)
    yield tango_server_obj


@pytest.fixture(scope="function")
def mock_mccs_master_proxy():
    dut_properties = {"MccsMasterFQDN": "low-mccs/control/control"}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update(
        {attr_name: callback}
    )
    with fake_tango_system(
        MccsMasterLeafNode, initial_dut_properties=dut_properties
    ) as tango_context:
        with mock.patch.object(
            TangoClient, "_get_deviceproxy", return_value=Mock()
        ) as mock_obj:
            tango_client_obj = TangoClient(dut_properties["MccsMasterFQDN"])
            yield tango_context.device, tango_client_obj, dut_properties[
                "MccsMasterFQDN"
            ], event_subscription_map


@pytest.fixture(scope="function")
def event_subscription_mock():
    dut_properties = {"MccsMasterFQDN": "low-mccs/control/control"}
    event_subscription_map = {}
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ) as mock_obj:
        tango_client_obj = TangoClient(dut_properties["MccsMasterFQDN"])
        tango_client_obj.deviceproxy.command_inout_asynch.side_effect = lambda command_name, arg, callback, *args, **kwargs: event_subscription_map.update(
            {command_name: callback}
        )
        yield event_subscription_map


def raise_devfailed_exception(*args):
    # "This function is called to raise DevFailed exception."
    tango.Except.throw_exception(
        "MccsMasterLeafNode_CommandFailed",
        const.ERR_DEVFAILED_MSG,
        " ",
        tango.ErrSeverity.ERR,
    )


def test_on_should_command_mccs_master_leaf_node_to_start(mock_mccs_master_proxy,
                                                          mock_tango_server_helper):
    (
        device_proxy,
        tango_client_obj,
        mccs_master_fqdn,
        event_subscription_map,
    ) = mock_mccs_master_proxy
    tango_server_obj = mock_tango_server_helper
    assert device_proxy.On() == [
        [ResultCode.OK],
        ["ON command invoked successfully from MCCS Master leaf node."],
    ]
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_ON, None, any_method(with_name="on_cmd_ended_cb")
    )


def test_on_should_command_to_on_with_callback_method(
    mock_mccs_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_mccs_master_proxy[:2]
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    dummy_event = command_callback(const.CMD_ON)
    event_subscription_mock[const.CMD_ON](dummy_event)
    assert const.STR_COMMAND + const.CMD_ON in device_proxy.activityMessage


def test_on_should_command_with_callback_method_with_event_error(
    mock_mccs_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_mccs_master_proxy[:2]
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    dummy_event = command_callback_with_event_error(const.CMD_ON)
    event_subscription_mock[const.CMD_ON](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_ON in device_proxy.activityMessage


def test_on_should_raise_devfailed_exception(mock_mccs_master_proxy, mock_tango_server_helper):
    (
        device_proxy,
        tango_client_obj,
        mccs_master_fqdn,
        event_subscription_map,
    ) = mock_mccs_master_proxy
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
        raise_devfailed_exception
    )
    with pytest.raises(tango.DevFailed) as df:
        tango_server_obj = mock_tango_server_helper
        device_proxy.On()
    assert const.ERR_DEVFAILED_MSG in str(df.value)


def test_off_should_command_mccs_master_leaf_node_to_stop(mock_mccs_master_proxy, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_mccs_master_proxy[:2]
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    assert device_proxy.Off() == [
        [ResultCode.OK],
        ["OFF command invoked successfully from MCCS Master leaf node."],
    ]
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_OFF, None, any_method(with_name="off_cmd_ended_cb")
    )


def test_off_should_command_to_off_with_callback_method(
    mock_mccs_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_mccs_master_proxy[:2]
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback(const.CMD_OFF)
    event_subscription_mock[const.CMD_OFF](dummy_event)
    assert const.STR_COMMAND + const.CMD_OFF in device_proxy.activityMessage


def test_off_should_command_with_callback_method_with_event_error(
    mock_mccs_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_mccs_master_proxy[:2]
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback_with_event_error(const.CMD_OFF)
    event_subscription_mock[const.CMD_OFF](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_OFF in device_proxy.activityMessage


def test_off_should_raise_devfailed_exception(mock_mccs_master_proxy, mock_tango_server_helper):
    (
        device_proxy,
        tango_client_obj,
        mccs_master_fqdn,
        event_subscription_map,
    ) = mock_mccs_master_proxy
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
        raise_devfailed_exception
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Off()
    assert const.ERR_DEVFAILED_MSG in str(df.value)


@pytest.fixture(
    scope="function",
    params=[
        (
            "AssignResources",
            const.CMD_ALLOCATE,
            assign_input_str,
            ObsState.EMPTY,
            const.ERR_DEVFAILED_MSG,
        ),
        (
            "ReleaseResources",
            const.CMD_Release,
            release_input_str,
            ObsState.IDLE,
            const.ERR_RELEASE_ALL_RESOURCES,
        ),
    ],
)
def command_with_arg(request):
    cmd_name, requested_cmd, input_str, obs_state, error_msg = request.param
    return cmd_name, requested_cmd, input_str, obs_state, error_msg


def test_command_raise_devfailed_exception(mock_mccs_master_proxy, command_with_arg,
                                           mock_tango_server_helper):
    (
        device_proxy,
        tango_client_obj,
        mccs_master_fqdn,
        event_subscription_map,
    ) = mock_mccs_master_proxy
    cmd_name, requested_cmd, input_str, obs_state, error_msg = command_with_arg
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
        raise_devfailed_exception
    )
    with pytest.raises(tango.DevFailed) as df:
        tango_server_obj = mock_tango_server_helper
        device_proxy.command_inout(cmd_name, input_str)
    assert error_msg in str(df.value)


def test_command_invoke_with_command_callback_method(
    mock_mccs_master_proxy, event_subscription_mock, command_with_arg, mock_tango_server_helper
):
    (
        device_proxy,
        tango_client_obj,
        mccs_master_fqdn,
        event_subscription_map,
    ) = mock_mccs_master_proxy
    cmd_name, requested_cmd, input_str, obs_state, error_msg = command_with_arg
    tango_server_obj = mock_tango_server_helper
    device_proxy.command_inout(cmd_name, input_str)
    dummy_event = command_callback(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.STR_INVOKE_SUCCESS in device_proxy.activityMessage


def test_command_with_command_callback_event_error(
    mock_mccs_master_proxy, event_subscription_mock, command_with_arg, mock_tango_server_helper
):
    (
        device_proxy,
        tango_client_obj,
        mccs_master_fqdn,
        event_subscription_map,
    ) = mock_mccs_master_proxy
    cmd_name, requested_cmd, input_str, obs_state, error_msg = command_with_arg
    tango_server_obj = mock_tango_server_helper
    device_proxy.command_inout(cmd_name, input_str)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage


def test_assign_command_with_callback_method_with_devfailed_error(
    mock_mccs_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    (
        device_proxy,
        tango_client_obj,
        mccs_master_fqdn,
        event_subscription_map,
    ) = mock_mccs_master_proxy
    device_proxy, tango_client_obj = mock_mccs_master_proxy[:2]
    device_proxy.On()
    with pytest.raises(tango.DevFailed) as df:
        tango_server_obj = mock_tango_server_helper
        device_proxy.AssignResources(assign_input_str)
        dummy_event = command_callback_with_devfailed_exception()
        event_subscription_mock[const.CMD_ADD_RECEPTORS](dummy_event)
    assert const.ERR_CALLBACK_CMD_FAILED in str(df.value)


def test_release_resource_should_command_mccs_master_to_release_all_resources(
    mock_mccs_master_proxy, mock_tango_server_helper
):
    (
        device_proxy,
        tango_client_obj,
        mccs_master_fqdn,
        event_subscription_map,
    ) = mock_mccs_master_proxy
    device_proxy, tango_client_obj = mock_mccs_master_proxy[:2]
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    device_proxy.ReleaseResources(release_input_str)
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_Release,
        release_input_str,
        any_method(with_name="releaseresources_cmd_ended_cb"),
    )


def raise_devfailed_exception(*args):
    # "This function is called to raise DevFailed exception."
    tango.Except.throw_exception(
        "MccsMasterLeafNode_CommandFailed",
        const.ERR_DEVFAILED_MSG,
        " ",
        tango.ErrSeverity.ERR,
    )


def test_read_activity_message(mock_mccs_master_proxy):
    # test case for method read_activityMessage
    device_proxy = mock_mccs_master_proxy[0]
    device_proxy.activityMessage = "test"
    assert_activity_message(device_proxy, "test")


def test_write_activity_message(mock_mccs_master_proxy):
    # test case for method write_activityMessage
    device_proxy = mock_mccs_master_proxy[0]
    device_proxy.activityMessage = "test"
    assert_activity_message(device_proxy, "test")


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


def command_callback_with_devfailed_exception():
    # "This function is called when command is failed with DevFailed exception."
    tango.Except.throw_exception(
        const.ERR_DEVFAILED_MSG,
        const.ERR_CALLBACK_CMD_FAILED,
        " ",
        tango.ErrSeverity.ERR,
    )


def any_method(with_name=None):
    class AnyMethod:
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute


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

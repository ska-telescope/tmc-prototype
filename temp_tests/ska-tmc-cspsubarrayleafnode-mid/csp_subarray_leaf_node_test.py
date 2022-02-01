# Standard Python imports
import contextlib
import importlib
import json
import sys
import types
from os.path import dirname, join

import mock
import pytest
import tango
from mock import MagicMock, Mock
from ska.base.control_model import HealthState, LoggingLevel, ObsState

# Additional import
from src.ska_tmc_cspsubarrayleafnode_mid import (
    CspSubarrayLeafNode,
    const,
    release,
)
from tango import DevState

# Tango imports
from tango.test_context import DeviceTestContext
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

obs_state_global = ObsState.IDLE

assign_input_file = "command_AssignResources.json"
path = join(dirname(__file__), "data", assign_input_file)
with open(path, "r") as f:
    assign_input_str = f.read()

scan_input_file = "command_Scan.json"
path = join(dirname(__file__), "data", scan_input_file)
with open(path, "r") as f:
    scan_input_str = f.read()

configure_input_file = "command_Configure.json"
path = join(dirname(__file__), "data", configure_input_file)
with open(path, "r") as f:
    configure_str = f.read()

invalid_json_assign_config_file = (
    "invalid_json_Assign_Resources_Configure.json"
)
path = join(dirname(__file__), "data", invalid_json_assign_config_file)
with open(path, "r") as f:
    invalid_key_str = f.read()

assign_invalid_key_file = "invalid_key_AssignResources.json"
path = join(dirname(__file__), "data", assign_invalid_key_file)
with open(path, "r") as f:
    assign_invalid_key = f.read()


@pytest.fixture(scope="function")
def mock_tango_server_helper():
    csp_subarray1_fqdn = "mid_csp/elt/subarray_01"
    tango_server_obj = TangoServerHelper.get_instance()
    tango_server_obj.read_property = Mock(return_value=csp_subarray1_fqdn)
    yield tango_server_obj


@pytest.fixture(scope="function")
def mock_csp_subarray():
    csp_subarray1_fqdn = "mid_csp/elt/subarray_01"
    dut_properties = {"CspSubarrayFQDN": csp_subarray1_fqdn}
    csp_subarray1_proxy_mock = Mock()
    proxies_to_mock = {csp_subarray1_fqdn: csp_subarray1_proxy_mock}
    with fake_tango_system(
        CspSubarrayLeafNode,
        initial_dut_properties=dut_properties,
        proxies_to_mock=proxies_to_mock,
    ) as tango_context:
        yield tango_context.device, csp_subarray1_proxy_mock


@pytest.fixture(scope="function")
def mock_tango_client():
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=MagicMock()
    ):
        tango_client_obj = TangoClient("mid_csp/elt/subarray_01")
        yield tango_client_obj


# This fixture is used for SP-1420
@pytest.fixture(scope="function")
def mock_csp_subarray_proxy(mock_tango_client):
    dut_properties = {"CspSubarrayFQDN": "mid_csp/elt/subarray_01"}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update(
        {attr_name: callback}
    )
    tango_client_obj = mock_tango_client
    with fake_tango_system(
        CspSubarrayLeafNode, initial_dut_properties=dut_properties
    ) as tango_context:
        yield tango_context.device, tango_client_obj, dut_properties[
            "CspSubarrayFQDN"
        ], event_subscription_map


# This fixture is used for SP-1420
@pytest.fixture(scope="function")
def event_subscription_mock():
    dut_properties = {"CspSubarrayFQDN": "mid_csp/elt/subarray_01"}
    event_subscription_map = {}
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(dut_properties["CspSubarrayFQDN"])
        tango_client_obj.deviceproxy.command_inout_asynch.side_effect = lambda command_name, arg, callback, *args, **kwargs: event_subscription_map.update(
            {command_name: callback}
        )
        yield event_subscription_map


@pytest.fixture(
    scope="function",
    params=[
        (
            "Configure",
            configure_str,
            const.CMD_CONFIGURE,
            ObsState.READY,
            const.ERR_DEVFAILED_MSG,
        ),
        (
            "Configure",
            configure_str,
            const.CMD_CONFIGURE,
            ObsState.IDLE,
            const.ERR_DEVFAILED_MSG,
        ),
        (
            "StartScan",
            scan_input_str,
            const.CMD_STARTSCAN,
            ObsState.READY,
            const.ERR_DEVFAILED_MSG,
        ),
        (
            "AssignResources",
            assign_input_str,
            const.CMD_ASSIGN_RESOURCES,
            ObsState.IDLE,
            const.ERR_DEVFAILED_MSG,
        ),
        (
            "AssignResources",
            assign_input_str,
            const.CMD_ASSIGN_RESOURCES,
            ObsState.EMPTY,
            const.ERR_DEVFAILED_MSG,
        ),
    ],
)
def command_with_arg(request):
    cmd_name, input_arg, requested_cmd, obs_state, error_msg = request.param
    return cmd_name, input_arg, requested_cmd, obs_state, error_msg


def test_command_cb_is_invoked_when_command_with_arg_is_called_async(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    command_with_arg,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    cmd_name, input_arg, requested_cmd, obs_state, _ = command_with_arg
    tango_client_obj.get_attribute.side_effect = Mock(return_value=obs_state)
    device_proxy.command_inout(cmd_name, input_arg)
    dummy_event = command_callback(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


@pytest.fixture(
    scope="function",
    params=[
        (
            "EndScan",
            const.CMD_ENDSCAN,
            ObsState.SCANNING,
            const.ERR_DEVFAILED_MSG,
        ),
        (
            "GoToIdle",
            const.CMD_GOTOIDLE,
            ObsState.READY,
            const.ERR_DEVFAILED_MSG,
        ),
        ("Abort", const.CMD_ABORT, ObsState.SCANNING, const.ERR_DEVFAILED_MSG),
        (
            "Restart",
            const.CMD_RESTART,
            ObsState.ABORTED,
            const.ERR_DEVFAILED_MSG,
        ),
        (
            "ObsReset",
            const.CMD_OBSRESET,
            ObsState.ABORTED,
            const.ERR_DEVFAILED_MSG,
        ),
    ],
)
def command_without_arg(request):
    cmd_name, requested_cmd, obs_state, error_msg = request.param
    return cmd_name, requested_cmd, obs_state, error_msg


def test_command_cb_is_invoked_when_command_without_arg_is_called_async(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    command_without_arg,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    cmd_name, requested_cmd, obs_state, _ = command_without_arg
    tango_client_obj.get_attribute.side_effect = Mock(return_value=obs_state)
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback(cmd_name)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


def test_command_cb_is_invoked_when_releaseresources_is_called_async(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.IDLE
    )
    device_proxy.ReleaseAllResources()
    dummy_event = command_callback(const.CMD_RELEASE_ALL_RESOURCES)
    event_subscription_mock[const.CMD_RELEASE_ALL_RESOURCES](dummy_event)
    assert (
        const.STR_COMMAND + const.CMD_RELEASE_ALL_RESOURCES
        in device_proxy.activityMessage
    )


def test_command_cb_is_invoked_when_command_with_event_error_is_called_async(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    command_with_arg,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    cmd_name, input_str, requested_cmd, obs_state, _ = command_with_arg
    tango_client_obj.get_attribute.side_effect = Mock(return_value=obs_state)
    device_proxy.TelescopeOn()
    device_proxy.command_inout(cmd_name, input_str)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert (
        const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage
    )


def test_command_cb_is_invoked_when_command_with_event_error_without_arg_is_called_async(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    command_without_arg,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    cmd_name, requested_cmd, obs_state, _ = command_without_arg
    tango_client_obj.get_attribute.side_effect = Mock(return_value=obs_state)
    device_proxy.TelescopeOn()
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.ERR_INVOKING_CMD + cmd_name in device_proxy.activityMessage


def test_command_cb_is_invoked_releaseresources_when_command_with_event_error_async(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.IDLE
    )
    device_proxy.ReleaseAllResources()
    dummy_event = command_callback_with_event_error(
        const.CMD_RELEASE_ALL_RESOURCES
    )
    event_subscription_mock[const.CMD_RELEASE_ALL_RESOURCES](dummy_event)
    assert (
        const.ERR_INVOKING_CMD + const.CMD_RELEASE_ALL_RESOURCES
        in device_proxy.activityMessage
    )


def test_command_with_arg_devfailed(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    command_with_arg,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    cmd_name, input_str, requested_cmd, obs_state, error_msg = command_with_arg
    tango_client_obj.get_attribute.side_effect = Mock(return_value=obs_state)
    device_proxy.TelescopeOn()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name, input_str)
        raise_devfailed_exception()
    assert error_msg in str(df.value)


def test_command_without_arg_devfailed(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    command_without_arg,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    cmd_name, requested_cmd, obs_state, error_msg = command_without_arg
    tango_client_obj.get_attribute.side_effect = Mock(return_value=obs_state)
    device_proxy.TelescopeOn()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name)
        raise_devfailed_exception()
    assert error_msg in str(df.value)


def test_command_releaseresources_devfailed(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.IDLE
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.ReleaseAllResources()
        raise_devfailed_exception()
    assert "This is error message for devfailed" in str(df.value)


@pytest.fixture(
    scope="function",
    params=[
        (
            "EndScan",
            ObsState.SCANNING,
            "endscan_cmd_ended_cb",
            const.STR_ENDSCAN_SUCCESS,
        ),
        (
            "GoToIdle",
            ObsState.READY,
            "gotoidle_cmd_ended_cb",
            const.STR_GOTOIDLE_SUCCESS,
        ),
        (
            "Abort",
            ObsState.SCANNING,
            "abort_cmd_ended_cb",
            const.STR_ABORT_SUCCESS,
        ),
        (
            "Abort",
            ObsState.RESETTING,
            "abort_cmd_ended_cb",
            const.STR_ABORT_SUCCESS,
        ),
        (
            "Abort",
            ObsState.IDLE,
            "abort_cmd_ended_cb",
            const.STR_ABORT_SUCCESS,
        ),
        (
            "Abort",
            ObsState.CONFIGURING,
            "abort_cmd_ended_cb",
            const.STR_ABORT_SUCCESS,
        ),
        (
            "Abort",
            ObsState.READY,
            "abort_cmd_ended_cb",
            const.STR_ABORT_SUCCESS,
        ),
        (
            "Restart",
            ObsState.FAULT,
            "restart_cmd_ended_cb",
            const.STR_RESTART_SUCCESS,
        ),
        (
            "Restart",
            ObsState.ABORTED,
            "restart_cmd_ended_cb",
            const.STR_RESTART_SUCCESS,
        ),
        (
            "ObsReset",
            ObsState.ABORTED,
            "obsreset_cmd_ended_cb",
            const.STR_OBSRESET_SUCCESS,
        ),
        (
            "ObsReset",
            ObsState.FAULT,
            "obsreset_cmd_ended_cb",
            const.STR_OBSRESET_SUCCESS,
        ),
    ],
)
def command_with_correct_obsstate(request):
    cmd_name, obs_state, cmd_callback, activity_msg = request.param
    return cmd_name, obs_state, cmd_callback, activity_msg


def test_command_correct_obsstate(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    command_with_correct_obsstate,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    (
        cmd_name,
        obs_state,
        cmd_callback,
        activity_msg,
    ) = command_with_correct_obsstate
    tango_client_obj.get_attribute.side_effect = Mock(return_value=obs_state)
    device_proxy.command_inout(cmd_name)
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        cmd_name, None, any_method(with_name=cmd_callback)
    )
    assert_activity_message(device_proxy, activity_msg)


@pytest.fixture(
    scope="function",
    params=[
        ("EndScan", ObsState.READY, const.ERR_DEVICE_NOT_IN_SCAN),
        ("GoToIdle", ObsState.IDLE, const.ERR_DEVICE_NOT_READY),
        ("Abort", ObsState.RESOURCING, const.ERR_UNABLE_ABORT_CMD),
        ("Abort", ObsState.EMPTY, const.ERR_UNABLE_ABORT_CMD),
        ("Restart", ObsState.EMPTY, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.RESOURCING, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.IDLE, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.CONFIGURING, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.SCANNING, const.ERR_UNABLE_RESTART_CMD),
        ("Restart", ObsState.READY, const.ERR_UNABLE_RESTART_CMD),
        ("ObsReset", ObsState.EMPTY, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.RESOURCING, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.IDLE, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.CONFIGURING, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.SCANNING, const.ERR_UNABLE_OBSRESET_CMD),
        ("ObsReset", ObsState.READY, const.ERR_UNABLE_OBSRESET_CMD),
        ("ReleaseAllResources", ObsState.EMPTY, const.ERR_DEVICE_NOT_IDLE),
    ],
)
def command_with_incorrect_obsstate(request):
    cmd_name, obs_state, activity_msg = request.param
    return cmd_name, obs_state, activity_msg


def test_command_fails_when_device_in_invalid_obstate(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    command_with_incorrect_obsstate,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    cmd_name, obs_state, activity_msg = command_with_incorrect_obsstate
    tango_client_obj.get_attribute.side_effect = Mock(return_value=obs_state)
    device_proxy.TelescopeOn()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name)
    assert activity_msg in str(df.value)


def test_assign_resources_should_send_csp_subarray_with_correct_receptor_id_list(
    mock_obstate_check, mock_csp_subarray_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.EMPTY
    )
    device_proxy.TelescopeOn()
    device_proxy.AssignResources(assign_input_str)
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_ASSIGN_RESOURCES,
        assign_input_str,
        any_method(with_name="assign_resources_ended"),
    )
    assert_activity_message(device_proxy, const.STR_ASSIGN_RESOURCES_SUCCESS)


def test_assign_command_with_callback_method_with_devfailed_error(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    event_subscription_mock,
    mock_tango_server_helper,
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.EMPTY
    )
    device_proxy.TelescopeOn()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
        dummy_event = command_callback_with_devfailed_exception()
        event_subscription_mock[const.CMD_ASSIGN_RESOURCES](dummy_event)
    assert const.ERR_CALLBACK_CMD_FAILED in str(df.value)


def test_release_resource_should_command_csp_subarray_to_release_all_resources(
    mock_obstate_check, mock_csp_subarray_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.EMPTY
    )
    device_proxy.TelescopeOn()
    device_proxy.AssignResources(assign_input_str)
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.IDLE
    )
    device_proxy.ReleaseAllResources()
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_RELEASE_ALL_RESOURCES,
        None,
        any_method(with_name="releaseallresources_cmd_ended_cb"),
    )
    assert_activity_message(
        device_proxy, const.STR_RELEASE_ALL_RESOURCES_SUCCESS
    )


@pytest.fixture(
    scope="function",
    params=[
        (
            "StartScan",
            scan_input_str,
            ObsState.IDLE,
            const.ERR_DEVICE_NOT_READY,
        ),
        (
            "Configure",
            configure_str,
            ObsState.SCANNING,
            const.ERR_DEVICE_NOT_READY_OR_IDLE,
        ),
        (
            "Configure",
            configure_str,
            ObsState.EMPTY,
            const.ERR_DEVICE_NOT_READY_OR_IDLE,
        ),
        (
            "AssignResources",
            assign_input_str,
            ObsState.READY,
            const.ERR_DEVICE_NOT_EMPTY_OR_IDLE,
        ),
    ],
)
def command_with_argin_should_not_allowed_in_obstate(request):
    cmd_name, input_str, obs_state, error_message = request.param
    return cmd_name, input_str, obs_state, error_message


def test_command_with_argin_should_failed_when_device_is_not_in_required_obstate(
    mock_obstate_check,
    mock_csp_subarray_proxy,
    command_with_argin_should_not_allowed_in_obstate,
    mock_tango_server_helper,
):
    (
        cmd_name,
        input_str,
        obs_state,
        error_message,
    ) = command_with_argin_should_not_allowed_in_obstate
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(return_value=obs_state)
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name, input_str)
    assert error_message in str(df.value)


@pytest.fixture(scope="function")
def mock_obstate_check():
    dut_properties = {"CspSubarrayFQDN": "mid_csp/elt/subarray_01"}
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(dut_properties["CspSubarrayFQDN"])
        with mock.patch.object(
            TangoClient, "get_attribute", Mock(return_value=ObsState.EMPTY)
        ):
            yield tango_client_obj


def test_configure_to_send_correct_configuration_data_when_csp_subarray_is_idle(
    mock_obstate_check, mock_csp_subarray_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    device_proxy.TelescopeOn()
    device_proxy.AssignResources(assign_input_str)
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.READY
    )
    device_proxy.Configure(configure_str)
    argin_json = json.loads(configure_str)
    csp_configuration = argin_json.copy()
    if "pointing" in csp_configuration:
        del csp_configuration["pointing"]
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_CONFIGURE,
        json.dumps(csp_configuration),
        any_method(with_name="configure_cmd_ended_cb"),
    )


def test_configure_should_raise_exception_when_called_invalid_json(
    mock_obstate_check, mock_csp_subarray_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.IDLE
    )
    device_proxy.TelescopeOn()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Configure(invalid_key_str)
    assert const.ERR_INVALID_JSON_CONFIG in str(df.value)


def test_configure_should_raise_assertion_exception_when_called_invalid_obsstate(
    mock_obstate_check, mock_csp_subarray_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.EMPTY
    )
    device_proxy.TelescopeOn()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Configure(configure_str)
    assert const.ERR_DEVICE_NOT_READY_OR_IDLE in str(df.value)


def test_start_scan_should_command_csp_subarray_to_start_its_scan_when_it_is_ready(
    mock_obstate_check, mock_csp_subarray_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.READY
    )
    scan_list = [scan_input_str]
    device_proxy.StartScan(scan_list)
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_STARTSCAN,
        scan_list[0],
        any_method(with_name="startscan_cmd_ended_cb"),
    )


def test_start_scan_should_not_command_csp_subarray_to_start_scan_when_it_is_idle(
    mock_obstate_check, mock_csp_subarray_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.IDLE
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.StartScan(scan_input_str)
    assert const.ERR_DEVICE_NOT_READY in str(df.value)


def test_command_reset_to_set_cspsln_off_when_in_fault(
    mock_obstate_check, mock_csp_subarray_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.EMPTY
    )
    device_proxy.TelescopeOn()
    with pytest.raises(tango.DevFailed):
        device_proxy.AssignResources('"wrong json"')
    device_proxy.Reset()
    assert device_proxy.State() == DevState.OFF


def test_command_reset_should_raise_devfailed_exception_when_not_in_fault_state(
    mock_obstate_check, mock_csp_subarray_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_csp_subarray_proxy[:2]
    tango_client_obj.get_attribute.side_effect = Mock(
        return_value=ObsState.EMPTY
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Reset()
    assert "Command Reset not allowed when the device is in OFF state" in str(
        df.value
    )


def create_dummy_event_state(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    fake_event.device = proxy_mock
    return fake_event


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


def command_callback_with_command_exception():
    # "This function is called when there is exception in command calling."
    return Exception("Exception in command callback")


def raise_devfailed_exception(*args):
    # "This function is called to raise DevFailed exception."
    tango.Except.throw_exception(
        "CspSubarrayLeafNode_CommandFailed",
        const.ERR_DEVFAILED_MSG,
        " ",
        tango.ErrSeverity.ERR,
    )


def test_status():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.Status() != const.STR_CSPSALN_INIT_SUCCESS


def test_read_delay_model():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.delayModel == " "


def test_write_delay_model():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.delayModel = " "
        assert tango_context.device.delayModel == " "


def test_health_state():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


def test_read_activity_message():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert (
            tango_context.device.activityMessage
            == const.STR_CSPSALN_INIT_SUCCESS
        )


def test_write_activity_message():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.activityMessage = "test"
        assert tango_context.device.activityMessage == "test"


def test_logging_level():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_read_version_info():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.versionInfo == " "


def test_logging_targets():
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        tango_context.device.loggingTargets = ["console::cout"]
        assert "console::cout" in tango_context.device.loggingTargets


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(CspSubarrayLeafNode) as tango_context:
        assert tango_context.device.buildState == (
            "{},{},{}".format(
                release.name, release.version, release.description
            )
        )


def any_method(with_name=None):
    class AnyMethod:
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False
            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def assert_activity_message(device_proxy, expected_message):
    assert (
        device_proxy.activityMessage == expected_message
    )  # reads tango attribute


@contextlib.contextmanager
def fake_tango_system(
    device_under_test,
    initial_dut_properties={},
    proxies_to_mock={},
    device_proxy_import_path="tango.DeviceProxy",
):
    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = (
            lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
        )
        patched_module = importlib.reload(
            sys.modules[device_under_test.__module__]
        )

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(
        device_under_test, properties=initial_dut_properties
    )
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()
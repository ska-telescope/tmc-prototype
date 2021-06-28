# Standard Python imports
import contextlib
import importlib
import sys
import types
import pytest
import mock
from mock import Mock, MagicMock
from os.path import dirname, join
import threading
import logging
import json

# Tango imports
import tango
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from subarraynodelow import SubarrayNode, const, release
from ska.base.control_model import HealthState, ObsState
from ska.base.commands import ResultCode
from subarraynodelow.device_data import DeviceData
from tmc.common.tango_client import TangoClient
from ska.base import SKASubarrayStateModel
from subarraynodelow.release_all_resources_command import ReleaseAllResources
from subarraynodelow.configure_command import Configure
from subarraynodelow.scan_command import Scan
from subarraynodelow.end_scan_command import EndScan
from subarraynodelow.end_command import End
from subarraynodelow.obsreset_command import ObsReset
from subarraynodelow.abort_command import Abort
from subarraynodelow.restart_command import Restart
from subarraynodelow.device_data import DeviceData
from tmc.common.tango_server_helper import TangoServerHelper
from subarraynodelow.health_state_aggregator import HealthStateAggregator

assign_input_file = "command_AssignResources.json"
path = join(dirname(__file__), "data", assign_input_file)
with open(path, "r") as f:
    assign_input_str = f.read()

configure_mccs_input_file = "command_mccs_configure.json"
path = join(dirname(__file__), "data", configure_mccs_input_file)
with open(path, "r") as f:
    configure_mccs_str = f.read()

configure_input_file = "command_Configure.json"
path = join(dirname(__file__), "data", configure_input_file)
with open(path, "r") as f:
    configure_str = f.read()

configure_invalid_input_file = "invalid_input_Configure.json"
path = join(dirname(__file__), "data", configure_invalid_input_file)
with open(path, "r") as f:
    invalid_conf_input = f.read()

scan_input_file = "command_Scan.json"
path = join(dirname(__file__), "data", scan_input_file)
with open(path, "r") as f:
    scan_input_str = f.read()

scan_invalid_input_file = "invalid_input_Scan.json"
path = join(dirname(__file__), "data", scan_invalid_input_file)
with open(path, "r") as f:
    invalid_scan_input = f.read()

@pytest.fixture
def subarray_state_model():
    """
    Yields a new SKASubarrayStateModel for testing
    """
    yield SKASubarrayStateModel(logging.getLogger())


@pytest.fixture
def device_data():
    yield DeviceData()


def set_timeout_event(timeout_event):
    timeout_event.set()


def wait_for(tango_context, obs_state_to_change, timeout=10):
    timer_event = threading.Event()
    timer_thread = threading.Timer(timeout, set_timeout_event, timer_event)
    timer_thread.start()

    # wait till timeout or obsState to change
    while (
        not timer_event.isSet() and tango_context.device.obsState != obs_state_to_change
    ):
        print("tango_context.device.obsState: ", tango_context.device.obsState)
        continue

    if timer_event.isSet():
        return "timeout"
    else:
        timer_thread.cancel()
        return True

@pytest.fixture(scope="function")
def mock_tango_server_helper():
    mccs_subarray1_ln_fqdn = "ska_low/tm_leaf_node/mccs_subarray01"
    tango_server_obj = TangoServerHelper.get_instance()
    tango_server_obj.read_property = Mock(return_value = mccs_subarray1_ln_fqdn)
    yield tango_server_obj


@pytest.fixture(scope="function")
def mock_tango_client():
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=MagicMock()
    ) as mock_obj:
        tango_client_obj = TangoClient("ska_low/tm_leaf_node/mccs_subarray01")
        yield tango_client_obj


@pytest.fixture(scope="function")
def mock_lower_devices_proxy(mock_tango_server_helper, mock_tango_client):
    mccs_subarray1_ln_fqdn = "ska_low/tm_leaf_node/mccs_subarray01"
    mccs_subarray1_fqdn = "low-mccs/subarray/01"

    dut_properties = {
        "MccsSubarrayLNFQDN": mccs_subarray1_ln_fqdn,
        "MccsSubarrayFQDN": mccs_subarray1_fqdn,
    }
    tango_client_obj = mock_tango_client
    with fake_tango_system(
        SubarrayNode, initial_dut_properties=dut_properties
    ) as tango_context:
        yield tango_context.device, tango_client_obj


@pytest.fixture(scope="function")
def mock_lower_devices():
    mccs_subarray1_ln_fqdn = "ska_low/tm_leaf_node/mccs_subarray01"
    mccs_subarray1_fqdn = "low-mccs/subarray/01"

    dut_properties = {
        "MccsSubarrayLNFQDN": mccs_subarray1_ln_fqdn,
        "MccsSubarrayFQDN": mccs_subarray1_fqdn,
    }

    mccs_subarray1_ln_proxy_mock = MagicMock()
    mccs_subarray1_proxy_mock = MagicMock()

    proxies_to_mock = {
        mccs_subarray1_ln_fqdn: mccs_subarray1_ln_proxy_mock,
        mccs_subarray1_fqdn: mccs_subarray1_proxy_mock,
    }

    event_subscription_map = {}

    mccs_subarray1_ln_proxy_mock.subscribe_event.side_effect = lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update(
        {attr_name: callback}
    )

    mccs_subarray1_proxy_mock.subscribe_event.side_effect = lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update(
        {attr_name: callback}
    )

    with fake_tango_system(
        SubarrayNode,
        initial_dut_properties=dut_properties,
        proxies_to_mock=proxies_to_mock,
    ) as tango_context:
        yield tango_context, mccs_subarray1_ln_proxy_mock, mccs_subarray1_proxy_mock, mccs_subarray1_ln_fqdn, mccs_subarray1_fqdn, event_subscription_map

def test_scan_id():
    """Test for scanID"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.scanID == ""


def test_read_activity_message(mock_tango_server_helper, mock_tango_client):
    """Test for activityMessage"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.activityMessage == const.STR_SA_INIT_SUCCESS


def test_write_activity_message():
    """Test for activityMessage"""
    with fake_tango_system(SubarrayNode) as tango_context:
        tango_context.device.activityMessage = "test"
        assert tango_context.device.activityMessage == "test"


# Test cases for Commands
def test_on_command_should_change_subarray_device_state_to_on(mock_lower_devices_proxy, mock_tango_server_helper):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    assert device_proxy.On() == [[ResultCode.OK], ["On command completed OK"]]
    assert device_proxy.state() == DevState.ON
    assert device_proxy.obsState == ObsState.EMPTY


def test_off_command_should_change_subarray_device_state_to_off(
    mock_lower_devices_proxy, mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    assert device_proxy.Off() == [[ResultCode.OK], ["Off command completed OK"]]
    assert device_proxy.state() == DevState.OFF
    assert device_proxy.obsState == ObsState.EMPTY


def test_start_scan_should_command_subarray_to_start_scan_when_it_is_ready(
    mock_lower_devices_proxy, mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()
    scan_cmd = Scan(device_data, subarray_state_model)
    assert scan_cmd.do(scan_input_str) == (
        ResultCode.STARTED,
        "Scan command is executed successfully.",
    )


def test_invalid_json_scan_should_command_subarray_to_raise_invalid_json_error(
    mock_lower_devices_proxy
):
    device_proxy, tango_client = mock_lower_devices_proxy
    scan_cmd = Scan(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        scan_cmd.do(invalid_scan_input)
    assert const.ERR_INVALID_JSON in str(df.value)

def test_start_scan_should_raise_devfailed_exception(
    mock_lower_devices_proxy, subarray_state_model, mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()
    tango_client.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    scan_cmd = Scan(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        scan_cmd.do(scan_input_str)
    assert "This is error message for devfailed" in str(df.value)


def test_off_should_raise_devfailed_exception(mock_lower_devices_proxy, mock_tango_server_helper):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    tango_client.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Off()
    assert "This is error message for devfailed" in str(df.value)


def test_end_should_command_subarray_to_end_when_it_is_ready(
    mock_lower_devices_proxy, subarray_state_model, mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    device_data = DeviceData.get_instance()
    end_cmd = End(device_data, subarray_state_model)
    subarray_state_model._straight_to_state(DevState.ON, None, ObsState.READY)
    assert end_cmd.do() == (
        ResultCode.OK,
        "End command invoked successfully on MCCS Subarray Leaf Node.",
    )


def test_end_should_raise_devfailed_exception_when_mccs_subarray_throws_devfailed_exception(
    mock_lower_devices_proxy, subarray_state_model, mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()
    tango_client.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    end_cmd = End(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        end_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_abort_command(device_data, subarray_state_model, mock_lower_devices_proxy, mock_tango_server_helper):
    _, _ = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_data.scan_timer_handler.start_scan_timer(10)
    abort_cmd = Abort(device_data, subarray_state_model)
    assert abort_cmd.do() == (ResultCode.STARTED, const.STR_ABORT_SUCCESS)


def test_abort_raise_devfailed(
    device_data, subarray_state_model, mock_lower_devices_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    device_data.scan_timer_handler.start_scan_timer(10)
    abort_cmd = Abort(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        abort_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_restart_command(device_data, subarray_state_model, mock_lower_devices_proxy):
    restart_cmd = Restart(device_data, subarray_state_model)
    assert restart_cmd.do() == (ResultCode.STARTED, const.STR_RESTART_SUCCESS)


def test_restart_raise_devfailed(device_data, subarray_state_model, mock_lower_devices_proxy):
    device_proxy, tango_client_obj = mock_lower_devices_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    restart_cmd = Restart(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        restart_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_assign_resource_should_raise_exception_when_called_when_device_state_off(mock_tango_server_helper, mock_tango_client):
    with fake_tango_system(SubarrayNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.AssignResources(assign_input_str)
        assert tango_context.device.State() == DevState.OFF
        assert tango_context.device.obsState == ObsState.EMPTY
        assert "Error executing command AssignResources" in str(df.value)


def test_configure_command(subarray_state_model, mock_lower_devices_proxy, mock_tango_server_helper):
    device_proxy, tango_client = mock_lower_devices_proxy
    device_data = DeviceData.get_instance()
    tango_server_obj = mock_tango_server_helper
    configure_cmd = Configure(device_data, subarray_state_model)
    subarray_state_model._straight_to_state(DevState.ON, None, ObsState.IDLE)
    assert configure_cmd.do(configure_str) == (
        ResultCode.STARTED,
        "Configure command invoked",
    )


def test_configure_command_subarray_with_invalid_configure_input(
    subarray_state_model, mock_lower_devices_proxy
):
    device_proxy, tango_client = mock_lower_devices_proxy
    device_data = DeviceData.get_instance()
    configure_cmd = Configure(device_data, subarray_state_model)
    subarray_state_model._straight_to_state(DevState.ON, None, ObsState.IDLE)
    with pytest.raises(tango.DevFailed) as df:
        configure_cmd.do(invalid_conf_input)
    assert const.ERR_INVALID_JSON in str(df.value)


def test_end_scan_should_command_subarray_to_end_scan_when_it_is_scanning(
    mock_lower_devices_proxy, subarray_state_model, mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()
    end_scan_cmd = EndScan(device_data, subarray_state_model)
    subarray_state_model._straight_to_state(DevState.ON, None, ObsState.SCANNING)
    device_data.scan_timer_handler.start_scan_timer(10)
    assert end_scan_cmd.do() == (
        ResultCode.OK,
        "EndScan command is executed successfully.",
    )


def test_end_scan_should_raise_devfailed_exception_when_mccs_subbarray_ln_throws_devfailed_exception(
    mock_lower_devices_proxy, subarray_state_model, mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()
    tango_client.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    end_scan_cmd = EndScan(device_data, subarray_state_model)
    device_data.scan_timer_handler.start_scan_timer(10)
    with pytest.raises(tango.DevFailed) as df:
        end_scan_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_obsreset_command(mock_lower_devices_proxy, subarray_state_model, mock_tango_server_helper):
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()
    obsreset_cmd = ObsReset(device_data, subarray_state_model)
    assert obsreset_cmd.do() == (ResultCode.STARTED, const.STR_OBSRESET_SUCCESS)


def test_obsreset_raise_devfailed(mock_lower_devices_proxy, subarray_state_model, mock_tango_server_helper):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()
    tango_client.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    obsreset_cmd = ObsReset(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        obsreset_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


# Test case for health state
def test_health_state():
    """Test for healthState"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


@pytest.fixture(
    scope="function",
    params=[
        HealthState.OK,
        # HealthState.DEGRADED,
        # HealthState.UNKNOWN,
        # HealthState.FAILED,
    ],
)
def health_state(request):
    health_state = request.param
    return health_state


# Test case for HealthState callback
def test_subarray_health_state_changes_as_per_mccs_subarray_ln_healthstate(
    mock_tango_server_helper, mock_tango_client, health_state
):
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()

    mccs_subarray1_ln_fqdn = "ska_low/tm_leaf_node/mccs_subarray01"
    dut_properties = {
        "MccsSubarrayLNFQDN": mccs_subarray1_ln_fqdn,
    }
    device_data = DeviceData.get_instance()
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ) as mock_obj:
        with mock.patch.object(
            TangoClient, "subscribe_attribute", side_effect=dummy_subscriber
        ):
            with fake_tango_system(
                SubarrayNode, initial_dut_properties=dut_properties
            ) as tango_context:
                tango_context.device.On()
    assert device_data._subarray_health_state == health_state


def dummy_subscriber(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"ska_mid/tm_leaf_node/mccs_subarray01/{attribute}"
    fake_event.attr_value.value = HealthState.OK
    print(fake_event.attr_value.value)
    callback_method(fake_event)
    return 10


@pytest.fixture(scope="function")
def error_in_health_state():
    device = "ska_mid/tm_leaf_node/mccs_subarray01"
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ) as mock_obj:
        with mock.patch.object(
            TangoClient,
            "subscribe_attribute",
            side_effect=create_dummy_event_healthstate_with_error,
        ) as obj:
            error_health_state = TangoClient(device)
            yield error_health_state, device



def test_subarray_health_state_with_error_event(error_in_health_state, mock_lower_devices_proxy, mock_tango_server_helper):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper

    error_health_state, device = error_in_health_state
    health_state_aggr = HealthStateAggregator()
    assert device not in health_state_aggr.subarray_ln_health_state_map.keys()


# Test case for assigned_resources_cb callback
@pytest.mark.xfail(reason="Need to update the implementation")
def test_subarray_assigned_resources_attr_changes_as_per_mccs_subarray_ln_assigned_resources_attr(
    mock_lower_devices_proxy, mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ) as mock_obj:
        with mock.patch.object(
            TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_mccs
        ):
            device_proxy.On()
            device_proxy.AssignResources(assign_input_str)
    test1 = {
    "interface": "https://schema.skao.int/ska-low-tmc-assignresources/2.0",
    "subarray_beam_ids": [1],
    "station_ids": [[1,2]],
    "channel_blocks": [3]
    }
    result = json.dumps(test1)
    assert device_data.assignd_resources_by_mccs == result


def dummy_subscriber_mccs(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"ska_mid/tm_leaf_node/mccs_subarray01/{attribute}"
    test1 = {
    "interface": "https://schema.skao.int/ska-low-tmc-assignresources/2.0",
    "subarray_beam_ids": [1],
    "station_ids": [[1,2]],
    "channel_blocks": [3]
    }
    result = json.dumps(test1)
    fake_event.attr_value.value = result
    print(fake_event.attr_value.value)
    callback_method(fake_event)
    return 10


@pytest.mark.xfail(reason="Need to update the implementation")
def test_subarray_assigned_resources_attr_callback_with_error_event(mock_lower_devices_proxy, mock_tango_server_helper):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_data = DeviceData.get_instance()
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ) as mock_obj:
        with mock.patch.object(
            TangoClient,
            "subscribe_attribute",
            side_effect=create_dummy_event_assign_resource_attr_with_error,
        ):
            device_proxy.On()
            device_proxy.AssignResources(assign_input_str)
    assert const.ERR_SUBSR_MCCSSA_ASSIGNED_RES_ATTR in device_proxy.activityMessage


def test_assign_resources_should_assign_resources_when_device_state_on(
    mock_lower_devices_proxy, mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    assert device_proxy.AssignResources(assign_input_str) == [
        [ResultCode.STARTED],
        ["AssignResources command executionSTARTED"],
    ]
    assert device_proxy.obsState == ObsState.RESOURCING


def test_release_all_resources_should_release_resources_when_obstate_idle(
    mock_lower_devices_proxy,
    subarray_state_model,
    mock_tango_server_helper
):
    device_proxy, tango_client = mock_lower_devices_proxy
    tango_server_obj = mock_tango_server_helper
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    device_data = DeviceData.get_instance()
    release_resources_cmd = ReleaseAllResources(device_data, subarray_state_model)
    assert release_resources_cmd.do() == (
        ResultCode.STARTED,
        "RELEASEALLRESOURCES command invoked successfully.",
    )


def create_dummy_event_healthstate_with_proxy(proxy_mock, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"ska_mid/tm_leaf_node/mccs_subarray01/{attribute}"
    fake_event.attr_value.value = HealthState.FAILED
    fake_event.device = proxy_mock
    return fake_event


def create_dummy_event_healthstate_with_error(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = True
    fake_event.attr_name = f"ska_mid/tm_leaf_node/mccs_subarray01/{attribute}"
    fake_event.attr_value.value = HealthState.OK
    callback_method(fake_event)
    return 10

def create_dummy_event_assign_resource_attr_with_error(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = True
    fake_event.attr_name = f"ska_mid/tm_leaf_node/mccs_subarray01/{attribute}"
    fake_event.attr_value.value = {"dummy_interface": "https://schema.skao.int/ska-low-tmc-assignresources/2.0",
    "subarray_beam_ids": [1],
    "station_ids": [[1,2]],
    "channel_blocks": [3]
    }
    callback_method(fake_event)
    return 10

def any_method(with_name=None):
    class AnyMethod:
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def create_dummy_event_state(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    fake_event.device = proxy_mock
    return fake_event


def create_dummy_event_state_with_error(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = "Invalid Value"
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    fake_event.device = proxy_mock
    return fake_event


def create_dummy_event_custom_exception(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = "Custom Exception"
    fake_event.attr_name = "{device_fqdn}/{attribute}"
    fake_event.attr_value = (
        "Subarray is not in IDLE obsState, please check the subarray obsState"
    )
    fake_event.device = proxy_mock
    return fake_event


# Throw Devfailed exception for command with argument
def raise_devfailed_exception(*args):
    tango.Except.throw_exception(
        "SubarrayNode_Commandfailed",
        "This is error message for devfailed",
        " ",
        tango.ErrSeverity.ERR,
    )


def raise_devfailed_for_event_subscription(
    evt_name, evt_type, callaback, stateless=True
):
    tango.Except.throw_exception(
        "SubarrayNode_CommandCallbackfailed",
        "This is error message for devfailed in event subscription",
        "From function test devfailed",
        tango.ErrSeverity.ERR,
    )


def raise_devfailed_scan_command(cmd_name, input_arg):
    if cmd_name == "Scan":
        tango.Except.throw_exception(
            "SubarrayNode_Commandfailed",
            "Failed to invoke Scan command on subarraynode.",
            cmd_name,
            tango.ErrSeverity.ERR,
        )


def raise_devfailed_end_command(cmd_name, input_arg):
    if cmd_name == "End":
        tango.Except.throw_exception(
            "SubarrayNode_Commandfailed",
            "Failed to invoke End command on subarraynode.",
            cmd_name,
            tango.ErrSeverity.ERR,
        )


def raise_devfailed_endscan_command(cmd_name, input_arg):
    if cmd_name == "EndScan":
        tango.Except.throw_exception(
            "SubarrayNode_Commandfailed",
            "Failed to invoke EndScan command on subarraynode.",
            cmd_name,
            tango.ErrSeverity.ERR,
        )


def command_callback_with_command_exception():
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = Exception("Exception in callback")
    return fake_event


def command_callback_with_devfailed_exception():
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = tango.Except.throw_exception(
        "TestDevfailed",
        "This is error message for devfailed",
        "From function test devfailed",
        tango.ErrSeverity.ERR,
    )
    return fake_event


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
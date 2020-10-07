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
from datetime import datetime, timedelta
import pytz

# Tango imports
from tango.test_context import DeviceTestContext

# Additional import
from mccssubarrayleafnode import MccsSubarrayLeafNode, const, release
from ska.base.control_model import HealthState, ObsState, LoggingLevel

@pytest.fixture(scope="function")
def tango_context():
    with fake_tango_system(MccsSubarrayLeafNode) as tango_context:
        yield tango_context

configure_input_file = 'command_Configure.json'
path = join(dirname(__file__), 'data', configure_input_file)
with open(path, 'r') as f:
    configure_str = f.read()

invalid_json_file = 'invalid_json.json'
path = join(dirname(__file__), 'data', invalid_json_file)
with open(path, 'r') as f:
    invalid_json_str = f.read()

scan_input_file= 'command_Scan.json'
path= join(dirname(__file__), 'data', scan_input_file)
with open(path, 'r') as f:
    scan_input_str=f.read()


@pytest.fixture(scope="function")
def event_subscription(mock_mccs_subarray):
    event_subscription_map = {}
    mock_mccs_subarray[1].command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map

@pytest.fixture(scope="function")
def event_subscription_without_arg(mock_mccs_subarray):
    event_subscription_map = {}
    mock_mccs_subarray[1].command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map

@pytest.fixture(scope="function")
def mock_mccs_subarray():
    mccs_subarray1_fqdn = 'low-mccs/subarray/01'
    dut_properties = {
        'MccsSubarrayFQDN': mccs_subarray1_fqdn
    }
    mccs_subarray1_proxy_mock = Mock()
    proxies_to_mock = {
        mccs_subarray1_fqdn: mccs_subarray1_proxy_mock
    }
    with fake_tango_system(MccsSubarrayLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, mccs_subarray1_proxy_mock


def test_configure_command_when_obstate_is_idle_with_callback_method(mock_mccs_subarray, event_subscription):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.Configure(configure_str)
    dummy_event = command_callback(const.CMD_CONFIGURE)
    event_subscription[const.CMD_CONFIGURE](dummy_event)
    assert const.STR_COMMAND + const.CMD_CONFIGURE in device_proxy.activityMessage

def test_configure_command_when_obstate_is_ready_with_callback_method(mock_mccs_subarray, event_subscription):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.Configure(configure_str)
    dummy_event = command_callback(const.CMD_CONFIGURE)
    event_subscription[const.CMD_CONFIGURE](dummy_event)
    assert const.STR_COMMAND + const.CMD_CONFIGURE in device_proxy.activityMessage


@pytest.mark.xfail
def test_configure_with_correct_configuration_data_when_mccs_subarray_is_idle(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.IDLE
    device_proxy.Configure(configure_str)

    sky_coordinates = []
    station_ids = []
    argin_json = json.loads(configure_str)
    station_beam_pointings = argin_json["station_beam_pointings"][0]
    azimuth_coord = station_beam_pointings["target"]["Az"]
    elevation_coord = station_beam_pointings["target"]["El"]

    # Append current timestamp into sky_coordinates set
    time_t0 = datetime.today() + timedelta(seconds=0)
    time_t0_utc = (time_t0.astimezone(pytz.UTC)).timestamp()
    sky_coordinates.append(time_t0_utc)

    # Append Azimuth and Azimuth_rate into sky_coordinates set
    sky_coordinates.append(azimuth_coord)
    sky_coordinates.append(0.0)

    # Append Elevation and Elevation_rate into sky_coordinates set
    sky_coordinates.append(elevation_coord)
    sky_coordinates.append(0.0)

    # Add in sky_coordinates set in station_beam_pointings
    station_beam_pointings["sky_coordinates"] = sky_coordinates
    # Add station_id in station_beam_pointings
    for station in argin_json["stations"]:
        station_ids.append(station["station_id"])
    station_beam_pointings["station_id"] = station_ids

    # Remove target block from station_beam_pointings
    station_beam_pointings.pop("target", None)

    argin_json["station_beam_pointings"][0] = station_beam_pointings
    argin_json["station_beams"] = argin_json["station_beam_pointings"]
    argin_json.pop("station_beam_pointings", None)
    
    mccs_subarray1_proxy_mock.command_inout_asynch.assert_any_call(const.CMD_CONFIGURE,
                                json.dumps(argin_json), any_method(with_name='configure_cmd_ended_cb'))


def test_configure_should_failed_when_device_obsstate_is_empty(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.EMPTY
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Configure(configure_str)
    assert "Unable to invoke Configure command" in str(df)


@pytest.fixture(
    scope="function",
    params=[
        ("End", const.CMD_END, ObsState.READY),
        ("EndScan", const.CMD_ENDSCAN, ObsState.SCANNING)
    ])
def command_event_error_without_arg(request):
    cmd_name, requested_cmd, ObsState = request.param
    return cmd_name, requested_cmd, ObsState


def test_command_with_callback_method_with_event_error(mock_mccs_subarray,event_subscription_without_arg, command_event_error_without_arg):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    cmd_name, requested_cmd, ObsState = command_event_error_without_arg
    mccs_subarray1_proxy_mock.obsState = ObsState
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription_without_arg[requested_cmd](dummy_event)
    assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage


@pytest.fixture(
    scope="function",
    params=[
        ("Configure", const.CMD_CONFIGURE, ObsState.IDLE),
        ("Scan", const.CMD_SCAN, ObsState.READY)
    ])
def command_event_error_with_arg(request):
    cmd_name, requested_cmd, ObsState = request.param
    return cmd_name, requested_cmd, ObsState


def test_command_with_callback_method_with_event_error_with_arg(mock_mccs_subarray,event_subscription, command_event_error_with_arg):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    cmd_name, requested_cmd, ObsState = command_event_error_with_arg
    mccs_subarray1_proxy_mock.obsState = ObsState
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription[requested_cmd](dummy_event)
    assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage


# def test_configure_command_with_callback_method_with_event_error(mock_mccs_subarray, event_subscription ):
#     device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
#     device_proxy.On()
#     mccs_subarray1_proxy_mock.obsState = ObsState.IDLE
#     device_proxy.Configure(configure_str)
#     dummy_event = command_callback_with_event_error(const.CMD_CONFIGURE)
#     event_subscription[const.CMD_CONFIGURE](dummy_event)
#     assert const.ERR_INVOKING_CMD + const.CMD_CONFIGURE in device_proxy.activityMessage


def test_configure_to_raise_devfailed_exception(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.IDLE
    mccs_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_with_arg
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Configure(configure_str)
    assert const.ERR_DEVFAILED_MSG in str(df.value)


def test_read_activity_message(tango_context):
    # test case for method read_activityMessage
    tango_context.device.activityMessage = 'test'
    assert tango_context.device.activityMessage == 'test'


def test_write_activity_message(tango_context):
    #test case for method write_activityMessage
    tango_context.device.activityMessage = 'test'
    assert tango_context.device.activityMessage == 'test'


def create_dummy_event_state(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    fake_event.device = proxy_mock
    return fake_event
def test_scan_should_command_mccs_subarray_to_start_its_scan_when_it_is_ready(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.Scan(scan_input_str)
    assert const.STR_SCAN_SUCCESS in device_proxy.activityMessage


def test_scan_command_with_callback_method(mock_mccs_subarray , event_subscription):
    # arrange:
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.Scan(scan_input_str)
    dummy_event = command_callback(const.CMD_SCAN)
    event_subscription[const.CMD_SCAN](dummy_event)
    assert const.STR_COMMAND + const.CMD_SCAN in device_proxy.activityMessage


# def test_scan_command_with_callback_method_with_event_error(mock_mccs_subarray, event_subscription ):
#     # arrange:
#     device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
#     mccs_subarray1_proxy_mock.obsState = ObsState.READY
#     device_proxy.Scan(scan_input_str)
#     dummy_event = command_callback_with_event_error(const.CMD_SCAN)
#     event_subscription[const.CMD_SCAN](dummy_event)
#     assert const.ERR_INVOKING_CMD + const.CMD_SCAN in device_proxy.activityMessage


def test_scan_should_not_command_mccs_subarray_to_start_scan_when_it_is_idle(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.IDLE
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Scan(scan_input_str)
    assert const.ERR_DEVICE_NOT_READY in str(df)


def test_Scan_should_raise_devfailed_exception(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    mccs_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Scan(scan_input_str)
    assert "raise_devfailed_exception" in str(df)


def test_end_command_with_callback_method(mock_mccs_subarray, event_subscription_without_arg):
    # arrange:
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.End()
    dummy_event = command_callback(const.CMD_END)
    event_subscription_without_arg[const.CMD_END](dummy_event)
    assert const.STR_COMMAND + const.CMD_END in device_proxy.activityMessage


# def test_end_command_with_callback_method_with_event_error(mock_mccs_subarray,event_subscription_without_arg):
#     device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
#     mccs_subarray1_proxy_mock.obsState = ObsState.READY
#     device_proxy.End()
#     dummy_event = command_callback_with_event_error(const.CMD_END)
#     event_subscription_without_arg[const.CMD_END](dummy_event)
#     assert const.ERR_INVOKING_CMD + const.CMD_END in device_proxy.activityMessage


def test_end_should_command_mccs_subarray_to_end_when_it_is_ready(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    device_proxy.End()
    mccs_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_END,
                                                                any_method(with_name='end_cmd_ended_cb'))


def test_end_should_raise_devfailed_exception(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.READY
    mccs_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.End()
    assert const.ERR_END_INVOKING_CMD in str(df)


def test_end_should_command_mccs_subarray_should_not_end_when_it_is_not_idle_or_ready(mock_mccs_subarray):
    device_proxy = mock_mccs_subarray[0]
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.End()
    assert const.ERR_DEVICE_NOT_READY in str(df)


def test_endscan_should_command_mccs_subarray_to_end_scan_when_it_is_scanning(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.EndScan()
    mccs_subarray1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ENDSCAN,
                                                                any_method(with_name='endscan_cmd_ended_cb'))


def test_endscan_command_with_callback_method(mock_mccs_subarray , event_subscription_without_arg):
    # arrange:
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.SCANNING
    device_proxy.EndScan()
    dummy_event = command_callback(const.CMD_ENDSCAN)
    event_subscription_without_arg[const.CMD_ENDSCAN](dummy_event)
    assert const.STR_COMMAND + const.CMD_ENDSCAN in device_proxy.activityMessage


def test_endscan_should_raise_devfailed_exception(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.SCANNING
    mccs_subarray1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception_with_arg
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.EndScan()
    assert const.ERR_ENDSCAN_COMMAND in str(df)


# def test_endscan_command_with_callback_method_with_event_error(mock_mccs_subarray, event_subscription_without_arg):
#     device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
#     mccs_subarray1_proxy_mock.obsState = ObsState.SCANNING
#     device_proxy.EndScan()
#     dummy_event = command_callback_with_event_error(const.CMD_ENDSCAN)
#     event_subscription_without_arg[const.CMD_ENDSCAN](dummy_event)
#     assert const.ERR_INVOKING_CMD + const.CMD_ENDSCAN in device_proxy.activityMessage


def test_end_scan_should_not_command_mccs_subarray_to_end_scan_when_it_is_idle(mock_mccs_subarray):
    device_proxy, mccs_subarray1_proxy_mock = mock_mccs_subarray
    mccs_subarray1_proxy_mock.obsState = ObsState.IDLE
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.EndScan()
    assert const.ERR_DEVICE_NOT_SCANNING in str(df)


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False
            return other.__func__.__name__ == with_name if with_name else True
    return AnyMethod()


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

def command_callback_with_devfailed_exception():
    # "This function is called when command is failed with DevFailed exception."
    tango.Except.throw_exception(const.ERR_DEVFAILED_MSG,
                                 const.ERR_CALLBACK_CMD_FAILED, " ", tango.ErrSeverity.ERR)


def raise_devfailed_with_arg(cmd_name, input_arg1, input_arg2):
    # "This function is called to raise DevFailed exception with arguments."
    tango.Except.throw_exception(const.STR_CMD_FAILED, const.ERR_DEVFAILED_MSG,
                                 cmd_name, tango.ErrSeverity.ERR)

def command_callback_with_command_exception():
    # "This function is called when there is exception in command calling."
    return Exception("Exception in command callback")


def raise_devfailed_exception(cmd_name, inp_str):
    # "This function is called to raise DevFailed exception."
    tango.Except.throw_exception("CspSubarrayLeafNode_CommandFailed", const.ERR_DEVFAILED_MSG,
                                 " ", tango.ErrSeverity.ERR)


def raise_devfailed_exception_with_arg(cmd_name, input_str):
    tango.Except.throw_exception("MccsSubarrayLeafNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)


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

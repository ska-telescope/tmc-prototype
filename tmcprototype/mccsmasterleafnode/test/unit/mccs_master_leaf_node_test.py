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
from tango.test_context import DeviceTestContext

# Additional import
from mccsmasterleafnode import MccsMasterLeafNode, const, release
from ska.base.control_model import HealthState, ObsState, LoggingLevel

assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()


assign_invalid_key_file = 'invalid_key_AssignResources.json'
path = join(dirname(__file__), 'data', assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key = f.read()


@pytest.fixture(scope="function")
def event_subscription(mock_mccs_master):
    event_subscription_map = {}
    mock_mccs_master[1].command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def mock_mccs_master():
    mccs_master_fqdn = 'low_mccs/elt/master'
    dut_properties = {
        'MccsmasterFQDN': mccs_master_fqdn
    }
    mccs_master_proxy_mock = Mock()
    proxies_to_mock = {
        mccs_master_fqdn: mccs_master_proxy_mock
    }
    with fake_tango_system(MccsMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, mccs_master_proxy_mock

    def test_assign_resources_should_raise_devfailed_exception(mock_mccs_master):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.EMPTY
        mccs_master_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_with_arg
        device_proxy.On()
        with pytest.raises(tango.DevFailed) as df:
            device_proxy.AssignResource(assign_input_str)
        assert const.ERR_DEVFAILED_MSG in str(df.value)
    
    def test_assign_command_with_callback_method(mock_mccs_master, event_subscription):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.EMPTY
        device_proxy.On()
        device_proxy.AssignResource(assign_input_str)
        dummy_event = command_callback(const.CMD_ALLOCATE)
        event_subscription[const.CMD_ALLOCATE](dummy_event)
        assert const.STR_INVOKE_SUCCESS in device_proxy.activityMessage

    def test_assign_command_with_callback_method_with_event_error(mock_mccs_master, event_subscription):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.EMPTY
        device_proxy.On()
        device_proxy.AssignResource(assign_input_str)
        dummy_event = command_callback_with_event_error(const.CMD_ALLOCATE)
        event_subscription[const.CMD_ALLOCATE](dummy_event)
        assert const.ERR_INVOKING_CMD + const.CMD_ALLOCATE in device_proxy.activityMessage
    
    def test_assign_command_with_callback_method_with_devfailed_error(mock_mccs_master, event_subscription):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.EMPTY
        device_proxy.On()
        with pytest.raises(tango.DevFailed) as df:
            device_proxy.AssignResources(assign_input_str)
            dummy_event = command_callback_with_devfailed_exception()
            event_subscription[const.CMD_ALLOCATE](dummy_event)
        assert const.ERR_CALLBACK_CMD_FAILED in str(df.value)
    
    def test_allocate_ended_should_raise_dev_failed_exception_for_invalid_obs_state(mock_mccs_master, event_subscription):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.READY
        with pytest.raises(tango.DevFailed) as df:
            device_proxy.AssignResources(json.dumps(assign_input_file))
        assert const.ERR_RAISED_EXCEPTION in str(df.value)

    def test_assign_resource_should_raise_exception_when_key_not_found():
        with fake_tango_system(MccsMasterLeafNode) as tango_context:
            with pytest.raises(tango.DevFailed) as df:
                tango_context.device.AssignResources(assign_invalid_key)
            assert const.ERR_RAISED_EXCEPTION in str(df)

    def raise_devfailed_with_arg(cmd_name, input_arg1, input_arg2):
        # "This function is called to raise DevFailed exception with arguments."
        tango.Except.throw_exception(const.STR_CMD_FAILED, const.ERR_DEVFAILED_MSG,
                                    cmd_name, tango.ErrSeverity.ERR)


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

    
    def any_method(with_name=None):
        class AnyMethod():
            def __eq__(self, other):
                if not isinstance(other, types.MethodType):
                    return False
                return other.__func__.__name__ == with_name if with_name else True
        return AnyMethod()


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


 

# Main execution
if __name__ == "__main__":
    main()

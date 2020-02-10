import contextlib
import importlib
import sys
import mock
import pytest
from mock import Mock

from CONST import HealthState, CMD_SET_STOW_MODE
from CentralNode import CentralNode
from tango.test_context import DeviceTestContext


@pytest.mark.skip
def test_telescope_health_state_is_degraded_when_csp_master_leaf_node_is_degraded_after_start():
    # arrange:
    device_under_test = CentralNode
    csp_master_fqdn = 'mid/csp_elt/master'
    csp_master_health_attribute = 'cspHealthState'
    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_fqdn
    }

    event_subscription_map = {}

    csp_master_device_proxy_mock = Mock()
    csp_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_fqdn: csp_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event(csp_master_fqdn)
        event_subscription_map[csp_master_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.DEGRADED


def test_stow_antennas_should_set_stow_mode_on_leaf_nodes():
    # arrange:
    device_under_test = CentralNode()
    initial_dut_properties = {
        'DishLeafNodePrefix': "ska_mid/tm_leaf_node/d"
    }
    leaf_node_device_name = "0001"

    leaf_node_device_proxy_mock = Mock()
    proxies_to_mock = {
        f"{initial_dut_properties['DishLeafNodePrefix']}{leaf_node_device_name}": leaf_node_device_proxy_mock
    }

    # act:
    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock):
        device_under_test.StowAntennas(argin=[leaf_node_device_name])
    
    # assert:
    leaf_node_device_proxy_mock.command_inout.assert_called_with(CMD_SET_STOW_MODE)


def create_dummy_event(csp_master_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.DEGRADED
    return fake_event


@contextlib.contextmanager
def fake_tango_system(device_under_test, initial_dut_properties={}, proxies_to_mock={},
                      device_proxy_import_path='tango.DeviceProxy'):

    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    if type(device_under_test) is not type:
        dut_pyclass = device_under_test.__class__
    device_under_test = getattr(patched_module, dut_pyclass.__name__)

    device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()


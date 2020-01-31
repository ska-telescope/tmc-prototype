import collections
import importlib
import sys
from unittest import mock
from unittest.mock import MagicMock, Mock

import pytest
import tango
from CONST import ENUM_DEGRADED
from tango.test_context import DeviceTestContext


@pytest.mark.parametrize(
    'subdevice_fqdn_prop_name,subdevice_fqdn_prop_value,subdevice_health_state_attribute,subdevice_health_state_value,expected_telescope_health_state',
    [
        ('CspMasterLeafNodeFQDN', 'mid/csp_elt/master', 'cspHealthState', ENUM_DEGRADED, ENUM_DEGRADED)
    ]
)
def test_telescope_health_state_is_degraded_when_any_subdevice_is_degraded_after_start(subdevice_fqdn_prop_name,
                                                                                       subdevice_fqdn_prop_value,
                                                                                       subdevice_health_state_attribute,
                                                                                       subdevice_health_state_value,
                                                                                       expected_telescope_health_state):
    # arrange:
    device_under_test = importlib.import_module("CentralNode", "tmcprototype").CentralNode
    initial_dut_properties = {
        subdevice_fqdn_prop_name: subdevice_fqdn_prop_value
    }

    device_proxy_mock = Mock()
    event_system = _prepare_event_system(device_proxy_mock, subdevice_health_state_attribute)

    tango_context = fake_tango_system(device_under_test, device_proxy_mock, initial_dut_properties)

    tango_context.start()

    # act:
    event_system.trigger(subdevice_health_state_attribute, f"{subdevice_fqdn_prop_value}/healthState",
                         subdevice_health_state_value, device_proxy_mock)

    # assert:
    assert tango_context.device.telescopeHealthState == expected_telescope_health_state
    tango_context.stop()


def fake_tango_system(device_under_test, dependent_device_proxy_mock, initial_dut_properties={},
                      device_proxy_import_path='tango.DeviceProxy'):

    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.return_value = dependent_device_proxy_mock
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)

    return DeviceTestContext(device_under_test, properties=initial_dut_properties)


def _prepare_event_system(mocked_device_proxy, attribute_to_mock):
    events = {
        attribute_to_mock: None,
    }

    def fake_subscribe_event(attribute_name, event_type, callback_fn, *args, **kwargs):
        events[attribute_name] = callback_fn

    mocked_device_proxy.subscribe_event.side_effect = fake_subscribe_event

    FakeEventSystem = collections.namedtuple('FakeEventSystem', ['events', 'trigger'])

    def trigger(attribute_name, attr_fqdn, attr_value, device_obj=MagicMock(), error=False):
        event = MagicMock(spec=tango.EventData)
        event.device = device_obj
        event.attr_value.value = attr_value
        event.attr_name = attr_fqdn
        event.err = error

        events[attribute_name](event)

    return FakeEventSystem(events, trigger)

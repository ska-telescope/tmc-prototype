import importlib
import tango
import pytest
import collections

from unittest import mock
from unittest.mock import MagicMock, Mock

from tango.test_context import DeviceTestContext
from tango import DevFailed


@pytest.mark.parametrize(
    'subdevice_fqdn_prop_name,subdevice_fqdn_prop_value,subdevice_health_state_attribute,subdevice_health_state_value,expected_telescope_health_state', [
        ('CspMasterLeafNodeFQDN', 'mid/csp_elt/master','cspHealthState',1, 1)
    ]
)
def test_telescope_health_state_is_degraded_when_any_subdevice_is_degraded_after_start(subdevice_fqdn_prop_name, subdevice_fqdn_prop_value, subdevice_health_state_attribute, subdevice_health_state_value, expected_telescope_health_state):
    # arrange:
    device_proxy_mock = Mock()
    event_system = _prepare_event_system(device_proxy_mock, subdevice_health_state_attribute)
    
    with mock.patch('tango.DeviceProxy') as patched_constructor:
        patched_constructor.return_value = device_proxy_mock
        klass = importlib.import_module("CentralNode", "tmcprototype").CentralNode

    tango_context = DeviceTestContext(klass, properties={
        subdevice_fqdn_prop_name: subdevice_fqdn_prop_value
    })
    
    tango_context.start()

    # act:
    event_system.trigger(subdevice_health_state_attribute, f"{subdevice_fqdn_prop_value}/healthState", subdevice_health_state_value, device_proxy_mock)

    # assert:
    assert tango_context.device.telescopeHealthState == expected_telescope_health_state
    tango_context.stop()


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


import importlib
import tango
import pytest

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
    events = {
            subdevice_health_state_attribute: None,
    }

    def subscribe_event(attribute_name, event_type, callback_fn, *args, **kwargs):
        events[attribute_name] = callback_fn
    
    with mock.patch('tango.DeviceProxy') as patched_constructor:
        device_proxy_mock = Mock()
        device_proxy_mock.subscribe_event.side_effect = subscribe_event

        patched_constructor.return_value = device_proxy_mock
        klass = importlib.import_module("CentralNode", "tmcprototype").CentralNode

    tango_context = DeviceTestContext(klass, properties={
        subdevice_fqdn_prop_name: subdevice_fqdn_prop_value
    })
    
    tango_context.start()

    # act:
    # simulated event
    event = MagicMock(spec=tango.EventData)
    event.err = False
    event.attr_value = Mock()
    event.attr_value.value = subdevice_health_state_value
    event.attr_name = subdevice_fqdn_prop_value + '/healthState'
    event.device = device_proxy_mock

    events[subdevice_health_state_attribute](event)

    # assert:
    assert tango_context.device.telescopeHealthState == expected_telescope_health_state


    # assert:
    assert tango_context.device.telescopeHealthState == 1

import importlib
import tango

from unittest import mock
from unittest.mock import MagicMock, Mock

from tango.test_context import DeviceTestContext
from tango import DevFailed


def test_telescope_health_state_is_degraded_when_csp_master_is_degraded_after_start():
    # arrange:
    events = {
            "cspHealthState": None,
    }

    def subscribe_event(attribute_name, event_type, callback_fn, *args, **kwargs):
        events[attribute_name] = callback_fn
    

    with mock.patch('tango.DeviceProxy') as patched_constructor:
        device_proxy_mock = Mock()
        device_proxy_mock.subscribe_event.side_effect = subscribe_event

        patched_constructor.return_value = device_proxy_mock
        klass = importlib.import_module("CentralNode", "tmcprototype").CentralNode

    degraded_device = "telescope/csp/master"
    tango_context = DeviceTestContext(klass, 
            properties={"CspMasterLeafNodeFQDN": degraded_device})

    tango_context.start()

    # act:
    # simulated event
    event = mock.MagicMock(spec=tango.EventData)
    event.err = False
    event.attr_value = Mock()
    event.attr_value.value = 1
    event.attr_name = degraded_device + "/healthState"
    event.device = device_proxy_mock

    events["cspHealthState"](event)


    # assert:
    assert tango_context.device.telescopeHealthState == 1

from tango.server import Device, device_property, is_tango_object
from tango.server import attribute as tango_attribute

from CentralNode.CentralNode import CentralNode


class RootDevice(Device):
    BaseDeviceProperty = device_property(
        dtype='str',
        doc="A base device property that should be inherited.",
    )

    baseTangoAttribute = tango_attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
        doc="An Enum Type Tango Attribute",
    )

    def read_baseTangoAttribute(self):
        return self._base_tango_attribute


class LeafDevice(RootDevice):
    LeafDeviceProperty = device_property(
        dtype='str',
        doc="A leaf device property"
    )

    telescopeHealthState = tango_attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
        doc="An Enum Type Tango Attribute",
    )

    def read_telescopeHealthState(self):
        return self._telescope_health_state


class PyTangoParsel():
    def __init__(self, pytango_device):
        self._device = pytango_device

    def extract_tango_properties(self):
        return [o for o in self._device.__dict__.values() if is_tango_object(o)
                and isinstance(o, device_property)]

    def extract_tango_attributes(self):
        return [o for o in self._device.__dict__.values() if is_tango_object(o)
                and isinstance(o, tango_attribute)]


def test_parsel_should_parse_device_properties_from_tango_device_and_all_its_parents():
    parsel = PyTangoParsel(LeafDevice)

    device_properties = parsel.extract_tango_properties()

    expected_properties = [RootDevice.BaseDeviceProperty,
                           LeafDevice.LeafDeviceProperty,
                           LeafDevice.LeafDeviceProperty]

    assert len(device_properties) == len(expected_properties)
    assert set(device_properties) == set(expected_properties)


def test_parsel_should_parse_device_properties_from_tango_device_and_all_its_parents():
    parsel = PyTangoParsel(LeafDevice)

    device_attributes = parsel.extract_tango_attributes()
    expected_attributes = [
        RootDevice.baseTangoAttribute,
        LeafDevice.telescopeHealthState]
    
    assert len(device_attributes) == len(expected_attributes)
    assert set(device_attributes) == set(expected_attributes)


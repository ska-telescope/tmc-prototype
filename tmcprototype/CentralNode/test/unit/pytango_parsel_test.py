from tango.server import Device, device_property, is_tango_object

from CentralNode.CentralNode import CentralNode


class BaseDevice(Device):
    BaseDeviceProperty = device_property(
        dtype='str',
        doc="A base device property that should be inherited.",
    )


class ChildDevice(BaseDevice):
    ChildDeviceProperty = device_property(
        dtype='str',
        doc="A child device property.",
    )


class PyTangoParsel():
    def __init__(self, pytango_device):
        self._device = pytango_device

    def extract_tango_properties(self):
        return [o for o in self._device.__dict__.values() if is_tango_object(o)
                and isinstance(o, device_property)]


def test_parsel_should_parse_device_properties_from_tango_device_and_all_its_parents():
    parsel = PyTangoParsel(ChildDevice)

    device_properties = parsel.extract_tango_properties()

    expected_properties = [BaseDevice.BaseDeviceProperty,
                           ChildDevice.ChildDeviceProperty]

    assert len(device_properties) == len(expected_properties)
    assert set(device_properties) == set(expected_properties)

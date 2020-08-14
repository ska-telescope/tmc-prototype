
# imports
from tango import DeviceProxy


def create_deviceproxy(fqdn):
    """
    Creates proxy of required device.
    """
    retry = 0
    while retry < 3:
        try:
            device_proxy = DeviceProxy(fqdn)
            break
        except Exception:
            retry += 1
            continue

    return device_proxy
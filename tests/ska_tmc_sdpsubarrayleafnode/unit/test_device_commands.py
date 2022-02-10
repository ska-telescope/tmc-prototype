import pytest


def test_commands(sdpsln_device):
    with pytest.raises(Exception):
        sdpsln_device.TelescopeOn()
        sdpsln_device.TelescopeOff()
        sdpsln_device.AssignResources()
        sdpsln_device.ReleaseResources()
        sdpsln_device.Configure()
        sdpsln_device.Scan()
        sdpsln_device.EndScan()
        sdpsln_device.ObsReset()
        sdpsln_device.Restart()
        sdpsln_device.Reset()

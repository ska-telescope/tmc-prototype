# TODO: Remove this module while using Adapter class from ska-tmc-common library
import enum

from ska_tmc_common.dev_factory import DevFactory


class AdapterType(enum.IntEnum):
    BASE = 0
    SUBARRAY = 1
    DISH = 2
    MCCS = 3
    SDPSUBARRAY = 4
    CSPSUBARRAY = 5
    SDPMASTER = 6


class AdapterFactory:
    def __init__(self) -> None:
        self._adapters = []
        self._dev_factory = DevFactory()

    def get_or_create_adapter(self, dev_name, adapter_type=AdapterType.BASE):
        """
        Get a generic adapter for a device if already created
        or create new adapter as per the device type and add to adpter list

        :param dev_name: device name

        :type str
        """

        for adapter in self._adapters:
            if adapter.dev_name == dev_name:
                return adapter

        new_adapter = None
        if adapter_type == AdapterType.DISH:
            new_adapter = DishAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        elif adapter_type == AdapterType.SUBARRAY:
            new_adapter = SubArrayAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        elif adapter_type == AdapterType.SDPSUBARRAY:
            new_adapter = SdpSubArrayAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        elif adapter_type == AdapterType.CSPSUBARRAY:
            new_adapter = CspSubarrayAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        elif adapter_type == AdapterType.SDPMASTER:
            new_adapter = SdpMasterAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        else:
            new_adapter = BaseAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )

        self._adapters.append(new_adapter)
        return new_adapter


class BaseAdapter:
    def __init__(self, dev_name, proxy) -> None:
        self._proxy = proxy
        self._dev_name = dev_name

    @property
    def proxy(self):
        return self._proxy

    @property
    def dev_name(self):
        return self._dev_name

    def On(self):
        self.proxy.TelescopeOn()

    def Off(self):
        self.proxy.TelescopeOff()

    def StandBy(self):
        self.proxy.TelescopeStandBy()

    def Reset(self):
        self.proxy.Reset()


class SubArrayAdapter(BaseAdapter):
    def __init__(self, dev_name, proxy) -> None:
        super().__init__(dev_name, proxy)

    def AssignResources(self, argin):
        return self._proxy.AssignResources(argin)

    def ReleaseAllResources(self):
        return self._proxy.ReleaseAllResources()

    def ReleaseResources(self, argin):
        return self._proxy.ReleaseResources(argin)

    def Configure(self, argin):
        return self._proxy.Configure(argin)

    def Scan(self, argin):
        return self._proxy.Scan(argin)

    def EndScan(self):
        return self._proxy.EndScan()

    def End(self):
        return self._proxy.End()

    def Abort(self):
        return self._proxy.Abort()

    def Restart(self):
        return self._proxy.Restart()

    def ObsReset(self):
        return self._proxy.ObsReset()


class MCCSAdapter(BaseAdapter):
    def __init__(self, dev_name, proxy) -> None:
        super().__init__(dev_name, proxy)

    def AssignResources(self, argin):
        return self._proxy.AssignResources(argin)

    def ReleaseResources(self, argin):
        return self._proxy.ReleaseResources(argin)


class DishAdapter(BaseAdapter):
    def __init__(self, dev_name, proxy) -> None:
        super().__init__(dev_name, proxy)

    def SetStandbyFPMode(self):
        self._proxy.SetStandbyFPMode()

    def SetOperateMode(self):
        self._proxy.SetOperateMode()

    def SetStandbyLPMode(self):
        self._proxy.SetStandbyLPMode()

    def SetStowMode(self):
        self._proxy.SetStowMode()

    def Configure(self, argin):
        self._proxy.Configure(argin)

    def Track(self, argin):
        self._proxy.Track(argin)

    def StopTrack(self):
        self._proxy.StopTrack()

    def Restart(self):
        self._proxy.Restart()

    def Abort(self):
        self._proxy.Abort()

    def ObsReset(self):
        self._proxy.ObsReset()


class SdpSubArrayAdapter(SubArrayAdapter):
    def __init__(self, dev_name, proxy) -> None:
        super().__init__(dev_name, proxy)

    def On(self):
        self._proxy.On()

    def Off(self):
        self._proxy.Off()


class CspSubarrayAdapter(SubArrayAdapter):
    def __init__(self, dev_name, proxy) -> None:
        super().__init__(dev_name, proxy)

    def End(self):
        return self._proxy.GoToIdle()


class SdpMasterAdapter(BaseAdapter):
    def __init__(self, dev_name, proxy) -> None:
        super().__init__(dev_name, proxy)

    def On(self):
        self._proxy.On()

    def Off(self):
        self._proxy.Off()

    def Standby(self):
        self._proxy.Standby()

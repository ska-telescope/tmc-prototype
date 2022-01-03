import mock

from ska_tmc_sdpsubarrayleafnode.manager.adapters import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    SdpsubarrayAdapter,
)


class HelperAdapterFactory(AdapterFactory):
    def __init__(self) -> None:
        self.adapters = []

    def get_or_create_adapter(
        self, dev_name, adapter_type=AdapterType.BASE, proxy=None, attrs=None
    ):
        if proxy is None:
            proxy = mock.Mock(attrs)

        for adapter in self.adapters:  # why exctly this for loop is required?
            if adapter.dev_name == dev_name:
                return adapter

        new_adapter = None
        if adapter_type == AdapterType.SDPSUBARRAY:
            new_adapter = SdpsubarrayAdapter(dev_name, proxy)
        else:
            new_adapter = BaseAdapter(dev_name, proxy)

        self.adapters.append(new_adapter)
        return new_adapter

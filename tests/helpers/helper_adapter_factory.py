import mock

# TODO: Uncomment below imports while using Adapter class from ska-tmc-common library
# from ska_tmc_common.adapters import (
#     AdapterFactory,
#     AdapterType,
#     BaseAdapter,
#     SdpSubArrayAdapter,
# )
from ska_tmc_sdpmasterleafnode.manager.adapters import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    SdpMasterAdapter,
    SdpSubArrayAdapter,
)


class HelperAdapterFactory(AdapterFactory):
    def __init__(self) -> None:
        self.adapters = []

    def get_or_create_adapter(
        self, dev_name, adapter_type=AdapterType.BASE, proxy=None, attrs=None
    ):
        if proxy is None:
            proxy = mock.Mock(attrs)

        for adapter in self.adapters:
            if adapter.dev_name == dev_name:
                return adapter

        new_adapter = None
        if adapter_type == AdapterType.SDPSUBARRAY:
            new_adapter = SdpSubArrayAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.SDPMASTER:
            new_adapter = SdpMasterAdapter(dev_name, proxy)
        else:
            new_adapter = BaseAdapter(dev_name, proxy)

        self.adapters.append(new_adapter)
        return new_adapter

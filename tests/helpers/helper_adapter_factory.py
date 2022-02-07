# TODO: Currently Sdpmasterleafnode tests are using helpers from common repo.
# This module will get deleted once Sdpsubarrayleafnode tests are also updated to utilise common classes.
import mock
from ska_tmc_common.adapters import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    MasterAdapter,
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
        elif adapter_type == AdapterType.MASTER:
            new_adapter = MasterAdapter(dev_name, proxy)
        else:
            new_adapter = BaseAdapter(dev_name, proxy)

        self.adapters.append(new_adapter)
        return new_adapter

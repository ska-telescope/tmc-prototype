import pytest
import tango
from tango.test_utils import DeviceTestContext

from ska_tmc_sdpmasterleafnode.sdp_master_leaf_node import SdpMasterLeafNode


@pytest.fixture
def sdpmln_device(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(SdpMasterLeafNode) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "SdpMasterLeafNode"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


@pytest.mark.sdpmln
def test_commands(sdpmln_device):
    sdpmln_device.On()
    sdpmln_device.Off()
    sdpmln_device.TelescopeStandby()
    sdpmln_device.Disable()

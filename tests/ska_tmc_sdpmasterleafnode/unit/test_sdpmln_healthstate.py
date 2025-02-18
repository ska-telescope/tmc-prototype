import pytest
import tango
from ska_control_model import HealthState
from tango.test_utils import DeviceTestContext

from ska_tmc_sdpmasterleafnode.sdp_master_leaf_node import TmcLeafNodeSdp


@pytest.fixture
def sdpmln_device(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(TmcLeafNodeSdp, process=True) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "SdpMasterLeafNode"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


def test_attributes(sdpmln_device):
    assert sdpmln_device.healthState == HealthState.OK

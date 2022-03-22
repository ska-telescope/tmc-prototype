import pytest
import tango
from tango.test_utils import DeviceTestContext

from ska_tmc_cspmasterleafnode.csp_master_leaf_node import CspMasterLeafNode


@pytest.fixture
def cspmln_device(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(CspMasterLeafNode) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "CspMasterLeafNode"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


@pytest.mark.cspmln
def test_commands(cspmln_device):
    cspmln_device.On()
    cspmln_device.Standby()

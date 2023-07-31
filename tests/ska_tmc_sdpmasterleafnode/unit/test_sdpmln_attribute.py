import pytest
import tango
from ska_control_model import HealthState
from ska_tmc_common.dev_factory import DevFactory
from tango import DevState
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


@pytest.mark.test1
def test_attributes(sdpmln_device, SdpMasterLeafNode):
    dev_factory = DevFactory()
    sdpmln_device = dev_factory.get_device(SdpMasterLeafNode)
    assert sdpmln_device.On()
    assert sdpmln_device.State() == DevState.ON
    assert sdpmln_device.Off()
    assert sdpmln_device.State() == DevState.OFF
    assert sdpmln_device.healthState == HealthState.OK
    assert not sdpmln_device.isSubsystemAvailable

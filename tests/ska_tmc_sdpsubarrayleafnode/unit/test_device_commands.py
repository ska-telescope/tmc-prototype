import pytest
import tango
from tango.test_utils import DeviceTestContext

from ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node import (
    SdpSubarrayLeafNode,
)


# @pytest.fixture
# def sdpsln_device(request):
#     """Create DeviceProxy for tests"""
#     true_context = request.config.getoption("--true-context")
#     if not true_context:
#         with DeviceTestContext(SdpSubarrayLeafNode) as proxy:
#             yield proxy
#     else:
#         database = tango.Database()
#         instance_list = database.get_device_exported_for_class(
#             "SdpSubarrayLeafNode"
#         )
#         for instance in instance_list.value_string:
#             yield tango.DeviceProxy(instance)
#             break


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

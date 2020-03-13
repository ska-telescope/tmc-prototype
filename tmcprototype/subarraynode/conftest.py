"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
import importlib
import mock
import pytest
from tango import DeviceProxy


from tango.test_context import DeviceTestContext


@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    # TODO: package_name and class_name can be used in future
    # fq_test_class_name = request.cls.__module__
    # fq_test_class_name_details = fq_test_class_name.split(".")
    # package_name = fq_test_class_name_details[1]
    # class_name = module_name = fq_test_class_name_details[1]
    # module = importlib.import_module("{}.{}".format(package_name, module_name))
    # klass = getattr(module, class_name)
    properties = {'CspSubarrayLNFQDN': 'ska_mid/tm_leaf_node/csp_subarray01',
                  'SdpSubarrayLNFQDN': 'ska_mid/tm_leaf_node/sdp_subarray01',
                  'DishLeafNodePrefix': 'ska_mid/tm_leaf_node/d',
                  'SdpSubarrayFQDN': 'mid_sdp/elt/subarray_1',
                  'CspSubarrayFQDN': 'mid_csp/elt/subarray_01'}
    module = importlib.import_module("{}.{}".format("src", "subarray_node"))
    klass = getattr(module, "SubarrayNode")
    tango_context = DeviceTestContext(klass, properties=properties)
    tango_context.start()
    klass.get_name = mock.Mock(side_effect=tango_context.get_device_access)
    yield tango_context
    tango_context.stop()

@pytest.fixture(scope="class")
def initialize_device(tango_context):
    """Re-initializes the device.

    Parameters
    ----------
    tango_context: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context.device.Init()

@pytest.fixture(scope="class")
def create_dish_proxy():
    dish_proxy = DeviceProxy("mid_d0001/elt/master")
    return dish_proxy

@pytest.fixture(scope="class")
def create_dishln_proxy():
    dishln_proxy = DeviceProxy("ska_mid/tm_leaf_node/d0001")
    return dishln_proxy
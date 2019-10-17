"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""

from __future__ import absolute_import
import importlib
import mock
import pytest
import tango


from tango import DeviceProxy, DevFailed
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
    module = importlib.import_module("{}.{}".format("CspSubarrayLeafNode", "CspSubarrayLeafNode"))
    klass = getattr(module, "CspSubarrayLeafNode")
    properties = {'SkaLevel': '3', 'GroupDefinitions': '', 'CentralLoggingTarget': '',
                  'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost',
                  'CspSubarrayFQDN': 'mid_csp/elt/subarray_02'
                  }
    tango_context = DeviceTestContext(klass, properties=properties, process=False)
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
def create_cspsubarray2_proxy():
    cspsubarray2_proxy = DeviceProxy("mid_csp/elt/subarray_02")
    return cspsubarray2_proxy

@pytest.fixture(scope="class")
def create_sdpsubarrayln1_proxy():
    sdpsubarrayln1_proxy = DeviceProxy("ska_mid/tm_leaf_node/sdp_subarray01")
    return sdpsubarrayln1_proxy

@pytest.fixture(scope="class")
def create_cbfsubarray1_proxy():
    cbfsubarray1_proxy = DeviceProxy("mid_csp_cbf/sub_elt/subarray_01")
    return cbfsubarray1_proxy

@pytest.fixture(scope="class")
def create_vcc1_proxy():
    vcc1_proxy = DeviceProxy("mid_csp_cbf/vcc/001")
    return vcc1_proxy

@pytest.fixture(scope="class")
def create_fsp1_proxy():
    fsp1_proxy = DeviceProxy("mid_csp_cbf/fsp/01")
    return fsp1_proxy

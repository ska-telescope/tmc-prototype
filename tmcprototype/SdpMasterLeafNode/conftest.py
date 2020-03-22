"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
from __future__ import absolute_import
import mock
import pytest
import importlib
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
    module = importlib.import_module("{}.{}".format("SdpMasterLeafNode", "SdpMasterLeafNode"))
    klass = getattr(module, "SdpMasterLeafNode")
    properties = {'SkaLevel': '4', 'GroupDefinitions': '',
                  'SdpMasterFQDN': 'mid_sdp/elt/master',
                  'LoggingLevelDefault': '4', 'LoggingTargetsDefault': 'console::cout'
                  }
    tango_context_sdpmasterln = DeviceTestContext(klass, properties=properties, process=False)
    tango_context_sdpmasterln.start()
    klass.get_name = mock.Mock(side_effect=tango_context_sdpmasterln.get_device_access)
    yield tango_context_sdpmasterln
    tango_context_sdpmasterln.stop()

@pytest.fixture(scope="function")
def initialize_device(tango_context_init):
    """Re-initializes the device.

    Parameters
    ----------
    tango_context: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context_init.device.Init()


@pytest.fixture(scope="class")
def create_sdp_master_proxy():
    sdp_master_proxy = DeviceProxy("mid_sdp/elt/master")
    return sdp_master_proxy
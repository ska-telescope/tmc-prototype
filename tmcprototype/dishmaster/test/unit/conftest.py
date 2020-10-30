"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
import mock
import pytest
import pkg_resources
import tempfile

from tango import Database
from tango.test_context import DeviceTestContext

from tango_simlib import tango_sim_generator
from tango_simlib.utilities import helper_module


@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    properties = {
        "SkaLevel": "4",
        "MetricList": "healthState",
        "GroupDefinitions": "",
        "LoggingLevelDefault": "4",
        "LoggingTargetsDefault": "console::cout",
        "NrSubarrays": "16",
        "CapabilityTypes": "",
        "MaxCapabilities": "",
        "ReceptorNumber": "",
    }
    _, tango_db_path = tempfile.mkstemp(prefix="tango")
    data_descr_files = []
    data_descr_files.append(pkg_resources.resource_filename("dishmaster", "dish_master.fgo"))
    data_descr_files.append(pkg_resources.resource_filename("dishmaster", "dish_master_SimDD.json"))
    device_name = "test/nodb/dishmaster"
    model = tango_sim_generator.configure_device_model(data_descr_files, device_name)
    DishMaster = tango_sim_generator.get_tango_device_server(model, data_descr_files)[0]
    tango_context = DeviceTestContext(
        DishMaster, db=tango_db_path, process=False, properties=properties
    )
    mock_get_db = mock.Mock(return_value=Database(tango_context.db))
    helper_module.get_database = mock_get_db
    tango_context.start()
    yield tango_context
    tango_context.stop()


@pytest.fixture(scope="class")
def initialize_device(tango_context):
    """Re-initializes the device.

    Parameters
    ----------
    tango_context_init: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context.device.Init()

"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
import tempfile

import mock
import pytest

from tango import Database
from tango.test_context import DeviceTestContext

from tango_simlib.utilities import helper_module
from dishmaster.utils import get_tango_server_class


@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """

    DishMaster = get_tango_server_class("test/nodb/dishmaster")
    _, tango_db_path = tempfile.mkstemp(prefix="tango")
    tango_context = DeviceTestContext(
        DishMaster, db=tango_db_path, process=False, properties={}
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

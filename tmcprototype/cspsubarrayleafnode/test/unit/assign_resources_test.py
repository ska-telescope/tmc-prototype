# Standard Python imports
import contextlib
import importlib
import sys
import json
import types
import pytest
import tango
import mock
from mock import Mock
from mock import MagicMock
from os.path import dirname, join

# Tango imports
from tango.test_context import DeviceTestContext

# Additional import
from ska.base import SKASubarray, SKASubarrayResourceManager, SKASubarrayStateModel
from cspsubarrayleafnode import CspSubarrayLeafNode, const, release
from ska.base.control_model import HealthState, ObsState, LoggingLevel

assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

@pytest.fixture
def subarray_state_model():
    """
    Yields a new SKASubarrayStateModel for testing
    """
    yield SKASubarrayStateModel(logging.getLogger())

@pytest.fixture
def resource_manager():
    """
    Fixture that yields an SKASubarrayResourceManager
    """
    yield SKASubarrayResourceManager()


def test_assign_resources():
    assign_resources = SKASubarray.AssignResourcesCommand(
            resource_manager,
            subarray_state_model
        )

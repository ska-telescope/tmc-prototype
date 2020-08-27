
# Standard Python imports
import contextlib
import importlib
import sys
import json
import types
import time
import pytest
import mock
from mock import Mock, MagicMock
from os.path import dirname, join
import threading


from subarraynode.configure_command import configuration_model
from subarraynode import SubarrayNode, const

@pytest.fixture
def config_model():
    """
    Fixture that yields an Configuration Model
    """
    yield configuration_model()

class TestConfigurationModel:
    """
    Test suit for Configuration Model class
    """
    def test_ConfigurationModel_configure(self, config_model):
        """
        Test that ConfigurationModel invokes Configure command correctly
        """
        # Create ConfigureCommand Object by passing state model and device
        configure_cmd = SubarrayNode.ConfigureCommand(config_model, subarray_state_model)
        # Use of lmc-base-classe's straight_to_state method to push it straigh to IDLE
        subarray_state_model._straight_to_state("IDLE")

        # attribute = "receiveAddresses"
        # dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
        #                                    receive_addresses_map)
        # event_subscription_map[attribute](dummy_event)
    
        # Invoke Configure command as a callable
        assert configure_cmd(configure_str) == (ResultCode.STARTED, "Configure command invoked")

# Standard Python imports
import pytest
import logging
from os.path import dirname, join

from subarraynode.configure_command import configuration_model
from subarraynode import SubarrayNode, const
from ska.base import SKASubarrayStateModel

configure_input_file= 'command_Configure.json'
path= join(dirname(__file__), 'data' , configure_input_file)
with open(path, 'r') as f:
    configure_str=f.read()


@pytest.fixture
def subarray_state_model():
    """
    Yields a new SKASubarrayStateModel for testing
    """
    yield SKASubarrayStateModel(logging.getLogger())

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
        config_model.configure(configure_str, logging.getLogger())
        config_model._configure_csp.side_effect = mock_csp_configure
        config_model._configure_sdp.side_effect = mock_csp_configure
        config_model._configure_dsh.side_effect = mock_csp_configure
        assert False

    def mock_csp_configure(self):
        pass


# def test_configure_command(config_model, subarray_state_model):
#     """
#     Test for SubarrayNode.ConfigureCommand
#     """
#     # tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
#     # Create ConfigureCommand Object by passing state model and device
#     configure_cmd = SubarrayNode.ConfigureCommand(config_model, subarray_state_model)
#     # Use of lmc-base-classe's straight_to_state method to push it straigh to IDLE
#     subarray_state_model._straight_to_state("IDLE")

#     # attribute = "receiveAddresses"
#     # dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
#     #                                    receive_addresses_map)
#     # event_subscription_map[attribute](dummy_event)

#     # Invoke Configure command as a callable
#     assert configure_cmd(configure_str) == (ResultCode.STARTED, "Configure command invoked")
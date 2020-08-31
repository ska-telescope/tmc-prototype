
# Standard Python imports
from os.path import dirname, join
import pytest
import logging
import mock
from mock import Mock, MagicMock

# from subarraynode.configure_command import configuration_model
from subarraynode.configure_command import ConfigureCommand
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

# @pytest.fixture
# def config_model():
#     """
#     Fixture that yields an Configuration Model
#     """
#     yield configuration_model()

@pytest.fixture
def subarray_model():
    yield subarray_model()

class TestConfigureCommand:
    """
    Test suit for ConfigureCommand class
    """

    def test_configure_command(subarray_model, subarray_state_model):
        configure_cmd = ConfigureCommand(subarray_model, subarray_state_model)
        subarray_state_model._straight_to_state("IDLE")

        assert configure_cmd.do(configure_str) == (ResultCode.STARTED, "Configure command invoked")


# class TestConfigurationModel:
#     """
#     Test suit for Configuration Model class
#     """
#     def test_ConfigurationModel_configure(self, config_model):
#         """
#         Test that ConfigurationModel invokes Configure command correctly
#         """
#         config_model._configure_csp = Mock()
#         config_model._configure_csp.side_effect = self.mock_csp_configure()

#         config_model._configure_sdp = Mock()
#         config_model._configure_sdp.side_effect = self.mock_csp_configure()

#         config_model._configure_dsh = Mock()
#         config_model._configure_dsh.side_effect = self.mock_csp_configure()
        
#         config_model.configure(configure_str, logging.getLogger())
#         assert config_model.this_subarray._read_activity_message == const.STR_CONFIGURE_CMD_INVOKED_SA

#     def mock_csp_configure(self):
#         print("Dummy mock method for testing")


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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the MCCSMasterLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the ."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
from PyTango import DevFailed, DevState
from devicetest import DeviceTestCase, main
from MCCSMasterLeafNode import MCCSMasterLeafNode

# Additional Imports
from mccsmasterleafnode import MccsMasterLeafNode, const, release


assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()


assign_invalid_key_file = 'invalid_key_AssignResources.json'
path = join(dirname(__file__), 'data', assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key = f.read()


@pytest.fixture(scope="function")
def event_subscription(mock_mccs_master):
    event_subscription_map = {}
    mock_mccs_master[1].command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def mock_mccs_master():
    mccs_master_fqdn = 'low_mccs/elt/master'
    dut_properties = {
        'MccsmasterFQDN': mccs_master_fqdn
    }
    mccs_master_proxy_mock = Mock()
    proxies_to_mock = {
        mccs_master_fqdn: mccs_master_proxy_mock
    }
    with fake_tango_system(MccsMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, mccs_master_proxy_mock



# Note:
#
# Since the device uses an inner thread, it is necessary to
# wait during the tests in order the let the device update itself.
# Hence, the sleep calls have to be secured enough not to produce
# any inconsistent behavior. However, the unittests need to run fast.
# Here, we use a factor 3 between the read period and the sleep calls.
#
# Look at devicetest examples for more advanced testing


# Device test case
class MCCSMasterLeafNodeDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_additionnal_import
    device = MCCSMasterLeafNode
    properties = {'SkaLevel': '3', 'GroupDefinitions': '', 'LoggingLevelDefault': '5', 'LoggingTargetsDefault': 'tango::logger', 'MCCSMasterFQDN': 'low_mccs/elt/master', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = MCCSMasterLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_Status

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_GetVersionInfo

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_Reset

    def test_AssignResource(self):
        """Test for AssignResource"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_AssignResource) ENABLED START #
        self.device.AssignResource("")
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_AssignResource

    def test_ReleaseResources(self):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_ReleaseResources) ENABLED START #
        self.device.ReleaseResources("")
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_ReleaseResources

    def test_On(self):
        """Test for On"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_On) ENABLED START #
        self.device.On()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_On

    def test_Off(self):
        """Test for Off"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_Off) ENABLED START #
        self.device.Off()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_Off

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_versionId

    def test_loggingLevel(self):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_loggingLevel) ENABLED START #
        self.device.loggingLevel
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_loggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_testMode

    def test_activitymessage(self):
        """Test for activitymessage"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_activitymessage) ENABLED START #
        self.device.activitymessage
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_activitymessage

    def test_loggingTargets(self):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_loggingTargets) ENABLED START #
        self.device.loggingTargets
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_loggingTargets


    # def test_assign_resources_should_send_mccs_master_with_correct_stationiDList_list(mock_mccs_master):
    #     #arrange
    #     device_proxy, mccs_master_proxy_mock = mock_mccs_master
    #     mccs_master_proxy_mock.obsState = ObsState.EMPTY
    #     device_proxy.On()
    #     device_proxy.AssignResource(assign_input_str)
    #     stationiDList = [] 
    #     json_argument = json.loads(assign_input_str)
    #     stationiDList_str = json_argument[const.STR_DISH][const.STR_RECEPTORID_LIST] ???????????
    #     # convert receptorIDList from list of string to list of int
    #     for receptor in receptorIDList_str: ???????
    #         receptorIDList.append(int(receptor)) ???????
    #     mccs_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ALLOCATE,
    #                                                                     ????????,
    #                                                                     any_method(with_name='allocate_ended'))
    #     assert_activity_message(device_proxy, const.STR_ALLOCATE_SUCCESS)
    
    def test_assign_resources_should_raise_devfailed_exception(mock_mccs_master):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.EMPTY
        mccs_master_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_with_arg
        device_proxy.On()
        with pytest.raises(tango.DevFailed) as df:
            device_proxy.AssignResource(assign_input_str)
        assert const.ERR_DEVFAILED_MSG in str(df.value)
    
    def test_assign_command_with_callback_method(mock_mccs_master, event_subscription):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.EMPTY
        device_proxy.On()
        device_proxy.AssignResource(assign_input_str)
        dummy_event = command_callback(const.CMD_ALLOCATE)
        event_subscription[const.CMD_ALLOCATE](dummy_event)
        assert const.STR_INVOKE_SUCCESS in device_proxy.activityMessage

    def test_assign_command_with_callback_method_with_event_error(mock_mccs_master, event_subscription):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.EMPTY
        device_proxy.On()
        device_proxy.AssignResource(assign_input_str)
        dummy_event = command_callback_with_event_error(const.CMD_ALLOCATE)
        event_subscription[const.CMD_ALLOCATE](dummy_event)
        assert const.ERR_INVOKING_CMD + const.CMD_ALLOCATE in device_proxy.activityMessage
    
    def test_assign_command_with_callback_method_with_devfailed_error(mock_mccs_master, event_subscription):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.EMPTY
        device_proxy.On()
        with pytest.raises(tango.DevFailed) as df:
            device_proxy.AssignResources(assign_input_str)
            dummy_event = command_callback_with_devfailed_exception()
            event_subscription[const.CMD_ALLOCATE](dummy_event)
        assert const.ERR_CALLBACK_CMD_FAILED in str(df.value)
    
    def test_allocate_ended_should_raise_dev_failed_exception_for_invalid_obs_state(mock_mccs_master, event_subscription):
        device_proxy, mccs_master_proxy_mock = mock_mccs_master
        mccs_master_proxy_mock.obsState = ObsState.READY
        with pytest.raises(tango.DevFailed) as df:
            device_proxy.AssignResources(json.dumps(assign_input_file))
        assert const.ERR_RAISED_EXCEPTION in str(df.value)

    def test_assign_resource_should_raise_exception_when_key_not_found():
        with fake_tango_system(MccsMasterLeafNode) as tango_context:
            with pytest.raises(tango.DevFailed) as df:
                tango_context.device.AssignResources(assign_invalid_key)
            assert const.ERR_RAISED_EXCEPTION in str(df)

    def raise_devfailed_with_arg(cmd_name, input_arg1, input_arg2):
        # "This function is called to raise DevFailed exception with arguments."
        tango.Except.throw_exception(const.STR_CMD_FAILED, const.ERR_DEVFAILED_MSG,
                                    cmd_name, tango.ErrSeverity.ERR)

    def command_callback(command_name):
        fake_event = MagicMock()
        fake_event.err = False
        fake_event.cmd_name = f"{command_name}"
        return fake_event
    
    def command_callback_with_event_error(command_name):
        fake_event = MagicMock()
        fake_event.err = True
        fake_event.errors = 'Event error in Command Callback'
        fake_event.cmd_name = f"{command_name}"
        return fake_event

    def command_callback_with_devfailed_exception():
        # "This function is called when command is failed with DevFailed exception."
        tango.Except.throw_exception(const.ERR_DEVFAILED_MSG,
                                    const.ERR_CALLBACK_CMD_FAILED, " ", tango.ErrSeverity.ERR)

    

# Main execution
if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the TrackDishLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the TrackDishLeafNode."""

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
from TrackDishLeafNode import TrackDishLeafNode

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
class TrackDishLeafNodeDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(TrackDishLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  TrackDishLeafNode.test_additionnal_import
    device = TrackDishLeafNode
    properties = {
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = TrackDishLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(TrackDishLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  TrackDishLeafNode.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(TrackDishLeafNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  TrackDishLeafNode.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(TrackDishLeafNode.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  TrackDishLeafNode.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(TrackDishLeafNode.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  TrackDishLeafNode.test_Status

    def test_TRACK(self):
        """Test for TRACK"""
        # PROTECTED REGION ID(TrackDishLeafNode.test_TRACK) ENABLED START #
        self.device.TRACK([""])
        # PROTECTED REGION END #    //  TrackDishLeafNode.test_TRACK

    def test_ATTR1(self):
        """Test for ATTR1"""
        # PROTECTED REGION ID(TrackDishLeafNode.test_ATTR1) ENABLED START #
        self.device.ATTR1
        # PROTECTED REGION END #    //  TrackDishLeafNode.test_ATTR1

    def test_ATTR2(self):
        """Test for ATTR2"""
        # PROTECTED REGION ID(TrackDishLeafNode.test_ATTR2) ENABLED START #
        self.device.ATTR2
        # PROTECTED REGION END #    //  TrackDishLeafNode.test_ATTR2


# Main execution
if __name__ == "__main__":
    main()

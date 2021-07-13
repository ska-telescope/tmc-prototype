# -*- coding: utf-8 -*-
"""
override class with command handlers for dsh-lmc.
"""
# Standard python imports
import enum
import logging

from collections import namedtuple

# Tango import
from tango import DevState, Except, ErrSeverity

class OverrideCspMaster(object):

    def action_on(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to ON.
        """
        tango_dev.set_state(DevState.ON)
        print("******On Invoked successfully******",tango_dev.state())


    def action_off(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to OFF.
        """
        tango_dev.set_state(DevState.OFF)
        print("******OFF Invoked successfully******",tango_dev.state())

    def action_standby(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to STANDBY.
        """
        tango_dev.set_state(DevState.OFF)
        print("******Standby Invoked successfully*****",tango_dev.state())

    
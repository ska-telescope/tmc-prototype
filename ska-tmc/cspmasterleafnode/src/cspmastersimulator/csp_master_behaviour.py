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
        on = "ON"
        _allowed_modes = (
            "OFF",
            "STANDBY"
        )
        if str(tango_dev.get_state()) in ["ON"]:
            print("CSP master is already in '%s' state", on)
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.ON)
            print("Csp Master transitioned to the '%s' state.", on)

    def action_off(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to OFF.
        """
        off = "OFF"
        _allowed_modes = (
            "ON",
            "ALARM"
            "STANDBY"
        )
        if str(tango_dev.get_state()) in ["OFF"]:
            print("CSP master is already in '%s' state", off)
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.OFF)
            print("Csp Master transitioned to the '%s' state.", off)

    def action_standby(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to STANDBY.
        """
        standby = "STANDBY"
        _allowed_modes = (
            "ON",
            "ALARM"
            "OFF"
        )
        if str(tango_dev.get_state()) in ["STANDBY"]:
            print("CSP master is already in '%s' state", standby)
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.STANDBY)
            print("Csp Master transitioned to the '%s' state.", standby)

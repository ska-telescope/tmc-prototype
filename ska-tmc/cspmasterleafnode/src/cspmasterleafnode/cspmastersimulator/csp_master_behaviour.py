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

    def action_on(self, models, tango_dev=None, data_input=[]):
        """Changes the State of the device to ON.
        """
        on = "ON"
        ok = "OK"
        _allowed_modes = (
            "OFF",
            "STANDBY"
        )
        if str(tango_dev.get_state()) in ["ON"]:
            print(f"CSP master is already in {on} state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.ON)
            #models.sim_quantities["healthState"].set_val("On command", model.time_func())
            print (f"Csp Master transitioned to the {on} state.")
            csp_mode_healthState = models.sim_quantities["healthState"]
            set_enum(csp_mode_healthState, ok, models.time_func())
            tango_dev.push_change_event("healthState", "test value On")
            tango_dev.set_status("device turned On successfully")
            print(f"heathState transitioned to {ok} state")

            # csp_mode_cspCbfHealthState = models.sim_quantities["cspCbfHealthState"]
            # set_enum(csp_mode_cspCbfHealthState, ok, models.time_func())
            # print(f"cspCbfHealthState transitioned to {ok} state")

            # csp_mode_cspPssHealthState = models.sim_quantities["cspPssHealthState"]
            # set_enum(csp_mode_cspPssHealthState, ok, models.time_func())
            # print(f"cspPssHealthState transitioned to {ok} state")

            # csp_mode_cspPstHealthState = models.sim_quantities["cspPstHealthState"]
            # set_enum(csp_mode_cspPstHealthState, ok, models.time_func())
            # print(f"cspPstHealthState transitioned to {ok} state")
        else:
            Except.throw_exception(
                    "ON Command Failed",
                    "Not allowed",
                    ErrSeverity.WARN,
                )

    def action_off(self, models, tango_dev=None, data_input=[]):
        """Changes the State of the device to OFF.
        """
        off = "OFF"
        ok = "OK"
        _allowed_modes = (
            "ON",
            "ALARM",
            "STANDBY"
        )
        if str(tango_dev.get_state()) in ["OFF"]:
            print(f"CSP master is already in {off} state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.OFF)
            #models.sim_quantities["TestAttr"].set_val("Off command", model.time_func())
            print (f"Csp Master transitioned to the {off} state.")
            csp_mode_healthState = models.sim_quantities["healthState"]
            set_enum(csp_mode_healthState, ok, models.time_func())
            tango_dev.push_change_event("healthState", "test value off")
            tango_dev.set_status("device turned off successfully")
            print(f"heathState transitioned to {ok} state")

            # csp_mode_cspCbfHealthState = models.sim_quantities["cspCbfHealthState"]
            # set_enum(csp_mode_cspCbfHealthState, ok, models.time_func())
            # print(f"cspCbfHealthState transitioned to {ok} state")

            # csp_mode_cspPssHealthState = models.sim_quantities["cspPssHealthState"]
            # set_enum(csp_mode_cspPssHealthState, ok, models.time_func())
            # print(f"cspPssHealthState transitioned to {ok} state")

            # csp_mode_cspPstHealthState = models.sim_quantities["cspPstHealthState"]
            # set_enum(csp_mode_cspPstHealthState, ok, models.time_func())
            # print(f"cspPstHealthState transitioned to {ok} state")
            
        else:
            Except.throw_exception(
                    "Off Command Failed",
                    "Not allowed",
                    ErrSeverity.WARN,
                )

    def action_standby(self, models, tango_dev=None, data_input=[]):
        """Changes the State of the device to STANDBY.
        """
        standby = "STANDBY"
        ok = "OK"
        _allowed_modes = (
            "ON",
            "ALARM",
            "OFF"
        )
        if str(tango_dev.get_state()) in ["STANDBY"]:
            print(f"CSP master is already in {standby} state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.STANDBY)
            #models.sim_quantities["TestAttr"].set_val("Standby command", model.time_func())
            print(f"Csp Master transitioned to the {standby} state.")
            csp_mode_healthState = models.sim_quantities["healthState"]
            set_enum(csp_mode_healthState, ok, models.time_func())
            tango_dev.push_change_event("healthState", "test value Standby")
            tango_dev.set_status("invoked Standby successfully")
            print(f"heathState transitioned to {ok} state")

            # csp_mode_cspCbfHealthState = models.sim_quantities["cspCbfHealthState"]
            # set_enum(csp_mode_cspCbfHealthState, ok, models.time_func())
            # print(f"cspCbfHealthState transitioned to {ok} state")

            # csp_mode_cspPssHealthState = models.sim_quantities["cspPssHealthState"]
            # set_enum(csp_mode_cspPssHealthState, ok, models.time_func())
            # print(f"cspPssHealthState transitioned to {ok} state")

            # csp_mode_cspPstHealthState = models.sim_quantities["cspPstHealthState"]
            # set_enum(csp_mode_cspPstHealthState, ok, models.time_func())
            # print(f"cspPstHealthState transitioned to {ok} state")
        else:
            Except.throw_exception(
                    "STANDBY Command Failed",
                    "Not allowed",
                    ErrSeverity.WARN,
                )

def get_enum_str(quantity):
    """Returns the enum label of an enumerated data type

    :param quantity: object
        The quantity object of a DevEnum attribute
    :return: str
        Current string value of a DevEnum attribute
    """
    EnumClass = enum.IntEnum("EnumLabels", quantity.meta["enum_labels"], start=0)
    return EnumClass(quantity.last_val).name


def set_enum(quantity, label, timestamp):
    """Sets the quantity last_val attribute to index of label

    :param quantity: object
        The quantity object from models
    :param label: str
        The desired label from enum list
    :param timestamp: float
        The time now
    """
    value = quantity.meta["enum_labels"].index(label)
    quantity.set_val(value, timestamp)

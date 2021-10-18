# -*- coding: utf-8 -*-
#
# This file is part of the SdpMasterSimulator project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# Standard Python imports
import pkg_resources
import enum
# import enum
import logging

# Tango imports
from tango import DevState, Except, ErrSeverity, Database, Group

# SKA imports
from ska.base.commands import ResultCode
from ska_ser_logging import configure_logging


class OverrideSdpMaster:
    """Class for sdp master simulator device"""

    def action_on(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        model.logger.info("Executing On command")
        _allowed_modes = (DevState.OFF, DevState.STANDBY)
        if tango_dev.get_state() == DevState.ON:
            model.logger.info("SDP master is already in ON state")
            return [[ResultCode.OK], ["SDP master is already in ON state"]]

        if tango_dev.get_state() in _allowed_modes:

            # set health state
            sdp_health_state = model.sim_quantities["healthState"]
            set_enum(sdp_health_state, "OK", model.time_func())
            sdp_health_state_enum = get_enum_int(sdp_health_state, "OK")
            tango_dev.push_change_event("healthState", sdp_health_state_enum)
            model.logger.info("heathState transitioned to OK state")

            # Set device state
            tango_dev.set_status("device turned on successfully")
            tango_dev.set_state(DevState.ON)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Sdp Master transitioned to the ON state.")
        else:
            Except.throw_exception(
                "ON Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["ON command invoked successfully on simulator."]]

    def action_off(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        _allowed_modes = (DevState.ON, DevState.ALARM, DevState.STANDBY)
        if tango_dev.get_state() == DevState.OFF:
            model.logger.info("SDP master is already in OFF state")
            return [[ResultCode.OK], ["SDP master is already in Off state"]]

        if tango_dev.get_state() in _allowed_modes:

            # Set device state
            tango_dev.set_status("device turned off successfully")
            tango_dev.set_state(DevState.OFF)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Sdp Master transitioned to the OFF state.")

        else:
            Except.throw_exception(
                "Off Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["OFF command invoked successfully on simulator."]]

    def action_sdpmasterfault(self, model, tango_dev=None, data_input=None):
        tango_dev.set_state(DevState.FAULT)
        tango_dev.push_change_event("State", tango_dev.get_state())

    def action_reset(self, model, tango_dev=None, data_input=None
    ):
        if tango_dev.get_state() == DevState.FAULT:
            tango_dev.set_state(DevState.OFF)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Reset command successful on simulator.")

    def action_standby(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        _allowed_modes = (DevState.ON, DevState.ALARM, DevState.OFF)
        if tango_dev.get_state() == DevState.STANDBY:
            model.logger.info("SDP master is already in STANDBY state")
            return [[ResultCode.OK], ["SDP master is already in STANDBY state"]]

        if tango_dev.get_state() in _allowed_modes:
            # Set device state
            tango_dev.set_status("device turned to STANDBY successfully")
            tango_dev.set_state(DevState.STANDBY)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Sdp Master transitioned to the STANDBY state.")

        else:
            Except.throw_exception(
                "STANDBY Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )
            
def set_enum(quantity, label, timestamp):
    """Sets the quantity last_val attribute to index of label

    :param quantity: tango_simlib.quantities.Quantity
        The quantity object from model
    :param label: str
        The desired label from enum list
    :param timestamp: float
        The time now
    """
    value = quantity.meta["enum_labels"].index(label)
    quantity.set_val(value, timestamp)


def get_enum_int(quantity, label):
    """Returns the integer index value of an enumerated data type

    :param quantity: tango_simlib.quantities.Quantity
        The quantity object from model
    :param label: str
        The desired label from enum list
    :return: Int
        Current integer value of a DevEnum attribute
    """
    return quantity.meta["enum_labels"].index(label)

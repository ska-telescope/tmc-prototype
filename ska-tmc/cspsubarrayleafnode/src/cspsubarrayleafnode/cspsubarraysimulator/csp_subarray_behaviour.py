# -*- coding: utf-8 -*-
"""
override class with command handlers for CspSubarray.
"""
# Standard python imports
import enum
import logging
import time

from collections import namedtuple

# Tango import
from tango import DevState, Except, ErrSeverity

# Additional import
# from ska.logging import configure_logging

# configure_logging()
MODULE_LOGGER = logging.getLogger(__name__)


class OverrideCspSubarray(object):

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
            models.logger.info(f"CSP Subarray is already in {on} state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.ON)
            models.logger.info(f"Csp Subarray transitioned to the {on} state.")
            csp_mode_healthState = models.sim_quantities["healthState"]
            set_enum(csp_mode_healthState, ok, models.time_func())
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
            models.logger.info(f"CSP master is already in {off} state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.OFF)
            models.logger.info(f"Csp Subarray transitioned to the {off} state.")
            csp_mode_healthState = models.sim_quantities["healthState"]
            set_enum(csp_mode_healthState, ok, models.time_func())
            models.logger.info(f"heathState transitioned to {ok} state")
        else:
            Except.throw_exception(
                    "ON Command Failed",
                    "Not allowed",
                    ErrSeverity.WARN,
                )

    def action_assignresources(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "EMPTY"):
            set_enum(obsstate_attribute, "RESOURCING", models.time_func())
            tango_dev.push_change_event("obsState", 1)
            tango_dev.set_status("ObsState in RESOURCING")
            models.logger.info("ObsState trasnitioned to RESOURCING")

            time.sleep(1)
            set_enum(obsstate_attribute, "IDLE", models.time_func())
            tango_dev.push_change_event("obsState", 2)
            tango_dev.set_status("ObsState in Idle")
            models.logger.info("ObsState trasnitioned to IDLE")
            
        else:
            Except.throw_exception(
                "Assign Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_endscan(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "SCANNING"):
            set_enum(obsstate_attribute, "READY", models.time_func())
            tango_dev.push_change_event("obsState", 4)
            tango_dev.set_status("ObsState in READY")
            models.logger.info("ObsState trasnitioned to READY")            
        else:
            Except.throw_exception(
                "EndScan Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        
    def action_abort(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        _allowed_obsstate = (
            "IDLE",
            "READY",
            "SCANNING",
            "CONFIGURING",
            "RESETTING"
        )
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate in _allowed_obsstate):
           set_enum(obsstate_attribute, "ABORTING", models.time_func())
           tango_dev.push_change_event("obsState", 6)
           tango_dev.set_status("ObsState in ABORTING")
           models.logger.info("ObsState trasnitioned to ABORTING")
           time.sleep(1)
           set_enum(obsstate_attribute, "ABORTED", models.time_func())
           tango_dev.push_change_event("obsState", 7)
           tango_dev.set_status("ObsState in ABORTED")
           models.logger.info("ObsState trasnitioned to ABORTED")
            
        else:
            Except.throw_exception(
                "Abort Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_releaseallresources(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "IDLE"):
            set_enum(obsstate_attribute, "RESOURCING", models.time_func())
            tango_dev.push_change_event("obsState",1)
            tango_dev.set_status("ObsState in RESOURCING")
            models.logger.info("ObsState trasnitioned to RESOURCING")

            time.sleep(1)
            set_enum(obsstate_attribute, "EMPTY", models.time_func())
            tango_dev.push_change_event("obsState", 0)
            tango_dev.set_status("ObsState in EMPTY")
            models.logger.info("ObsState trasnitioned to EMPTY")
           
        else:
            Except.throw_exception(
                "Release Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_configure(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        _allowed_obsstate = (
            "IDLE",
            "READY"
        )
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate in _allowed_obsstate):
            set_enum(obsstate_attribute, "CONFIGURING", models.time_func())
            tango_dev.push_change_event("obsState", 3)
            tango_dev.set_status("ObsState in CONFIGURING")
            models.logger.info("ObsState trasnitioned to CONFIGURING")

            time.sleep(1)
            set_enum(obsstate_attribute, "READY", models.time_func())
            tango_dev.push_change_event("obsState", 4)
            tango_dev.set_status("ObsState in READY")
            models.logger.info("ObsState trasnitioned to READY")

        else:
            Except.throw_exception(
                "Configure Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_scan(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "READY"):
            set_enum(obsstate_attribute, "SCANNING", models.time_func())
            tango_dev.push_change_event("obsState", 5)
            tango_dev.set_status("ObsState in SCANNING")
            models.logger.info("ObsState trasnitioned to SCANNING")

            time.sleep(10)
            set_enum(obsstate_attribute, "READY", models.time_func())
            tango_dev.push_change_event("obsState", 4)
            tango_dev.set_status("ObsState in READY")
            models.logger.info("ObsState trasnitioned to READY")
        else:
            Except.throw_exception(
                "Scan Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        

    def action_gotoidle(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "READY"):
            set_enum(obsstate_attribute, "IDLE", models.time_func())
            tango_dev.push_change_event("obsState", 2)
            tango_dev.set_status("ObsState in IDLE")
            models.logger.info("ObsState trasnitioned to IDLE")
            
        else:
            Except.throw_exception(
                "gotoidle Command Failed",
                "Not allowed in current Obstate.",
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


def get_direction_sign(here, there):
    """Return sign (+1 or -1) required to move from here to there."""
    return 1 if here < there else -1

# -*- coding: utf-8 -*-
"""
override class with command handlers for CspSubarray.
"""
# Standard python imports
import enum
import logging
import time

# Tango import
from tango import DevState, Except, ErrSeverity

# Additional import
# from ska.logging import configure_logging

# configure_logging()
MODULE_LOGGER = logging.getLogger(__name__)


class OverrideCspSubarray(object):

    def action_on(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to ON.
        """
        _allowed_modes = (
            "OFF",
            "STANDBY"
        )
        if str(tango_dev.get_state())== DevState.ON:
            model.logger.info("CSP Subarray is already in ON state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.ON)
            model.logger.info("Csp Subarray transitioned to the ON state.")
            csp_mode_healthState = model.sim_quantities["healthState"]
            set_enum(csp_mode_healthState, "OK", model.time_func())
        else:
            Except.throw_exception(
                    "ON Command Failed",
                    "Not allowed",
                    ErrSeverity.WARN,
                )

    def action_off(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to OFF.
        """
        _allowed_modes = (
            "ON",
            "ALARM",
            "STANDBY"
        )
        if str(tango_dev.get_state()) == DevState.OFF:
            model.logger.info("CSP master is already in OFF state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.OFF)
            model.logger.info("Csp Subarray transitioned to the OFF state.")
            csp_mode_healthState = model.sim_quantities["healthState"]
            set_enum(csp_mode_healthState, "OK" , model.time_func())
            model.logger.info("heathState transitioned to OK state")
        else:
            Except.throw_exception(
                    "ON Command Failed",
                    "Not allowed",
                    ErrSeverity.WARN,
                )

    def action_assignresources(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to .
        """
        obsstate_attribute = model.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "EMPTY"):
            set_enum(obsstate_attribute, "RESOURCING", model.time_func())
            enum_int = get_enum_int("RESOURCING",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in RESOURCING")
            model.logger.info("ObsState trasnitioned to RESOURCING")

            time.sleep(1)
            set_enum(obsstate_attribute, "IDLE", model.time_func())
            enum_int = get_enum_int("IDLE",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in Idle")
            model.logger.info("ObsState trasnitioned to IDLE")
            
        else:
            Except.throw_exception(
                "Assign Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_endscan(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to .
        """
        obsstate_attribute = model.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "SCANNING"):
            set_enum(obsstate_attribute, "READY", model.time_func())
            enum_int = get_enum_int("READY",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in READY")
            model.logger.info("ObsState trasnitioned to READY")            
        else:
            Except.throw_exception(
                "EndScan Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        
    def action_abort(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to .
        """
        _allowed_obsstate = (
            "IDLE",
            "READY",
            "SCANNING",
            "CONFIGURING",
            "RESETTING"
        )
        obsstate_attribute = model.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate in _allowed_obsstate):
            set_enum(obsstate_attribute, "ABORTING", model.time_func())
            enum_int = get_enum_int("ABORTING",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in ABORTING")
            model.logger.info("ObsState trasnitioned to ABORTING")
            time.sleep(1)
            set_enum(obsstate_attribute, "ABORTED", model.time_func())
            enum_int = get_enum_int("ABORTED",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in ABORTED")
            model.logger.info("ObsState trasnitioned to ABORTED")
            
        else:
            Except.throw_exception(
                "Abort Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_releaseallresources(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to .
        """
        obsstate_attribute = model.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "IDLE"):
            set_enum(obsstate_attribute, "RESOURCING", model.time_func())
            enum_int = get_enum_int("RESOURCING",model)
            tango_dev.push_change_event("obsState",enum_int)
            tango_dev.set_status("ObsState in RESOURCING")
            model.logger.info("ObsState trasnitioned to RESOURCING")

            time.sleep(1)
            set_enum(obsstate_attribute, "EMPTY", model.time_func())
            enum_int = get_enum_int("EMPTY",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in EMPTY")
            model.logger.info("ObsState trasnitioned to EMPTY")
           
        else:
            Except.throw_exception(
                "Release Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_configure(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to .
        """
        _allowed_obsstate = (
            "IDLE",
            "READY"
        )
        obsstate_attribute = model.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate in _allowed_obsstate):
            set_enum(obsstate_attribute, "CONFIGURING", model.time_func())
            enum_int = get_enum_int("CONFIGURING",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in CONFIGURING")
            model.logger.info("ObsState trasnitioned to CONFIGURING")

            time.sleep(1)
            set_enum(obsstate_attribute, "READY", model.time_func())
            enum_int = get_enum_int("READY",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in READY")
            model.logger.info("ObsState trasnitioned to READY")

        else:
            Except.throw_exception(
                "Configure Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_scan(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to .
        """
        obsstate_attribute = model.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "READY"):
            set_enum(obsstate_attribute, "SCANNING", model.time_func())
            enum_int = get_enum_int("SCANNING",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in SCANNING")
            model.logger.info("ObsState trasnitioned to SCANNING")

            time.sleep(10)
            set_enum(obsstate_attribute, "READY", model.time_func())
            enum_int = get_enum_int("READY",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in READY")
            model.logger.info("ObsState trasnitioned to READY")
        else:
            Except.throw_exception(
                "Scan Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        

    def action_gotoidle(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to .
        """
        obsstate_attribute = model.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "READY"):
            set_enum(obsstate_attribute, "IDLE", model.time_func())
            enum_int = get_enum_int("IDLE",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in IDLE")
            model.logger.info("ObsState trasnitioned to IDLE")
            
        else:
            Except.throw_exception(
                "gotoidle Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_restart(self, model, tango_dev=None, data_input=None):# pylint: disable=W0613
        """Changes the State of the device to .
        """
        obsstate_attribute = model.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "ABORTED"):
            set_enum(obsstate_attribute, "EMPTY", model.time_func())
            enum_int = get_enum_int("EMPTY",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in EMPTY")
            model.logger.info("ObsState trasnitioned to EMPTY")
            
        else:
            Except.throw_exception(
                "Restart Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
            
    def action_obsreset(self, model, tango_dev=None, data_input=None): # pylint: disable=W0613
        """Changes the State of the device to .
        """
        obsstate_attribute = model.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        if (obsstate == "ABORTED"):
            set_enum(obsstate_attribute, "IDLE", model.time_func())
            enum_int = get_enum_int("IDLE",model)
            tango_dev.push_change_event("obsState", enum_int)
            tango_dev.set_status("ObsState in IDLE")
            model.logger.info("ObsState trasnitioned to IDLE")
            
        else:
            Except.throw_exception(
                "Obsreset Command Failed",
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

def get_enum_int(value,model):
    """Returns the enum label of an enumerated data type

    :param quantity: object
        The quantity object of a DevEnum attribute
    :return: str
        Current string value of a DevEnum attribute
    """
    enum_int = model.sim_quantities["obsState"].meta["enum_labels"].index(value)
    return enum_int

def set_enum(quantity, label, timestamp):
    """Sets the quantity last_val attribute to index of label

    :param quantity: object
        The quantity object from model
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

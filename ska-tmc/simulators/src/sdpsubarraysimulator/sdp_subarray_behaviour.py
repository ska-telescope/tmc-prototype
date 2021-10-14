# -*- coding: utf-8 -*-
"""
override class with command handlers for SdpSubarray.
"""
# Standard python imports
import enum
import logging
import time
import json
import threading

# Tango import
from tango import DevState, Except, ErrSeverity

# Additional import

from ska.base import SKABaseDevice
from ska.base.control_model import ObsState
from ska.base.commands import ResultCode

MODULE_LOGGER = logging.getLogger(__name__)


class OverrideSdpSubarray(object):
    def action_on(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ON."""
        _allowed_modes = (DevState.OFF, DevState.STANDBY)
        if tango_dev.get_state() == DevState.ON:
            model.logger.info("SDP Subarray is already in ON state")
            return [[ResultCode.OK], ["SDP Subarray is already in ON state"]]

        if tango_dev.get_state() in _allowed_modes:
            tango_dev.set_state(DevState.ON)
            model.logger.info("SDP Subarray transitioned to the ON state.")
            sdp_mode_healthState = model.sim_quantities["healthState"]
            set_enum(sdp_mode_healthState, "OK", model.time_func())
        else:
            Except.throw_exception(
                "ON Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["On command successful on simulator."]]

    def action_off(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to OFF."""
        _allowed_modes = (DevState.ON, DevState.STANDBY, DevState.ALARM)
        if tango_dev.get_state() == DevState.OFF:
            model.logger.info("SDP Subarray is already in OFF state")
            return [[ResultCode.OK], ["SDP Subarray is already in OFF state"]]

        if tango_dev.get_state() in _allowed_modes:
            tango_dev.set_state(DevState.OFF)
            model.logger.info("Sdp Subarray transitioned to the OFF state.")
            sdp_mode_healthState = model.sim_quantities["healthState"]
            set_enum(sdp_mode_healthState, "OK", model.time_func())
            model.logger.info("heathState transitioned to OK state")
        else:
            Except.throw_exception(
                "ON Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["Off command successful on simulator."]]

    def action_assignresources(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ."""
        obsstate_attribute = model.sim_quantities["obsState"]
        obs_state = get_enum_str(obsstate_attribute)
        if obs_state == "EMPTY":
            set_enum(obsstate_attribute, "RESOURCING", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "RESOURCING")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in RESOURCING")
            model.logger.info("ObsState trasnitioned to RESOURCING")

            time.sleep(1)
            receive_address_value = json.dumps(
                {
                    "science_A": {
                        "host": [
                            [0, "192.168.0.1"],
                            [400, "192.168.0.2"],
                            [744, "192.168.0.3"],
                            [1144, "192.168.0.4"],
                        ],
                        "mac": [[0, "06-00-00-00-00-00"], [744, "06-00-00-00-00-01"]],
                        "port": [
                            [0, 9000, 1],
                            [400, 9000, 1],
                            [744, 9000, 1],
                            [1144, 9000, 1],
                        ],
                    },
                    "calibration_B": {
                        "host": [[0, "192.168.1.1"]],
                        "port": [[0, 9000, 1]],
                    },
                }
            )
            model.sim_quantities["receiveAddresses"].set_val(
                receive_address_value, model.time_func()
            )
            tango_dev.push_change_event("receiveAddresses", receive_address_value)
            set_enum(obsstate_attribute, "IDLE", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "IDLE")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in Idle")
            model.logger.info("ObsState trasnitioned to IDLE")

        else:
            Except.throw_exception(
                "Assign Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["Assign resources command successful on simulator."]]

    def action_sdpsubarrayfault(self, model, tango_dev=None, data_input=None):
        tango_dev.set_state(DevState.FAULT)
        tango_dev.push_change_event("State", tango_dev.get_state())

    def action_reset(self, model, tango_dev=None, data_input=None
    ):
        if tango_dev.get_state() == DevState.FAULT:
            tango_dev.set_state(DevState.OFF)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Reset command successful on simulator.")

    def action_endscan(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ."""
        obsstate_attribute = model.sim_quantities["obsState"]
        obs_state = get_enum_str(obsstate_attribute)
        if obs_state == "SCANNING":
            set_enum(obsstate_attribute, "READY", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "READY")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in READY")
            model.logger.info("ObsState trasnitioned to READY")
        else:
            Except.throw_exception(
                "EndScan Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["EndScan command successful on simulator."]]

    def action_abort(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ."""
        _allowed_obsstate = ("IDLE", "READY", "SCANNING", "CONFIGURING", "RESETTING")
        obsstate_attribute = model.sim_quantities["obsState"]
        obs_state = get_enum_str(obsstate_attribute)
        if obs_state in _allowed_obsstate:
            set_enum(obsstate_attribute, "ABORTING", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "ABORTING")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in ABORTING")
            model.logger.info("ObsState trasnitioned to ABORTING")
            time.sleep(1)
            set_enum(obsstate_attribute, "ABORTED", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "ABORTED")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in ABORTED")
            model.logger.info("ObsState trasnitioned to ABORTED")

        else:
            Except.throw_exception(
                "Abort Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["Abort command successful on simulator."]]

    def action_releaseresources(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ."""
        obsstate_attribute = model.sim_quantities["obsState"]
        obs_state = get_enum_str(obsstate_attribute)
        if obs_state == "IDLE":
            set_enum(obsstate_attribute, "RESOURCING", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "RESOURCING")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in RESOURCING")
            model.logger.info("ObsState trasnitioned to RESOURCING")

            time.sleep(1)
            set_enum(obsstate_attribute, "EMPTY", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "EMPTY")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in EMPTY")
            model.logger.info("ObsState trasnitioned to EMPTY")

        else:
            Except.throw_exception(
                "Release Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        return [
            [ResultCode.OK],
            ["Release_resources command successful on simulator."],
        ]

    def action_configure(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ."""
        _allowed_obsstate = ("IDLE", "READY")
        obsstate_attribute = model.sim_quantities["obsState"]
        obs_state = get_enum_str(obsstate_attribute)
        if obs_state in _allowed_obsstate:
            set_enum(obsstate_attribute, "CONFIGURING", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(
                obsstate_attribute, "CONFIGURING"
            )
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in CONFIGURING")
            model.logger.info("ObsState trasnitioned to CONFIGURING")
            time.sleep(1)
            set_enum(obsstate_attribute, "READY", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "READY")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in READY")
            model.logger.info("ObsState trasnitioned to READY")

        else:
            Except.throw_exception(
                "Configure Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["Configure command successful on simulator."]]

    def action_scan(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ."""
        obsstate_attribute = model.sim_quantities["obsState"]
        obs_state = get_enum_str(obsstate_attribute)
        if obs_state == "READY":
            set_enum(obsstate_attribute, "SCANNING", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "SCANNING")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in SCANNING")
            model.logger.info("ObsState trasnitioned to SCANNING")
            # create thread
            self.logger.info("Starting thread to to execute scan.")
            scan_thread = threading.Thread(
                target=self.execute_scan(obsstate_attribute, model, tango_dev)
            )
            scan_thread.start()

        else:
            Except.throw_exception(
                "Scan Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["Scan command successful on simulator."]]

    def action_end(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ."""
        obsstate_attribute = model.sim_quantities["obsState"]
        obs_state = get_enum_str(obsstate_attribute)
        if obs_state == "READY":
            set_enum(obsstate_attribute, "IDLE", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "IDLE")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in IDLE")
            model.logger.info("ObsState trasnitioned to IDLE")

        else:
            Except.throw_exception(
                "gotoidle Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["End command successfull on simulator."]]

    def action_restart(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ."""
        obsstate_attribute = model.sim_quantities["obsState"]
        obs_state = get_enum_str(obsstate_attribute)
        if obs_state == "ABORTED":
            set_enum(obsstate_attribute, "RESTARTING", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "RESTARTING")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in RESTARTING")
            model.logger.info("ObsState trasnitioned to RESTARTING")
            time.sleep(2)
            set_enum(obsstate_attribute, "EMPTY", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "EMPTY")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in EMPTY")
            model.logger.info("ObsState trasnitioned to EMPTY")

        else:
            Except.throw_exception(
                "Restart Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["Restart command successful on simulator."]]

    def action_obsreset(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ."""
        obsstate_attribute = model.sim_quantities["obsState"]
        obs_state = get_enum_str(obsstate_attribute)
        if obs_state == "ABORTED":
            set_enum(obsstate_attribute, "RESETTING", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "RESETTING")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in RESETTING")
            model.logger.info("ObsState trasnitioned to RESETTING")
            time.sleep(2)
            set_enum(obsstate_attribute, "IDLE", model.time_func())
            sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "IDLE")
            tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
            tango_dev.set_status("ObsState in IDLE")
            model.logger.info("ObsState trasnitioned to IDLE")

        else:
            Except.throw_exception(
                "Obsreset Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["ObsReset command successful on simulator."]]

    def execute_scan(self, obsstate_attribute, model, tango_dev):
        time.sleep(10)
        set_enum(obsstate_attribute, "READY", model.time_func())
        sdp_subarray_obs_state_enum = get_enum_int(obsstate_attribute, "READY")
        tango_dev.push_change_event("obsState", sdp_subarray_obs_state_enum)
        tango_dev.set_status("ObsState in READY")
        model.logger.info("ObsState trasnitioned to READY")


def get_enum_str(quantity):
    """Returns the enum label of an enumerated data type

    :param quantity: tango_simlib.quantities.Quantity
        The quantity object of a DevEnum attribute
    :return: str
        Current string value of a DevEnum attribute
    """
    EnumClass = enum.IntEnum("EnumLabels", quantity.meta["enum_labels"], start=0)
    return EnumClass(quantity.last_val).name


def get_enum_int(quantity, label):
    """Returns the integer index value of an enumerated data type
    :param quantity: tango_simlib.quantities.Quantity
        The quantity object of a DevEnum attribute
    :param label: str
        The desired value in enum list
    :return: Int
        Current integer value of a DevEnum attribute
    """
    return quantity.meta["enum_labels"].index(label)


def set_enum(quantity, label, timestamp):
    """Sets the quantity last_val attribute to index of label

    :param quantity: tango_simlib.quantities.Quantity
        The quantity object of a DevEnum attribute
    :param label: str
        The desired label from enum list
    :param timestamp: float
        The time now
    """
    value = quantity.meta["enum_labels"].index(label)
    quantity.set_val(value, timestamp)

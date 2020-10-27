# -*- coding: utf-8 -*-
"""
override class with command handlers for dsh-lmc.
"""
import time
import enum
import logging

from collections import namedtuple

from tango import Except, ErrSeverity

MODULE_LOGGER = logging.getLogger(__name__)

AzEl = namedtuple("AzEl", ["azim", "elev"])


class OverrideDish(object):
    TS_IDX = 0
    AZIM_IDX = 1
    ELEV_IDX = 2
    # az & el limits for desired/achieved pointing
    MAINT_AZIM = 90.0
    MAX_DESIRED_AZIM = 270.0
    MIN_DESIRED_AZIM = -270.0
    MAX_DESIRED_ELEV = 90.0
    MIN_DESIRED_ELEV = 15.0
    # unit for drive rate in degrees per second
    AZIM_DRIVE_MAX_RATE = 3.0
    ELEV_DRIVE_MAX_RATE = 1.0
    # ack code interpretation
    OK = 0
    FAILED = 2
    # limit on number of desiredPointing samples to keep
    # (calls to pre_update happen once per second)
    MAX_SAMPLE_HISTORY = 2400

    # initialise positions to match achievedPointing and
    # desiredPointing values in ska_mpi_dsh_lmc.fgo
    requested_position = AzEl(azim=0.0, elev=30.0)
    actual_position = AzEl(azim=0.0, elev=30.0)
    desired_pointings = []

    # Latest update between programTrackTable and desiredPointing
    last_coordinate_update_timestamp = 0.0

    def _configureband(self, model, timestamp, band_number):
        _allowed_modes = ('STANDBY-FP', 'OPERATE', 'STOW')
        ds_indexer_position = model.sim_quantities['dsIndexerPosition']
        configured_band = model.sim_quantities['configuredBand']
        dish_mode_quantity = model.sim_quantities['dishMode']
        dish_mode = get_enum_str(dish_mode_quantity)
        if dish_mode in _allowed_modes:
            set_enum(dish_mode_quantity, 'CONFIG', timestamp)
            model.logger.info("Configuring DISH to operate in frequency band {}."
                              .format(band_number))
            # Sleep for some time to allow the dishMode to remain in 'CONFIG' to simulate
            # the real DSH LMC.
            time.sleep(2)
            # timestamp (data_input) generated by proxy for desiredPointing is converted
            # to .2f pecision as required by data_format in the fgo file. use same
            # conversion for now
            now = float('%.2f' % model.time_func())
            set_enum(ds_indexer_position, 'B{}'.format(band_number), now)
            set_enum(configured_band, 'B{}'.format(band_number), now)
            model.logger.info("Done configuring DISH to operate in frequency band"
                              " {}.".format(band_number))
            model.logger.info("DISH reverting back to '{}' mode.".format(
                dish_mode))
            now = float('%.2f' % model.time_func())
            set_enum(dish_mode_quantity, dish_mode, now)
        else:
            Except.throw_exception("DISH Command Failed",
                                   "DISH is not in {} mode.".format(_allowed_modes),
                                   "ConfigureBand{}()".format(band_number),
                                   ErrSeverity.WARN)

    def action_configureband1(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the CONFIGURE Dish Element
        Mode, and returns to the caller. To configure the Dish to operate in frequency
        band 1. On completion of the band configuration, Dish will automatically
        revert to the previous Dish mode (OPERATE or STANDBY-FP).

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._configureband(model, data_input, '1')

    def action_configureband2(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the CONFIGURE Dish Element
        Mode, and returns to the caller. To configure the Dish to operate in frequency
        band 2. On completion of the band configuration, Dish will automatically
        revert to the previous Dish mode (OPERATE or STANDBY-FP).

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._configureband(model, data_input, '2')

    def action_configureband3(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the CONFIGURE Dish Element
        Mode, and returns to the caller. To configure the Dish to operate in frequency
        band 3. On completion of the band configuration, Dish will automatically
        revert to the previous Dish mode (OPERATE or STANDBY-FP).

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._configureband(model, data_input, '3')

    def action_configureband4(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the CONFIGURE Dish Element
        Mode, and returns to the caller. To configure the Dish to operate in frequency
        band 4. On completion of the band configuration, Dish will automatically
        revert to the previous Dish mode (OPERATE or STANDBY-FP).

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._configureband(model, data_input, '4')

    def action_configureband5a(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the CONFIGURE Dish Element
        Mode, and returns to the caller. To configure the Dish to operate in frequency
        band 5a. On completion of the band configuration, Dish will automatically
        revert to the previous Dish mode (OPERATE or STANDBY-FP).

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._configureband(model, data_input, '5a')

    def action_configureband5b(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the CONFIGURE Dish Element
        Mode, and returns to the caller. To configure the Dish to operate in frequency
        band 5b. On completion of the band configuration, Dish will automatically
        revert to the previous Dish mode (OPERATE or STANDBY-FP).

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._configureband(model, data_input, '5b')

    def action_configureband5c(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the CONFIGURE Dish Element
        Mode, and returns to the caller. To configure the Dish to operate in frequency
        band 5c. On completion of the band configuration, Dish will automatically
        revert to the previous Dish mode (OPERATE or STANDBY-FP).

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._configureband(model, data_input, '5c')

    def _throw_exception(self, command, allowed_modes):
        Except.throw_exception("DISH Command Failed",
                               "DISH is not in {} mode.".format(allowed_modes),
                               "{}()".format(command),
                               ErrSeverity.WARN)

    def action_lowpower(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the LOW power
        state. All subsystems go into a low power state to power only the
        essential equipment. Specifically the Helium compressor will be set
        to a low power consumption, and the drives will be disabled. When
        issued a STOW command while in LOW power, the DS controller
        should be able to turn the drives on, stow the dish and turn the
        drives off again. The purpose of this mode is to enable the
        observatory to perform power management (load curtailment), and
        also to conserve energy for non-operating dishes.

        data_input: None
        """
        _allowed_modes = ('STOW', 'MAINTENANCE')
        dish_mode = get_enum_str(model.sim_quantities['dishMode'])
        if dish_mode in _allowed_modes:
            now = float('%.2f' % model.time_func())
            set_enum(model.sim_quantities['powerState'], 'LOW', now)
            model.logger.info("Dish transitioning to 'LOW' power state.")
        else:
            self._throw_exception('LowPower', _allowed_modes)

    def _reset_pointing_state(self, model):
        action = "NONE"
        pointing_state_quantity = model.sim_quantities['pointingState']
        pointing_state = get_enum_str(pointing_state_quantity)
        if pointing_state != action:
            model.logger.info("Current pointingState is {}."
                              .format(pointing_state))
            now = float('%.2f' % model.time_func())
            set_enum(pointing_state_quantity, action, now)
            model.logger.info("pointingState reset to 'NONE'.")
        else:
            model.logger.warning("pointingState is already '{}'."
                                 .format(action))

    def action_setmaintenancemode(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the MAINTENANCE
        Dish Element Mode, and returns to the caller. To go into a state that
        is safe to approach the Dish by a maintainer, and to enable the
        Engineering interface to allow direct access to low level control and
        monitoring by engineers and maintainers. This mode will also enable
        engineers and maintainers to upgrade SW and FW. Dish also enters
        this mode when an emergency stop button is pressed.

        data_input: None
        """
        _allowed_modes = ('STANDBY-LP', 'STANDBY-FP')
        dish_mode_quantity = model.sim_quantities['dishMode']
        dish_mode = get_enum_str(dish_mode_quantity)

        if dish_mode == "MAINTENANCE":
            return [[self.OK], ["DISH is already in 'MAINTENANCE' mode"]]

        if dish_mode in _allowed_modes:
            now = float('%.2f' % model.time_func())
            elev = self.MIN_DESIRED_ELEV
            desiredPointing = [0.0] * len(
                model.sim_quantities['desiredPointing'].last_val)
            desiredPointing[self.TS_IDX] = now
            desiredPointing[self.AZIM_IDX] = self.MAINT_AZIM
            desiredPointing[self.ELEV_IDX] = elev
            model.sim_quantities['desiredPointing'].set_val(desiredPointing, now)
            set_enum(dish_mode_quantity, 'MAINTENANCE', now)
            model.logger.info("Dish transitioned to the 'MAINTENANCE' mode.")
            self._reset_pointing_state(model)
        else:
            self._throw_exception('SetMaintenanceMode', _allowed_modes)
        return [[self.OK], ["Dish transitioned to 'MAINTENANCE' Mode"]]

    def action_setoperatemode(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the OPERATE Dish
        Element Mode, and returns to the caller. This mode fulfils the main
        purpose of the Dish, which is to point to designated directions while
        capturing data and transmitting it to CSP.

        data_input: None
        """
        _allowed_modes = ('STANDBY-FP',)
        dish_mode_quantity = model.sim_quantities['dishMode']
        dish_mode = get_enum_str(dish_mode_quantity)

        if dish_mode == "OPERATE":
            return [[self.OK], ["DISH is already in 'OPERATE' mode"]]

        if dish_mode in _allowed_modes:
            configuredBand = model.sim_quantities['configuredBand']
            band_error_labels = ['NONE', 'UNKNOWN', 'ERROR', 'UNDEFINED']
            if configuredBand in band_error_labels:
                Except.throw_exception("DISH Command Failed",
                                       "Configured band is {} .".format(configuredBand),
                                       "SetOperateMode()",
                                       ErrSeverity.WARN)
            now = float('%.2f' % model.time_func())
            set_enum(dish_mode_quantity, 'OPERATE', now)
            model.logger.info("Dish transitioned to the 'OPERATE' Dish Element Mode.")
            pointing_state_quantity = model.sim_quantities['pointingState']
            set_enum(pointing_state_quantity, 'READY', now)
            model.logger.info("Dish pointing state set to 'READY'.")
        else:
            self._throw_exception('SetOperateMode', _allowed_modes)
        return [[self.OK], ["Dish transitioned to 'OPERATE' Mode"]]

    def action_setstandbyfpmode(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the STANDBY-FP Dish
        Element Mode, and returns to the caller. To prepare all subsystems
        for active observation, once a command is received by TM to go to the
        FULL_POWER mode.

        data_input: None
        """
        _allowed_modes = ('STANDBY-LP', 'STOW', 'OPERATE', 'MAINTENANCE')
        dish_mode_quantity = model.sim_quantities['dishMode']
        dish_mode = get_enum_str(dish_mode_quantity)

        if dish_mode == "STANDBY-FP":
            return [[self.OK], ["DISH is already in 'STANDBY-FP' mode"]]

        if dish_mode in _allowed_modes:
            now = float('%.2f' % model.time_func())
            set_enum(dish_mode_quantity, 'STANDBY-FP', now)
            model.logger.info("Dish transitioned to the 'STANDBY-FP' Dish Element Mode.")
            self._reset_pointing_state(model)
        else:
            self._throw_exception('SetStandbyFPMode', _allowed_modes)
        return [[self.OK], ["Dish transitioned to 'STANDBY-FP' mode"]]

    def action_setstandbylpmode(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the STANDBY-LP Dish Element
        Mode, and returns to the caller. Standby_LP is the default mode when the Dish
        is configured for low power consumption, and is the mode wherein Dish ends after
        a start up procedure.

        data_input: None
        """
        _allowed_modes = ('OFF', 'STARTUP', 'SHUTDOWN', 'STANDBY-FP',
                          'MAINTENANCE', 'STOW', 'CONFIG', 'OPERATE')
        dish_mode_quantity = model.sim_quantities['dishMode']
        dish_mode = get_enum_str(dish_mode_quantity)

        if dish_mode == "STANDBY-LP":
            return [[self.OK], ["DISH is already in 'STANDBY-LP' mode"]]

        if dish_mode in _allowed_modes:
            now = float('%.2f' % model.time_func())
            set_enum(dish_mode_quantity, 'STANDBY-LP', now)
            model.logger.info("Dish transitioned to the 'STANDBY-LP' Dish Element Mode.")
            self._reset_pointing_state(model)
        else:
            self._throw_exception('SetStandbyLPMode', _allowed_modes)
        return [[self.OK], ["Dish transitioned to 'STANDBY-LP' mode"]]

    def action_setstowmode(self, model, tango_dev=None, data_input=None):
        """This command triggers the Dish to transition to the STOW Dish
        Element Mode, and returns to the caller. To point the dish in a
        direction that minimises the wind loads on the structure, for survival
        in strong wind conditions. The Dish is able to observe in the stow
        position, for the purpose of transient detection.

        data_input: None
        """
        _allowed_modes = ('OFF', 'STARTUP', 'SHUTDOWN', 'STANDBY-LP', 'STANDBY-FP',
                          'MAINTENANCE', 'CONFIG', 'OPERATE')
        dish_mode_quantity = model.sim_quantities['dishMode']
        dish_mode = get_enum_str(dish_mode_quantity)

        if dish_mode == "STOW":
            return [[self.OK], ["DISH is already in 'STOW' mode"]]

        if dish_mode in _allowed_modes:
            now = float('%.2f' % model.time_func())
            elev = self.MAX_DESIRED_ELEV
            current_azim = (
                model.sim_quantities['achievedPointing'].last_val[self.AZIM_IDX])
            desiredPointing = (
                [0.0] * len(model.sim_quantities['desiredPointing'].last_val))
            desiredPointing[self.TS_IDX] = now
            desiredPointing[self.AZIM_IDX] = current_azim
            desiredPointing[self.ELEV_IDX] = elev
            model.sim_quantities['desiredPointing'].set_val(desiredPointing, now)
            set_enum(dish_mode_quantity, 'STOW', now)
            model.logger.info("Dish transitioned to the 'STOW' Dish Element Mode.")
            self._reset_pointing_state(model)
        else:
            self._throw_exception('SetStowMode', _allowed_modes)
        return [[self.OK], ["Dish transitioned to 'STOW' mode."]]

    def _change_pointing_state(self, model, data_input, action, allowed_modes):
        dish_mode_quantity = model.sim_quantities['dishMode']
        dish_mode = get_enum_str(dish_mode_quantity)
        if dish_mode not in allowed_modes:
            self._throw_exception(action, allowed_modes)

        pointing_state_quantity = model.sim_quantities['pointingState']
        pointing_state = get_enum_str(pointing_state_quantity)
        if pointing_state != action:
            now = float('%.2f' % model.time_func())
            try:
                if now > float(data_input):
                    Except.throw_exception("DISH Command Failed",
                                           "Requested timestamp has expired.",
                                           "{}()".format(action), ErrSeverity.WARN)
            except TypeError:
                pass
            set_enum(pointing_state_quantity, action, now)
            model.logger.info("Dish pointingState set to {}.".format(action))
        else:
            model.logger.warning("pointingState is already '{}'."
                                 .format(action))

    def action_track(self, model, tango_dev=None, data_input=None):
        """The Dish is tracking the commanded pointing positions within the
        specified TRACK pointing accuracy.

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._change_pointing_state(model, data_input, 'TRACK', ('OPERATE',))
        model.logger.info("'Track' command executed successfully.")

    def action_trackstop(self, model, tango_dev=None, data_input=None):
        """The Dish will stop tracking but will not apply brakes.
        Stops movement, but doesn't clear tables/queues.

        data_input: None
        """
        dish_mode = model.sim_quantities['dishMode']
        dish_mode = get_enum_str(dish_mode)
        _allowed_mode = "OPERATE"

        if dish_mode != _allowed_mode:
            Except.throw_exception("DISH Command Failed",
                                   "DISH is not in {} mode.".format(_allowed_mode),
                                   "TrackStop",
                                   ErrSeverity.WARN)

        pointing_state = model.sim_quantities['pointingState']
        now = float('%.2f' % model.time_func())
        set_enum(pointing_state, 'READY', now)

    def action_resettracktable(self, model, tango_dev=None, data_input=None):
        """Resets the coordinates in the queue. Clear ACU's table (should show number of
        coordinates drops to zero)

        data_input: None
        """
        now = float('%.2f' % model.time_func())
        program_track_quantity = model.sim_quantities['programTrackTable']
        track_table_size = len(program_track_quantity.last_val)
        default_values = [0.0] * track_table_size
        model.sim_quantities['programTrackTable'].set_val(default_values, now)

    def action_resettracktablebuffer(self, model, tango_dev=None, data_input=None):
        """Resets the Dish LMC's buffer. (In our case it's desired_pointings)

        data_input: None
        """
        self.desired_pointings = []

    def action_slew(self, model, tango_dev=None, data_input=None):
        """The Dish moves to the commanded pointing angle at the maximum
        speed, as defined by the specified slew rate.

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._change_pointing_state(model, data_input, 'SLEW', ('OPERATE',))
        model.logger.info("'Slew' command executed successfully.")

    def action_scan(self, model, tango_dev=None, data_input=None):
        """ The Dish is tracking the commanded pointing positions within the
        specified SCAN pointing accuracy.

        data_input: str
            Timestamp in UTC at which command execution should start
        """
        self._change_pointing_state(model, data_input, 'SCAN', ('OPERATE',))
        model.logger.info("'Scan' command executed successfully.")

    def find_next_position(self, desired_pointings, sim_time):
        """Return the latest desiredPointing not in the future, or last requested."""
        best_pointing = None
        for pointing in desired_pointings:
            timestamp = pointing[self.TS_IDX] / 1000.0  # convert ms to sec
            if timestamp <= sim_time:
                best_pointing = pointing
            else:
                break  # all other samples are in the future
        if best_pointing is not None:
            return AzEl(azim=best_pointing[self.AZIM_IDX],
                        elev=best_pointing[self.ELEV_IDX])
        else:
            # no useful samples, so use last requested position
            return self.requested_position

    @staticmethod
    def is_movement_allowed(model):
        pointing_state = get_enum_str(model.sim_quantities['pointingState'])
        return pointing_state in ['SLEW', 'TRACK', 'SCAN']

    def is_on_target(self):
        actual = self.actual_position
        target = self.requested_position
        return (self._almost_equal(actual.azim, target.azim)
                and self._almost_equal(actual.elev, target.elev))

    def update_movement_attributes(self, model, sim_time):
        self.set_lock_attribute(model, self.is_on_target())
        self.set_achieved_pointing_attribute(model, sim_time, self.actual_position)

    @staticmethod
    def set_lock_attribute(model, target_reached):
        target_lock = model.sim_quantities['targetLock']
        if target_lock.last_val != target_reached:
            target_lock.last_val = target_reached
            model.logger.info("Attribute 'targetLock' set to %s.", target_reached)

    def set_achieved_pointing_attribute(self, model, sim_time, position):
        # use millisecond timestamp
        sim_time *= 1000
        achievedPointing = [0, 0, 0]
        achievedPointing[self.TS_IDX] = sim_time
        achievedPointing[self.AZIM_IDX] = position.azim
        achievedPointing[self.ELEV_IDX] = position.elev
        model.sim_quantities['achievedPointing'].set_val(achievedPointing, sim_time)
        model.logger.info("Attribute 'achievedPointing' updated to: val: {!r}".format(
            achievedPointing))

    def get_rate_limited_position(self, current_pos, next_pos, dt):
        # calc required deltas in az and el
        required_delta_azim = abs(current_pos.azim - next_pos.azim)
        required_delta_elev = abs(current_pos.elev - next_pos.elev)

        # calc max deltas in az and el due to speed limits
        max_slew_azim = self.AZIM_DRIVE_MAX_RATE * dt
        max_slew_elev = self.ELEV_DRIVE_MAX_RATE * dt

        # limit
        allowed_delta_azim = min(max_slew_azim, required_delta_azim)
        allowed_delta_elev = min(max_slew_elev, required_delta_elev)

        # get direction signs: +1 or -1
        sign_azim = get_direction_sign(current_pos.azim, next_pos.azim)
        sign_elev = get_direction_sign(current_pos.elev, next_pos.elev)

        return AzEl(
            azim=(current_pos.azim + sign_azim * allowed_delta_azim),
            elev=(current_pos.elev + sign_elev * allowed_delta_elev),
        )

    def ensure_within_mechanical_limits(self, next_pos):
        if (next_pos.azim > self.MAX_DESIRED_AZIM
                or next_pos.azim < self.MIN_DESIRED_AZIM):
            Except.throw_exception(
                "Skipping dish movement.",
                "Desired azimuth angle '%s' is out of pointing limits %s."
                % (next_pos.azim, [self.MIN_DESIRED_AZIM, self.MAX_DESIRED_AZIM]),
                "ensure_within_mechanical_limits()",
                ErrSeverity.WARN)
        elif (next_pos.elev > self.MAX_DESIRED_ELEV
                or next_pos.elev < self.MIN_DESIRED_ELEV):
            Except.throw_exception(
                "Skipping dish movement.",
                "Desired elevation angle '%s' is out of pointing limits %s."
                % (next_pos.elev, [self.MIN_DESIRED_ELEV, self.MAX_DESIRED_ELEV]),
                "ensure_within_mechanical_limits()",
                ErrSeverity.WARN)

    def move_towards_target(self, sim_time, dt):
        next_requested_pos = self.find_next_position(self.desired_pointings, sim_time)
        self.requested_position = next_requested_pos

        self.ensure_within_mechanical_limits(next_requested_pos)
        next_achievable_pos = self.get_rate_limited_position(
            self.actual_position, next_requested_pos, dt)
        self.actual_position = next_achievable_pos

    def get_new_unverified_pointings(self, model):
        """Return the latest list of coordinates

        Parameters
        ----------
        model : Model
            The device Model

        Returns
        -------
        List
            - Empty if no updates have occured since the last time
            - 1 entry of desiredPointing if it is the latest
            - All the entries of programTrackTable if it is the latest (7 in testing)
        """
        programTrackTable_last_update = model.sim_quantities[
            "programTrackTable"
        ].last_update_time
        desiredPointing_last_update = model.sim_quantities[
            "desiredPointing"
        ].last_update_time

        if programTrackTable_last_update > desiredPointing_last_update:
            if programTrackTable_last_update > self.last_coordinate_update_timestamp:
                self.last_coordinate_update_timestamp = programTrackTable_last_update
                all_values = model.sim_quantities["programTrackTable"].last_val
                assert len(all_values) % 3 == 0, ("Length of programTrackTable should ",
                                                  "be divisble by 3")
                # Group in 3s
                return list(map(list, zip(*(iter(all_values),) * 3)))
        else:
            if desiredPointing_last_update > self.last_coordinate_update_timestamp:
                self.last_coordinate_update_timestamp = desiredPointing_last_update
                return [model.sim_quantities["desiredPointing"].last_val]
        return []

    def get_new_valid_pointings(self, model):
        unverified_pointings = self.get_new_unverified_pointings(model)
        now_millisec = model.time_func() * 1000.0
        return [
            pointing for pointing in unverified_pointings
            if pointing[self.TS_IDX] >= now_millisec
        ]

    def update_desired_pointing_history(self, model):
        latest_pointings = self.get_new_valid_pointings(model)
        self.desired_pointings.extend(latest_pointings)
        if len(self.desired_pointings) > self.MAX_SAMPLE_HISTORY:
            # drop older samples
            self.desired_pointings = self.desired_pointings[-self.MAX_SAMPLE_HISTORY:]

    def pre_update(self, model, sim_time, dt):
        if self.is_movement_allowed(model):
            self.update_desired_pointing_history(model)
            self.move_towards_target(sim_time, dt)
            self.update_movement_attributes(model, sim_time)
        else:
            model.logger.debug("Skipping quantity updates - movement not allowed")

    def _almost_equal(self, x, y, abs_threshold=5e-3):
        '''Takes two values return true if they are almost equal'''
        return abs(x - y) <= abs_threshold


def get_enum_str(quantity):
    """Returns the enum label of an enumerated data type

    Parameters
    ----------
    quantity : object
        The quantity object of a DevEnum attribute

    Returns
    -------
    return_value : str
        Current string value of a DevEnum attribute
    """
    EnumClass = enum.IntEnum('EnumLabels', quantity.meta['enum_labels'], start=0)
    return EnumClass(quantity.last_val).name


def set_enum(quantity, label, timestamp):
    """Sets the quantity last_val attribute to index of label

    Parameters
    ----------
    quantity : object
        The quantity object from model
    label : str
        The desired label from enum list
    timestamp : float
        The time now
    """
    value = quantity.meta['enum_labels'].index(label)
    quantity.set_val(value, timestamp)


def get_direction_sign(here, there):
    """Return sign (+1 or -1) required to move from here to there."""
    return 1 if here < there else -1
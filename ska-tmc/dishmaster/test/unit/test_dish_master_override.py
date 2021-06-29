#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the SKA Dish simulator.
"""

import pkg_resources
import time
import pytest

from tango_simlib import tango_sim_generator
from dishmaster.dish_master_behaviour import AzEl, OverrideDish, get_enum_str, set_enum

FGO_FILE_PATH = pkg_resources.resource_filename("dishmaster", "dish_master.fgo")
JSON_FILE_PATH = pkg_resources.resource_filename("dishmaster", "dish_master_SimDD.json")


class TestMpiDshModel:
    @pytest.fixture(scope="function")
    def provision_setup(self):
        model = tango_sim_generator.configure_device_models(
            [FGO_FILE_PATH, JSON_FILE_PATH], "test/nodb/mpidish"
        )
        return model["test/nodb/mpidish"], OverrideDish()

    def test_update_desired_pointing_history(self, provision_setup):
        """Check the logic in get_new_pointing_coordinates and that the update gets
        applied correctly
        """
        # Note: coords are are sets of 3: [timestamp, azim, elev]
        device_model, dish_override = provision_setup
        now = time.time()
        now_millisec = now * 1000.0
        dish_override.desired_pointings = [[now_millisec + 10.0, 2.0, 3.0]]
        desired_pointing_coordinates = [now_millisec + 40.0, 5.0, 6.0]
        program_track_table_coordinates = [
            now_millisec + 70.0,
            8.0,
            9.0,
            now_millisec + 100.0,
            11.0,
            12.0,
        ]

        # desiredPointing is newest, so must be used
        dish_override.last_coordinate_update_timestamp = now - 5.0
        device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 3.0
        )
        device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 2.0
        )
        current_pointings = list(dish_override.desired_pointings)
        dish_override.update_desired_pointing_history(device_model)
        expected_pointings = current_pointings + [desired_pointing_coordinates]
        assert dish_override.desired_pointings == expected_pointings

        # programTrackTable is newest, so must be used
        dish_override.last_coordinate_update_timestamp = now - 5.0
        device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 3.0
        )
        device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 2.0
        )
        current_pointings = list(dish_override.desired_pointings)
        dish_override.update_desired_pointing_history(device_model)
        expected_pointings = (
            current_pointings
            + [program_track_table_coordinates[0:3]]
            + [program_track_table_coordinates[3:6]]
        )
        assert dish_override.desired_pointings == expected_pointings

        # Neither is newest, so no update expected
        current_pointings = list(dish_override.desired_pointings)
        dish_override.last_coordinate_update_timestamp = now
        device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 2.0
        )
        device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 3.0
        )
        dish_override.update_desired_pointing_history(device_model)
        assert dish_override.desired_pointings == current_pointings
        device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 3.0
        )
        device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 2.0
        )
        dish_override.update_desired_pointing_history(device_model)
        assert dish_override.desired_pointings == current_pointings

        # New updates, but timestamps in the past, so no update expected
        desired_pointing_coordinates = [now_millisec - 40.0, 5.0, 6.0]
        program_track_table_coordinates = [
            now_millisec - 60.0,
            8.0,
            9.0,
            now_millisec - 50.0,
            10.0,
            11.0,
        ]

        dish_override.last_coordinate_update_timestamp = now - 10
        device_model.sim_quantities["desiredPointing"].set_val(desired_pointing_coordinates, now)
        device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 1.0
        )
        dish_override.update_desired_pointing_history(device_model)
        assert dish_override.desired_pointings == current_pointings

        dish_override.last_coordinate_update_timestamp = now - 10
        device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 1.0
        )
        device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now
        )
        dish_override.update_desired_pointing_history(device_model)
        assert dish_override.desired_pointings == current_pointings

    def test_pointing_state_reports_track_when_on_target(self, provision_setup):
        device_model, dish_override = provision_setup
        now = time.time()
        timestamp_ms = now * 1000.0

        # requested new pointing position
        desired_pointing_coordinates = [timestamp_ms + 40.0, 10, 40]
        device_model.sim_quantities["desiredPointing"].set_val(desired_pointing_coordinates, now)
        # ensure dish is in allowed mode before requesting track and check pointing state is SLEW
        set_enum(device_model.sim_quantities["dishMode"], "OPERATE", now)
        dish_override.action_track(device_model)
        current_pointing_state = get_enum_str(device_model.sim_quantities["pointingState"])
        assert current_pointing_state == "SLEW"

        # move the dish to the desired position and check that pointing state is TRACK
        device_model.sim_quantities["achievedPointing"].set_val(desired_pointing_coordinates, now)
        dish_override.update_movement_attributes(device_model, now)
        current_pointing_state = get_enum_str(device_model.sim_quantities["pointingState"])
        assert current_pointing_state == "TRACK"

    def test_achieved_pointing_changes_when_dish_is_stowing(self, provision_setup):
        device_model, dish_override = provision_setup
        # send the dish closer to the stow position
        dish_override.requested_position = AzEl(azim=0.0, elev=82.0)
        dish_override.actual_position = AzEl(azim=0.0, elev=82.0)
        # record initial az, el before movement
        initial_az = device_model.sim_quantities["achievedPointing"].last_val[1]
        initial_el = device_model.sim_quantities["achievedPointing"].last_val[2]

        # request stow mode and move the dish close to the stow position
        dish_override.action_setstowmode(device_model)
        stow_position = dish_override.STOW_ELEV_POSITION
        dish_far_from_target = True
        last_time = time.time()
        timeout = time.time() + 5  # 5 seconds from now
        while dish_far_from_target:
            start_time = time.time()
            dish_override.pre_update(device_model, start_time, start_time - last_time)
            last_time = start_time
            current_el = device_model.sim_quantities["achievedPointing"].last_val[2]
            dish_far_from_target = not (stow_position - current_el == pytest.approx(1, abs=1))
            time.sleep(1)
            if timeout < start_time:
                raise(Exception("Timeout occurred"))

        current_az = device_model.sim_quantities["achievedPointing"].last_val[1]
        current_el = device_model.sim_quantities["achievedPointing"].last_val[2]

        assert current_el != initial_el, "The stow command did not move the dish at all"
        assert (
            current_az == initial_az
        ), "The dish should only move in elevation to stow, azimuth movement detected"
        assert stow_position - current_el == pytest.approx(
            1, abs=1
        ), "Dish did not arrive at stow position"

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the SKA Dish simulator.
"""

import pkg_resources
import time
import pytest

from tango_simlib import tango_sim_generator
from dishmaster.dish_master_behaviour import OverrideDish

FGO_FILE_PATH = pkg_resources.resource_filename("dishmaster", "dish_master.fgo")
JSON_FILE_PATH = pkg_resources.resource_filename("dishmaster", "dish_master_SimDD.json")


class TestMpiDshModel:
    device_model = None
    dish_override = None

    @pytest.fixture(scope="class")
    def provision_setup(self):
        model = tango_sim_generator.configure_device_models(
            [FGO_FILE_PATH, JSON_FILE_PATH], "test/nodb/mpidish"
        )
        self.device_model = model["test/nodb/mpidish"]
        self.dish_override = OverrideDish()


    def test_update_desired_pointing_history(self, provision_setup):
        """Check the logic in get_new_pointing_coordinates and that the update gets
        applied correctly
        """
        # Note: coords are are sets of 3: [timestamp, azim, elev]
        now = time.time()
        now_millisec = now * 1000.0
        self.dish_override.desired_pointings = [[now_millisec + 10.0, 2.0, 3.0]]
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
        self.dish_override.last_coordinate_update_timestamp = now - 5.0
        self.device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 3.0
        )
        self.device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 2.0
        )
        current_pointings = list(self.dish_override.desired_pointings)
        self.dish_override.update_desired_pointing_history(self.device_model)
        expected_pointings = current_pointings + [desired_pointing_coordinates]
        self.assertEqual(self.dish_override.desired_pointings, expected_pointings)

        # programTrackTable is newest, so must be used
        self.dish_override.last_coordinate_update_timestamp = now - 5.0
        self.device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 3.0
        )
        self.device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 2.0
        )
        current_pointings = list(self.dish_override.desired_pointings)
        self.dish_override.update_desired_pointing_history(self.device_model)
        expected_pointings = (
            current_pointings
            + [program_track_table_coordinates[0:3]]
            + [program_track_table_coordinates[3:6]]
        )
        self.assertEqual(self.dish_override.desired_pointings, expected_pointings)

        # Neither is newest, so no update expected
        current_pointings = list(self.dish_override.desired_pointings)
        self.dish_override.last_coordinate_update_timestamp = now
        self.device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 2.0
        )
        self.device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 3.0
        )
        self.dish_override.update_desired_pointing_history(self.device_model)
        self.assertEqual(self.dish_override.desired_pointings, current_pointings)
        self.device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 3.0
        )
        self.device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 2.0
        )
        self.dish_override.update_desired_pointing_history(self.device_model)
        self.assertEqual(self.dish_override.desired_pointings, current_pointings)

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

        self.dish_override.last_coordinate_update_timestamp = now - 10
        self.device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now
        )
        self.device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now - 1.0
        )
        self.dish_override.update_desired_pointing_history(self.device_model)
        self.assertEqual(self.dish_override.desired_pointings, current_pointings)

        self.dish_override.last_coordinate_update_timestamp = now - 10
        self.device_model.sim_quantities["desiredPointing"].set_val(
            desired_pointing_coordinates, now - 1.0
        )
        self.device_model.sim_quantities["programTrackTable"].set_val(
            program_track_table_coordinates, now
        )
        self.dish_override.update_desired_pointing_history(self.device_model)
        self.assertEqual(self.dish_override.desired_pointings, current_pointings)

    def test_pointing_state_reports_track_when_on_target(self, provision_setup):
        pass
    
import importlib.resources

import katpoint

from .device_data import DeviceData


class AzElConverter:
    def __init__(self, log):
        self.logger = log

    def create_antenna_obj(self):
        """ This method identifies the KATPoint.Antenna object to be used from the Dish Number. """
        try:
            device_data = DeviceData.get_instance()

            with importlib.resources.open_text(
                "src.ska_tmc_dishleafnode_mid.src.ska_tmc_dishleafnode_mid",
                "ska_antennas.txt",
            ) as f:
                ska_antennas = f.readlines()
            antennas = [
                katpoint.Antenna(antenna_details)
                for antenna_details in ska_antennas
            ]
        except OSError as err:
            self.logger.exception(err)
            raise Exception(
                f"OSError.'{err}'in device_data.create_antenna_obj."
            )
        except ValueError as verr:
            self.logger.exception(verr)
            raise Exception(
                f"ValueError.'{verr}'in device_data.create_antenna_obj."
            )

        for ant in antennas:
            if ant.name == device_data.dish_number:
                device_data.observer = ant

    def point(self, ra_value, dec_value, timestamp):
        """This method converts Target RaDec coordinates to the AzEl coordinates. It is called
        continuosly from Track command (in a thread) at interval of 50ms till the StopTrack command is invoked.
        """
        device_data = DeviceData.get_instance()
        # Create KATPoint Target object
        target = katpoint.Target.from_radec(ra_value, dec_value)
        # obtain az el co-ordinates for dish
        azel = target.azel(timestamp, device_data.observer)
        # list of az el co-ordinates
        az_el_coordinates = [azel.az.deg, azel.alt.deg]
        return az_el_coordinates

    def download_IERS_file(self):
        """This method performs one pointing calculation with dummy values to download the IERS file in advanced
        to the potinting calcualtions on DishLeafNode."""
        # Create an example radec target
        ra = "21:08:47.92"
        dec = "-88:57:22.9"
        target = katpoint.Target.from_radec(ra, dec)
        ant = katpoint.Antenna(
            "0001, -30:42:39.8d, 21:26:38d, 1086, 13.5, 1.1205 -171.762 8.4705, , 0.0"
        )
        timestamp = "2021-04-29 05:36:50.031567"
        azel = target.azel(timestamp, ant)
        self.logger.info("IERS file downloading is completed: '%s'", azel)

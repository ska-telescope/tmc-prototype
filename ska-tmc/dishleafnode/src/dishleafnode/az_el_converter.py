import katpoint
import importlib.resources
from .device_data import DeviceData

class AzElConverter:
    def __init__(self, log):
        self.logger = log
        self.logger.info("In AzElConverter init: '%s' ", str(self.logger))

    def create_antenna_obj(self):
        """ This method identifies the KATPoint.Antenna object to be used from the Dish Number. """
        try:
            device_data = DeviceData.get_instance()

            with importlib.resources.open_text("dishleafnode", "ska_antennas.txt") as f:
                ska_antennas = f.readlines()
            antennas = [
                katpoint.Antenna(antenna_details) for antenna_details in ska_antennas
            ]
        except OSError as err:
            self.logger.exception(err)
            raise Exception(f"OSError.'{err}'in device_data.create_antenna_obj.")
        except ValueError as verr:
            self.logger.exception(verr)
            raise Exception(f"ValueError.'{verr}'in device_data.create_antenna_obj.")

        for ant in antennas:
            if ant.name == device_data.dish_number:
                device_data.observer = ant
            self.logger.info("ant: '%s'", str(ant))

    def point(self, ra_value, dec_value, timestamp):
        """This method converts Target RaDec coordinates to the AzEl coordinates. It is called
        continuosly from Track command (in a thread) at interval of 50ms till the StopTrack command is invoked.
        """
        self.logger.info("In point function: '%s'", str(ra_value))
        device_data = DeviceData.get_instance()
        self.logger.info("device_data 5: '%s'", str(device_data))
        self.logger.info("katpoint.Target 6: '%s'", str(katpoint.Target))
        # Create KATPoint Target object
        target = katpoint.Target.from_radec(ra_value, dec_value)
        self.logger.info("target 7: '%s'", str(target))
        # obtain az el co-ordinates for dish
        azel = target.azel(timestamp, device_data.observer)
        self.logger.info("azel 8: '%s'", str(azel))
        # list of az el co-ordinates
        az_el_coordinates = [azel.az.deg, azel.alt.deg]
        self.logger.info("device_data.observer: '%s' ", str(device_data.observer))
        self.logger.info("ra_value: '%s'", str(ra_value))
        self.logger.info("dec_value: '%s'", str(dec_value))
        self.logger.info("timestamp: '%s' ", str(timestamp))
        self.logger.info("az_el_coordinates: '%s' ", str(az_el_coordinates))
        return az_el_coordinates
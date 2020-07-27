"""
Module for DishLeafNode utils
"""

# Imports
import enum
import math
import re
import logging

module_logger = logging.getLogger(__name__)


# In future, PointingState class will be moved to a file for all the enum attributes for DishLeafNode.
class PointingState(enum.IntEnum):
    """
    Pointing state of the dish.
    """
    READY = 0
    SLEW = 1
    TRACK = 2
    SCAN = 3


class UnitConverter:
    def __init__(self, logger=module_logger):
        self.logger = logger

    def dms_to_rad(self, argin):
        """
        Converts a number in Deg:Min:Sec to radians.

        :param argin: list of numbers in degrees, minutes, seconds respectively in string.

        Example: ['20', '30', '40']

        :return: A number in radians.

        Example: 20.500193925472445 is the returned value for ['20', '30', '40'] input.

        """
        try:
            degrees = float(argin[0])
            minutes = float(argin[1])
            seconds = float(argin[2])
            rad_value = ((math.pi / 180) * (degrees + (minutes / 60) + (seconds / 3600)))
            return rad_value
        except IndexError as error:
            log_msg = "Error while converting Deg:Min:Sec to radians." + str(error)
            self.logger.error(log_msg)
        except SyntaxError as error:
            log_msg = "Error while converting Deg:Min:Sec to radians." + str(error)
            self.logger.error(log_msg)


    def rad_to_dms(self, argin):
        """
        Converts a number in radians to Deg:Min:Sec.

        :param argin: A number in radians.

        Example: 0.123472

        :return: List of numbers in degrees, minutes, seconds respectively in string.

        Example: [7.0, 4.0, 27.928156941480466] is returned value for input 0.123472.

        """
        try:
            dms = []
            frac_min, degrees = math.modf(argin * (180 / math.pi))
            frac_sec, minutes = math.modf(frac_min * 60)
            seconds = frac_sec * 60
            dms.append(degrees)
            dms.append(minutes)
            dms.append(seconds)
            return dms
        except SyntaxError as error:
            log_msg = "Error while converting radians to dig:min:sec." + str(error)
            self.logger.error(log_msg)

    def dms_to_dd(self, argin):
        """
        Converts a number in dig:Min:sec to decimal degrees.

        :param argin: A number in Deg:Min:Sec.

        Example: 18:31:48.0

        :return: A number in decimal Degrees.

        Example : "18.529999999999998" is the returned value for 18:31:48.0 input.

        """
        try:
            dd = re.split('[:]+', argin)
            deg_dec = abs(float(dd[0])) + ((float(dd[1])) / 60) + ((float(dd[2])) / 3600)
            if "-" in dd[0]:
                return deg_dec * (-1)
            else:
                return deg_dec
        except IndexError as error:
            log_msg = "Error while converting Deg:Min:Sec to decimal degrees." + str(error)
            self.logger.error(log_msg)
        except SyntaxError as error:
            log_msg = "Error while converting Deg:Min:Sec to decimal degrees." + str(error)
            self.logger.error(log_msg)

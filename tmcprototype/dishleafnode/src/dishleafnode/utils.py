"""
Module for DishLeafNode utils
"""

# Imports
import enum
import math
import re


class PointingState(enum.IntEnum):
    """
    Pointing state of the dish.
    """
    READY = 0
    SLEW = 1
    TRACK = 2
    SCAN = 3


class UnitConverter:
    def __init__(self):
        pass

    def dms_to_rad(self, dms):
        """
        Converts a number in Deg:Min:Sec to radians.

        :param argin: list of numbers in degrees, minutes, seconds respectively in string.

        Example: ['20', '30', '40']

        :return: A number in radians.

        Example: 20.500193925472445 is the returned value for ['20', '30', '40'] input.

        """
        deg = float(dms[0])
        min = float(dms[1])
        sec = float(dms[2])
        rad_value = ((math.pi / 180) * ((deg) + (min / 60) + (sec / 3600)))
        return rad_value

    def rad_to_dms(self, rad_value):
        """
        Converts a number in radians to dig:min:sec.

        :param argin: A number in radians.

        Example: 0.123472

        :return: List of numbers in degrees, minutes, seconds respectively in string.

        Example: [7.0, 4.0, 27.928156941480466] is returned value for input 0.123472.

        """
        dms = []
        frac_min, deg = math.modf(rad_value * (180 / math.pi))
        frac_sec, min = math.modf(frac_min * 60)
        sec = frac_sec * 60
        dms.append(deg)
        dms.append(min)
        dms.append(sec)
        return dms

    def dms_to_dd(self, angle):
        """
        Converts a number in dig:min:sec to decimal degrees.

        :param angle: A number in Deg:Min:Sec.

        Example: 18:31:48.0

        :return: A number in decimal Degrees.

        Example : "18.529999999999998" is the returned value for 18:31:48.0 input.

        """
        dd = re.split('[:]+', angle)
        deg_dec = abs(float(dd[0])) + ((float(dd[1])) / 60) + ((float(dd[2])) / 3600)
        if "-" in dd[0]:
            return deg_dec * (-1)
        else:
            return deg_dec

"""
Module for DishLeafNode utils
"""
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
        Converts dig:min:sec to radians.
        """
        deg = float(dms[0])
        min = float(dms[1])
        sec = float(dms[2])
        rad_value = ((math.pi / 180) * ((deg) + (min / 60) + (sec / 3600)))
        return rad_value

    def rad_to_dms(self, rad_value):
        """
        Converts radians to dig:min:sec.
        """
        dms = []
        frac_min, deg = math.modf(rad_value * (180 / math.pi))
        frac_sec, min = math.modf(frac_min * 60)
        sec = frac_sec * 60
        dms.append(deg)
        dms.append(min)
        dms.append(sec)
        return dms

    def dms_to_dd(self, dish_antenna_latitude):
        """
        Converts latitude from deg:min:sec to decimal degree format.

        :param dish_antenna_latitude: latitude of Dish location in Deg:Min:Sec.
        Example: 18:31:48.0

        :return: latitude of Dish location in decimal Degree.

        Example : "18.529999999999998" is the returned value of dmstodd
        """
        dd = re.split('[:]+', dish_antenna_latitude)
        deg_dec = abs(float(dd[0])) + ((float(dd[1])) / 60) + ((float(dd[2])) / 3600)
        if "-" in dd[0]:
            return deg_dec * (-1)
        else:
            return deg_dec

"""
Test cases for DishLeafNode's utils module.
"""

# import statements
import math
from dishleafnode.utils import UnitConverter


class TestUnitConverter:
    """
    Class to test UnitConverter's methods.
    """
    def test_dms_to_rad(self):
        """
        This function tests whether dms_to_rad() converts dig:min:sec to radians correctly.
        """
        ref_input = ['10', '11', '12.1']
        expected_output = (float(ref_input[0]) + (float(ref_input[1]) / 60) + (float(ref_input[2]) / 3600))\
                          * (math.pi / 180)
        actual_output = UnitConverter().dms_to_rad(ref_input)
        assert actual_output == expected_output

    def test_rad_to_dms(self):
        """
        This function tests whether rad_to_dms() converts radians to dig:min:sec correctly.
        """
        ref_input = 0.1866052706727415
        ref_input_dd = ref_input * (180 / math.pi)
        expected_output = []
        expected_output.append(float(int(ref_input_dd)))
        expected_output.append(float(int((ref_input_dd-int(ref_input_dd)) * 60)))
        expected_output.append((((ref_input_dd-int(ref_input_dd)) * 60)-int((ref_input_dd-int(ref_input_dd))
                                                                            * 60)) * 60)
        actual_output = UnitConverter().rad_to_dms(ref_input)
        assert actual_output == expected_output

    def test_dms_to_dd(self):
        """
        This function tests whether dms_to_dd() converts deg:min:sec to decimal degree correctly.
        """
        ref_input = '10:11:12.1'
        ref_input_list = ref_input.split(":")
        expected_output = float(ref_input_list[0]) + (float(ref_input_list[1]) / 60) +\
                          (float(ref_input_list[2]) / 3600)
        actual_output = UnitConverter().dms_to_dd(ref_input)
        assert actual_output == expected_output

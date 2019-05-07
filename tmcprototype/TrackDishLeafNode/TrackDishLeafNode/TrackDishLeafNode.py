# -*- coding: utf-8 -*-
#
# This file is part of the TrackDishLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" TrackDishLeafNode

"""

# PyTango imports
import tango
from tango import DebugIt, ApiUtil
from tango.server import run
from tango.server import Device, DeviceMeta
from tango.server import attribute, command
from tango import AttrQuality, DispLevel, DevState
from tango import AttrWriteType, PipeWriteType, DeviceProxy
# Additional import
# PROTECTED REGION ID(TrackDishLeafNode.additionnal_import) ENABLED START #
import katpoint
import re
import numpy
import datetime
import math
import time
import threading
# PROTECTED REGION END #    //  TrackDishLeafNode.additionnal_import

__all__ = ["TrackDishLeafNode", "main"]


class TrackDishLeafNode(Device):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(TrackDishLeafNode.class_variable) ENABLED START #

    def dmstodd(self, dish_antenna_latitude):
        # Convert latitude from deg:min:sec to degree decimal
        dd = re.split('[:]+', dish_antenna_latitude)
        deg_dec = abs(float(dd[0])) + ((float(dd[1])) / 60) + ((float(dd[2])) / 3600)
        if "-" in dd[0]:
            return deg_dec * (-1)
        else:
            return deg_dec

    def convert_radec_to_azel(self, data):
        try:
            # Setting Observer Position as Pune
            dish_antenna = katpoint.Antenna(name='d1',
                                            latitude='18:31:48:00',
                                            longitude='73:50:23.99',
                                            altitude=570)
            # Antenna latitude
            dish_antenna_latitude = dish_antenna.ref_observer.lat
            # Compute Target Coordinates
            target_radec = data[0]
            desired_target = katpoint.Target(target_radec)
            timestamp = katpoint.Timestamp(timestamp=data[1])
            target_apparnt_radec = katpoint.Target.apparent_radec(desired_target,
                                                                  timestamp=timestamp,
                                                                  antenna=dish_antenna)

            # TODO: Conversion of apparent ra and dec using katpoint library for future refererence.
            # target_apparnt_ra = katpoint._ephem_extra.angle_from_hours(target_apparnt_radec[0])
            # target_apparnt_dec = katpoint._ephem_extra.angle_from_degrees(target_apparnt_radec[1])

            # calculate sidereal time in radians
            side_time = dish_antenna.local_sidereal_time(timestamp=timestamp)
            side_time_radian = katpoint.deg2rad(math.degrees(side_time))

            # converting ra to ha
            hour_angle = side_time_radian - target_apparnt_radec[0]

            # TODO: Conversion of hour angle from radian to HH:MM:SS for future refererence.
            # print("Hour angle in hours: ", katpoint._ephem_extra.angle_from_hours(hour_angle))

            # Geodetic latitude of the observer
            # TODO: For refererence
            latitude_degree_decimal = self.dmstodd(str(dish_antenna_latitude))
            latitude_radian = katpoint.deg2rad(latitude_degree_decimal)
            # Calculate enu coordinates
            enu_array = katpoint.hadec_to_enu(hour_angle, target_apparnt_radec[1], latitude_radian)

            # Calculate Az El coordinates
            self.az_el_coordinates = katpoint.enu_to_azel(enu_array[0], enu_array[1], enu_array[2])
            self.az = katpoint.rad2deg(self.az_el_coordinates[0])
            if self.az < 0:
                self.az = 360 + self.az
            print("Az coordinate: ", self.az)
            self.el = katpoint.rad2deg(self.az_el_coordinates[1])
            print("El Coordinate: ", self.el)

        except Exception as except_occurred:
            print("Exception occured in Conversion")


    def commandCallback(self, event):
        """
        Checks whether the command has been successfully invoked on DishMaster.
        :param event: response from DishMaster for the invoked command
        :return: None
        """
        try:
            #print("timestamp_commandCallback(): ", datetime.datetime.utcnow())
            if event.err:
                log = "Error in invoking command:" + event.cmd_name
                print("Error in invoking command:" + event.cmd_name + "\n" + str(event.errors))
                self._read_activity_message = "Error in invoking command:" + str(event.cmd_name) + "\n" + str(
                    event.errors)
            else:
                log = "Command :-> " + event.cmd_name + " invoked successfully."
                print(log)
                self._read_activity_message = log
        except Exception as except_occurred:
            print("Exception in CommandCallback!: \n", except_occurred)
            self._read_activity_message = "Exception in CommandCallback!: \n" + str(except_occurred)


    def track(self,argin):
        for i in range(20):
            try:
                #Jive Input : radec|2:31:50.91|89:15:51.4   #Polaris
                radec_value = argin.replace('|', ',')
                #timestamp_value = argin[1].replace('|', ' ')
                timestamp_value = str(datetime.datetime.utcnow())
                print("\n")
                print(i ,"th iteration")
                katpoint_arg = []
                katpoint_arg.insert(0, radec_value)
                katpoint_arg.insert(1, timestamp_value)
                self.convert_radec_to_azel(katpoint_arg)

                # Invoke Track command on DishMaster with az and el as inputs
                if (self.el >= 17.5 and self.el < 90):
                    # To obtain positive value of azimuth coordinate
                    if self.az < 0:
                        self.az = 360 - abs(self.az)
                    roundoff_az_el = [round(self.az, 2), round(self.el, 2)]
                    spectrum = [0]
                    spectrum.extend((roundoff_az_el))
                    self._dish_proxy.desiredPointing = spectrum
                    print("self._dish_proxy.desiredPointing", self._dish_proxy.desiredPointing)

                    self._dish_proxy.command_inout_asynch("Track", timestamp_value, self.commandCallback)
                else:
                    print("Elevation limit is reached")
                    break
            except Exception as except_occurred:
                print("Exception occured in Track")
            time.sleep(0.098)

    # PROTECTED REGION END #    //  TrackDishLeafNode.class_variable

    # ----------
    # Attributes
    # ----------

    ATTR1 = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
    )

    ATTR2 = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(TrackDishLeafNode.init_device) ENABLED START #
        self._dish_proxy = DeviceProxy("mid_d0001/elt/master")
        self._attr1 = 0
        self._attr2 = ""
        ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
        # PROTECTED REGION END #    //  TrackDishLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(TrackDishLeafNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TrackDishLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(TrackDishLeafNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TrackDishLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_ATTR1(self):
        # PROTECTED REGION ID(TrackDishLeafNode.ATTR1_read) ENABLED START #
        return self._attr1
        # PROTECTED REGION END #    //  TrackDishLeafNode.ATTR1_read

    def write_ATTR1(self, value):
        # PROTECTED REGION ID(TrackDishLeafNode.ATTR1_write) ENABLED START #
	    self._attr1 = value
        #pass
        # PROTECTED REGION END #    //  TrackDishLeafNode.ATTR1_write

    def read_ATTR2(self):
        # PROTECTED REGION ID(TrackDishLeafNode.ATTR2_read) ENABLED START #
        return self._attr2
        # PROTECTED REGION END #    //  TrackDishLeafNode.ATTR2_read

    def write_ATTR2(self, value):
        # PROTECTED REGION ID(TrackDishLeafNode.ATTR2_write) ENABLED START #
	    self._attr2 = value
        #pass
        # PROTECTED REGION END #    //  TrackDishLeafNode.ATTR2_write


    # --------
    # Commands
    # --------

    @command(
    dtype_in=('str',), 
    dtype_out=('str',), 
    )
    @DebugIt()
    def TRACK(self, argin):
        self.track_thread = threading.Thread(None, self.track, 'TrackDishLeafNode', args=argin)
        self.track_thread.start()

        return [""]

        # PROTECTED REGION END #    //  TrackDishLeafNode.TRACK


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(TrackDishLeafNode.main) ENABLED START #
    return run((TrackDishLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  TrackDishLeafNode.main

if __name__ == '__main__':
    main()

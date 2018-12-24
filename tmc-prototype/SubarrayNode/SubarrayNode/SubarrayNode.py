# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Subarray Node

Provides the monitoring and control interface required by users as well as
other TM Components (such as OET, Central Node) for a Subarray.
"""

# tango imports
import random
import string

import tango
from tango import DebugIt, DevState, AttrWriteType
from tango.server import run, DeviceMeta, attribute, command, device_property
from SKASubarray import SKASubarray
# Additional import
# PROTECTED REGION ID(SubarrayNode.additionnal_import) ENABLED START #
import CONST
# PROTECTED REGION END #    //  SubarrayNode.additionnal_import

__all__ = ["SubarrayNode", "main"]


class SubarrayNode(SKASubarray):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SubarrayNode.class_variable) ENABLED START #

    @command(
        dtype_in=('str',),
        doc_in="Execute Scan on the Subarray",
    )
    @DebugIt()
    def Scan(self, argin):
        """
        This function schedules a scan for execution on a subarray. Command has a parameter which
        indicates the time (TAI) at which the Scan will start. Subarray transitions to
        obsState = SCANNING, when the execution of a scan starts.
        :param argin:
        :return:
        """
        try:
            print CONST.STR_SCAN_IP_ARG, argin
            print CONST.STR_GRP_DEF, self._dish_leaf_node_group.get_device_list()

            self._read_activity_message = CONST.STR_SCAN_IP_ARG + str(argin)
            self._read_activity_message = CONST.STR_GRP_DEF\
                                          + str(self._dish_leaf_node_group.get_device_list())
            cmdData = tango.DeviceData()
            cmdData.insert(tango.DevString, argin[0])
            self._dish_leaf_node_group.command_inout(CONST.CMD_SCAN, cmdData)
            self._obs_state = 3
            # set obsState to SCANNING when the scan is started
            self.set_status(CONST.STR_SA_SCANNING)
            self.devlogmsg(CONST.STR_SA_SCANNING, 4)

        except Exception as e:
            print CONST.ERR_SCAN_CMD
            print e

            self._read_activity_message = CONST.ERR_SCAN_CMD + str(e)

            self.devlogmsg(CONST.ERR_SCAN_CMD, 2)

    def is_Scan_allowed(self):
        """ This method is an internal construct of TANGO """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]
    @command(
    )
    @DebugIt()
    def EndScan(self):
        """
        This method schedules an end scan commandcan be either an automatic or an externally
        triggered transition after the scanning completes normally.
        :return:
        """
        try:
            print CONST.STR_GRP_DEF, self._dish_leaf_node_group.get_device_list()
            cmdData = tango.DeviceData()
            cmdData.insert(tango.DevString, "0")
            self._dish_leaf_node_group.command_inout(CONST.CMD_END_SCAN, cmdData)
            self._obs_state = 0
            # set obsState to IDLE when the scan is ended
            self._scan_id = ""
            self._sb_id = ""
            self.set_status(CONST.STR_SCAN_COMPLETE)
            self.devlogmsg(CONST.STR_SCAN_COMPLETE, 4)

        except Exception as e:
            print CONST.ERR_END_SCAN_CMD
            print e

            self._read_activity_message = CONST.ERR_END_SCAN_CMD + str(e)

            self.devlogmsg(CONST.ERR_END_SCAN_CMD, 2)

    def is_EndScan_allowed(self):
        """ This method is an internal construct of TANGO """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]


    @command(
        dtype_in=('str',),
        doc_in="List of Resources to add to subarray.",
        dtype_out=('str',),
        doc_out="A list of Resources added to the subarray.",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        This method issues assign resources command on a subarray.
        :param argin: List of receptors
        :return:
        """
        try:

            for leafId in range(0, len(argin)):
                self._dish_leaf_node_group.add(self.DishLeafNodePrefix +  argin[leafId])
                devProxy = tango.DeviceProxy(self.DishLeafNodePrefix + argin[leafId])
                self._dish_leaf_node_proxy.append(devProxy)
                self._event_id = devProxy.subscribe_event(CONST.EVT_DISH_HEALTH_STATE,
                                                          tango.EventType.CHANGE_EVENT,
                                                          self.setHealth,
                                                          stateless=True)
                self.testDeviceVsEventID[devProxy] = self._event_id
                self._health_event_id.append(self._event_id)
                self._receptor_id_list.append(int(argin[leafId]))
                self.dishHealthStateMap[devProxy] = -1
            print CONST.STR_TEST_DEV_VS_EVT_ID, self.testDeviceVsEventID
            print CONST.STR_GRP_DEF, self._dish_leaf_node_group.get_device_list(True)
            print CONST.STR_LN_PROXIES, self._dish_leaf_node_proxy

            self._read_activity_message = CONST.STR_GRP_DEF\
                                      + str(self._dish_leaf_node_group.get_device_list(True))
            self._read_activity_message = CONST.STR_LN_PROXIES + str(self._dish_leaf_node_proxy)

            print CONST.STR_SUBS_HEALTH_ST_LN

            self._read_activity_message = CONST.STR_SUBS_HEALTH_ST_LN

            print CONST.STR_HS_EVNT_ID, self._health_event_id

            self._read_activity_message = CONST.STR_HS_EVNT_ID +  str(self._health_event_id)

            self.set_state(DevState.ON)
            # Set state = ON
            self._obs_state = 0
            # set obsState to "IDLE"
            self.set_status(CONST.STR_ASSIGN_RES_SUCCESS)
            self.devlogmsg(CONST.STR_ASSIGN_RES_SUCCESS, 4)

        except Exception as e:
            print CONST.ERR_ASSIGN_RES_CMD
            print e

            self._read_activity_message = CONST.ERR_ASSIGN_RES_CMD + str(e)

            self.devlogmsg(CONST.ERR_ASSIGN_RES_CMD, 2)
            argin = str(e)

        return argin

    def is_AssignResources_allowed(self):
        """"""
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]

    @command(
        dtype_out=('str',),
        doc_out="List of resources removed from the subarray.",
    )
    @DebugIt()
    def ReleaseAllResources(self):
        """
        This method releases all the resources from a subarray
        :return:
        """
        argout = []
        try:
            print CONST.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True))
            self._dish_leaf_node_group.remove_all()
            print CONST.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True))

            self._read_activity_message = CONST.STR_GRP_DEF \
                                          + str(self._dish_leaf_node_group.get_device_list(True))

            argout.extend(self._dish_leaf_node_group.get_device_list(True))

            print CONST.STR_DISH_PROXY_LIST, self._dish_leaf_node_proxy
            print CONST.STR_HEALTH_ID, self._health_event_id
            #self._dish_leaf_node_proxy[0].unsubscribe_event(self._health_event_id[0])
            #self._dish_leaf_node_proxy[1].unsubscribe_event(self._health_event_id[1])
            print CONST.STR_TEST_DEV_VS_EVT_ID, self.testDeviceVsEventID

            for dev in self.testDeviceVsEventID:
                dev.unsubscribe_event(self.testDeviceVsEventID[dev])
            self.testDeviceVsEventID = {}
            #
            #     self._dish_leaf_node_proxy[leaf].unsubscribe_event(self._health_event_id[leaf])
            #     print "after unsubscribing"
            self._health_event_id = []
            self._dish_leaf_node_proxy = []
            del self._receptor_id_list[:]

            self._scan_id = ""
            self._sb_id = ""

            self.set_state(DevState.OFF)    # Set state = OFF
            self._obs_state = 0             # set obsState to "IDLE"
            self.set_status(CONST.STR_RECEPTORS_REMOVE_SUCCESS)
            self.devlogmsg(CONST.STR_RECEPTORS_REMOVE_SUCCESS, 4)
        except Exception as e:
            print CONST.ERR_RELEASE_RES_CMD
            print e
            print CONST.STR_DISH_PROXY_LIST, self._dish_leaf_node_proxy
            print CONST.STR_HEALTH_ID, self._health_event_id

            self._read_activity_message = CONST.ERR_RELEASE_RES_CMD + str(e)

            argout = []
            self.devlogmsg(CONST.ERR_RELEASE_RES_CMD, 2)
        return argout

    def is_ReleaseAllResources_allowed(self):
        """"""
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]

    def setHealth(self, evt):
        """
        This method assigns health status of the subarray.
        :param evt: Health status of the subarray
        :return:
        """
        if evt.err is False:
            try:
                self._dish_health_state = evt.attr_value.value
                self.dishHealthStateMap[evt.device] = self._dish_health_state
                if self._dish_health_state == ENUM_OK:
                    print CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_OK
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device)\
                                                  + CONST.STR_OK

                elif self._dish_health_state == ENUM_DEGRADED:
                    print CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_DEGRADED
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device)
                    + CONST.STR_DEGRADED

                elif self._dish_health_state == ENUM_FAILED:
                    print CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_FAILED
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device)
                    + CONST.STR_FAILED

                elif self._dish_health_state == ENUM_UNKNOWN:
                    print CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_UNKNOWN
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device)
                    + CONST.STR_UNKNOWN

                else:
                    print CONST.STR_HEALTH_STATE_UNKNOWN_VAL, evt
                    self._read_activity_message = CONST.STR_HEALTH_STATE_UNKNOWN_VAL + str(evt)

                #Aggregated Health State
                failed = 0
                degraded = 0
                unknown = 0
                ok = 0
                for value in self.dishHealthStateMap.values():
                    if value == 2:
                        failed = failed + 1
                        break
                    elif value == 1:
                        self._health_state = 1
                        degraded = degraded + 1
                    elif value == 3:
                        self._health_state = 3
                        unknown = unknown + 1

                    else:
                        self._health_state = 0
                        ok = ok + 1

                if ok == len(self.dishHealthStateMap.values()):
                    self._health_state = 0

                elif failed != 0:
                    self._health_state = 2

                elif degraded != 0:
                    self._health_state = 1

                else:
                    self._health_state = 3

            except Exception as e:
                print CONST.ERR_AGGR_HEALTH_STATE, e.message
                self._read_activity_message = CONST.ERR_AGGR_HEALTH_STATE + str(e.message)

                self.devlogmsg(CONST.ERR_AGGR_HEALTH_STATE, 2)
        else:
            print CONST.ERR_SUBSR_SA_HEALTH_STATE, evt.errors
            self._read_activity_message = CONST.ERR_SUBSR_SA_HEALTH_STATE + str(evt.errors)
            self.devlogmsg(CONST.ERR_SUBSR_SA_HEALTH_STATE, 2)



    # PROTECTED REGION END #    //  SubarrayNode.class_variable

    # -----------------
    # Device Properties
    # -----------------









    DishLeafNodePrefix = device_property(
        dtype='str', default_value="ska_mid/tm_leaf_node/d"
    )

    # ----------
    # Attributes
    # ----------
















    scanID = attribute(
        dtype='str',
    )

    sbID = attribute(
        dtype='str',
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )



    receptorIDList = attribute(
        dtype=('uint16',),
        max_dim_x=100,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """
        This method initializes the attributes of a subarray node
        :return:
        """
        SKASubarray.init_device(self)
        # PROTECTED REGION ID(SubarrayNode.init_device) ENABLED START #

        self.set_state(DevState.INIT)
        self.set_status(CONST.STR_SA_INIT)
        self.SkaLevel = 2                       # set SKALevel to "2"
        self._admin_mode = 0                    # set adminMode to "ON-LINE"
        self._health_state = 0                  # set health state to "OK"
        self._obs_state = 0                     # set obsState to "IDLE"
        self._obs_mode = 0                     # set obsMode to "IDLE"
        self._simulation_mode = False
        self._scan_id = ""
        self._sb_id = ""
        self._receptor_id_list = []
        self.dishHealthStateMap = {}

        self._dish_leaf_node_group = tango.Group(CONST.GRP_DISH_LEAF_NODE)
        self._dish_leaf_node_proxy = []
        self._health_event_id = []
        self.testDeviceVsEventID = {}
        self.set_state(DevState.OFF)            # Set state = OFF
        self._read_activity_message = CONST.STR_SA_INIT_SUCCESS
        self.set_status(CONST.STR_SA_INIT_SUCCESS)
        self.devlogmsg(CONST.STR_SA_INIT_SUCCESS, 4)

        # PROTECTED REGION END #    //  SubarrayNode.init_device

    def always_executed_hook(self):
        """ This method is an internal construct of TANGO """
        # PROTECTED REGION ID(SubarrayNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SubarrayNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SubarrayNode.delete_device) ENABLED START #
        """ This method is an internal construct of TANGO """
        pass
        # PROTECTED REGION END #    //  SubarrayNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_scanID(self):
        """ This is a getter method for the scanID attribute """
        # PROTECTED REGION ID(SubarrayNode.scanID_read) ENABLED START #
        return self._scan_id
        # PROTECTED REGION END #    //  SubarrayNode.scanID_read

    def read_sbID(self):
        """ This is a getter method for the sbID attribute """
        # PROTECTED REGION ID(SubarrayNode.sbID_read) ENABLED START #
        return self._sb_id
        # PROTECTED REGION END #    //  SubarrayNode.sbID_read

    def read_activityMessage(self):
        """ This is a getter method for the activityMessage attribute """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_read

    def write_activityMessage(self, value):
        """ This is a setter method for activityMessage attribute """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_write

    def read_receptorIDList(self):
        """ This is a getter method for the receptorIDList attribute """
        # PROTECTED REGION ID(SubarrayNode.receptorIDList_read) ENABLED START #
        return self._receptor_id_list
        # PROTECTED REGION END #    //  SubarrayNode.receptorIDList_read


    # --------
    # Commands
    # --------

    @command(
        dtype_in=('str',),
        doc_in="Pointing parameters of Dish - Azimuth and Elevation Angle.",
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(SubarrayNode.Configure) ENABLED START #
        """
        This method issues the configure command for a Dish.
        :param argin: "Pointing parameters of Dish - Azimuth and Elevation Angle."
        :return:
        """
        try:
            print CONST.STR_CONFIGURE_IP_ARG, argin
            print CONST.STR_GRP_DEF_CONFIGURE_FN,
            self._dish_leaf_node_group.get_device_list()

            self._read_activity_message = CONST.STR_CONFIGURE_IP_ARG + str(argin)
            self._read_activity_message = CONST.STR_GRP_DEF_CONFIGURE_FN\
            + str(self._dish_leaf_node_group.get_device_list())

            cmdData = tango.DeviceData()
            cmdData.insert(tango.DevVarStringArray, argin)
            self._obs_state = 1     # set obsState to CONFIGURING when the configuration is started
            self._dish_leaf_node_group.command_inout(CONST.CMD_CONFIGURE, cmdData)
            self._obs_state = 2
            # set obsState to READY when the configuration is completed
            self._scan_id = ''.join(random.choice(string.ascii_uppercase\
            + string.digits) for _ in range(4))
            self._sb_id = ''.join(random.choice(string.ascii_uppercase\
            + string.digits) for _ in range(4))
            self.devlogmsg(CONST.STR_CONFIGURE_CMD_INVOKED_SA, 4)
        except Exception as e:
            print CONST.ERR_CONFIGURE_CMD
            print e

            self._read_activity_message = CONST.ERR_CONFIGURE_CMD + str(e)

            self.devlogmsg(CONST.ERR_CONFIGURE_CMD, 2)

        # PROTECTED REGION END #    //  SubarrayNode.Configure

    def is_Configure_allowed(self):
        # PROTECTED REGION ID(SubarrayNode.is_Configure_allowed) ENABLED START #
        """ This method is an internal construct of TANGO """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]
        # PROTECTED REGION END #    //  SubarrayNode.is_Configure_allowed

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SubarrayNode.main) ENABLED START #
    """
    This method runs the Subarray node.
    :param args:
    :param kwargs:
    :return:
    """
    return run((SubarrayNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SubarrayNode.main

if __name__ == '__main__':
    main()

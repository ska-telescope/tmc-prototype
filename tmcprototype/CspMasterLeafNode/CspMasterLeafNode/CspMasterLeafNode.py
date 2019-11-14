# -*- coding: utf-8 -*-
#
# This file is part of the CspMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" CspMasterLeafNode - Leaf Node to monitor and control CSP Master.

"""

from __future__ import print_function
from __future__ import absolute_import

# Tango imports
import sys
import os
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, DeviceMeta, command, device_property, attribute
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice

# Additional import
# PROTECTED REGION ID(CspMasterLeafNode.additionnal_import) ENABLED START #
from future.utils import with_metaclass
import CONST

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspMasterLeafNode"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)
# PROTECTED REGION END #    //  CspMasterLeafNode.additionnal_import

__all__ = ["CspMasterLeafNode", "main"]

class CspMasterLeafNode(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    **Properties:**

    - CspMasterFQDN   - Property to provide FQDN of CSP Master Device

    **Attributes:**

    - cspHealthState  - Forwarded attribute to provide CSP Master Health State
    - activityMessage - Attribute to provide activity message

    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(CspMasterLeafNode.class_variable) ENABLED START #\
    def cspCbfHealthCallback(self, evt):
        """
        Retrieves the subscribed cspCbfHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspCbfHealthState attribute.

        :return: None
        """
        if evt.err is False:
            try:
                self._csp_cbf_health = evt.attr_value.value
                if self._csp_cbf_health == CONST.ENUM_HEALTH_OK:
                    print(CONST.STR_CSP_CBF_HEALTH_OK)
                    self._read_activity_message = CONST.STR_CSP_CBF_HEALTH_OK
                elif self._csp_cbf_health == CONST.ENUM_HEALTH_DEGRADED:
                    print(CONST.STR_CSP_CBF_HEALTH_DEGRADED)
                    self._read_activity_message = CONST.STR_CSP_CBF_HEALTH_DEGRADED
                elif self._csp_cbf_health == CONST.ENUM_HEALTH_FAILED:
                    print(CONST.STR_CSP_CBF_HEALTH_FAILED)
                    self._read_activity_message = CONST.STR_CSP_CBF_HEALTH_FAILED
                else:
                    print(CONST.STR_CSP_CBF_HEALTH_UNKNOWN)
                    self._read_activity_message = CONST.STR_CSP_CBF_HEALTH_UNKNOWN
            except DevFailed as dev_failed:
                self.devfailed_exception(dev_failed, CONST.ERR_ON_SUBS_CSP_CBF_HEALTH)
                # print(CONST.ERR_ON_SUBS_CSP_CBF_HEALTH, dev_failed)
                # self._read_activity_message = CONST.ERR_ON_SUBS_CSP_CBF_HEALTH + str(dev_failed)
                # self.dev_logging(CONST.ERR_ON_SUBS_CSP_CBF_HEALTH, int(tango.LogLevel.LOG_FATAL))
            except Exception as except_occurred:
                self.exception_generic_exception(except_occurred, CONST.ERR_CSP_CBF_HEALTH_CB)
                # print(CONST.ERR_CSP_CBF_HEALTH_CB, except_occurred.message)
                # self._read_activity_message = CONST.ERR_CSP_CBF_HEALTH_CB + str(except_occurred.message)
                # self.dev_logging(CONST.ERR_CSP_CBF_HEALTH_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_CSP_CBF_HEALTH, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_CSP_CBF_HEALTH + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_CSP_CBF_HEALTH, int(tango.LogLevel.LOG_ERROR))

    def cspPssHealthCallback(self, evt):
        """
        Retrieves the subscribed cspPssHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspPssHealthState attribute.

        :return: None
        """
        if evt.err is False:
            try:
                self._csp_pss_health = evt.attr_value.value
                if self._csp_pss_health == CONST.ENUM_HEALTH_OK:
                    print(CONST.STR_CSP_PSS_HEALTH_OK)
                    self._read_activity_message = CONST.STR_CSP_PSS_HEALTH_OK
                elif self._csp_pss_health == CONST.ENUM_HEALTH_DEGRADED:
                    print(CONST.STR_CSP_PSS_HEALTH_DEGRADED)
                    self._read_activity_message = CONST.STR_CSP_PSS_HEALTH_DEGRADED
                elif self._csp_pss_health == CONST.ENUM_HEALTH_FAILED:
                    print(CONST.STR_CSP_PSS_HEALTH_FAILED)
                    self._read_activity_message = CONST.STR_CSP_PSS_HEALTH_FAILED
                else:
                    print(CONST.STR_CSP_PSS_HEALTH_UNKNOWN)
                    self._read_activity_message = CONST.STR_CSP_PSS_HEALTH_UNKNOWN
            except DevFailed as dev_failed:
                self.devfailed_exception(dev_failed, CONST.ERR_ON_SUBS_CSP_PSS_HEALTH)
                # print(CONST.ERR_ON_SUBS_CSP_PSS_HEALTH, dev_failed)
                # self._read_activity_message = CONST.ERR_ON_SUBS_CSP_PSS_HEALTH + str(dev_failed)
                # self.dev_logging(CONST.ERR_ON_SUBS_CSP_PSS_HEALTH, int(tango.LogLevel.LOG_FATAL))
            except Exception as except_occurred:
                self.exception_generic_exception(CONST.ERR_CSP_PSS_HEALTH_CB)
                # print(CONST.ERR_CSP_PSS_HEALTH_CB, except_occurred.message)
                # self._read_activity_message = CONST.ERR_CSP_PSS_HEALTH_CB + str(except_occurred.message)
                # self.dev_logging(CONST.ERR_CSP_PSS_HEALTH_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_CSP_PSS_HEALTH, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_CSP_PSS_HEALTH + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_CSP_PSS_HEALTH, int(tango.LogLevel.LOG_ERROR))

    def cspPstHealthCallback(self, evt):
        """
        Retrieves the subscribed cspPstHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspPstHealthState attribute.

        :return: None
        """
        if evt.err is False:
            try:
                self._csp_pst_health = evt.attr_value.value
                if self._csp_pst_health == CONST.ENUM_HEALTH_OK:
                    print(CONST.STR_CSP_PST_HEALTH_OK)
                    self._read_activity_message = CONST.STR_CSP_PST_HEALTH_OK
                elif self._csp_pst_health == CONST.ENUM_HEALTH_DEGRADED:
                    print(CONST.STR_CSP_PST_HEALTH_DEGRADED)
                    self._read_activity_message = CONST.STR_CSP_PST_HEALTH_DEGRADED
                elif self._csp_pst_health == CONST.ENUM_HEALTH_FAILED:
                    print(CONST.STR_CSP_PST_HEALTH_FAILED)
                    self._read_activity_message = CONST.STR_CSP_PST_HEALTH_FAILED
                else:
                    print(CONST.STR_CSP_PST_HEALTH_UNKNOWN)
                    self._read_activity_message = CONST.STR_CSP_PST_HEALTH_UNKNOWN
            except DevFailed as dev_failed:
                self.devfailed_exception(dev_failed, CONST.ERR_ON_SUBS_CSP_PSS_HEALTH)
                # print(CONST.ERR_ON_SUBS_CSP_PSS_HEALTH, dev_failed)
                # self._read_activity_message = CONST.ERR_ON_SUBS_CSP_PSS_HEALTH + str(dev_failed)
                # self.dev_logging(CONST.ERR_ON_SUBS_CSP_PSS_HEALTH, int(tango.LogLevel.LOG_FATAL))
            except Exception as except_occurred:
                self.exception_generic_exception(CONST.ERR_CSP_PST_HEALTH_CB)

                # print(CONST.ERR_CSP_PST_HEALTH_CB, except_occurred.message)
                # self._read_activity_message = CONST.ERR_CSP_PST_HEALTH_CB + str(except_occurred.message)
                # self.dev_logging(CONST.ERR_CSP_PST_HEALTH_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_CSP_PST_HEALTH, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_CSP_PST_HEALTH + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_CSP_PST_HEALTH, int(tango.LogLevel.LOG_ERROR))

    def commandCallback(self, event):
        """
        Checks whether the command has been successfully invoked on CSPMaster.

        :param event: response from CspMaster for the invoked command.

        :return: None
        """
        excpt_count = 0
        excpt_msg = []
        try:
            if event.err:
                log = CONST.ERR_INVOKING_CMD + event.cmd_name
                print(CONST.ERR_INVOKING_CMD + event.cmd_name + "\n" + str(event.errors))
                self._read_activity_message = CONST.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                    event.errors)
                self.dev_logging(str(log), int(tango.LogLevel.LOG_ERROR))
            else:
                log = CONST.STR_COMMAND + event.cmd_name + CONST.STR_INVOKE_SUCCESS
                self._read_activity_message = log
                self.dev_logging(log, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occurred:
            self.exception_generic_exception(CONST.ERR_EXCEPT_CMD_CB)
            # print(CONST.ERR_EXCEPT_CMD_CB, except_occurred)
            # self._read_activity_message = CONST.ERR_EXCEPT_CMD_CB + str(except_occurred)
            # self.dev_logging(CONST.ERR_EXCEPT_CMD_CB, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # Throw Exception
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_CSP_CMD_CALLBK, tango.ErrSeverity.ERR)

    #Exception handling
    def devfailed_exception(self, df, read_actvity_msg):
        print(read_actvity_msg, df)
        self.dev_logging(read_actvity_msg + str(df), int(tango.LogLevel.LOG_ERROR))
        self._read_activity_message = read_actvity_msg + str(df)

    def exception_generic_exception(self, read_actvity_msg):
        print(read_actvity_msg, Exception)
        self.dev_logging(read_actvity_msg + str(Exception), int(tango.LogLevel.LOG_ERROR))
        self._read_activity_message = read_actvity_msg + str(Exception)

    # PROTECTED REGION END #    //  CspMasterLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------
    CspMasterFQDN = device_property(
        dtype='str'
    )

    # ----------
    # Attributes
    # ----------

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    cspHealthState = attribute(name="cspHealthState", label="cspHealthState", forwarded=True)
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """
        Initializes the attributes and properties of CSPMasterLeafNode and subscribes change event
        on attributes of CSPMaster.

        :return: None
        """
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(CspMasterLeafNode.init_device) ENABLED START #
        try:
            self._read_activity_message = CONST.STR_CSP_INIT_LEAF_NODE
            self.SkaLevel = CONST.INT_SKA_LEVEL
            self._admin_mode = CONST.ENUM_ADMIN_MODE_ONLINE  # Setting adminMode to "ONLINE"
            self._health_state = CONST.ENUM_HEALTH_OK  # Setting healthState to "OK"
            self._simulation_mode = False  # Enabling the simulation mode
            self._test_mode = "False"

        except DevFailed as dev_failed:
            print(CONST.ERR_INIT_PROP_ATTR)
            self._read_activity_message = CONST.ERR_INIT_PROP_ATTR
            self.devfailed_exception(dev_failed, CONST.ERR_INIT_PROP_ATTR)
            # self.dev_logging(CONST.ERR_INIT_PROP_ATTR, int(tango.LogLevel.LOG_ERROR))
            # self._read_activity_message = CONST.ERR_MSG + str(dev_failed)
            # print(CONST.ERR_MSG, dev_failed)

        try:
            self._read_activity_message = CONST.STR_CSPMASTER_FQDN + str(self.CspMasterFQDN)
            # Creating proxy to the CSPMaster
            print("CSP Master name: ", str(self.CspMasterFQDN))
            self._csp_proxy = DeviceProxy(str(self.CspMasterFQDN))
        except DevFailed as dev_failed:
            print(CONST.ERR_IN_CREATE_PROXY, self.CspMasterFQDN)
            self._read_activity_message = CONST.ERR_IN_CREATE_PROXY + str(self.CspMasterFQDN)
            self.set_state(DevState.FAULT)
            self.devfailed_exception(dev_failed, CONST.ERR_IN_CREATE_PROXY_CSP_MASTER)
            # print(CONST.ERR_MSG, dev_failed)
            # self._read_activity_message = CONST.ERR_MSG + str(dev_failed)
            # self.dev_logging(CONST.ERR_IN_CREATE_PROXY_CSP_MASTER, int(tango.LogLevel.LOG_ERROR))

        # Subscribing to CSPMaster Attributes
        try:
            self._csp_proxy.subscribe_event(CONST.EVT_CBF_HEALTH, EventType.CHANGE_EVENT, self.cspCbfHealthCallback, stateless=True)
            self._csp_proxy.subscribe_event(CONST.EVT_PSS_HEALTH, EventType.CHANGE_EVENT,
                                            self.cspPssHealthCallback, stateless=True)
            self._csp_proxy.subscribe_event(CONST.EVT_PST_HEALTH, EventType.CHANGE_EVENT,
                                            self.cspPstHealthCallback, stateless=True)

            self.set_state(DevState.ON)
            self.set_status(CONST.STR_CSP_MASTER_LEAF_INIT_SUCCESS)
            self.dev_logging(CONST.STR_CSP_MASTER_LEAF_INIT_SUCCESS, int(tango.LogLevel.LOG_INFO))

        except DevFailed as dev_failed:
            print(CONST.ERR_SUBS_CSP_MASTER_LEAF_ATTR, dev_failed)
            self._read_activity_message = CONST.ERR_SUBS_CSP_MASTER_LEAF_ATTR + str(dev_failed)
            self.set_state(DevState.FAULT)
            self.set_status(CONST.ERR_CSP_MASTER_LEAF_INIT)
            self.dev_logging(CONST.ERR_CSP_MASTER_LEAF_INIT, int(tango.LogLevel.LOG_ERROR))

        ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
        print(CONST.STR_SETTING_CB_MODEL, ApiUtil.instance().get_asynch_cb_sub_model())
        self._read_activity_message = CONST.STR_SETTING_CB_MODEL + str(
            ApiUtil.instance().get_asynch_cb_sub_model())
        # PROTECTED REGION END #    //  CspMasterLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CspMasterLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CspMasterLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CspMasterLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CspMasterLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(CspMasterLeafNode.activityMessage_read) ENABLED START #
        """ Returns the activityMessage. """
        return self._read_activity_message
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspMasterLeafNode.activityMessage_write) ENABLED START #
        """ Sets the activityMessage. """
        self._read_activity_message = value
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_write


    # --------
    # Commands
    # --------

    @command(
        dtype_in=('str',),
        doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array "
               "length is > 1, each array element specifies the FQDN of the\nCSP SubElement to switch ON.",
    )
    @DebugIt()
    def On(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.On) ENABLED START #
        """ Triggers On the CSP Element.

        :param argin: DevStringArray.

        If the array length is 0, the command applies to the whole CSP Element. If the array length is > 1,
        each array element specifies the FQDN of the CSP SubElement to switch ON.

        :return: None
        """
        self._csp_proxy.command_inout_asynch(CONST.CMD_ON, argin, self.commandCallback)

        # PROTECTED REGION END #    //  CspMasterLeafNode.On

    @command(
        dtype_in=('str',),
        doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array "
               "length is > 1, each array element specifies the FQDN of the\nCSP SubElement to switch OFF.",
    )
    @DebugIt()
    def Off(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.Off) ENABLED START #
        """ Triggers Off the CSP Element.

        :param argin: DevStringArray.

        If the array length is 0, the command applies to the whole CSP Element. If the array length is > 1,
        each array element specifies the FQDN of the CSP SubElement to switch OFF.

        :return: None
        """
        self._csp_proxy.command_inout_asynch(CONST.CMD_OFF, argin, self.commandCallback)

        # PROTECTED REGION END #    //  CspMasterLeafNode.Off

    @command(
        dtype_in=('str',),
        doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array "
               "length is > 1, each array element specifies the FQDN of the\nCSP SubElement to put in "
               "STANDBY mode.",
    )
    @DebugIt()
    def Standby(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.Standby) ENABLED START #
        """ Sets Standby Mode on the CSP Element.

        :param argin: DevStringArray.

        If the array length is 0, the command applies to the whole CSP Element. If the array length is > 1,
        each array element specifies the FQDN of the CSP SubElement to put in
        STANDBY mode.

        :return: None
        """
        self._csp_proxy.command_inout_asynch(CONST.CMD_STANDBY, argin, self.commandCallback)

        # PROTECTED REGION END #    //  CspMasterLeafNode.Standby

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CspMasterLeafNode.main) ENABLED START #
    """
    Runs the CspMasterLeafNode.

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: CspMasterLeafNode TANGO object.
    """
    return run((CspMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspMasterLeafNode.main

if __name__ == '__main__':
    main()


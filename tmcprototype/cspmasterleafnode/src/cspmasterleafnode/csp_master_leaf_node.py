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
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run,command, device_property, attribute
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, AdminMode, SimulationMode, TestMode
# Additional import
# PROTECTED REGION ID(CspMasterLeafNode.additionnal_import) ENABLED START #
from . import const
# PROTECTED REGION END #    //  CspMasterLeafNode.additionnal_import

__all__ = ["CspMasterLeafNode", "main"]

class CspMasterLeafNode(SKABaseDevice):
    """
    **Properties:**

    - CspMasterFQDN   - Property to provide FQDN of CSP Master Device

    **Attributes:**

    - cspHealthState  - Forwarded attribute to provide CSP Master Health State
    - activityMessage - Attribute to provide activity message

    """

    # PROTECTED REGION ID(CspMasterLeafNode.class_variable) ENABLED START #\
    def cspCbfHealthCallback(self, evt):
        """
        Retrieves the subscribed cspCbfHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspCbfHealthState attribute.

        :return: None
        """
        try:
            if evt.err is False:
                self._csp_cbf_health = evt.attr_value.value
                if self._csp_cbf_health == HealthState.OK:
                    self.logger.debug(const.STR_CSP_CBF_HEALTH_OK)
                    self._read_activity_message = const.STR_CSP_CBF_HEALTH_OK
                elif self._csp_cbf_health == HealthState.DEGRADED:
                    self.logger.debug(const.STR_CSP_CBF_HEALTH_DEGRADED)
                    self._read_activity_message = const.STR_CSP_CBF_HEALTH_DEGRADED
                elif self._csp_cbf_health == HealthState.FAILED:
                    self.logger.debug(const.STR_CSP_CBF_HEALTH_FAILED)
                    self._read_activity_message = const.STR_CSP_CBF_HEALTH_FAILED
                else:
                    self.logger.debug(const.STR_CSP_CBF_HEALTH_UNKNOWN)
                    self._read_activity_message = const.STR_CSP_CBF_HEALTH_UNKNOWN
            else:
                log_msg = const.ERR_ON_SUBS_CSP_CBF_HEALTH + str(evt.errors)
                self.logger.error(log_msg)
                self._read_activity_message = const.ERR_ON_SUBS_CSP_CBF_HEALTH + str(evt.errors)
                self.logger.error(const.ERR_ON_SUBS_CSP_CBF_HEALTH)
        except Exception as except_occurred:
            self._handle_generic_exception(const.ERR_CSP_CBF_HEALTH_CB + ": " + str(except_occurred))

    def cspPssHealthCallback(self, evt):
        """
        Retrieves the subscribed cspPssHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspPssHealthState attribute.

        :return: None
        """
        try:
            if evt.err is False:
                self._csp_pss_health = evt.attr_value.value
                if self._csp_pss_health == HealthState.OK:
                    self.logger.debug(const.STR_CSP_PSS_HEALTH_OK)
                    self._read_activity_message = const.STR_CSP_PSS_HEALTH_OK
                elif self._csp_pss_health == HealthState.DEGRADED:
                    self.logger.debug(const.STR_CSP_PSS_HEALTH_DEGRADED)
                    self._read_activity_message = const.STR_CSP_PSS_HEALTH_DEGRADED
                elif self._csp_pss_health == HealthState.FAILED:
                    self.logger.debug(const.STR_CSP_PSS_HEALTH_FAILED)
                    self._read_activity_message = const.STR_CSP_PSS_HEALTH_FAILED
                else:
                    self.logger.debug(const.STR_CSP_PSS_HEALTH_UNKNOWN)
                    self._read_activity_message = const.STR_CSP_PSS_HEALTH_UNKNOWN

            else:
                log_msg = const.ERR_ON_SUBS_CSP_PSS_HEALTH + str(evt.errors)
                self.logger.error(log_msg)
                self._read_activity_message = const.ERR_ON_SUBS_CSP_PSS_HEALTH + str(evt.errors)
                self.logger.error(const.ERR_ON_SUBS_CSP_PSS_HEALTH)
        except Exception as except_occurred:
            self._handle_generic_exception(const.ERR_CSP_PSS_HEALTH_CB + ": " + str(except_occurred))

    def cspPstHealthCallback(self, evt):
        """
        Retrieves the subscribed cspPstHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspPstHealthState attribute.

        :return: None
        """
        try:
            if evt.err is False:
                self._csp_pst_health = evt.attr_value.value
                if self._csp_pst_health == HealthState.OK:
                    self.logger.debug(const.STR_CSP_PST_HEALTH_OK)
                    self._read_activity_message = const.STR_CSP_PST_HEALTH_OK
                elif self._csp_pst_health == HealthState.DEGRADED:
                    self.logger.debug(const.STR_CSP_PST_HEALTH_DEGRADED)
                    self._read_activity_message = const.STR_CSP_PST_HEALTH_DEGRADED
                elif self._csp_pst_health == HealthState.FAILED:
                    self.logger.debug(const.STR_CSP_PST_HEALTH_FAILED)
                    self._read_activity_message = const.STR_CSP_PST_HEALTH_FAILED
                else:
                    self.logger.debug(const.STR_CSP_PST_HEALTH_UNKNOWN)
                    self._read_activity_message = const.STR_CSP_PST_HEALTH_UNKNOWN
            else:
                log_msg = const.ERR_ON_SUBS_CSP_PST_HEALTH + str(evt.errors)
                self.logger.error(log_msg)
                self._read_activity_message = const.ERR_ON_SUBS_CSP_PST_HEALTH + str(evt.errors)
                self.logger.error(const.ERR_ON_SUBS_CSP_PST_HEALTH)
        except Exception as except_occurred:
            self._handle_generic_exception(const.ERR_CSP_PST_HEALTH_CB + ": " + str(except_occurred))

    def commandCallback(self, event):
        """
        Checks whether the command has been successfully invoked on CSPMaster.

        :param event: response from CspMaster for the invoked command.

        :return: None
        """
        exception_count = 0
        exception_message = []
        try:
            if event.err:
                log = const.ERR_INVOKING_CMD + event.cmd_name
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                self._read_activity_message = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                    event.errors)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                self._read_activity_message = log
        except Exception as except_occurred:
            self._handle_generic_exception(const.ERR_EXCEPT_CMD_CB + ": " + str(except_occurred))
            exception_message.append(self._read_activity_message)
            exception_count += 1

        # Throw Exception
        if exception_count > 0:
            err_msg = ''
            for item in exception_message:
                err_msg += item + "\n"
            tango.Except.throw_exception(const.STR_CMD_FAILED, err_msg,
                                         const.STR_CSP_CMD_CALLBK, tango.ErrSeverity.ERR)

    #Exception handling
    def _handle_devfailed_exception(self, df, read_actvity_msg):
        log_msg = read_actvity_msg + str(df)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(df)

    def _handle_generic_exception(self, read_actvity_msg):
        log_msg = read_actvity_msg + str(Exception)
        self.logger.error(log_msg)
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
        self.SkaLevel = const.INT_SKA_LEVEL
        self._admin_mode = AdminMode.ONLINE  # Setting adminMode to "ONLINE"
        self._health_state = HealthState.OK # Setting healthState to "OK"
        self._simulation_mode = SimulationMode.FALSE  # Enabling the simulation mode
        self._test_mode = TestMode.NONE
        self._read_activity_message = const.STR_CSP_INIT_LEAF_NODE
        try:
            self._read_activity_message = const.STR_CSPMASTER_FQDN + str(self.CspMasterFQDN)
            # Creating proxy to the CSPMaster
            log_msg = "CSP Master name: " + str(self.CspMasterFQDN)
            self.logger.debug(log_msg)
            self._csp_proxy = DeviceProxy(str(self.CspMasterFQDN))
        except DevFailed as dev_failed:
            log_msg = const.ERR_IN_CREATE_PROXY + str(self.CspMasterFQDN)
            self.logger.error(log_msg)
            self._read_activity_message = const.ERR_IN_CREATE_PROXY + str(self.CspMasterFQDN)
            self.set_state(DevState.FAULT)
            self._handle_devfailed_exception(dev_failed, const.ERR_IN_CREATE_PROXY_CSP_MASTER)

        # Subscribing to CSPMaster Attributes
        try:
            self._csp_proxy.subscribe_event(const.EVT_CBF_HEALTH, EventType.CHANGE_EVENT,
                                            self.cspCbfHealthCallback, stateless=True)
            self._csp_proxy.subscribe_event(const.EVT_PSS_HEALTH, EventType.CHANGE_EVENT,
                                            self.cspPssHealthCallback, stateless=True)
            self._csp_proxy.subscribe_event(const.EVT_PST_HEALTH, EventType.CHANGE_EVENT,
                                            self.cspPstHealthCallback, stateless=True)

            self.set_state(DevState.ON)

        except DevFailed as dev_failed:
            log_msg = const.ERR_SUBS_CSP_MASTER_LEAF_ATTR + str(dev_failed)
            self.logger.error(log_msg)
            self._read_activity_message = const.ERR_SUBS_CSP_MASTER_LEAF_ATTR + str(dev_failed)
            self.set_state(DevState.FAULT)
            self.set_status(const.ERR_CSP_MASTER_LEAF_INIT)
            self.logger.error(const.ERR_CSP_MASTER_LEAF_INIT)

        ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
        log_msg = const.STR_SETTING_CB_MODEL + str(ApiUtil.instance().get_asynch_cb_sub_model())
        self.logger.debug(log_msg)
        self._read_activity_message = const.STR_SETTING_CB_MODEL + str(
            ApiUtil.instance().get_asynch_cb_sub_model())
        self.set_status(const.STR_CSP_MASTER_LEAF_INIT_SUCCESS)
        self.logger.info(const.STR_CSP_MASTER_LEAF_INIT_SUCCESS)

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
        """ Internal construct of TANGO. Returns the activityMessage. """
        return self._read_activity_message
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspMasterLeafNode.activityMessage_write) ENABLED START #
        """Internal construct of TANGO. Sets the activityMessage. """
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
        self._csp_proxy.command_inout_asynch(const.CMD_ON, argin, self.commandCallback)
        self.logger.debug(const.STR_ON_CMD_ISSUED)

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
        self._csp_proxy.command_inout_asynch(const.CMD_OFF, argin, self.commandCallback)
        self.logger.debug(const.STR_OFF_CMD_ISSUED)

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
        self._csp_proxy.command_inout_asynch(const.CMD_STANDBY, argin, self.commandCallback)
        self.logger.debug(const.STR_STANDBY_CMD_ISSUED)

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


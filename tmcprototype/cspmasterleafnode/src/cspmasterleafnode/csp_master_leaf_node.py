"""
CSP Master Leaf node monitors the CSP Master and issues control actions during an observation.
"""

# -*- coding: utf-8 -*-
#
# This file is part of the CspMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PROTECTED REGION ID(CspMasterLeafNode.import) ENABLED START #
# Third party imports
# PyTango imports
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from ska.base.control_model import HealthState, SimulationMode, TestMode
from . import const, release, On, Off, StandBy, tango_client, device_data
from .device_data import DeviceData

# PROTECTED REGION END #    //  CspMasterLeafNode imports

__all__ = ["CspMasterLeafNode", "main", "On", "Off", "StandBy"]


class CspMasterLeafNode(SKABaseDevice):
    """
    **Properties:**

    - CspMasterFQDN   - Property to provide FQDN of CSP Master Device

    **Attributes:**

    - cspHealthState  - Forwarded attribute to provide CSP Master Health State
    - activityMessage - Attribute to provide activity message

    """

    # PROTECTED REGION ID(CspMasterLeafNode.class_variable) ENABLED START #\
    def csp_cbf_health_state_cb(self, evt):
        """
        Retrieves the subscribed cspCbfHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspCbfHealthState attribute.

        :return: None

        """
        log_msg = 'CspCbfHealthState attribute change event is : ' + str(evt)
        self.logger.info(log_msg)
        if not evt.err:
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
            self._read_activity_message = log_msg
            self.logger.error(const.ERR_ON_SUBS_CSP_CBF_HEALTH)

    def csp_pss_health_state_cb(self, evt):
        """
        Retrieves the subscribed cspPssHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspPssHealthState attribute.

        :return: None

        """
        log_msg = 'CspPssHealthState Attribute change event is : ' + str(evt)
        self.logger.info(log_msg)
        if not evt.err:
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
            self._read_activity_message = log_msg

    def csp_pst_health_state_cb(self, evt):
        """
        Retrieves the subscribed cspPstHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspPstHealthState attribute.

        :return: None

        """
        log_msg = 'CspPstHealthState Attribute change event is : ' + str(evt)
        self.logger.info(log_msg)
        if not evt.err:
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
            self._read_activity_message = log_msg

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

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC CSP Master Leaf Node's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the CspMasterLeafNode.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if error occurs while creating the device proxy for CSP Master or
                    subscribing the evennts.
            """
            super().do()
            device = self.target
            # device_data = device_data.get_instance()
            device._health_state = HealthState.OK  # Setting healthState to "OK"
            device._simulation_mode = SimulationMode.FALSE  # Enabling the simulation mode
            device._test_mode = TestMode.NONE
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device._read_activity_message = const.STR_CSP_INIT_LEAF_NODE
            # device.device_data_obj = DeviceData.get_instance()
            device.csp_master_ln_fqdn = device.CspMasterFQDN
            try:
                device._read_activity_message = const.STR_CSPMASTER_FQDN + str(device.CspMasterFQDN)
                # Creating proxy to the CSPMaster
                log_msg = "CSP Master name: " + str(device.CspMasterFQDN)
                self.logger.debug(log_msg)
                device._csp_proxy = DeviceProxy(str(device.CspMasterFQDN))
            except DevFailed as dev_failed:
                log_msg = const.ERR_IN_CREATE_PROXY + str(device.CspMasterFQDN)
                self.logger.debug(log_msg)
                self.logger.exception(dev_failed)
                device._read_activity_message = log_msg
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CspMasterLeafNode.InitCommand.do()",
                                             tango.ErrSeverity.ERR)

            # Subscribing to CSPMaster Attributes
            try:
                # csp_sa_client = TangoClient(device.CspMasterFQDN)
                device._csp_proxy.subscribe_event(const.EVT_CBF_HEALTH, EventType.CHANGE_EVENT,
                                                  device.csp_cbf_health_state_cb, stateless=True)
                device._csp_proxy.subscribe_event(const.EVT_PSS_HEALTH, EventType.CHANGE_EVENT,
                                                  device.csp_pss_health_state_cb, stateless=True)
                device._csp_proxy.subscribe_event(const.EVT_PST_HEALTH, EventType.CHANGE_EVENT,
                                                  device.csp_pst_health_state_cb, stateless=True)
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBS_CSP_MASTER_LEAF_ATTR + str(dev_failed)
                self.logger.debug(log_msg)
                device.set_status(const.ERR_CSP_MASTER_LEAF_INIT)
                device._read_activity_message = log_msg
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CspMasterLeafNode.InitCommand.do()",
                                             tango.ErrSeverity.ERR)

            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_msg = const.STR_SETTING_CB_MODEL + str(ApiUtil.instance().get_asynch_cb_sub_model())
            self.logger.debug(log_msg)

            device._read_activity_message = const.STR_INIT_SUCCESS
            self.logger.info(device._read_activity_message)
            return (ResultCode.OK, device._read_activity_message)

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


    def is_Standby_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("Standby")
        return handler.check_allowed()

    @command(
        dtype_in=('str',),
        doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array "
               "length is > 1, each array element specifies the FQDN of the\nCSP SubElement to put in "
               "STANDBY mode.",
    )
    @DebugIt()
    def Standby(self, argin):
        """ Sets Standby Mode on the CSP Element. """
        handler = self.get_command_object("Standby")
        handler(argin)

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()
        self.register_command_object("Off", Off.OffCommand(self, self.state_model, self.logger))
        self.register_command_object("On", On.OnCommand(self, self.state_model, self.logger))
        self.register_command_object("Standby", StandBy.StandbyCommand(self, self.state_model, self.logger))


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

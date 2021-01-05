# """
# StartUpTelescope class for CentralNodelow.
# """
# # Tango imports
# import tango
# from tango import DebugIt, AttrWriteType, DeviceProxy, EventType, DevState, DevFailed
#
# # Additional import
# from ska.base import SKABaseDevice
# from ska.base.commands import ResultCode, BaseCommand
# from ska.base.control_model import HealthState
# from . import const
# from centralnodelow.device_data import DeviceData
# from tmc.common.tango_client import TangoClient
# class StandByTelescope(SKABaseDevice.OffCommand):
#     """
#     A class for Low CentralNode's StandByTelescope() command.
#     """
#
#     def check_allowed(self):
#
#         """
#         Checks whether this command is allowed to be run in current device state
#
#         :return: True if this command is allowed to be run in current device state
#
#         :rtype: boolean
#
#         :raises: DevFailed if this command is not allowed to be run in current device state
#         """
#         if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
#             tango.Except.throw_exception("Command StandByTelescope is not allowed in current state.",
#                                          "Failed to invoke StandByTelescope command on CentralNodeLow.",
#                                          "CentralNodeLow.StandByTelescope()",
#                                          tango.ErrSeverity.ERR)
#         return True
#
#     def do(self):
#         """
#         Sets the CentralNodeLow into OFF state. Invokes the respective command on lower level nodes and devices.
#
#         param argin: None.
#
#         :return: A tuple containing a return code and a string message indicating status.
#         The message is for information purpose only.
#
#         :rtype: (ResultCode, str)
#
#         :raises: DevFailed if error occurs while invoking command on any of the devices like SubarrayNode or
#                  MccsMasterLeafNode.
#
#         """
#         device = self.target
#         log_msg = const.STR_STANDBY_CMD_ISSUED
#         self.logger.info(log_msg)
#         device._read_activity_message = log_msg
#
#         try:
#             device._mccs_master_leaf_proxy.command_inout(const.CMD_OFF)
#             self.logger.info(const.STR_CMD_OFF_MCCSMLN_DEV)
#         except DevFailed as dev_failed:
#             log_msg = const.ERR_EXE_OFF_CMD + str(dev_failed)
#             self.logger.exception(dev_failed)
#             device._read_activity_message = const.ERR_EXE_OFF_CMD
#             tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
#                                          "CentralNodeLow.StandByTelescopeCommand",
#                                          tango.ErrSeverity.ERR)
#
#         try:
#             for subarray_id in range(1, len(device.TMLowSubarrayNodes) + 1):
#                 device.subarray_FQDN_dict[subarray_id].command_inout(const.CMD_OFF)
#                 self.logger.info(const.STR_CMD_OFF_SA_LOW_DEV)
#
#         except DevFailed as dev_failed:
#             log_msg = const.ERR_EXE_OFF(dev_failed)
#             self.logger.exception(dev_failed)
#             device._read_activity_message = const.ERR_EXE_OFF_CMD
#             tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
#                                          "CentralNodeLow.StandByTelescopeCommand",
#                                          tango.ErrSeverity.ERR)
#         return (ResultCode.OK, device._read_activity_message)

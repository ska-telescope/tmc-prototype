# Will get Uncommented after refactoring for command is done.
# """
# ReleaseResources command class for SDPSubarrayLeafNode.
# """
# from ska_tango_base.commands import ResultCode
# from ska_tango_base.control_model import ObsState
# from ska_tmc_common.adapters import AdapterFactory
# from ska_tmc_common.exceptions import InvalidObsStateError
# from tango import DevFailed

# from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import
# SdpSLNCommand


# class ReleaseResources(SdpSLNCommand):
#     """
#     A class for SdpSubarayLeafNode's ReleaseResources() command.

#     Releases all the resources of given SDP Subarray Leaf Node.
#     It accepts the subarray id, releaseALL flag and receptorIDList in
#     JSON string format.
#     """

#     def __init__(
#         self,
#         target,
#         op_state_model,
#         adapter_factory=None,
#         logger=None,
#     ):
#         super().__init__(target, logger)
#         self.op_state_model = op_state_model
#         self._adapter_factory = adapter_factory or AdapterFactory()

#     def check_allowed(self):
#         """
#         Checks whether this command is allowed
#         It checks that the device is in the right state
#         to execute this command and that all the
#         component needed for the operation are not unresponsive

#         :return: True if this command is allowed

#         :rtype: boolean

#         """
#         component_manager = self.target

#         self.check_op_state("ReleaseResources")
#         self.check_unresponsive()
#         obs_state_val = component_manager.get_device().obs_state
#         self.logger.info("sdp_subarray_obs_state value is: %s",
# obs_state_val)

#         if obs_state_val != ObsState.IDLE:
#             self.logger.info(
#                 "sdp_subarray_obs_state value is: %s", obs_state_val
#             )
#             message = (
#                 "ReleaseAllResources command is not allowed in current"
#                 + "observation state on device"
#                 + "{}".format(component_manager._sdp_subarray_dev_name)
#                 + "Reason: The current observation state for observation is"
#                 + "{}".format(obs_state_val)
#                 + 'The "ReleaseAllResources" command has NOT been executed.'
#                 + "This device will continue with normal operation."
#             )
#             raise InvalidObsStateError(message)
#         return True

#     def do(self, argin=None):
#         """
#         Method to invoke ReleaseAllResources command on SDP Subarray.

#         :param argin: None.

#         return:
#             None
#         """
#         ret_code, message = self.init_adapter()
#         if ret_code == ResultCode.FAILED:
#             return ret_code, message
#         log_msg = "Invoking ReleaseAllResources command on:" + "{}".format(
#             self.sdp_subarray_adapter.dev_name
#         )
#         self.logger.info(log_msg)
#         try:
#             log_msg = (
#                 "Invoking ReleaseAllResources command on SDP Subarray"
#                 + "{}".format(self.sdp_subarray_adapter.dev_name),
#             )
#             self.logger.debug(log_msg)
#             self.sdp_subarray_adapter.ReleaseAllResources()
#         except (AttributeError, ValueError, TypeError, DevFailed) as e:
#             self.logger.exception("Command invocation failed: %s", e)
#             return self.generate_command_result(
#                 ResultCode.FAILED,
#                 "The invocation of the ReleaseAllResources command isfailed"
#                 + "on Sdp Subarray Device {}".format(
#                     self.sdp_subarray_adapter.dev_name
#                 )
#                 + "Reason: Error in invoking the ReleaseAllResourcescommand"
#                 "on Sdp"
#                 + "Subarray. The command has NOT been executed."
#                 + "This device will continue with normal operation.",
#             )
#         log_msg = (
#             "ReleaseAllResources command successfully invoked on:"
#             + "{}".format(self.sdp_subarray_adapter.dev_name)
#         )
#         self.logger.info(log_msg)
#         return (ResultCode.OK, "")

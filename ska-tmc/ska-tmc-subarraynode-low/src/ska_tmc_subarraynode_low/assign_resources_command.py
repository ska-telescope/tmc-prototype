"""
AssignResourcesCommand class for SubarrayNodeLow.
"""
# Standard python imports
import json

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray

from . import const
from tmc.common.tango_server_helper import TangoServerHelper


class AssignResources(SKASubarray.AssignResourcesCommand):
    """
    A class for SubarrayNodelow's AssignResources() command.

    Assigns the resources to the subarray. It accepts station ids, channels, station beam ids and channels
    in JSON string format.

    """

    def do(self, argin):
        """
        Method to invoke AssignResources command.

        :param argin: DevString in JSON form containing following fields:
            interface: Schema to allocate assign resources.

            mccs:
                subarray_beam_ids: list of integers

                station_ids: list of integers

                channel_blocks: list of integers

        Example:

        {"interface":"https://schema.skao.int/ska-low-tmc-assignedresources/2.0","mccs":{"subarray_beam_ids":[1],"station_ids":[[1,2]],"channel_blocks":[3]}}

        return:
            A tuple containing ResultCode and string.
        """
        device_data = self.target
        this_server = TangoServerHelper.get_instance()
        device_data.is_end_command = False
        device_data.is_release_resources = False
        device_data.is_abort_command_executed = False
        device_data.is_obsreset_command_executed = False
        device_data.is_restart_command_executed = False
        # TODO: For now storing resources as station ids
        input_str = json.loads(argin)
        device_data.resource_list = input_str["mccs"]["station_ids"]
        log_msg = f"{const.STR_ASSIGN_RES_EXEC}STARTED"
        self.logger.debug(log_msg)
        this_server.write_attr("activityMessage", log_msg, False)
        return (ResultCode.STARTED, log_msg)
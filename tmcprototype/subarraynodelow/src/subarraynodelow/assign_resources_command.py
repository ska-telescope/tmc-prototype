"""
AssignResourcesCommand class for SubarrayNodeLow.
"""
# Standard python imports
import json

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray

from . import const
from subarraynodelow.device_data import DeviceData
from tmc.common.tango_server_helper import TangoServerHelper
from .assigned_resources_maintainer import AssignedResourcesMaintainer


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

        {"interface":"https://schema.skatelescope.org/ska-low-tmc-assignedresources/1.0","mccs":{"subarray_beam_ids":[1],"station_ids":[[1,2]],"channel_blocks":[3]}}

        return:
            A tuple containing ResultCode and string.
        """
        device_data = DeviceData.get_instance()
        this_server = TangoServerHelper.get_instance()
        device_data.is_end_command = False
        device_data.is_release_resources = False
        device_data.is_abort_command_executed = False
        device_data.is_obsreset_command_executed = False
        # TODO: For now storing resources as station ids
        input_str = json.loads(argin)
        device_data.resource_list = input_str["mccs"]["station_ids"]
        log_msg = f"{const.STR_ASSIGN_RES_EXEC}STARTED"
        self.logger.debug(log_msg)
        this_server.write_attr("activityMessage", log_msg, False)
        device_data.assigned_resources_maintainer = AssignedResourcesMaintainer()
        device_data.assigned_resources_maintainer.subscribe()

        return (ResultCode.STARTED, log_msg)

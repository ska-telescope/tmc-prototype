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


class AssignResources(SKASubarray.AssignResourcesCommand):
    """
    A class for SubarrayNodelow's AssignResources() command.
    """

    def do(self, argin):
        """
        Assigns the resources to the subarray. It accepts station ids, channels, station beam ids

        :param argin: DevString in JSON form containing following fields:
            station_ids: list of integers

            channels: list of integers

            station_beam_ids: list of integers

        Example:

        {"station_ids":[1,2],"channels":[[0,8,1,1],[8,8,2,1],[24,16,2,1]],"station_beam_ids":[1]}

        :return: A tuple containing ResultCode and string.
        """
        device_data = DeviceData.get_instance()
        device_data.is_end_command = False
        device_data.is_release_resources = False
        device_data.is_abort_command_executed = False
        device_data.is_obsreset_command_executed = False
        # TODO: For now storing resources as station ids
        input_str = json.loads(argin)
        device_data.resource_list = input_str["station_ids"]
        log_msg = f"{const.STR_ASSIGN_RES_EXEC}STARTED"
        self.logger.debug(log_msg)
        device_data.activity_message = log_msg

        return (ResultCode.STARTED, log_msg)

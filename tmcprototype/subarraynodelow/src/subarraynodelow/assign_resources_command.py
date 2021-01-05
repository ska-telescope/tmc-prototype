"""
AssignResourcesCommand class for SubarrayNodeLow.
"""
# Standard python imports
import json

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from . import const


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

        {"station_ids": [1, 2], "channels": [1, 2, 3, 4, 5, 6, 7, 8], "station_beam_ids": [1]}

        :return: A tuple containing ResultCode and string.

        """

        device = self.target
        device.is_end_command = False
        device.is_release_resources = False
        # TODO: For now storing resources as station ids
        input_str = json.loads(argin)
        device._resource_list = input_str["station_ids"]
        log_msg = const.STR_ASSIGN_RES_EXEC + "STARTED"
        self.logger.debug(log_msg)
        device._read_activity_message = log_msg
        
        return (ResultCode.STARTED, log_msg)
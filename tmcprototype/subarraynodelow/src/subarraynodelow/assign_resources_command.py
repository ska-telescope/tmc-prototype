"""
AssignResourcesCommand class for SubarrayNode.
"""

import json
# Tango imports
import tango
from tango import DevFailed
# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class AssignResourcesCommand(SKASubarray.AssignResourcesCommand):
    """
    A class for SubarrayNode's AssignResources() command.
    """
    def do(self, argin):
        """
        Assigns the resources to the subarray. It accepts station ids, channels, station beam ids, and tile ids

        :param argin: DevString in JSON form containing following fields:
            station_ids: list of DevInt

            channels: list of integers

            station_beam_ids: list of integers

            tile_ids: list of integers

        Example:

        {"station_ids": [1, 2], "channels": [1, 2, 3, 4, 5, 6, 7, 8], "station_beam_ids": [1], "tile_ids": [1, 2, 3, 4]}

        :return: A tuple containing ResultCode and string.

        """

        device = self.target
        device.is_end_command = False
        device.is_release_resources = False
    
        log_msg = const.STR_ASSIGN_RES_EXEC + "STARTED"
        self.logger.debug(log_msg)
        device._read_activity_message = log_msg
        
        return (ResultCode.STARTED, log_msg)
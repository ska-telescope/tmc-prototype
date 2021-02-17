"""
ReleaseAllResourcesCommand for SubarrayNodeLow
"""
# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray

from . import const
from subarraynodelow.device_data import DeviceData


class ReleaseAllResources(SKASubarray.ReleaseAllResourcesCommand):
    """
    A class for SKASubarrayLow's ReleaseAllResources() command.

    It invokes ReleaseAllResources command on Subarray Node Low.

    """

    def do(self):
        """
        Method to invoke ReleaseAllResources command.

        return:
            A tuple containing a return code and RELEASEALLRESOURCES command invoked successfully as a string on successful release all resources.
        Example: RELEASEALLRESOURCES command invoked successfully as string on successful release all resources.

        rtype:
            (ResultCode, str)

        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = True
        # TODO: Clearing the assigned resources
        device_data.resource_list = []
        self.logger.debug(const.STR_RELEASE_SUCCESS)
        return (ResultCode.STARTED, const.STR_RELEASE_SUCCESS)

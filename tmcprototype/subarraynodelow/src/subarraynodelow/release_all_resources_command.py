"""
ReleaseAllResourcesCommand for SubarrayNodeLow
"""
# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class ReleaseAllResourcesCommand(SKASubarray.ReleaseAllResourcesCommand):
    """
    A class for SKASubarrayLow's ReleaseAllResources() command.
    """
    def do(self):
        """
        It invokes ReleaseAllResources command on Subarraylow.

        :return: A tuple containing a return code and RELEASEALLRESOURCES command invoked successfully as a string on successful release all resources.
        Example: RELEASEALLRESOURCES command invoked successfully as string on successful release all resources.

        :rtype: (ResultCode, str)

        """
        device = self.target
        device.is_release_resources = True
        device._resource_list = []
        self.logger.debug(const.STR_RELEASE_SUCCESS)
        return (ResultCode.STARTED, const.STR_RELEASE_SUCCESS )
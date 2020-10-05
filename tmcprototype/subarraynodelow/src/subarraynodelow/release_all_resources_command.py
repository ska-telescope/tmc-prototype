"""
ReleaseAllResourcesCommand for SubarrayNodelow
"""
# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class ReleaseAllResourcesCommand(SKASubarray.ReleaseAllResourcesCommand):
    """
    A class for SKASubarraylow's ReleaseAllResources() command.
    """
    def do(self):
        """
        It invokes ReleaseAllResources command on Subarraylow.

        :return: A tuple containing a return code and "[]" as a string on successful release all resources.
        Example: "[]" as string on successful release all resources.

        :rtype: (ResultCode, str)

        """
        device = self.target
        device.is_release_resources = True
        # TODO: Clearing the assigned resources
        device._resource_list = []
        self.logger.debug(const.STR_RELEASE_SUCCESS)
        return (ResultCode.STARTED,const.STR_RELEASE_SUCCESS )
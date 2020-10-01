"""
ReleaseAllResourcesCommand for SubarrayNode
"""

# Tango imports
import tango
from tango import DevFailed

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
        It checks whether all resources are already released. If yes then it throws error while
        executing command. If not it Releases all the resources from the subarray i.e. Releases
        resources from TMC Subarray Node.

        :return: A tuple containing a return code and "[]" as a string on successful release all resources.
        Example: "[]" as string on successful release all resources.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device = self.target
        device.is_release_resources = False
        try:
            device.is_release_resources = True
            self.logger.debug(const.STR_RELEASE_SUCCESS)
            return (ResultCode.STARTED,const.STR_RELEASE_SUCCESS )

        except DevFailed as dev_failed:
            log_msg = const.ERR_RELEASE_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_RELEASE_EXEC,
                                         log_msg,
                                         "SubarrayNode.ReleaseAllResourcesCommand",
                                         tango.ErrSeverity.ERR)
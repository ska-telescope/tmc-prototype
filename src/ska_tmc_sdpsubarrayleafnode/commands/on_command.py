"""
On command class for SDPSubarrayLeafNode.

"""

from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import AbstractOnOff


class On(AbstractOnOff):
    """
    A class for SdpsubarrayLeafNode's On() command.

    On command on SdpsubarrayLeafNode enables the telescope to perform further
    operations and observations.
    It Invokes On command on Sdp Subarray device.

    """

    def do(self, argin=None):
        """
        Method to invoke Telescope On command on Sdp Subarray.

        """

        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message
        result = self.call_adapter_method(
            "Sdp Subarray", self.sdp_subarray_adapter, "On"
        )
        return result

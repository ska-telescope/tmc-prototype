"""
SDP Master Leaf node acts as a SDP contact point for Master Node and also to monitor
and issue commands to the SDP Master.
"""

from ska_tango_base.commands import ResultCode
from tango.server import device_property, run

from ska_tmc_sdpmasterleafnode.sdp_master_leaf_node import (
    AbstractSdpMasterLeafNode,
)

__all__ = ["SdpMasterLeafNodeMid", "main"]


class SdpMasterLeafNodeMid(AbstractSdpMasterLeafNode):
    """
    SDP Master Leaf node acts as a SDP contact point for Master Node and also to monitor
    and issue commands to the SDP Master.
    """

    # ----------
    # Attributes
    # ----------

    SleepTime = device_property(dtype="DevFloat", default_value=1)

    # ---------------
    # General methods
    # ---------------
    class InitCommand(AbstractSdpMasterLeafNode.InitCommand):
        """
        A class for the TMC SdpMasterLeafNode's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the SdpMasterLeafNode.

            return:
                A tuple containing a return code and a string message indicating status.
                The message is for information purpose only.

            rtype:
                (ResultCode, str)
            """
            super().do()

            return (ResultCode.OK, "")

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the SdpMasterLeafNodeMid.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: SdpMasterLeafNodeMid TANGO object.
    """
    return run((SdpMasterLeafNodeMid,), args=args, **kwargs)


if __name__ == "__main__":
    main()

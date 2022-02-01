"""
SDP Master Leaf node is to monitor the SDP Master and issue control actions during an observation.
It also acts as a SDP contact point for Master Node for observation execution
"""
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType
from tango.server import attribute, device_property, run

from ska_tmc_sdpmasterleafnode.sdp_master_leaf_node import (
    AbstractSdpMasterLeafNode,
)

__all__ = ["SdpMasterLeafNodeMid", "main"]


class SdpMasterLeafNodeMid(AbstractSdpMasterLeafNode):
    """
    SDP Master Leaf node is to monitor the SDP Master and issue control actions during an observation.

    """

    # ----------
    # Attributes
    # ----------

    sdpMasterDevName = attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
    )

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

    # ------------------
    # Attributes methods
    # ------------------

    def read_sdpMasterDevName(self):
        """Return the sdpmasterdevname attribute."""
        return self.component_manager.input_parameter.sdp_master_dev_name

    def write_sdpMasterDevName(self, value):
        """Set the sdpmasterdevname attribute."""
        self.component_manager.input_parameter.sdp_master_dev_name = value
        self.component_manager.update_input_parameter()

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

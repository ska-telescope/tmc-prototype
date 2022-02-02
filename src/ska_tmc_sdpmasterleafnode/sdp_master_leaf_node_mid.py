"""
SDP Master Leaf node acts as a SDP contact point for Master Node and also to monitor
and issue commands to the SDP Master.
"""

from ska_tango_base.commands import ResultCode
from tango.server import device_property, run

from ska_tmc_sdpmasterleafnode.commands.telescope_off_command import (
    TelescopeOff,
)
from ska_tmc_sdpmasterleafnode.commands.telescope_on_command import TelescopeOn
from ska_tmc_sdpmasterleafnode.commands.telescope_standby_command import (
    TelescopeStandby,
)
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
        # TODO:Uncomment below code once commands refactoring AT1-1061 is done
        args = ()
        for (command_name, command_class) in [
            ("TelescopeOn", TelescopeOn),
            ("TelescopeOff", TelescopeOff),
            ("TelescopeStandby", TelescopeStandby),
        ]:
            command_obj = command_class(
                self.component_manager,
                self.op_state_model,
                *args,
                logger=self.logger,
            )
            self.register_command_object(command_name, command_obj)


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

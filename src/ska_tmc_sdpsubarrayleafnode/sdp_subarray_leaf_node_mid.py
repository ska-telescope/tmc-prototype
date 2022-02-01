"""
SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution
"""
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType
from tango.server import attribute, device_property, run

from ska_tmc_sdpsubarrayleafnode.commands.abort_command import Abort
from ska_tmc_sdpsubarrayleafnode.commands.assign_resources_command import (
    AssignResources,
)
from ska_tmc_sdpsubarrayleafnode.commands.configure_command import Configure
from ska_tmc_sdpsubarrayleafnode.commands.end_command import End
from ska_tmc_sdpsubarrayleafnode.commands.endscan_command import EndScan
from ska_tmc_sdpsubarrayleafnode.commands.obsreset_command import ObsReset
from ska_tmc_sdpsubarrayleafnode.commands.release_resources_command import (
    ReleaseResources,
)
from ska_tmc_sdpsubarrayleafnode.commands.reset_command import Reset
from ska_tmc_sdpsubarrayleafnode.commands.restart_command import Restart
from ska_tmc_sdpsubarrayleafnode.commands.scan_command import Scan
from ska_tmc_sdpsubarrayleafnode.commands.telescope_off_command import (
    TelescopeOff,
)
from ska_tmc_sdpsubarrayleafnode.commands.telescope_on_command import (
    TelescopeOn,
)
from ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node import (
    AbstractSdpSubarrayLeafNode,
)

__all__ = ["SdpSubarrayLeafNodeMid", "main"]


class SdpSubarrayLeafNodeMid(AbstractSdpSubarrayLeafNode):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.

    """

    # ----------
    # Attributes
    # ----------

    sdpSubarrayDevName = attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
    )

    SleepTime = device_property(dtype="DevFloat", default_value=1)

    # ---------------
    # General methods
    # ---------------
    class InitCommand(AbstractSdpSubarrayLeafNode.InitCommand):
        """
        A class for the TMC SdpSubarrayLeafNode's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the SdpSubarrayLeafNode.

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

    def read_sdpSubarrayDevName(self):
        """Return the sdpsubarraydevname attribute."""
        return self.component_manager.input_parameter.sdp_subarray_dev_name

    def write_sdpSubarrayDevName(self, value):
        """Set the sdpsubarraydevname attribute."""
        self.component_manager.input_parameter.sdp_subarray_dev_name = value
        self.component_manager.update_input_parameter()

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()
        args = ()
        for (command_name, command_class) in [
            ("TelescopeOn", TelescopeOn),
            ("TelescopeOff", TelescopeOff),
            ("AssignResources", AssignResources),
            ("ReleaseResources", ReleaseResources),
            ("Configure", Configure),
            ("Scan", Scan),
            ("EndScan", EndScan),
            ("End", End),
            ("ObsReset", ObsReset),
            ("Abort", Abort),
            ("Restart", Restart),
        ]:
            command_obj = command_class(
                self.component_manager,
                self.op_state_model,
                *args,
                logger=self.logger,
            )
            self.register_command_object(command_name, command_obj)
        self.register_command_object(
            "Reset",
            Reset(
                self.component_manager,
                self.op_state_model,
                self.logger,
            ),
        )


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the SdpSubarrayLeafNodeMid.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: SdpSubarrayLeafNodeMid TANGO object.
    """
    return run((SdpSubarrayLeafNodeMid,), args=args, **kwargs)


if __name__ == "__main__":
    main()

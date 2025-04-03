"""
SDP Master Leaf node acts as a SDP contact point
for Master Node and also to monitor
and issue commands to the SDP Master.
"""

from tango.server import run

from ska_tmc_sdpmasterleafnode.sdp_master_leaf_node import TmcLeafNodeSdp

__all__ = ["MidTmcLeafNodeSdp", "main"]


class MidTmcLeafNodeSdp(TmcLeafNodeSdp):
    """
    Tango device class for TMC SDP Master Leaf Node MID.
    """


def main(args=None, **kwargs):
    """
    Runs the MidTmcLeafNodeSdp.
    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO
    :return: MidTmcLeafNodeSdp TANGO object.
    """
    return run((MidTmcLeafNodeSdp,), args=args, **kwargs)


if __name__ == "__main__":
    main()

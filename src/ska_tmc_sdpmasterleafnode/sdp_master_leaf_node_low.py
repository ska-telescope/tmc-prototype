"""
SDP Master Leaf node acts as a SDP contact point
for Master Node and also to monitor
and issue commands to the SDP Master.
"""

from tango.server import run

from ska_tmc_sdpmasterleafnode.sdp_master_leaf_node import TmcLeafNodeSdp

__all__ = ["LowTmcLeafNodeSdp", "main"]


class LowTmcLeafNodeSdp(TmcLeafNodeSdp):
    """
    Tango device class for TMC SDP Master Leaf Node Low.
    """


def main(args=None, **kwargs):
    """
    Runs the LowTmcLeafNodeSdp.
    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO
    :return: LowTmcLeafNodeSdp TANGO object.
    """
    return run((LowTmcLeafNodeSdp,), args=args, **kwargs)


if __name__ == "__main__":
    main()

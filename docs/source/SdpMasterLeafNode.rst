.. SKA-TMC documentation master file, created by
   sphinx-quickstart on Thu Jan 31 16:54:35 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SDP Master Leaf Node
================================================
.. autoclass:: ska-tmc.sdpmasterleafnode.src.sdpmasterleafnode.sdp_master_leaf_node.SdpMasterLeafNode
    :members: None
    :undoc-members: Disable
.. autoclass:: ska-tmc.sdpmasterleafnode.src.sdpmasterleafnode.off_command.Off
    :members: do
    :undoc-members:
.. autoclass:: ska-tmc.sdpmasterleafnode.src.sdpmasterleafnode.disable_command.Disable
    :members: do
    :undoc-members:
.. autoclass:: ska-tmc.sdpmasterleafnode.src.sdpmasterleafnode.on_command.On
    :members: do
    :undoc-members:
.. autoclass:: ska-tmc.sdpmasterleafnode.src.sdpmasterleafnode.standby_command.Standby
    :members: do
    :undoc-members:

Note: Simulator for SDP Master device is available. It enables SDP Master Leaf Node to be deployed 
to execute in standalone mode. To run SDP Master Leaf Node in standalone mode, set STANDALONE_MODE
environment variable to "TRUE". The SDP Master simulator device executes inside the SDP Master Leaf 
Node device server. As of now the device has to be manually added in tango database.
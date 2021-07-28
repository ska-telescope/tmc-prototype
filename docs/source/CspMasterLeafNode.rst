.. SKA-TMC documentation master file, created by
   sphinx-quickstart on Thu Jan 31 16:54:35 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CSP Master Leaf Node
===================================================

.. autoclass:: ska-tmc.cspmasterleafnode.src.cspmasterleafnode.csp_master_leaf_node.CspMasterLeafNode
    :members: None
    :undoc-members:
.. autoclass:: ska-tmc.cspmasterleafnode.src.cspmasterleafnode.off_command.Off
    :members: do
    :undoc-members:
.. autoclass:: ska-tmc.cspmasterleafnode.src.cspmasterleafnode.on_command.On
    :members: do
    :undoc-members:
.. autoclass:: ska-tmc.cspmasterleafnode.src.cspmasterleafnode.standby_command.Standby
    :members: do
    :undoc-members:

Note: Simulator for CSP Master device is available. It enables CSP Master Leaf Node to be deployed 
to execute in standalone mode. To run CSP Master Leaf Node in standalone mode, set STANDALONE_MODE
environment variable to "TRUE". The CSP Master simulator device executes inside the CSP Master Leaf 
Node device server. As of now the device has to be manually added in tango database

ska\_tmc\_sdpmasterleafnode package
===================================

Subpackages
-----------

.. toctree::
   :maxdepth: 4

   ska_tmc_sdpmasterleafnode.commands
   ska_tmc_sdpmasterleafnode.manager

Submodules
----------

ska\_tmc\_sdpmasterleafnode._sdp\_master\_leaf\_node module
-----------------------------------------------------------

.. automodule:: ska_tmc_sdpmasterleafnode.sdp_master_leaf_node
   :members:
   :undoc-members:
   :show-inheritance:


Module contents
---------------

.. automodule:: ska_tmc_sdpmasterleafnode
   :members:
   :undoc-members:
   :show-inheritance:



##################################
Properties in SDP Master Leaf Node
##################################


+-------------------------------+---------------+--------------------------------------------------------------------------------+
| Property Name                 | Data Type     | Description                                                                    |
+===============================+===============+================================================================================+
| SdpMasterFQDN                 | DevString     | FQDN of the SDP Master Tango Device Server.                                    |
+-------------------------------+---------------+----------------------+---------------------------------------------------------+
| livelinessCheckPeriod         | DevFloat      | Period for the liveliness probe to monitor each device in a loop.              |
+-------------------------------+---------------+----------------------+---------------------------------------------------------+
| eventSubscriptionCheckPeriod  | DevFloat      | Period for the event subscriber to check the device subscriptions in a loop.   |                     |
+-------------------------------+---------------+----------------------+---------------------------------------------------------+
| AdapterTimeOut                | DevFloat      | Timeout for the adapter creation. This property is for internal use.           |
+-------------------------------+---------------+----------------------+---------------------------------------------------------+


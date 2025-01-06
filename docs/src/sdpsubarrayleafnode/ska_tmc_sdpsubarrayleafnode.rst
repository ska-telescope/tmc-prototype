ska\_tmc\_sdpsubarrayleafnode package
=====================================

Subpackages
-----------

.. toctree::
   :maxdepth: 4

   ska_tmc_sdpsubarrayleafnode.commands
   ska_tmc_sdpsubarrayleafnode.manager

Submodules
----------

ska\_tmc\_sdpsubarrayleafnode._sdp\_subarray\_leaf\_node module
---------------------------------------------------------------

.. automodule:: ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node
   :members:
   :undoc-members:
   :show-inheritance:


Module contents
---------------

.. automodule:: ska_tmc_sdpsubarrayleafnode
   :members:
   :undoc-members:
   :show-inheritance:



+-------------------------------+---------------+--------------------------------------------------------------------------------+
| Property Name                 | Data Type     | Description                                                                    |
+===============================+===============+================================================================================+
| SdpSubarrayFQDN               | DevString     | FQDN of the SDP Subarray Tango Device Server.                                  |
+-------------------------------+---------------+----------------------+---------------------------------------------------------+
| livelinessCheckPeriod         | DevFloat      | Period for the liveliness probe to monitor each device in a loop.              |
+-------------------------------+---------------+----------------------+---------------------------------------------------------+
| eventSubscriptionCheckPeriod  | DevFloat      | Period for the event subscriber to check the device subscriptions in a loop.   |                     |
+-------------------------------+---------------+----------------------+---------------------------------------------------------+
| AdapterTimeOut                | DevFloat      | Timeout for the adapter creation. This property is for internal use.           |
+-------------------------------+---------------+----------------------+---------------------------------------------------------+
| CommandTimeOut                | DevFloat      | Timeout for the command execution                                              |
+-------------------------------+---------------+----------------------+---------------------------------------------------------+


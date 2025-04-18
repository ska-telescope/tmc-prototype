###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

[Master]
************

Fixed
------
[0.21.3]
* Removed the transitional obsState RESOURCING check from AssignResources command tracker.
* Spike SAH-1691 is created for further investigation.

[0.21.2]
* Removed processing from Tango event handler and perform in call backs function.

[0.21.1]
* Fixed SKB-732

[0.21.0]
* Updated FQDN's as per ADR-9

[0.19.3]
*  Fixed SKB-592 issue with variable initialization.
  
[0.19.2]
*  Update Abort() to notify observers

[0.19.1]
*  Resolved SKB-658.

[0.19.0]
*  Implemented Exception handling for End, Scan and EndScan commands.

[0.18.0]
*  Resolve SKB-525 update with command callback tracker changes.

[0.17.3]
*  Fixed SKB-618(Fix KeyError for Missing 'resources' Key in SDP Subarray AssignResources Command)

[0.17.2]
********
* Resolved skb-536
* The SDP Subarray Device can transition to the ABORTING state before reaching the ABORTED state.
* Updated the .readthdocs.yaml
* Fixed documentation missing information issue
* Fixed Logger strings.
* Improved the test case execution time.


[0.17.1]
********
* Remove a spam log from component manager method

[0.17.0]
********
* Utilized the ska-tmc-common v0.20.2 which has new liveliness probe implementation

[0.16.5]
******
* Utilized the latest ska-tmc-common 0.19.7 which clears abort event in tracker thread.

[0.16.4]
******
* Resolving the issues of error propagation.

[0.16.3]
******
* Enable polling of all attributes by setting and pushing archive 
events to resolve SKB-434

[0.16.2]
******
* Improve loggers statement and version of common


[0.16.1]
******
* Enable obsState check for Abort commad


[0.16.0]
------
* Update Sdp master leaf node and Sdp Subarray Leaf Node to use Base class v1.0.0 and pytango v9.5.0

[0.15.1]
------
* CommandTimeOut Device property added to Sdp Subarray Leaf Node device

[0.15.0]
************
* Updated pytango v9.4.2
* Updated ska-tango-base library v0.19.1
* Updated ska-tango-base chart v0.4.8
* Updated ska-tango-util chart v0.4.10
* Updated ska-tmc-common v0.14.0

[0.1.2]
************

Release of feature SP-354
-----

* Accept configuration as strings (JSON) from OET for following commands:
    * AssignResources
    * ReleaseResources
* Accept Dish, CSP and SDP configuration as JSON string from OET
* Configure Dishes, CSP subarray and SDP subarray
* Accept Scan command with time (in seconds) from OET and perform simple scan for the duration
* Accept EndSB command from OET
* Calculate dummy delay models and provide them to CSP subarray periodically


[0.1.1]
************

Release for SP-142 demo
-----

* Accept configuration as strings (JSON) from OET for following commands:
    * AssignResources
    * ReleaseResources
* Accept Dish configuration as JSON string from OET


[0.1.0]
************

Added
-----
[0.20.2]
*********
* Updated latest common  to include changes in SDP helper dish device for scan error propogation


[0.20.1]
*********
* Updated latest common repository to include changes related to index error

[0.20.0]
*********
* Added AdminMode functionality.

* Monitoring and control functionality with hierarchy of nodes
* Automatic control actions on Alerts using Elettra Alarm Handler
* LMC simulator for Dish
* Allocation and Deallocation of receptors in Subarray
* Basic configuration (setting target pointing coordinates) of a Subarray
* Commands and Events propagation
* TANGO group commands
* Conversion of Ra-Dec to Az-El coordinates using KATPoint
* Calculate Az-El periodically in Dish Leaf Node and implement tracking functionality in Dish Master
* Interface between the TMC and CSP Master:
	* Develop a CSP Master Leaf Node
	* Monitor/subscribe CSP Master attributes from CSP Master Leaf Node
	* Modify aggregation of overall Telescope Health (residing in Central Node) to include CSP Master health
	* Modify StartUpTelescope command on Central Node to start CSP Master device
* Accept configuration as strings (JSON) from OET for following commands:
    * AssignResources
    * ReleaseResources

Fixed
-----

* `Issue #26: AssignResources command is disabled in SubArray <https://github.com/ska-telescope/ska-tmc/issues/26>`_
* `Issue #12: make up fails <https://github.com/ska-telescope/ska-tmc/issues/12>`_
* `Issue #11: missing katpoint dependency <https://github.com/ska-telescope/ska-tmc/issues/11>`_
* `Issue #10: ska-registry.av.it.pt <https://github.com/ska-telescope/ska-tmc/issues/10>`_

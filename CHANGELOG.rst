###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

[0.1.0]
************

Added
-----

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

* `Issue #26: AssignResources command is disabled in SubArray <https://github.com/ska-telescope/tmc-prototype/issues/26>`_
* `Issue #12: make up fails <https://github.com/ska-telescope/tmc-prototype/issues/12>`_
* `Issue #11: missing katpoint dependency <https://github.com/ska-telescope/tmc-prototype/issues/11>`_
* `Issue #10: ska-registry.av.it.pt <https://github.com/ska-telescope/tmc-prototype/issues/10>`_

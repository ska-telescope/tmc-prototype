[![Documentation Status](https://readthedocs.org/projects/tmc-prototype/badge/?version=master)](https://developer.skatelescope.org/projects/tmc-prototype/en/master/?badge=master)

# tmc-prototype
This is the repository for TMC evolutionary prototype. The prototype aims to realize Telescope Monitoring and Control functionality, and utilizes the platform, tools and technology specified for the SKA construction. The prototype utilizes the base classes created in-line with the SKA Control System Guidelines and Tango coding standards.

## Prototype Scope
The design for the  TMC prototype (Stage I) is targeting the following architectural aspects and functionality:
### Architecture
* [x] Use of base classes for development of control nodes and Dish Master Simulator
* [x] Hierarchy of control nodes - Central node, Subarray node, Leaf Node
* [x] Interface between the TMC and Element LMC (Dish Master)
* [x] Use of Alarm Handler
* [x] Use of Central Logger

### Functionality
* [x] Monitoring and control functionality with hierarchy of nodes
* [ ] Alarm detection and handling 
* [x] Automatic control actions on Alerts
* [x] LMC simulator for Dish
* [x] Allocation and Deallocation of receptors in Subarray
* [x] Basic configuration (setting target pointing coordinates) of a Subarray
* [x] Commands and Events propagation
* [x] TANGO group commands

### Other (Tools/Technology/Framework)
* Linux/Ubuntu (16.04 LTS)
* Tango (9.2.5a)
* PyTango (9.2.4)
* Elettra, PANIC
* Pytest

## Install
TMC prototype (Stage I) includes the developement of Control Nodes and Dish Master Simulator. Installation steps for the Control nodes and Dish Master Simulator are provided in respective folders.

## Testing
Unit test cases are needed to be developed for testing of the Control Nodes and Dish Master Simulator.

## Docs
* [TMC Prototype (Stage I) Design Document](https://docs.google.com/document/d/1JFGXb8NGXPfi9ZwOQMPU6_Dwc1UxCHelRc-tjVVuoD0/edit?usp=sharing)

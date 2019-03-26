[![Documentation Status](https://readthedocs.org/projects/tmc-prototype/badge/?version=master)](https://developer.skatelescope.org/projects/tmc-prototype/en/master/?badge=master)

# TABLE OF CONTENTS

 * 1   - Introduction
     * 1.1 - Architecture
     * 1.2 - Functionality
 * 2   - Prerequisites
 * 3   - Installing, configuring and running the prototype (non-containerised environment)
     * 3.1 - Install SKA Base classes
     * 3.2 - Install Elettra Alarm Handler
     * 3.3 - Running tmc-prototype
     * 3.4 - Configuration of TANGO devices
     * 3.5 - Configure logging
     * 3.6 - Running the GUI
 * 4   - Unit and Integration Testing
     * 4.1 - Testing DishMaster
     * 4.2 - Testing DishLeafNode
     * 4.3 - Testing SubarrayNode
     * 4.4 - Testing CentralNode
 * 5   - Running tmcprototype inside Docker containers
 * 6   - Documentation

# 1: Introduction
This is the repository for TMC evolutionary prototype. The prototype aims to realize Telescope Monitoring and Control functionality, and utilizes the platform, tools and technology specified for the SKA construction.

The prototype utilizes the base classes created in-line with the SKA Control System Guidelines and Tango coding standards. Developed in **Python 3.5.2** (PyTango 9.5.2a), it is a single repository consisting four packages - CentralNode, SubarrayNode, DishLeafNode and DishMaster.

It also consists a Taurus based GUI in a separate folder which is only compatible with **Python 2.7.12**.

TMC prototype has covered (or planning to cover) following architectural aspects and functionality:

### 1.1: Architecture
* [x] Use of base classes for development of control nodes and Dish Master Simulator
* [x] Hierarchy of control nodes - Central node, Subarray node, Leaf Node
* [x] Interface between the TMC and Element LMC (Dish Master)
* [x] Integration of KATPOINT library
* [x] Use of Alarm Handler
* [x] Use of Central Logger
* [ ] Interface between the CentralNode/SubarrayNode and OET
* [ ] Interface between the TMC and CSP Master
* [ ] Source tracking

### 1.2: Functionality
* [x] Monitoring and control functionality with hierarchy of nodes
* [x] Automatic control actions on Alerts using Elettra Alarm Handler
* [x] LMC simulator for Dish
* [x] Allocation and Deallocation of receptors in Subarray
* [x] Basic configuration (setting target pointing coordinates) of a Subarray
* [x] Commands and Events propagation
* [x] TANGO group commands
* [x] Conversion of Ra-Dec to Az-El coordinates using KATPOINT
* [ ] Accept configuration as strings (JSON) from OET for following commands:
    * [ ] AssignResources
    * [ ] ReleaseResources
    * [ ] Configure (not planned for PI #2)
    * [ ] Scan (not planned for PI #2)
    * [ ] EndScan (not planned for PI #2)

* [ ] Calculate Az-El periodically in Dish Leaf Node and implement tracking functionality in Dish Master
* [ ] Monitor CSP Master using CSP Master Leaf Node

# 2: Prerequisites
* Linux/Ubuntu (16.04 LTS)
* Python 3.5.2
* pip for Python3
* [Tango (9.2.5a)](https://docs.google.com/document/d/1TMp5n380YMvaeqeKZvRHHXa7yVxT8oBn5xsEymyNFC4/edit?usp=sharing)
* [PyTango (9.2.4)](https://docs.google.com/document/d/1DtuIs1PeYGHlDXx8RyOzZyRQ-_Eiup-ncqeDDCtcNxk/edit?usp=sharing)
* skabase (LMC Base classes for SKA): Refer Section 3.1 for installation guide
* [Elettra Alarm Handler](https://docs.google.com/document/d/1uGnVrBGs6TvnORsM2m4hbORcAzn_KK2kAO8Roaocxjo/edit?usp=sharing)
* [katpoint](https://pypi.org/project/katpoint/)
* [pytest](https://pypi.org/project/pytest/)
* [pytest-cov](https://pypi.org/project/pytest-cov/)
* [pytest-json-report](https://pypi.org/project/pytest-json-report/)
* [pycodestyle](https://pypi.org/project/pycodestyle/)
* [pylint](https://pypi.org/project/pylint/)
* rsyslog

# 3: Installing, configuring and running the prototype (non-containerised environment)

### 3.1: Install SKA Base classes
Since TMC prototype is developed using SKA Base classes, we need to install them prior to running tmc-prototype.
Follow the steps specified at [this link](https://github.com/ska-telescope/lmc-base-classes) to install SKA Base classes.

### 3.2: Install Elettra Alarm Handler
Refer [this](https://docs.google.com/document/d/1uGnVrBGs6TvnORsM2m4hbORcAzn_KK2kAO8Roaocxjo/edit?usp=sharing) document for installation guide.

### 3.3: Running tmc-prototype
Scripts are provided in tmcprototype folder in order to start and stop all the TANGO Devices.

Navigate to the tmcprototype folder and run:

`./startAllDevices` #To start all the TMC Devices
`./stopAllDevices` #To stop all the TMC Devices



### 3.4: Configuration of TANGO devices

Start the TMC Devices and follow the screenshots for configuration of TANGO devices which are saved on Google drive at << this link >>.

#### DishMaster
Define and configure 4 instances of DishMaster TANGO Device server as specified in the given screenshots.

[Properties]

[Attribute Polling and Events]

[Miscellaneous]

#### DishLeafNode
Define and configure 4 instances of DishLeafNode TANGO Device server as specified in the given screenshots.

[Properties]

[Attribute Polling and Events]

[Miscellaneous]

#### SubarrayNode
Define and configure 2 instances of SubarrayNode TANGO Device server as specified in the given screenshots.

[Properties]

[Attribute Polling and Events]

[Miscellaneous]

#### CentralNode
Define and configure CentralNode TANGO Device server as specified in the given screenshots.

[Properties]

[Attribute Polling and Events]

[Miscellaneous]

#### AlarmHandler
Define and configure AlarmHandler TANGO Device server as specified in the given screenshots.

[Properties]

[Attribute Polling and Events]

[Miscellaneous]

#### SKALogger
Define and configure SKALogger TANGO Device server as specified in the given screenshots.

[Properties]

[Attribute Polling and Events]

[Miscellaneous]


### 3.5: Configure logging
To be updated soon...

### 3.6: Running the GUI

Once all the TMC TANGO devices are up and running, one can proceed to run the taurus GUI by following these steps:

* Navigate to the GUI folder on terminal (tmcprototype > GUI)
* Run the mainWindow_SKA.py file using the command:

    `python2 mainWindow_SKA.py`

**NOTE:** The GUI code is only compatible with Python 2.7.12.


# 4: Unit and Integration Testing
The hierarchy of TANGO devices are as follows:

Central Node -> SubarrayNode -> DishLeafNode -> DishMaster

(The flow from left to right depicts the Client -> Server relationship)

One needs to have DishMaster running prior to executing the test cases of DishLeafNode.
Similarly, one needs to have DishLeafNode and DishMaster running prior to executing the test cases of SubarrayNode.
And at last, SubarrayNode, DishLeafNode and DishMaster should be running prior to executing the test cases of CentralNode.

We are required to start the dependent TANGO devices in order to test a given TANGO devices due to this [issue.](http://www.tango-controls.org/community/forum/c/development/python/testing-tango-devices-using-pytest/)

Once the configuration of TMC TANGO devices is successful, one can proceed to test the prototype. Start the TMC TANGO devices as specified in (#running-tmc-prototype) section.

### 4.1: Testing DishMaster
* Navigate to the DishMaster folder:

    `cd tmcprototype/DishMaster/DishMaster`
* To excute test cases, run:

    `py.test --cov=DishMaster test/`

### 4.2 Testing DishLeafNode
**Note:** DishMaster TANGO Device should be up and running.

* Navigate to the DishLeafNode folder:

    `cd tmcprototype/DishLeafNode/DishLeafNode`
* To excute test cases, run:

    `py.test --cov=DishLeafNode test/`

### 4.3 Testing SubarrayNode
**Note:** DishLeafNode and DishMaster TANGO Devices should be up and running.

* Navigate to the SubarrayNode folder:

    `cd tmcprototype/SubarrayNode/SubarrayNode`
* To excute test cases, run:

    `py.test --cov=SubarrayNode test/`

### 4.4 Testing CentralNode
**Note:** Two instances of SubarrayNode (sub1, sub2), DishLeafNode and DishMaster TANGO Devices should be up and running.

* Navigate to the CentralNode folder:

    `cd tmcprototype/CentralNode/CentralNode`
* To excute test cases, run:

    `py.test --cov=CentralNode test/`

# 5: Running tmcprototype inside Docker containers
Although TMC prototype is running successfully using docker containers in CI Pipeline, there are some issues reported on running tmc-prototype with docker on local environment.
This section will be updated once those issues will be resolved.

# 6: Documentation
* [TMC Prototype (Stage I) Design Document](https://docs.google.com/document/d/1JFGXb8NGXPfi9ZwOQMPU6_Dwc1UxCHelRc-tjVVuoD0/edit?usp=sharing)
* [ReadTheDocs](https://developer.skatelescope.org/projects/tmc-prototype/en/master/)
* [OSO-UI / TMC PI2 meeting notes](https://docs.google.com/document/d/1sEEXwSMJatzFlP1iIw1d4ZrtEgvYvOS-_FPBmKd1i9A/edit)
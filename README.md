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
     * 3.5 - Running the GUI
 * 4   - Unit and Integration Testing
     * 4.1 - Testing DishMaster
     * 4.2 - Testing DishLeafNode
     * 4.3 - Testing SubarrayNode
     * 4.4 - Testing CentralNode
 * 5   - Running tmc-prototype inside Docker containers
 * 6   - Documentation

# 1: Introduction
This is the repository for TMC evolutionary prototype. The prototype aims to realize Telescope Monitoring and Control functionality, and utilizes the platform, tools and technology specified for the SKA construction.

The prototype utilizes the base classes created in-line with the SKA Control System Guidelines and Tango coding standards. Developed in **Python 3.5.2** (PyTango 9.5.2a), it is a single repository consisting four packages - CentralNode, SubarrayNode, DishLeafNode and DishMaster.

It also consists a Taurus based GUI in a separate folder which is compatible only with **Python 2.7.12**.

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
* [ ] Calculate Az-El periodically in Dish Leaf Node and implement tracking functionality in Dish Master
* [ ] Monitor CSP Master using CSP Master Leaf Node
* [x] Accept configuration as strings (JSON) from OET for following commands:
    * [x] AssignResources
    * [x] ReleaseResources

**NOTE:** Refer the Demo link provided in the [Documentation](#6-documentation) section for more details.

# 2: Prerequisites
* Linux/Ubuntu (16.04 LTS) (preferably)
* Python 3.5.2
* Python 2.7.12 (for Taurus GUI)
* [python3-pip](https://packages.ubuntu.com/xenial/python3-pip)
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
* [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) (for running in a containerised environment)
* [python-taurus](https://packages.ubuntu.com/xenial/python-taurus)

# 3: Installing, configuring and running the prototype (non-containerised environment)

### 3.1: Install SKA Base classes
Since TMC prototype is developed using SKA Base classes, we need to install them prior to running tmc-prototype.
Follow the steps specified at [this link](https://github.com/ska-telescope/lmc-base-classes) to install SKA Base classes.

### 3.2: Install Elettra Alarm Handler
Refer [this](https://docs.google.com/document/d/1uGnVrBGs6TvnORsM2m4hbORcAzn_KK2kAO8Roaocxjo/edit?usp=sharing) document for installation guide.

### 3.3: Running tmc-prototype on local environment (non-containerised)
Scripts are provided in tmcprototype folder in order to start and stop all the TANGO Devices.

Navigate to the tmcprototype folder and run:

`./startAllDevices`  #To start all the TMC Devices

`./stopAllDevices`   #To stop all the TMC Devices



### 3.4: Configuration of TANGO devices

Start the TMC Devices and follow the screenshots for configuration of TANGO devices which are saved on Google drive at [this link](https://drive.google.com/drive/folders/1NWyVQMNW1mw-YvEhACyhPKtEdKsysH1I).

#### DishMaster
Define and configure 4 instances of DishMaster TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/1OyuOe1bdexS6BAYndghnQ10OJeC-rnHD/view?usp=sharing)
* [Attribute Polling Configuration](https://drive.google.com/file/d/1JgYrDh2QTyOC72ABrTg1wxbXv5Au7FXK/view?usp=sharing)
* [Events Configuration](https://drive.google.com/file/d/1RTmY91IF23Qk3CtTu6WTIkJ3QIEGHpY8/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/12Wl5mL367BNP_Ss0xlSCOtcsbKg-K3ut/view?usp=sharing)

#### DishLeafNode
Define and configure 4 instances of DishLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/18Mezq9axZLl-ruxkrxWJUOXKDObICd_S/view?usp=sharing)
* [Attribute Polling Configuration](https://drive.google.com/file/d/1J5AJvdn5cJotRmkkySdkDlds1Y4WWvBK/view?usp=sharing)
* [Events Configuration](https://drive.google.com/file/d/1wxo33D5O-D83R4PunZQ9I3n1AzwfYxEO/view?usp=sharing)
* [Attribute Property](https://drive.google.com/file/d/1rDGLJcZB9_m-J9mdFVU7mug3AhUHFF19/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/1cZVDc6uK_z7JKlQbStWkceFQXaRL4QWu/view?usp=sharing)


#### SubarrayNode
Define and configure 2 instances of SubarrayNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/1AB7ZuviRw4h5rDxiXUjl4huU969z4Sg8/view?usp=sharing)
* [Attribute Polling Configuration](https://drive.google.com/file/d/1wtyaIfxOY2Cc_GwyDWmb7GUzf5syMqwE/view?usp=sharing)
* [Events Configuration](https://drive.google.com/file/d/1MVpcP-g6s67jje42nJuZH0sEp2GUdN8R/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/159Kl4Q7uvHzVNGrsZVzpYsdQbLiAeAc0/view?usp=sharing)

#### CentralNode
Define and configure CentralNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/1lzFvdrwSZKxdRoCnpsYcuMPQE8TME7Mr/view?usp=sharing)
* [Attribute Polling Configuration](https://drive.google.com/file/d/1XKItAKnK4Zqgs6-KQAcDUvu1om7ED1zk/view?usp=sharing)
* [Events Configuration](https://drive.google.com/file/d/1_jglNHV6jzVT3mSINhQ2LJnIxuo5Bdyk/view?usp=sharing)
* [Attribute Property 1](https://drive.google.com/file/d/1r-Fdd_vTitjZ7m3FCtZ5Y9_S2dKYKPOZ/view?usp=sharing)
* [Attribute Property 2](https://drive.google.com/file/d/1E5ig4n8eBwfI8TOdvXpXI3NnGOoeu-yN/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/1o9FH1blAfulYAYD8EuKebcxpQrG3LDqs/view?usp=sharing)


#### AlarmHandler
Define and configure AlarmHandler TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/11CETSDM9UMWeXF8mbL8zOXcKqZK5-N-j/view?usp=sharing)
* [Attribute Property](https://drive.google.com/file/d/1T_KhGFcPZzAIvT_YgDbTxmZNkHL3F5eQ/view?usp=sharing)

#### SKALogger
Define and configure SKALogger TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/1UxBUb71euQQrqMfMRQe7brfaClFnEL3t/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/1ExPvqqKg-2tXPZg_-rQophfDV5LpTa-a/view?usp=sharing)


### 3.5: Running the GUI

Once all the TMC TANGO devices are up and running, one can proceed to run the taurus GUI by following these steps:

* Navigate to the GUI folder on terminal
* Run the mainWindow_SKA.py file using the command:

    `python2 mainWindow_SKA.py`


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

# 5: Running tmc-prototype inside Docker containers

tmc-prototype can run on dockers using following command:

`make up`

In order to test the entire prototype, execute:

`make test`

To open the interactive mode using terminal, execute:

`make interactive`

# 6: Documentation
* [TMC Prototype (Stage I) Design Document](https://docs.google.com/document/d/1JFGXb8NGXPfi9ZwOQMPU6_Dwc1UxCHelRc-tjVVuoD0/edit?usp=sharing)
* [ReadTheDocs](https://developer.skatelescope.org/projects/tmc-prototype/en/master/)
* [OSO-UI / TMC PI2 meeting notes](https://docs.google.com/document/d/1sEEXwSMJatzFlP1iIw1d4ZrtEgvYvOS-_FPBmKd1i9A/edit)
* [TMC Stage I Prototype Demo](https://replay.skatelescope.org/replay/showRecordingExternal.html?key=3Na630an0coGgdK)

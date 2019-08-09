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
   * 4.2 - Testing CspMasterLeafNode
   * 4.3 - Testing CspSubarrayLeafNode
   * 4.4 - Testing SdpMasterLeafNode
   * 4.5 - Testing SdpSubarrayLeafNode
   * 4.6 - Testing DishLeafNode
   * 4.7 - Testing CSPMasterLeafNode
   * 4.8 - Testing SubarrayNode
   * 4.9 - Testing CentralNode
 * 5   - Running tmc-prototype inside Docker containers
 * 6   - Documentation

# 1: Introduction
This is the repository for TMC evolutionary prototype. The prototype aims to realize Telescope Monitoring and Control functionality, and utilizes the platform, tools and technology specified for the SKA construction.

The prototype utilizes the base classes created in-line with the SKA Control System Guidelines and Tango coding standards. Developed in **Python 3.5.2** (PyTango 9.5.2a), it is a single repository consisting eight packages - CentralNode, SubarrayNode, DishLeafNode, CspMasterLeafNode, CspSubarrayLeafNode, SdpMasterLeafNode, SdpSubarrayLeafNode and DishMaster.

TMC prototype addresses the  following architectural aspects and functionality:

### 1.1: Architecture
* [x] Use of base classes for development of control nodes and Dish Master, CspMaster, CspSubarray, SdpMaster, SdpSubarray and CbfTestMaster Simulators
* [x] Hierarchy of control nodes - Central node, Subarray node, Leaf Node
* [x] Interface between the TMC and Element LMC (Dish Master)
* [x] Integration of KATPoint library
* [x] Use of Alarm Handler
* [x] Use of Central Logger
* [x] Interface between the CentralNode/SubarrayNode and OET
* [x] Interface between the TMC and CSP (CspMaster and CspSubarray)
* [x] Interface between the TMC and SDP (SdpMaster and SdpSubarray)
* [x] Source tracking

### 1.2: Functionality

* [x] Monitoring and control functionality with hierarchy of nodes
* [x] Automatic control actions on Alerts using Elettra Alarm Handler
* [x] LMC simulator for Dish
* [x] Allocation and Deallocation of receptors to a Subarray
* [x] Commands and Events propagation
* [x] TANGO group commands
* [x] Conversion of Ra-Dec to Az-El coordinates using KATPoint
* [x] Calculate Az-El periodically in Dish Leaf Node and implement tracking functionality in the Dish simulator
* [x] Interface between the TMC and CSP:
   * [x] Develop CSP Master Leaf Node and CSP Subarray Leaf Node
   * [x] Monitor/subscribe CSP Master and CSP Subarray attributes from CSP Master Leaf Node and CSP Subarray Leaf Node respectively
   * [x] Aggregation of overall Telescope Health (residing in Central Node) to include CSP Master health
   * [x] Aggregation of Subarray Node health state to include CSP Subarray health
   * [x] StartUpTelescope command on Central Node to start CSP Master device
   * [x] Configure the CSP for a simple scan by relaying the configuration received from the OET
* [x] Interface between the TMC and SDP:
   * [x] Develop SDP Master Leaf Node and SDP Subarray Leaf Node
   * [x] Monitor/subscribe SDP Master and SDP Subarray attributes from SDP Master Leaf Node and SDP Subarray Leaf Node respectively
   * [x] Aggregation of overall Telescope Health (residing in Central Node) to include SDP Master health
   * [x] Aggregation of Subarray Node health state to include SDP Subarray health
   * [x] StartUpTelescope command on Central Node to start SDP Master device
   * [x] Configure the SDP for a simple scan by providing the configuration received from the OET
* [x] Accept configuration as strings (JSON) from OET for following commands:
  * [x] AssignResources
  * [x] ReleaseResources
* [x] Start a simple Scan and End the Scan
* [x] Calculation of time delay polynomials (Currently dummy delays are populated.)

**NOTE:** Refer to the Demo link provided in the [Documentation](#6-documentation) section for more details.

# 2: Prerequisites
* Linux/Ubuntu (16.04 LTS) (preferably)
* Python 3.5.2
* Python 2.7.12 (for Taurus GUI)
* [python3-pip](https://packages.ubuntu.com/xenial/python3-pip)
* [Tango (9.2.5a)](https://docs.google.com/document/d/1TMp5n380YMvaeqeKZvRHHXa7yVxT8oBn5xsEymyNFC4/edit?usp=sharing)
* [PyTango (9.2.4)](https://docs.google.com/document/d/1DtuIs1PeYGHlDXx8RyOzZyRQ-_Eiup-ncqeDDCtcNxk/edit?usp=sharing)
* skabase (LMC Base classes for SKA): Refer Section 3.1 for installation guide
* [Elettra Alarm Handler](https://docs.google.com/document/d/1uGnVrBGs6TvnORsM2m4hbORcAzn_KK2kAO8Roaocxjo/edit?usp=sharing)
* [KATPoint](https://pypi.org/project/katpoint/)
* [pytest](https://pypi.org/project/pytest/)
* [pytest-cov](https://pypi.org/project/pytest-cov/)
* [pytest-json-report](https://pypi.org/project/pytest-json-report/)
* [pycodestyle](https://pypi.org/project/pycodestyle/)
* [pylint](https://pypi.org/project/pylint/)
* rsyslog
* [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) (for running the prototype in a containerised environment)
* [Kubernetes (K8s)]([https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/))

# 3: Installing, configuring and running the prototype (non-containerised environment)

### 3.1: Install SKA Base classes
Since TMC prototype is developed using SKA Base classes, we need to install them prior to running tmc-prototype.
Follow the steps specified at [this link](https://github.com/ska-telescope/lmc-base-classes) to install SKA Base classes.

### 3.2: Install Elettra Alarm Handler
Alarm handler is optional feature and can be installed if desired. Refer [this](https://docs.google.com/document/d/1uGnVrBGs6TvnORsM2m4hbORcAzn_KK2kAO8Roaocxjo/edit?usp=sharing) document for installation guide.

### 3.3: Running tmc-prototype on local environment (non-containerised)
Scripts are provided in tmcprototype folder in order to start and stop all the TANGO Devices.

Navigate to the tmcprototype folder and run:

`./startAllDevices` #To start all the TMC Devices

`./stopAllDevices` #To stop all the TMC Devices


### 3.4: Configuration of TANGO devices

Start the TMC Devices and follow the screenshots for configuration of TANGO devices which are saved on Google drive at [this link](https://drive.google.com/drive/folders/1NWyVQMNW1mw-YvEhACyhPKtEdKsysH1I).

#### DishMaster
Define and configure 4 instances of DishMaster TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/1OyuOe1bdexS6BAYndghnQ10OJeC-rnHD/view?usp=sharing)
* [Attribute Polling Configuration](https://drive.google.com/file/d/1JgYrDh2QTyOC72ABrTg1wxbXv5Au7FXK/view?usp=sharing)
* [Events Configuration](https://drive.google.com/file/d/1RTmY91IF23Qk3CtTu6WTIkJ3QIEGHpY8/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/12Wl5mL367BNP_Ss0xlSCOtcsbKg-K3ut/view?usp=sharing)

#### CspMasterLeafNode
Define and configure 4 instances of CspMasterLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/11rdsQxq4sbkkyg3MgrcRVbh5iEAVKC9S/view?usp=sharing)
* [Attribute Polling Configuration](https://drive.google.com/file/d/188km3WwMApz1GkVdNVBmzsWp-VHP6KEK/view?usp=sharing)
* [Events Configuration](https://drive.google.com/file/d/1ZVJIDUvjphWfrFQCvr_lpFhBaYUSFDzV/view?usp=sharing)
* [Attribute Property](https://drive.google.com/file/d/1IU719MZJYPPv4C0w__XFaxzLLrDNsSEY/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/17Bd7zE-tDBaHu4O1ciIow8XxNsNioVDJ/view?usp=sharing)

#### CspSubarrayLeafNode
Define and configure 4 instances of CspSubarrayLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/1iraqklKUvnH3fAMEVRW9PKXspyeRMmxk/view?usp=sharing)
* [Attribute Polling Configuration](https://drive.google.com/file/d/1W5P9MbkqCJpWhhdLuUrcVE-48zUSTKcW/view?usp=sharing)
* [Events Configuration](https://drive.google.com/file/d/1ZQdWDeOTOzTT4YI-u3yn0dE6C80R6M8X/view?usp=sharing)
* [Attribute Property](https://drive.google.com/file/d/1N-KPCOmXPQrI8c7LVttdnYpyg1D_hsDC/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/1F_AuoB39Xvlz-9FiOqF14_QnfqpLT1hF/view?usp=sharing)

#### SdpMasterLeafNode
Define and configure 4 instances of SdpMasterLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/13AIHf7sM9YdHkIYqVaBjdl8OeX-pYwmz/view?usp=sharing)
* [Attribute Polling Configuration](https://drive.google.com/file/d/1LHjxu9F9dAaWW6_D5sPnqYgBKFO_PE7F/view?usp=sharing)
* [Events Configuration](https://drive.google.com/file/d/1KW1ZKUlz5ylYwUcoCL6xhpW7jo6OK7BI/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/1LbdTD4g-W4zUnKHvc1eLjMkFCdzo37Vu/view?usp=sharing)

#### SdpSubarrayLeafNode
Define and configure 4 instances of SdpSubarrayLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/file/d/1Op_H8GGW3t9xd-e36LikDayZF3zMvQ8x/view?usp=sharing)
* [Attribute Polling Configuration](https://drive.google.com/file/d/1ah6jPSQAmNin40Ec4Qquf14FT5f8P9Q2/view?usp=sharing)
* [Events Configuration](https://drive.google.com/file/d/1d_6JCW7ekEXboZAlkDNXotqvV6y4qnvI/view?usp=sharing)
* [Attribute Property](https://drive.google.com/file/d/1ky8LSE25L4uOppybyheovCEFxH0NjpnW/view?usp=sharing)
* [Logging Configuration](https://drive.google.com/file/d/13cYGQTlhpxDnkiFHPy8u_O6NJ6tG9bTf/view?usp=sharing)

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


### 3.5: GUI

The GUI is an optional component not contained in the TMC prototype repository. The GUI is created using Webjive and configured for the TMC devices.

# 4: Unit and Integration Testing
The hierarchy of TANGO devices are as follows:

Central Node -> SubarrayNode -> DishLeafNode/CspMasterLeafNode/CspSubarrayLeafNode/SdpMasterLeafNode/SdpSubarrayLeafNode -> DishMaster/CspMaster/CspSubarray/SdpMaster/SdpSubarray

(The flow from left to right depicts the Client -> Server relationship)

One needs to have DishMaster/CspMaster/CspSubarray/SdpMaster/SdpSubarray running prior to executing the test cases of DishLeafNode/CspMasterLeafNode/CspSubarrayLeafNode/SdpMasterLeafNode/ SdpSubarrayLeafNode.
Similarly, one needs to have DishLeafNode/CspMasterLeafNode/CspSubarrayLeafNode/ SdpMasterLeafNode/SdpSubarrayLeafNode and DishMaster/CspMaster/CspSubarray/SdpMaster /SdpSubarray running prior to executing the test cases of SubarrayNode. And at last, SubarrayNode, DishLeafNode/CspMasterLeafNode/CspSubarrayLeafNode/SdpMasterLeafNode/SdpSubarrayLeafNode and DishMaster/CspMaster/CspSubarray/SdpMaster/SdpSubarray should be running prior to executing the test cases of CentralNode.

The dependent TANGO devices are required to be started in order to test a given TANGO device due to this [issue.](http://www.tango-controls.org/community/forum/c/development/python/testing-tango-devices-using-pytest/)

The prototype can be tested once the configuration of TMC TANGO devices is completed. Start the TMC TANGO devices as specified in (#running-tmc-prototype) section.

**Note:** Refer [csp-lmc-prototype](https://github.com/ska-telescope/csp-lmc-prototype) for CSP TANGO devices.

### 4.1 Testing DishMaster
* Navigate to the DishMaster folder:

    `cd tmcprototype/DishMaster/DishMaster`

* To execute test cases, run:

    `py.test --cov=DishMaster test/`

### 4.2 Testing CspMasterLeafNode
**Prerequisite:** CspMaster TANGO Device should be up and running.

* Navigate to the CspMasterLeafNode folder:

    `cd tmcprototype/CspMasterLeafNode/CspMasterLeafNode`

* To execute test cases, run:

    `py.test --cov=CspMasterLeafNode test/`

### 4.3 Testing CspSubarrayLeafNode
**Prerequisite:** CspSubarray TANGO Device should be up and running.

* Navigate to the CspSubarrayLeafNode folder:

    `cd tmcprototype/CspSubarrayLeafNode/CspSubarrayLeafNode`

* To execute test cases, run:

    `py.test --cov=CspSubarrayLeafNode test/`

### 4.4 Testing SdpMasterLeafNode
**Prerequisite:** SdpMaster TANGO Device should be up and running.

* Navigate to the SdpMasterLeafNode folder:

    `cd tmcprototype/SdpMasterLeafNode/SdpMasterLeafNode`

* To execute test cases, run:

    `py.test --cov=SdpMasterLeafNode test/`

### 4.5 Testing SdpSubarrayLeafNode
**Prerequisite:** SdpSubarray TANGO Device should be up and running.

* Navigate to the SdpSubarrayLeafNode folder:

    `cd tmcprototype/SdpSubarrayLeafNode/SdpSubarrayLeafNode`

* To execute test cases, run:

    `py.test --cov=SdpSubarrayLeafNode test/`

### 4.6 Testing DishLeafNode
**Prerequisite:** DishMaster TANGO Device should be up and running.

* Navigate to the DishLeafNode folder:

    `cd tmcprototype/DishLeafNode/DishLeafNode`

* To execute test cases, run:

    `py.test --cov=DishLeafNode test/`

### 4.8 Testing SubarrayNode
**Prerequisite:** DishLeafNode and DishMaster TANGO Devices should be up and running.

* Navigate to the SubarrayNode folder:

    `cd tmcprototype/SubarrayNode/SubarrayNode`

* To execute test cases, run:

    `py.test --cov=SubarrayNode test/`

### 4.9 Testing CentralNode
**Prerequisite:** Two instances of SubarrayNode (sub1, sub2), DishLeafNode and DishMaster TANGO Devices should be up and running.

* Navigate to the CentralNode folder:

    `cd tmcprototype/CentralNode/CentralNode`

* To execute test cases, run:

    `py.test --cov=CentralNode test/`

# 5: Running tmc-prototype inside Docker containers

tmc-prototype can run on dockers using following command:

`make up`

 To stop the containers, use command:

```  make down```

In order to test the entire prototype, execute:

`make test`


# 6: Documentation
* [TMC Prototype (Stage II) Design Document](https://docs.google.com/document/d/1DaLCQZ79yMlGYm2GPE03KpQ80kzjb1f98bWhgV_2Rpo/edit?usp=sharing)
* [ReadTheDocs](https://developer.skatelescope.org/projects/tmc-prototype/en/master/)
* [TMC Prototype Learnings](https://docs.google.com/document/d/1DMhb_6NM0oaZMhSwEE79_B-MwycwzuH-RJsuOd5Zjlw/edit?usp=sharing)
* [System Demo #2 (Recording)]([https://www.dropbox.com/sh/ecqqky7ze5oaehm/AACBPF95iub58Y_OIIT-V4XZa?dl=0](https://www.dropbox.com/sh/ecqqky7ze5oaehm/AACBPF95iub58Y_OIIT-V4XZa?dl=0))
* [System Demo #2 (PPT)](https://drive.google.com/file/d/1pv8B3HDvNlUR3fd69_urpALWF7wwmlKG/view?usp=sharing)
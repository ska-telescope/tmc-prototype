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
   * 4.3 - Testing CspMasterLeafNode
   * 4.4 - Testing CspSubarrayLeafNode
   * 4.5 - Testing SdpMasterLeafNode
   * 4.6 - Testing SdpSubarrayLeafNode
   * 4.7 - Testing SubarrayNode
   * 4.8 - Testing CentralNode
 * 5   - Running tmc-prototype inside Docker containers
 * 6   - Documentation

# 1: Introduction
This is the repository for TMC evolutionary prototype. The prototype aims to realize Telescope Monitoring and Control functionality, and utilizes the platform, tools and technology specified for the SKA construction.

The prototype utilizes the base classes created in-line with the SKA Control System Guidelines and Tango coding standards. Developed in **Python 3.6** (PyTango 9.5.2a), it is a single repository consisting eight packages - CentralNode, SubarrayNode, DishLeafNode, CspMasterLeafNode, CspSubarrayLeafNode, SdpMasterLeafNode, SdpSubarrayLeafNode and DishMaster.

TMC prototype addresses the  following architectural aspects and functionality:

### 1.1: Architecture
* [x] Use of base classes for development of TMC control nodes and element simulator such as Dish Master
* [x] Hierarchy of control nodes - Central Node, Subarray Node, Leaf Node
* [x] Interface between the TMC and Element LMC (Dish Master)
* [x] Interface between the CentralNode/SubarrayNode and OET
* [x] Interface between the TMC and CSP (CspMaster and CspSubarray)
* [x] Interface between the TMC and SDP (SdpMaster and SdpSubarray)
* [x] Integration of KATPoint library for pointing and delay calculation 
* [x] Use of Alarm Handler
* [x] Use of SKA Logger
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
   * [x] Use of CSP Master health to calculate overall Telescope Health (in Central Node)
   * [x] Use of CSP Subarray health to calculate Subarray Node health state
   * [x] StartUpTelescope command on Central Node to change CSP Master device state to ON
   * [x] Configure the CSP for a simple scan
   * [x] Publish Delay coefficients at regular time interval on CSP Subarray Leaf Node per Subarray
* [x] Interface between the TMC and SDP:
   * [x] Develop SDP Master Leaf Node and SDP Subarray Leaf Node
   * [x] Monitor/subscribe SDP Master and SDP Subarray attributes from SDP Master Leaf Node and SDP Subarray Leaf Node respectively
   * [x] Use of SDP Master health to calculate overall Telescope Health (in Central Node)
   * [x] Use of SDP Subarray health to calculate Subarray Node health state
   * [x] StartUpTelescope command on Central Node to change SDP Master device state to ON
   * [x] Configure the SDP for a simple scan
* [x] Telescope Startup and Standby
* [x] Accept configuration as strings (JSON) from OET for following commands:
  * [x] AssignResources
  * [x] ReleaseResources
* [x] Start Configure command on Subarray
* [x] Start a simple Scan and End the Scan
* [x] EndSB command on SubarrayNode
* [x] Calculate Geometric delay values (in seconds) per antenna on CSP Subarray Leaf Node
* [x] Convert delay values (in seconds) to 5th order polynomial coefficients

**NOTE:** Refer to the Demo link provided in the [Documentation](#6-documentation) section for more details.

# 2: Prerequisites
* Linux/Ubuntu (18.04 LTS) 
* Python 3.6
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
* [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) (for running the prototype in a containerised environment)
* [Kubernetes (K8s)](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/)

# 3: Installing, configuring and running the prototype (non-containerised environment)

### 3.1: Install SKA Base classes
Since TMC prototype is developed using SKA Base classes, we need to install them prior to running tmc-prototype.
Follow the steps specified at [this link](https://github.com/ska-telescope/lmc-base-classes) to install SKA Base classes.

### 3.2: Install Elettra Alarm Handler
Alarm handler is an optional feature and can be installed if desired. Refer [this](https://docs.google.com/document/d/1uGnVrBGs6TvnORsM2m4hbORcAzn_KK2kAO8Roaocxjo/edit?usp=sharing) document for installation guide.

### 3.3: Running tmc-prototype on local environment (non-containerised)
Scripts are provided in tmcprototype folder in order to start and stop all the TANGO Devices.

Navigate to the tmcprototype folder and run:

`./startAllDevices` #To start all the TMC Devices

`./stopAllDevices` #To stop all the TMC Devices


### 3.4: Configuration of TANGO devices

Start the TMC Devices and follow the screenshots for configuration of TANGO devices which are saved on Google drive at [this link](https://drive.google.com/drive/folders/1NWyVQMNW1mw-YvEhACyhPKtEdKsysH1I).

#### DishMaster
Define and configure 4 instances of DishMaster TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=1G1NHeK-XJ_lFtVT8anjk9J3-tpH4c_IV)
* [Attribute Polling Configuration](https://drive.google.com/open?id=1NlduVk23cBcGou1jpkrRILzwW-53Fl28)
* [Events Configuration](https://drive.google.com/open?id=13EdgU_5BhesN9wloeHIvSEZGJ7nY00EA)

#### CspMasterLeafNode
Define and configure 1 instance of CspMasterLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=1VyLxuuFJjA94iYDt3y0JZe6cDg8jh25U)
* [Attribute Polling Configuration](https://drive.google.com/open?id=1GAjvKtTAGkMg_77eqGdBy7HNNg4El01v)
* [Events Configuration](https://drive.google.com/open?id=1GAjvKtTAGkMg_77eqGdBy7HNNg4El01v)
* [Attribute Property](https://drive.google.com/open?id=15ZYaVP8vKeIDXZ05qhlSzsvjhsAEZFT4)

#### CspSubarrayLeafNode
Define and configure 3 instances of CspSubarrayLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=1NQmm5fSkrDNRU51VKGOUIpUFliqBJe6G)
* [Attribute Polling Configuration](https://drive.google.com/open?id=1rVIayVKOmp0Uzr3vgl5hL5klpmEnoDWX)
* [Events Configuration](https://drive.google.com/open?id=1-O79aqX_5QgKOz9iwSDKAgPJ-rquKOoC)
* [Attribute Property](https://drive.google.com/open?id=1NQmm5fSkrDNRU51VKGOUIpUFliqBJe6G)

#### SdpMasterLeafNode
Define and configure 1 instances of SdpMasterLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=1mwgI569BURblQEkA21g2Dcc6icX0UDnR)
* [Attribute Polling Configuration](https://drive.google.com/open?id=1b8qLjuNU2FYhLyEcs212vcrkzSHhWJVz)
* [Events Configuration](https://drive.google.com/open?id=173vg_wcNLayRbMK75Ii_lsih8MRPdW6F)

#### SdpSubarrayLeafNode
Define and configure 3 instances of SdpSubarrayLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=1mykD_LXB1KoLAAcNvlIx4RJABLf4M8bf)
* [Attribute Polling Configuration](https://drive.google.com/open?id=1y6NP3hT367F-DqegFStQWTTemxriv4jK)
* [Events Configuration](https://drive.google.com/open?id=1GpgCrbDvn9x780TXziw-TzxGT8_i7Ngl)
* [Attribute Property](https://drive.google.com/open?id=1hMQ74xkrdB16J4JGcr3E7hBFshNdBJZQ)

#### DishLeafNode
Define and configure 4 instances of DishLeafNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=18vNSpi4Jx6fCZGKYwlhX55dY7ZbVXGnW)
* [Attribute Polling Configuration](https://drive.google.com/open?id=1f4tjcswQpEsRYBaDUdoh-ZWTCqhVUwBU)
* [Events Configuration](https://drive.google.com/open?id=13YtvVCDzmqDbhzI3ukCEHarReh6R2urr)
* [Attribute Property](https://drive.google.com/open?id=1B2ehixv08yGrqHorL27KHIIGiZnMWw8M)

#### SubarrayNode
Define and configure 3 instances of SubarrayNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=1OrZ3y1xbLhN-4_jxtCejAbSefVEUrId-)
* [Attribute Polling Configuration](https://drive.google.com/open?id=1T-lzMrwW8e6b4GZIrdHZJCSXSOQj8s4O)
* [Events Configuration](https://drive.google.com/open?id=1haJAKSLNrnkx7RAZlyylhkah31LiRJ75)

#### CentralNode
Define and configure CentralNode TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=1A5bQvtvRv_EZbNelrsb0rS38GZ5bXbnY)
* [Attribute Polling Configuration](https://drive.google.com/open?id=1AfVIwQJmULBHBAbArTm_CEILYfXTvzl8)
* [Events Configuration](https://drive.google.com/open?id=15UBTGLLKobWTf53xgc88e3YjEJSyHPK3)
* [Attribute Property 1](https://drive.google.com/file/d/1r-Fdd_vTitjZ7m3FCtZ5Y9_S2dKYKPOZ/view?usp=sharing)
* [Attribute Property 2](https://drive.google.com/file/d/1E5ig4n8eBwfI8TOdvXpXI3NnGOoeu-yN/view?usp=sharing)

#### AlarmHandler
Define and configure AlarmHandler TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=1eOtmi1ANOm1tkgDiJMjB7dvMhY7J2IxH)
* [Attribute Property](https://drive.google.com/open?id=1r0hrbsmt-8AwCGkeHvsYy9Nd9eUZ46CO)

#### SKALogger
Define and configure SKALogger TANGO Device server as specified in the given screenshots.

* [Device Properties](https://drive.google.com/open?id=1zNe5jLZMWJmdq2iQVNAYsWJ-IhTe_t8J)


# 4: Unit and Integration Testing
The hierarchy of TANGO devices are as follows:
Central Node -> SubarrayNode -> DishLeafNode/DishMaster
                             -> CspMasterLeafNode/CspMaster
                             -> CspSubarrayLeafNode/CspSubarray
                             -> SdpMasterLeafNode/SdpMaster
                             -> SdpSubarrayLeafNode ->SdpSubarray

(The flow from left to right depicts the Client -> Server relationship)

One needs to have DishMaster/CspMaster/CspSubarray/SdpMaster/SdpSubarray running prior to executing the test cases of DishLeafNode/CspMasterLeafNode/CspSubarrayLeafNode/SdpMasterLeafNode/ SdpSubarrayLeafNode.
Similarly, one needs to have DishLeafNode/CspMasterLeafNode/CspSubarrayLeafNode/SdpMasterLeafNode/SdpSubarrayLeafNode and DishMaster/CspMaster/CspSubarray/SdpMaster /SdpSubarray running prior to executing the test cases of SubarrayNode. And at last, SubarrayNode, DishLeafNode/CspMasterLeafNode/CspSubarrayLeafNode/SdpMasterLeafNode/SdpSubarrayLeafNode and DishMaster/CspMaster/CspSubarray/SdpMaster/SdpSubarray should be running prior to executing the test cases of CentralNode.

The dependent TANGO devices are required to be started in order to test a given TANGO device due to this [issue.](http://www.tango-controls.org/community/forum/c/development/python/testing-tango-devices-using-pytest/)

The prototype can be tested once the configuration of TMC TANGO devices is completed. Start the TMC TANGO devices as specified in (#running-tmc-prototype) section.

**Note:** Refer [csp-lmc-prototype](https://github.com/ska-telescope/csp-lmc-prototype) for CSP TANGO devices.
          Refer [sdp-prototype](https://github.com/ska-telescope/sdp-prototype) for SDP TANGO devices.

### 4.1 Testing DishMaster
* Navigate to the DishMaster folder:

    `cd tmcprototype/DishMaster/DishMaster`

* To execute test cases, run:

    `py.test --cov=DishMaster test/`

### 4.2 Testing DishLeafNode
**Prerequisite:** DishMaster TANGO Device should be up and running.

* Navigate to the DishLeafNode folder:

    `cd tmcprototype/DishLeafNode/DishLeafNode`

* To execute test cases, run:

    `py.test --cov=DishLeafNode test/`

### 4.3 Testing CspMasterLeafNode
**Prerequisite:** CspMaster TANGO Device should be up and running.

* Navigate to the CspMasterLeafNode folder:

    `cd tmcprototype/CspMasterLeafNode/CspMasterLeafNode`

* To execute test cases, run:

    `py.test --cov=CspMasterLeafNode test/`

### 4.4 Testing CspSubarrayLeafNode
**Prerequisite:** CspSubarray TANGO Device should be up and running.

* Navigate to the CspSubarrayLeafNode folder:

    `cd tmcprototype/CspSubarrayLeafNode/CspSubarrayLeafNode`

* To execute test cases, run:

    `py.test --cov=CspSubarrayLeafNode test/`

### 4.5 Testing SdpMasterLeafNode
**Prerequisite:** SdpMaster TANGO Device should be up and running.

* Navigate to the SdpMasterLeafNode folder:

    `cd tmcprototype/SdpMasterLeafNode/SdpMasterLeafNode`

* To execute test cases, run:

    `py.test --cov=SdpMasterLeafNode test/`

### 4.6 Testing SdpSubarrayLeafNode
**Prerequisite:** SdpSubarray TANGO Device should be up and running.

* Navigate to the SdpSubarrayLeafNode folder:

    `cd tmcprototype/SdpSubarrayLeafNode/SdpSubarrayLeafNode`

* To execute test cases, run:

    `py.test --cov=SdpSubarrayLeafNode test/`

### 4.7 Testing SubarrayNode
**Prerequisite:** All TMC LeafNodes, DishMaster, CSPMaster, CSPSubarray, SDPMaster and SDPSubarray TANGO Devices should be up and running.

* Navigate to the SubarrayNode folder:

    `cd tmcprototype/SubarrayNode/SubarrayNode`

* To execute test cases, run:

    `py.test --cov=SubarrayNode test/`

### 4.8 Testing CentralNode
**Prerequisite:** All instances of SubarrayNodes, all TMC LeafNodes, DishMaster, CSPMaster, CSPSubarray, SDPMaster and SDPSubarray TANGO Devices should be up and running.

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
* [TMC Stage I Prototype Demo](https://replay.skatelescope.org/replay/showRecordingExternal.html?key=3Na630an0coGgdK)
* [System Demo #2 (Recording)](https://www.dropbox.com/sh/ecqqky7ze5oaehm/AACBPF95iub58Y_OIIT-V4XZa?dl=0)
* [System Demo #2 (PPT)](https://drive.google.com/file/d/1pv8B3HDvNlUR3fd69_urpALWF7wwmlKG/view?usp=sharing)
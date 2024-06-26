[![Documentation Status](https://readthedocs.org/projects/ska-telescope-ska-tmc-sdpleafnodes/badge/?version=latest)](https://developer.skao.int/projects/ska-tmc-sdpleafnodes/en/latest/?badge=latest)
 
# TABLE OF CONTENTS
 
* 1   - Introduction
 * 1.1 - Architecture
 * 1.2 - TMC Functionality
* 2   - Prerequisites
* 3   - Installing, configuring and running the ska-tmc-sdpleafnodes (non-containerised environment)
 * 3.1 - Installing Dependencies
* 4   - Testing
 * 4.1 - Unit Testing
 * 4.2 - Integration Testing
 * 4.3 - Manual Testing
* 5   - Formatting & Linting
* 6   - Documentation
 
# 1 Introduction
 
This is the repository for the TMC evolutionary prototype. Ska-tmc-sdpleafnodes aims to realize TMC SdpLeafNodes Monitoring and Control functionality, and utilizes the platform, tools and technology specified for the SKA construction.
 
The ska-tmc-sdpleafnodes utilizes the base classes created in-line with the SKA Control System Guidelines and Tango coding standards. Developed in **Python 3.7** (PyTango 9.3.3), it is a single repository which releases a single package called ska-tmc-sdpleafnodes. ska-tmc-sdpleafnodes contains two sub packages - SdpMasterLeafNode and SdpSubarrayLeafNode.
CentralNode device is implementated in a separate gitlab repository which is available at <https://gitlab.com/ska-telescope/ska-tmc-centralnode> .
SubarrayNode device is implemented in a separate gitlab repository which is available at <https://gitlab.com/ska-telescope/ska-tmc-subarraynode> .
SKA-TMC-SDPLEAFNODES addresses the  following architectural aspects and functionality:
 
## 1.1 Architecture
* [x] Use of LMC base classes for development of TMC SDP Leaf nodes.
* [x] Hierarchy of control nodes for Mid and Low- Central Node, Subarray Node, Leaf Node
 
* [x] Interface between the Dish Leaf Node and Dish(Master simulator)
* [x] Interface between the CSP Leaf Node and CSP (CSP Master and Csp Subarray devices)
* [x] Interface between the SDP Leaf Node  and SDP (SDP Master and SDP Subarray devices)
* [x] Interface between the MCCS Leaf Node and MCCS (MCCS Master and MCCS Subarray devices)
* [x] Integration of KATPoint library (1.0a1) for pointing and delay calculation for CSP Leaf Nodes.
* [x] Use of SKA Logger as the logging solution
* [x] Use of HDB++ Archiver as the archiving solution
* [x] Source tracking for TMC-Mid
* [x] Adopted ADR-8 observation state machine
 
## 1.2 TMC Functionality
 
* [x] Monitoring and control functionality with hierarchy of nodes
* [x] Automatic control actions on Alerts using Elettra Alarm Handler
* [x] Simulator for DishMaster
* [x] Allocation and Deallocation of receptors to a Subarray
* [x] Commands and Events propagation
* [x] TANGO group commands
* [x] Conversion of Ra-Dec to Az-El coordinates using KATPoint for TMC-Mid
* [x] Calculate Az-El periodically in Dish Leaf Node and implement tracking functionality in the Dish simulator
* [x] Interface between the TMC and CSP:
 * [x] Implementation of CSP Master Leaf Node and CSP Subarray Leaf Node
 * [x] Monitor/subscribe CSP Master and CSP Subarray attributes from CSP Master Leaf Node and CSP Subarray Leaf Node respectively
 * [x] Use of CSP Master health to calculate overall Telescope Health (in Central Node Mid)
 * [x] Use of CSP Subarray health to calculate Subarray Node health state
 * [x] StartUpTelescope command on Central Node to change CSP Master device and CSP Subarray device state to ON
 * [x] Configure the CSP for a simple scan
 * [x] Publish Delay coefficients at regular time interval (every 10 seconds) on CSP Subarray Leaf Node per Subarray
* [x] Interface between the TMC and SDP:
 * [x] Implementation of SDP Master Leaf Node and SDP Subarray Leaf Node
 * [x] Monitor/subscribe SDP Master and SDP Subarray attributes from SDP Master Leaf Node and SDP Subarray Leaf Node respectively
 * [x] Use of SDP Master health to calculate overall Telescope Health (in Central Node Mid)
 * [x] Use of SDP Subarray health to calculate Subarray Node health state
 * [x] StartUpTelescope command on Central Node to change SDP Master device and SDP Subarray device state to ON
 * [x] Configure the SDP for a simple scan
* [x] Interface between the TMC and MCCS:
 * [x] Implementation of MCCS Master Leaf Node and MCCS Subarray Leaf Node
 * [x] Monitor/subscribe MCCS Master and MCCS Subarray attributes from MCCS Master Leaf Node and MCCS Subarray Leaf Node respectively
 * [x] Use of MCCS Master health to calculate overall Telescope Health (in Central Node Low)
 * [x] Use of MCCS Subarray health to calculate Subarray Node health state
 * [x] StartUpTelescope command on Central Node Low to change MCCS Master device state to ON
 * [X] AssignResources command on Central Node Low to change MCCS Subarray device state to ON and allocates resources to MCCS Subarray through MCCS Master
 * [x] Configure the MCCS for a simple scan
 * [x] TMC commands/functionality to execute entire obsevation cycle
 * [x] Telescope Startup
 * [x] AssignResources command to allocate resources to the SubarrayNode
 * [x] Execute Configure command for a Subarray
 * [x] Execute Scan and End the Scan
 * [x] End command on SubarrayNode to end the scheduling block
 * [x] ReleaseResources commands to deallocate resources from the SubarrayNode
 * [x] Telescope Standby
* [x] Configure and execute multiple scans for TMC-Mid
* [x] Implement the observation state model and state transitions as per [ADR-8.](https://confluence.skatelescope.org/pages/viewpage.action?pageId=105416556)
* [x] Calculate Geometric delay values (in seconds) per antenna on CSP Subarray Leaf Node
* [x] Convert delay values (in seconds) to 5th order polynomial coefficients for TMC-Mid
* [x] Abort an ongoing operation, and Restart the control nodes, catch exceptions in the AssignResource workflow, log the exception details and raise them to the calling components for TMC-Mid.
* [x] Implementation of obsReset functinality (as per ADR-8) in which resource allocation in Subarray is retained and only the scan configuration parameters are cleared for TMC-Mid.
* [x] Update the JSON strings (command inputs and attributes) in the TMC as per ADR-35
 
**NOTE:** Refer to the Demo link provided in the [Documentation](#6-documentation) section for more details.
 
# 2 Prerequisites
 
* Linux/Ubuntu (18.04 LTS)
* Python 3.7
* [python3-pip](https://packages.ubuntu.com/xenial/python3-pip)
* [Tango (9.3.4-rc2)](https://docs.google.com/document/d/1TMp5n380YMvaeqeKZvRHHXa7yVxT8oBn5xsEymyNFC4/edit?usp=sharing)
* [PyTango (9.3.3)](https://docs.google.com/document/d/1DtuIs1PeYGHlDXx8RyOzZyRQ-_Eiup-ncqeDDCtcNxk/edit?usp=sharing)
* [ska-tango-base (0.11.3)] (LMC Base classes for SKA)
* [ska-ser-logging](https://gitlab.com/ska-telescope/ska-ser-logging)
* [ska-tmc-cdm](https://gitlab.com/ska-telescope/ska-tmc-cdm)
* [telescope-model](https://gitlab.com/ska-telescope/telescope-model)
* [KATPoint](https://pypi.org/project/katpoint/)
* [pytest](https://pypi.org/project/pytest/)
* [pytest-cov](https://pypi.org/project/pytest-cov/)
* [pytest-json-report](https://pypi.org/project/pytest-json-report/)
* [pycodestyle](https://pypi.org/project/pycodestyle/)
* [pylint](https://pypi.org/project/pylint/)
* [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) (for running the ska-tmc in a containerised environment)
* [Kubernetes (K8s)/Minikube](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/)
* [tango-simlib](https://tango-simlib.readthedocs.io/en/latest/)
* [poetry (1.1.13)](https://python-poetry.org/docs/)
 
# 3 Installing, configuring and running the ska-tmc-sdpleafnodes
 
## 3.1 Installing dependencies
 
Since the SKA-TMC-SDPLEAFNODES is developed using LMC Base and SKA-TMC_Common classes, we need to install them prior to running ska-tmc-sdpleafnodes.
 
Use following commmand to install all necessary dependencies on your virtual environment:       `poetry install`
 
# 4 Testing
 
## 4.1 Unit Testing
 
As depicted above, the higher level of TMC SDP leaf nodes are dependent on lower level devices in normal operation.
However for better testability, the unit testing is carried out by mocking the dependent devices.
This enables us to test each of the nodes independently without setting up the entire hierarchy of control nodes.
In order to execute the entire suit of test cases in the repository, a command in makefile is implemented. \
The command to run the unit tests in python virtual environment is: `make python-test` \
 
## 4.2 Integration Testing
 
_Note: This section will soon be updated._
 
Integration Testing is performed on SKA Integration on K8S environment. For this testing TMC-SDPLEAFNODES image is required to
build locally or need to be available on Nexus repository.
All the Dependent Nodes are mocked in our kubernetes cluster, while integration testing.
The command to run the Integration tests is: `make k8s-test` \
 
## 4.3 Manual Testing
 
The SKA-TMC-SDPLEAFNODES can be deployed in the development environment. The TMC-SDPLEAFNODES needs to be deployed in kubernetes environment. The deployment consists of real TMC SDP leaf nodes and mocked dependent nodes(SDP).
 
### 4.3.1 System Requirements
 
Following are the system requirements to deploy the TMC-SDPLEAFNODES:
 
Requirement | Minimum | Recommended
---- | ---- | ----
CPU cores    | 4       | 8
RAM          | 8 GB       | 16 GB
Storage      | 64 GB      | 100 GB
 
### 4.3.2 Deploying TMC
 
This section is TBD:
Deploy the TMC-SDPLEAFNODES using `make k8s-install-chart` command.
The `make k8s-watch` command can be used to monitor the pods to ensure all required pods are up and running.
 
 
<!-- **Deployment in standalone mode**
 
Note: This section is WIP. The simulator work is in progress.
TMC can be deployed in standalone mode as well. That means, for smaller setup other subsystem devices are not required to be deployed along with TMC. Simulators for the devices which interact with TMC are developed. Simulator for SDP Master,CSP Master, CSP Subarray and SDP Subarray devices are developed. It can be executed within Leaf Node device. To deploy any Leaf Node in standalone mode, an environment variable STANDALONE_MODE should be exported with the value "TRUE". -->
 
### 4.3.3 Deleting the deployment and clean up
 
The command `make k8s-uninstall-chart` deletes the deployment from kubernetes cluster.
The command `make k8s-clean` performs cleanup like deleting the kubernetes namespace. This is optional.
 
# 5 Formatting & Linting
 
[Pylint](http://pylint.pycqa.org/en/stable/), code analysis tool used for the linting in the SKA-TMC-SDPLEAFNODES.
Configuration for linting is provided in *.pylintrc* file. For the code analysis of entire TMC-SDPLEAFNODES, a command in the
makefile is implemented.
 
The command used for formatting is: `make python-format`
 
The command used for linting is: `make python-lint`
 
After completion of linting job, *linting.xml* file is generated, which is used in generation of *lint errors*,
*lint failures* and *lint tests* gitlab badges.
 
# 6 Documentation
<!--
* [ReadTheDocs](https://ska-tmc.readthedocs.io/en/master/)
* [ADR-8: Subarray observation control state machine](https://confluence.skatelescope.org/x/bIdIBg)
* [SKA-TMC Learnings](https://docs.google.com/document/d/1DMhb_6NM0oaZMhSwEE79_B-MwycwzuH-RJsuOd5Zjlw/edit?usp=sharing)
* [TMC Stage I Prototype Demo](https://replay.skatelescope.org/replay/showRecordingExternal.html?key=3Na630an0coGgdK)
* [System Demo #3.2 (Recording)](https://www.dropbox.com/sh/ecqqky7ze5oaehm/AACBPF95iub58Y_OIIT-V4XZa?dl=0)
* [System Demo #3.2 (PPT)](https://drive.google.com/file/d/1pv8B3HDvNlUR3fd69_urpALWF7wwmlKG/view?usp=sharing)
* [System Demo #6.4 (PPT)](https://docs.google.com/presentation/d/1Xrm-Fa9ymxoAsLEU_icXXV99QYApDEXZIVfL2ksGREs/edit?usp=sharing)
* [System Demo #7.4 (PPT)](https://docs.google.com/presentation/d/1SDcMZY2jfCh61fgDOCMzsr69RY9triNChi3F8wU7rVw/edit?usp=sharing)
* [Sysyem Demo #7.5 (PPT)](https://docs.google.com/presentation/d/1-bOaxvquCmLbA8j6I0o_-rAjFMNLnjMnTNz_z1dOP2I/edit?usp=sharing)
* [PI Demo #7 (Recording)](https://confluence.skatelescope.org/download/attachments/116917697/NCRA_Abort_Restart_MVP_Demo.mp4?version=1&modificationDate=1598450515807&api=v2)
* [Exception Handling Guidelines](https://docs.google.com/document/d/1Er9WBsApHqJ3Yu66F7gFe8-dY8FYIl-L0PSB2cIWMZE/edit?usp=sharing) -->
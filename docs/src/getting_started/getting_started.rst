Getting started
===============

This page contains instructions for software developers who want to get
started with usage and development of the TMC SDP Leaf Nodes.

Background
----------
Detailed information on how the SKA Software development
community works is available at the `SKA software developer portal <https://developer.skao.int/en/latest/>`__.
There you will find guidelines, policies, standards and a range of other
documentation.

Set up your development environment
-----------------------------------
This project is structured to use k8s for development and testing so that the build environment, test environment and test results are all completely reproducible and are independent of host environment. It uses ``make`` to provide a consistent UI (run ``make help`` for targets documentation).

Install minikube
^^^^^^^^^^^^^^^^

You will need to install `minikube` or equivalent k8s installation in order to set up your test environment. You can follow the instruction `here <https://gitlab.com/ska-telescope/sdi/deploy-minikube/>`__:
.. code-block::

    git clone git@gitlab.com:ska-telescope/sdi/deploy-minikube.git
    cd deploy-minikube
    make all
    eval $(minikube docker-env)

*Please note that the command `eval $(minikube docker-env)` will point your local docker client at the docker-in-docker for minikube. Use this only for building the docker image and another shell for other work.*

How to Use
^^^^^^^^^^

Clone this repo:
.. code-block::
    git clone https://gitlab.com/ska-telescope/ska-tmc-sdpleafnodes.git
    cd ska-tmc-sdpleafnodes

Install dependencies
.. code-block::

    apt update
    apt install -y curl git build-essential libboost-python-dev libtango-dev 
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
    source $HOME/.poetry/env

Please note that:
 * the `libtango-dev` will install an old version of the TANGO-controls framework (9.2.5);
 * the best way to get the framework is compiling it (instructions can be found `here <https://gitlab.com/tango-controls/cppTango/-/blob/main/INSTALL.md>`_);
 * the above script has been tested with Ubuntu 20.04.

*During this step, `libtango-dev` instalation can ask for the Tango Server IP:PORT. Just accept the default proposed value.*

Install python requirements for linting and unit testing:
.. code-block::
    $ poetry install

Activate the poetry environment:
.. code-block::
    $ source $(poetry env info --path)/bin/activate

Follow the steps till installation of dependencies then run below command:
.. code-block::
    $ virtualenv cn_venv
    $ source cn_venv/bin/activate
    $ make requirements

Run python-test:
.. code-block::
    $ make python-test
    PyTango 9.3.3 (9, 3, 3)
    PyTango compiled with:
    Python : 3.8.5
    Numpy  : 0.0.0 ## output generated from a WSL windows machine
    Tango  : 9.2.5
    Boost  : 1.71.0

    PyTango runtime is:
    Python : 3.8.5
    Numpy  : None
    Tango  : 9.2.5

    PyTango running on:
    uname_result(system='Linux', node='LAPTOP-5LBGJH83', release='4.19.128-microsoft-standard', version='#1 SMP Tue Jun 23 12:58:10 UTC 2020', machine='x86_64', processor='x86_64')

    ============================= test session starts ==============================
    platform linux -- Python 3.8.5, pytest-5.4.3, py-1.10.0, pluggy-0.13.1 -- /home/
    [....]

    --------------------------------- JSON report ----------------------------------
    JSON report written to: build/reports/report.json (165946 bytes)

    ----------- coverage: platform linux, python 3.8.5-final-0 -----------
    Coverage HTML written to dir build/htmlcov
    Coverage XML written to file build/reports/code-coverage.xml

    ======================== 48 passed, 5 deselected in 42.42s ========================


Formatting the code:
.. code-block::
    $ make python-format
    [...]
    --------------------------------------------------------------------
    Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)


Python linting:
.. code-block::
    $ make python-lint
    [...]
    --------------------------------------------------------------------
    Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
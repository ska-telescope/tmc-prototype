# Project makefile for a ska-tmc project. You should normally only need to modify
# CAR_OCI_REGISTRY_USER and PROJECT below.

# CAR_OCI_REGISTRY_HOST, CAR_OCI_REGISTRY_USER and PROJECT are combined to define
# the Docker tag for this project. The definition below inherits the standard
# value for CAR_OCI_REGISTRY_HOST (artefact.skao.int) and overwrites
# CAR_OCI_REGISTRY_USER and PROJECT to give a final Docker tag of
# artefact.skao.int/ska-tmc

CAR_OCI_REGISTRY_HOST:=artefact.skao.int
PROJECT = ska-tmc
PYTHON_SWITCHES_FOR_FLAKE8=--ignore=W503,E203 --max-line-length=180
TANGO_HOST ?= tango-databaseds:10000 ## TANGO_HOST connection to the Tango DS
PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src \
							 TANGO_HOST=$(TANGO_HOST)
MARK ?= ## What -m opt to pass to pytest
# run one test with FILE=acceptance/test_subarray_node.py::test_check_internal_model_according_to_the_tango_ecosystem_deployed
FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest

CI_REGISTRY ?= gitlab.com
CUSTOM_VALUES = --set sdpsln_mid.sdpslnmid.image.tag=$(VERSION)
K8S_TEST_IMAGE_TO_TEST=$(CAR_OCI_REGISTRY_HOST)/$(PROJECT):$(VERSION)
ifneq ($(CI_JOB_ID),)
CUSTOM_VALUES = --set sdpsln_mid.sdpslnmid.image.image=$(PROJECT) \
	--set sdpsln_mid.sdpslnmid.image.registry=$(CI_REGISTRY)/ska-telescope/$(PROJECT) \
	--set sdpsln_mid.sdpslnmid.image.tag=$(VERSION)-dev.$(CI_COMMIT_SHORT_SHA)
K8S_TEST_IMAGE_TO_TEST=$(CI_REGISTRY)/ska-telescope/$(PROJECT)/$(PROJECT):$(VERSION)-dev.$(CI_COMMIT_SHORT_SHA)
endif


ifeq ($(MAKECMDGOALS),python-test)
ADD_ARGS +=  --forked
MARK = not post_deployment and not acceptance
endif
PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK)' $(ADD_ARGS) $(FILE)

-include .make/*.mk
-include PrivateRules.mak
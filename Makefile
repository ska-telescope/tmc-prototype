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
TELESCOPE ?= SKA-mid
MARK ?= ## What -m opt to pass to pytest
# run one test with FILE=acceptance/test_subarray_node.py::test_check_internal_model_according_to_the_tango_ecosystem_deployed
FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
KUBE_NAMESPACE ?= ska-tmc

# HELM_RELEASE is the release that all Kubernetes resources will be labelled
# with
HELM_RELEASE ?= test

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with
HELM_CHART=test-parent
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/
K8S_CHARTS ?= ska-tmc test-parent## list of charts
K8S_CHART ?= $(HELM_CHART)

TEST_VERSION ?= $(VERSION)
CI_REGISTRY ?= gitlab.com
CUSTOM_VALUES = --set sdpsln_mid.sdpslnmid.image.tag=$(VERSION)
K8S_TEST_IMAGE_TO_TEST=$(CAR_OCI_REGISTRY_HOST)/$(PROJECT):$(VERSION)
ifneq ($(CI_JOB_ID),)
CUSTOM_VALUES = --set sdpsln_mid.sdpslnmid.image.image=$(PROJECT) \
	--set sdpsln_mid.sdpslnmid.image.registry=$(CI_REGISTRY)/ska-telescope/$(PROJECT) \
	--set sdpsln_mid.sdpslnmid.image.tag=$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA)
K8S_TEST_IMAGE_TO_TEST=$(CI_REGISTRY)/ska-telescope/$(PROJECT)/$(PROJECT):$(TEST_VERSION)-dev.c$(CI_COMMIT_SHORT_SHA)
endif

CI_PROJECT_DIR ?= .

XAUTHORITY ?= $(HOME)/.Xauthority
THIS_HOST := $(shell ip a 2> /dev/null | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | head -n1)
DISPLAY ?= $(THIS_HOST):0
JIVE ?= false# Enable jive
TARANTA ?= false
MINIKUBE ?= true ## Minikube or not
FAKE_DEVICES ?= true ## Install fake devices or not
TANGO_HOST ?= tango-databaseds:10000## TANGO_HOST connection to the Tango DS

ITANGO_DOCKER_IMAGE = $(CAR_OCI_REGISTRY_HOST)/ska-tango-images-tango-itango:9.3.5

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
K8S_TEST_RUNNER = test-runner-$(HELM_RELEASE)

CI_PROJECT_PATH_SLUG ?= ska-tmc
CI_ENVIRONMENT_SLUG ?= ska-tmc
$(shell echo 'global:\n  annotations:\n    app.gitlab.com/app: $(CI_PROJECT_PATH_SLUG)\n    app.gitlab.com/env: $(CI_ENVIRONMENT_SLUG)' > gilab_values.yaml)

ifeq ($(MAKECMDGOALS),python-test)
ADD_ARGS +=  --forked
MARK = not post_deployment and not acceptance
endif
ifeq ($(MAKECMDGOALS),k8s-test)
ADD_ARGS +=  --true-context
MARK = $(shell echo $(TELESCOPE) | sed s/-/_/) and (post_deployment or acceptance)
endif

PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK)' $(ADD_ARGS) $(FILE)

K8S_CHART_PARAMS = --set global.minikube=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set ska-tango-base.display=$(DISPLAY) \
	--set ska-tango-base.xauthority=$(XAUTHORITY) \
	--set ska-tango-base.jive.enabled=$(JIVE) \
	--set sdpsln_mid.telescope=$(TELESCOPE) \
	--set sdpsln_mid.deviceServers.mocks.enabled=$(FAKE_DEVICES) \
	--set ska-taranta.enabled=$(TARANTA) \
	$(CUSTOM_VALUES) \
	--values gilab_values.yaml

K8S_TEST_TEST_COMMAND = cd .. && $(PYTHON_VARS_BEFORE_PYTEST) $(PYTHON_RUNNER) \
						pytest \
						$(PYTHON_VARS_AFTER_PYTEST) ./tests \
						 | tee pytest.stdout && mv build tests/
-include .make/*.mk
-include PrivateRules.mak

test-requirements:
	@poetry export --without-hashes --dev --format requirements.txt --output tests/requirements.txt

k8s-pre-test: python-pre-test test-requirements


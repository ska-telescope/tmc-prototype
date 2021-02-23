HELM_HOST ?= https://nexus.engageska-portugal.pt## helm host url https
MINIKUBE ?= true## Minikube or not
MARK ?= all
IMAGE_TO_TEST ?= $(DOCKER_REGISTRY_HOST)/$(DOCKER_REGISTRY_USER)/$(PROJECT):latest## docker image that will be run for testing purpose
TANGO_DATABASE_DS ?= tango-host-databaseds-from-makefile-$(RELEASE_NAME) ## Stable name for the Tango DB
TANGO_HOST ?= $(TANGO_DATABASE_DS):10000## TANGO_HOST is an input!
PROJECT = tmcprototype

CHARTS ?= tmc-mid tmc-low tmc-mid-umbrella tmc-low-umbrella ## list of charts to be published on gitlab -- umbrella charts for testing purpose

CI_PROJECT_PATH_SLUG ?= tmcprototype
CI_ENVIRONMENT_SLUG ?= tmcprototype	

.DEFAULT_GOAL := help

CI_REGISTRY ?= gitlab.com/ska-telescope/$(PROJECT)

k8s: ## Which kubernetes are we connected to
	@echo "Kubernetes cluster-info:"
	@kubectl cluster-info
	@echo ""
	@echo "kubectl version:"
	@kubectl version
	@echo ""
	@echo "Helm version:"
	@helm version --client

clean: ## clean out references to chart tgz's
	@rm -f ./charts/*/charts/*.tgz ./charts/*/Chart.lock ./charts/*/requirements.lock ./repository/*

watch:
	watch kubectl get all,pv,pvc,ingress -n $(KUBE_NAMESPACE)

namespace: ## create the kubernetes namespace
	@kubectl describe namespace $(KUBE_NAMESPACE) > /dev/null 2>&1 ; \
		K_DESC=$$? ; \
		if [ $$K_DESC -eq 0 ] ; \
		then kubectl describe namespace $(KUBE_NAMESPACE); \
		else kubectl create namespace $(KUBE_NAMESPACE); \
		fi

namespace_sdp: ## create the kubernetes namespace for SDP dynamic deployments
	@kubectl describe namespace $(SDP_KUBE_NAMESPACE) > /dev/null 2>&1 ; \
 	K_DESC=$$? ; \
	if [ $$K_DESC -eq 0 ] ; \
	then kubectl describe namespace $(SDP_KUBE_NAMESPACE) ; \
	else kubectl create namespace $(SDP_KUBE_NAMESPACE); \
	fi

delete_namespace: ## delete the kubernetes namespace
	@if [ "default" == "$(KUBE_NAMESPACE)" ] || [ "kube-system" == "$(KUBE_NAMESPACE)" ]; then \
	echo "You cannot delete Namespace: $(KUBE_NAMESPACE)"; \
	exit 1; \
	else \
	kubectl describe namespace $(KUBE_NAMESPACE) && kubectl delete namespace $(KUBE_NAMESPACE); \
	fi

delete_namespace-sdp: ## delete the kubernetes namespace
	@if [ "default" == "$(SDP_KUBE_NAMESPACE)" ] || [ "kube-system" == "$(SDP_KUBE_NAMESPACE)" ]; then \
	echo "You cannot delete Namespace: $(SDP_KUBE_NAMESPACE)"; \
	exit 1; \
	else \
	kubectl describe namespace $(SDP_KUBE_NAMESPACE) && kubectl delete namespace $(SDP_KUBE_NAMESPACE); \
	fi

# To package a chart directory into a chart archive
package: ## package charts
	@echo "Packaging helm charts. Any existing file won't be overwritten."; \
	mkdir -p ../tmp
	@for i in $(CHARTS); do \
	helm package charts/$${i} --destination ../tmp > /dev/null; \
	done; \
	mkdir -p ../repository && cp -n ../tmp/* ../repository; \
	cd ../repository && helm repo index .; \
	rm -rf ../tmp

dep-up: ## update dependencies for every charts in the env var CHARTS
	@cd charts; \
	for i in $(CHARTS); do \
	echo "+++ Updating $${i} chart +++"; \
	helm dependency update $${i}; \
	done;

# This job is used to create a deployment of tmc-mid charts
# Currently umbrealla chart for tmc-mid path is given
install-chart: dep-up namespace namespace_sdp ## install the helm chart with name HELM_RELEASE and path UMBRELLA_CHART_PATH on the namespace KUBE_NAMESPACE 
	# Understand this better
	@sed -e 's/CI_PROJECT_PATH_SLUG/$(CI_PROJECT_PATH_SLUG)/' $(UMBRELLA_CHART_PATH)values.yaml > generated_values.yaml; \
	sed -e 's/CI_ENVIRONMENT_SLUG/$(CI_ENVIRONMENT_SLUG)/' generated_values.yaml > values.yaml; \
	helm install $(HELM_RELEASE) \
	--set minikube=$(MINIKUBE) \
	--set global.minikube=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set tangoDatabaseDS=$(TANGO_DATABASE_DS) \
	--set sdp.helmdeploy.namespace=$(SDP_KUBE_NAMESPACE) \
	--set tmcprototype.image.registry=$(CI_REGISTRY)/ska-telescope \
	--set tmcprototype.image.tag=$(CI_COMMIT_SHORT_SHA) \
	 $(UMBRELLA_CHART_PATH) --namespace $(KUBE_NAMESPACE); \
	 rm generated_values.yaml; \
	 rm values.yaml

template-chart: clean dep-up## install the helm chart with name RELEASE_NAME and path UMBRELLA_CHART_PATH on the namespace KUBE_NAMESPACE
	@sed -e 's/CI_PROJECT_PATH_SLUG/$(CI_PROJECT_PATH_SLUG)/' $(UMBRELLA_CHART_PATH)values.yaml > generated_values.yaml; \
	sed -e 's/CI_ENVIRONMENT_SLUG/$(CI_ENVIRONMENT_SLUG)/' generated_values.yaml > values.yaml; \
	helm template $(RELEASE_NAME) \
	--set minikube=$(MINIKUBE) \
	--set global.minikube=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set tangoDatabaseDS=$(TANGO_DATABASE_DS) \
	--set sdp.helmdeploy.namespace=$(SDP_KUBE_NAMESPACE) \
	--set tmcprototype.image.registry=$(CI_REGISTRY)/ska-telescope \
	--set tmcprototype.image.tag=$(CI_COMMIT_SHORT_SHA) \
	--debug \
	 $(UMBRELLA_CHART_PATH) --namespace $(KUBE_NAMESPACE); \
	 rm generated_values.yaml; \
	 rm values.yaml

# This job is used to delete a deployment of tmc-mid charts
# Currently umbreall chart for tmc-mid path is given
uninstall-chart: ## uninstall the tmc-mid helm chart on the namespace tmcprototype
	helm template  $(HELM_RELEASE) $(UMBRELLA_CHART_PATH) --namespace $(KUBE_NAMESPACE)  | kubectl delete -f - ; \
	helm uninstall  $(HELM_RELEASE) --namespace $(KUBE_NAMESPACE) 

reinstall-chart: uninstall-chart install-chart ## reinstall the tmc-mid helm chart on the namespace tmcprototype

upgrade-chart: ## upgrade the tmc-mid helm chart on the namespace tmcprototype
	helm upgrade --set minikube=$(MINIKUBE) $(HELM_RELEASE) $(UMBRELLA_CHART_PATH) --namespace $(KUBE_NAMESPACE) 

wait:## wait for pods to be ready
	@echo "Waiting for pods to be ready"
	@date
	@kubectl -n $(KUBE_NAMESPACE) get pods
	@jobs=$$(kubectl get job --output=jsonpath={.items..metadata.name} -n $(KUBE_NAMESPACE)); kubectl wait job --for=condition=complete --timeout=240s $$jobs -n $(KUBE_NAMESPACE)
	@kubectl -n $(KUBE_NAMESPACE) wait --for=condition=ready -l app=tmc-prototype --timeout=240s pods
	@kubectl get pods -n $(KUBE_NAMESPACE)
	@date

# Error in --set
show: ## show the helm chart
	@helm template $(HELM_RELEASE) charts/$(HELM_CHART)/ \
		--namespace $(KUBE_NAMESPACE) \
		--set xauthority="$(XAUTHORITYx)" \
		--set display="$(DISPLAY)" 

# Linting chart tmc-mid
chart_lint: ## lint check the helm chart
	@helm lint $(UMBRELLA_CHART_PATH) \
		--namespace $(KUBE_NAMESPACE) 

describe: ## describe Pods executed from Helm chart
	@for i in `kubectl -n $(KUBE_NAMESPACE) get pods -l release=$(HELM_RELEASE) -o=name`; \
	do echo "---------------------------------------------------"; \
	echo "Describe for $${i}"; \
	echo kubectl -n $(KUBE_NAMESPACE) describe $${i}; \
	echo "---------------------------------------------------"; \
	kubectl -n $(KUBE_NAMESPACE) describe $${i}; \
	echo "---------------------------------------------------"; \
	echo ""; echo ""; echo ""; \
	done

logs: ## show Helm chart POD logs
	@for i in `kubectl -n $(KUBE_NAMESPACE) get pods -l release=$(HELM_RELEASE) -o=name`; \
	do \
	echo "---------------------------------------------------"; \
	echo "Logs for $${i}"; \
	echo kubectl -n $(KUBE_NAMESPACE) logs $${i}; \
	echo kubectl -n $(KUBE_NAMESPACE) get $${i} -o jsonpath="{.spec.initContainers[*].name}"; \
	echo "---------------------------------------------------"; \
	for j in `kubectl -n $(KUBE_NAMESPACE) get $${i} -o jsonpath="{.spec.initContainers[*].name}"`; do \
	RES=`kubectl -n $(KUBE_NAMESPACE) logs $${i} -c $${j} 2>/dev/null`; \
	echo "initContainer: $${j}"; echo "$${RES}"; \
	echo "---------------------------------------------------";\
	done; \
	echo "Main Pod logs for $${i}"; \
	echo "---------------------------------------------------"; \
	for j in `kubectl -n $(KUBE_NAMESPACE) get $${i} -o jsonpath="{.spec.containers[*].name}"`; do \
	RES=`kubectl -n $(KUBE_NAMESPACE) logs $${i} -c $${j} 2>/dev/null`; \
	echo "Container: $${j}"; echo "$${RES}"; \
	echo "---------------------------------------------------";\
	done; \
	echo "---------------------------------------------------"; \
	echo ""; echo ""; echo ""; \
	done
log: 	# get the logs of pods @param: $POD_NAME
	kubectl logs -n $(KUBE_NAMESPACE) $(POD_NAME)


# Utility target to install Helm dependencies
helm_dependencies:
	@which helm ; rc=$$?; \
	if [[ $$rc != 0 ]]; then \
	curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3; \
	chmod 700 get_helm.sh; \
	./get_helm.sh; \
	fi; \
	helm version --client

# Utility target to install K8s dependencies
kubectl_dependencies:
	@([ -n "$(KUBE_CONFIG_BASE64)" ] && [ -n "$(KUBECONFIG)" ]) || (echo "unset variables [KUBE_CONFIG_BASE64/KUBECONFIG] - abort!"; exit 1)
	@which kubectl ; rc=$$?; \
	if [[ $$rc != 0 ]]; then \
		curl -L -o /usr/bin/kubectl "https://storage.googleapis.com/kubernetes-release/release/$(KUBERNETES_VERSION)/bin/linux/amd64/kubectl"; \
		chmod +x /usr/bin/kubectl; \
		mkdir -p /etc/deploy; \
		echo $(KUBE_CONFIG_BASE64) | base64 -d > $(KUBECONFIG); \
	fi
	@echo -e "\nkubectl client version:"
	@kubectl version --client
	@echo -e "\nkubectl config view:"
	@kubectl config view
	@echo -e "\nkubectl config get-contexts:"
	@kubectl config get-contexts
	@echo -e "\nkubectl version:"
	@kubectl version

kubeconfig: ## export current KUBECONFIG as base64 ready for KUBE_CONFIG_BASE64
	@KUBE_CONFIG_BASE64=`kubectl config view --flatten | base64`; \
	echo "KUBE_CONFIG_BASE64: $$(echo $${KUBE_CONFIG_BASE64} | cut -c 1-40)..."; \
	echo "appended to: PrivateRules.mak"; \
	echo -e "\n\n# base64 encoded from: kubectl config view --flatten\nKUBE_CONFIG_BASE64 = $${KUBE_CONFIG_BASE64}" >> PrivateRules.mak

# enable_test_auth:
# 	@helm upgrade --install testing-auth post-deployment/resources/testing_auth \
# 		--namespace $(KUBE_NAMESPACE) \
# 		--set accountName=$(TESTING_ACCOUNT)

rlint:  ## run lint check on Helm Chart using gitlab-runner
	if [ -n "$(RDEBUG)" ]; then DEBUG_LEVEL=debug; else DEBUG_LEVEL=warn; fi && \
	gitlab-runner --log-level $${DEBUG_LEVEL} exec $(EXECUTOR) \
	--docker-privileged \
	--docker-disable-cache=false \
	--docker-host $(DOCKER_HOST) \
	--docker-volumes  $(DOCKER_VOLUMES) \
	--docker-pull-policy always \
	--timeout $(TIMEOUT) \
	--env "DOCKER_HOST=$(DOCKER_HOST)" \
  --env "DOCKER_REGISTRY_USER_LOGIN=$(DOCKER_REGISTRY_USER_LOGIN)" \
  --env "CI_REGISTRY_PASS_LOGIN=$(CI_REGISTRY_PASS_LOGIN)" \
  --env "CI_REGISTRY=$(CI_REGISTRY)" \
	lint-check-chart || true

# K8s testing with local gitlab-runner
# Run the powersupply tests in the TEST_RUNNER run to completion Pod:
#   set namespace
#   install dependencies for Helm and kubectl
#   deploy into namespace
#   run test in run to completion Pod
#   extract Pod logs
#   set test return code
#   delete
#   delete namespace
#   return result
rk8s_test:  ## run k8s_test on K8s using gitlab-runner
	if [ -n "$(RDEBUG)" ]; then DEBUG_LEVEL=debug; else DEBUG_LEVEL=warn; fi && \
	KUBE_NAMESPACE=`git rev-parse --abbrev-ref HEAD | tr -dc 'A-Za-z0-9\-' | tr '[:upper:]' '[:lower:]'` && \
	gitlab-runner --log-level $${DEBUG_LEVEL} exec $(EXECUTOR) \
	--docker-privileged \
	--docker-disable-cache=false \
	--docker-host $(DOCKER_HOST) \
	--docker-volumes  $(DOCKER_VOLUMES) \
	--docker-pull-policy always \
	--timeout $(TIMEOUT) \
	--env "DOCKER_HOST=$(DOCKER_HOST)" \
	--env "DOCKER_REGISTRY_USER_LOGIN=$(DOCKER_REGISTRY_USER_LOGIN)" \
	--env "CI_REGISTRY_PASS_LOGIN=$(CI_REGISTRY_PASS_LOGIN)" \
	--env "CI_REGISTRY=$(CI_REGISTRY)" \
	--env "KUBE_CONFIG_BASE64=$(KUBE_CONFIG_BASE64)" \
	--env "KUBECONFIG=$(KUBECONFIG)" \
	--env "KUBE_NAMESPACE=$${KUBE_NAMESPACE}" \
	test-chart || true


helm_tests:  ## run Helm chart tests 
	helm test $(HELM_RELEASE) --cleanup

help:  ## show this help.
	@echo "make targets:"
	@grep -hE '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""; echo "make vars (+defaults):"
	@grep -hE '^[0-9a-zA-Z_-]+ \?=.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = " \?\= "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\#\#/  \#/'
	
traefik: ## install the helm chart for traefik (in the kube-system namespace). @param: EXTERNAL_IP (i.e. private ip of the master node).
	@TMP=`mktemp -d`; \
	$(helm_add_stable_repo) && \
	helm fetch stable/traefik --untar --untardir $$TMP && \
	helm template $(helm_install_shim) $$TMP/traefik -n traefik0 --namespace kube-system \
		--set externalIP="$(EXTERNAL_IP)" \
		| kubectl apply -n kube-system -f - && \
		rm -rf $$TMP ; \


delete_traefik: ## delete the helm chart for traefik. @param: EXTERNAL_IP
	@TMP=`mktemp -d`; \
	$(helm_add_stable_repo) && \
	helm fetch stable/traefik --untar --untardir $$TMP && \
	helm template $(helm_install_shim) $$TMP/traefik -n traefik0 --namespace kube-system \
		--set externalIP="$(EXTERNAL_IP)" \
		| kubectl delete -n kube-system -f - && \
		rm -rf $$TMP

#this is so that you can load dashboards previously saved, TODO: make the name of the pod variable
dump_dashboards: # @param: name of the dashborad
	kubectl exec -i pod/mongodb-webjive-test-0 -n $(KUBE_NAMESPACE) -- mongodump --archive > $(DASHBOARD)

load_dashboards: # @param: name of the dashborad
	kubectl exec -i pod/mongodb-webjive-test-0 -n $(KUBE_NAMESPACE) -- mongorestore --archive < $(DASHBOARD)

# How to test unit-test cases
unit-test:
	cd tmcprototype; \
	chmod 755 run_tox.sh; \
	./run_tox.sh;
# How to run lint job
lint:
	cd tmcprototype; \
	chmod 755 run_lint.sh; \
	./run_lint.sh;





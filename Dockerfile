#ARG DOCKER_REGISTRY_USER
#ARG DOCKER_REGISTRY_HOST
#FROM ${DOCKER_REGISTRY_HOST}/${DOCKER_REGISTRY_USER}/ska-python-buildenv:latest AS buildenv
#FROM ${DOCKER_REGISTRY_HOST}/${DOCKER_REGISTRY_USER}/ska-python-runtime:latest AS runtime
FROM ska-registry.av.it.pt/ska-docker/ska-python-buildenv:latest AS buildenv
FROM ska-registry.av.it.pt/ska-docker/ska-python-runtime:latest AS runtime

#install lmc-base-classes
# RUN apt install git
# RUN git clone --single-branch --branch story_AT1-163 https://github.com/ska-telescope/lmc-base-classes.git
# RUN cd lmc-base-classes
# RUN python3 setup.py install

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#install lmc-base-classes
USER root
RUN buildDeps="ca-certificates git" \
   && DEBIAN_FRONTEND=noninteractive apt-get update \
   && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends $buildDeps \
   && su tango -c "/venv/bin/pip install git+https://github.com/ska-telescope/lmc-base-classes.git" \
   && apt-get purge -y --auto-remove $buildDeps \
   && rm -rf /var/lib/apt/lists/* /home/tango/.cache
#   && rm -rf /var/lib/apt/lists/* /home/tango/.cache \
#   && DEBIAN_FRONTEND=noninteractive apt-get update \
#   && DEBIAN_FRONTEND=noninteractive apt-get -y install rsyslog

USER tango

CMD ["/venv/bin/python", "tmc-prototype/tmcprototype/DishMaster/DishMaster/DishMaster.py"]

#FROM ${DOCKER_REGISTRY_HOST}/${DOCKER_REGISTRY_USER}/ska-python-buildenv:latest AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/tango-cpp:latest AS buildenv


#install alarm handler
USER root

COPY bin/alarmhandler-srv /app/
RUN chmod 777 /app/alarmhandler-srv
RUN ls -l /app

USER tango

CMD ["/bin/bash", "-c", "./app/alarmhandler-srv 01"]
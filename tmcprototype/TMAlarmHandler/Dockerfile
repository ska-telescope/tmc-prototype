FROM ${DOCKER_REGISTRY_HOST}/ska-docker/tango-cpp:latest AS buildenv

#install alarm handler
USER root
COPY bin/alarmhandler-srv /app/
RUN chmod 777 /app/alarmhandler-srv
RUN ls -l /app

USER tango

CMD ["/bin/bash", "-c", "./app/alarmhandler-srv 01"]
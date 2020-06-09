FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:0.2.2 AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:0.2.2 AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#install lmc-base-classes
USER root
RUN python3 -m pip install https://nexus.engageska-portugal.pt/repository/pypi/packages/ska-logging/0.2.1/ska_logging-0.2.1.tar.gz
#RUN python3 -m pip install https://nexus.engageska-portugal.pt/repository/pypi/packages/lmcbaseclasses/0.5.1+22db2b66/lmcbaseclasses-0.5.1+22db2b66.tar.gz
RUN python3 -m pip install https://nexus.engageska-portugal.pt/repository/pypi/packages/lmcbaseclasses/0.5.4+d12da018/lmcbaseclasses-0.5.4+d12da018.tar.gz

# install all local TMC packages
RUN python3 -m pip install \
    /app/tmcprototype/centralnode \
    /app/tmcprototype/cspmasterleafnode \
    /app/tmcprototype/cspsubarrayleafnode \
    /app/tmcprototype/dishleafnode \
    /app/tmcprototype/dishmaster \
    /app/tmcprototype/sdpmasterleafnode \
    /app/tmcprototype/sdpsubarrayleafnode \
    /app/tmcprototype/subarraynode

USER tango

CMD ["/venv/bin/CentralNodeDS"]

FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:9.3.2 AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:9.3.2 AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#install lmc-base-classes
USER root
RUN python3 -m pip install ska-logging==0.3.0
RUN python3 -m pip install lmcbaseclasses==0.7.2
# install cdm-shared-library
RUN python3 -m pip install cdm-shared-library==2.0.0
#install ska-telescope-model
RUN python3 -m pip install ska-telescope-model==0.3.0
# install transaction id
RUN python3 -m pip install install ska-log-transactions
# install ska tmc common package
RUN python3 -m pip install skatmccommon==0.1.3+1c307e75
# install all local TMC packages
RUN python3 -m pip install \
    /app/tmcprototype/centralnodelow \
    /app/tmcprototype/cspmasterleafnode \
    /app/tmcprototype/cspsubarrayleafnode \
    /app/tmcprototype/dishleafnode \
    /app/tmcprototype/dishmaster \
    /app/tmcprototype/sdpmasterleafnode \
    /app/tmcprototype/sdpsubarrayleafnode \
    /app/tmcprototype/mccsmasterleafnode \
    /app/tmcprototype/mccssubarrayleafnode \
    /app/tmcprototype/subarraynodelow 

USER tango

CMD ["/usr/local/bin/CentralNodeLowDS"]

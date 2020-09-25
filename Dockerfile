FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:9.3.2 AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:9.3.2 AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#install lmc-base-classes
USER root
RUN python3 -m pip install ska-logging==0.3.0
RUN python3 -m pip install lmcbaseclasses==0.6.5
# install cdm-shared-library
RUN python3 -m pip install cdm-shared-library==2.0.0
#install ska-telescope-model
RUN python3 -m pip install ska-telescope-model==0.1.4

# install all local TMC packages
RUN python3 -m pip install \
    /app/tmcprototype/centralnode \
    /app/tmcprototype/cspmasterleafnode \
    /app/tmcprototype/cspsubarrayleafnode \
    /app/tmcprototype/dishleafnode \
    /app/tmcprototype/dishmaster \
    /app/tmcprototype/sdpmasterleafnode \
    /app/tmcprototype/sdpsubarrayleafnode \
    /app/tmcprototype/subarraynode \
    /app/tmcprototype/mccsmasterleafnode 


USER tango

CMD ["/usr/local/bin/CentralNodeDS"]

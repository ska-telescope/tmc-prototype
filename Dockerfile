FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:9.3.2 AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:9.3.2 AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#install lmc-base-classes
USER root

RUN python3 -m pip install lmcbaseclasses==0.7.2 \
    ska-telescope-model==0.3.0 \
    katpoint==1.0a1

FROM artefact.skao.int/ska-tango-images-pytango-builder:9.3.10 
FROM artefact.skao.int/ska-tango-images-pytango-runtime:9.3.10

RUN python3 -m pip install ska-tmc-cdm==6.0.0 \
    ska-tmc-common==0.1.7+d39e6423 \
    ska-ser-logging==0.4.0 \
    ska-ser-log-transactions 

# install all local TMC packages
RUN python3 -m pip install \
    /app/ska-tmc/centralnodelow 
# /app/ska-tmc/cspmasterleafnode \
# /app/ska-tmc/cspsubarrayleafnode \
# /app/ska-tmc/dishleafnode \
# /app/ska-tmc/dishmaster \
# /app/ska-tmc/sdpmasterleafnode \
# /app/ska-tmc/sdpsubarrayleafnode \
# /app/ska-tmc/mccsmasterleafnode \
# /app/ska-tmc/mccssubarrayleafnode \
# /app/ska-tmc/subarraynodelow 

USER tango

CMD ["/usr/local/bin/CentralNodeLowDS"]

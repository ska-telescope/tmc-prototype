FROM artefact.skao.int/ska-tango-images-pytango-builder:9.3.10 AS buildenv
FROM artefact.skao.int/ska-tango-images-pytango-runtime:9.3.10 AS runtime
# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#install lmc-base-classes
USER root

# install all local TMC packages
RUN python3 -m pip install -r requirements.txt \
    /app/ska-tmc/ska-tmc-centralnode-low \
    /app/ska-tmc/cspmasterleafnode \
    /app/ska-tmc/cspsubarrayleafnode \
    /app/ska-tmc/dishleafnode \
    /app/ska-tmc/dishmaster \
    /app/ska-tmc/sdpmasterleafnode \
    /app/ska-tmc/sdpsubarrayleafnode \
    /app/ska-tmc/ska-tmc-mccsmasterleafnode-low \
    /app/ska-tmc/ska-tmc-mccssubarrayleafnode-low \
    /app/ska-tmc/ska-tmc-subarraynode-low 

USER tango

CMD ["/usr/local/bin/CentralNodeLowDS"]

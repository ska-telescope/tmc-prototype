FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:9.3.2 AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:9.3.2 AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#install lmc-base-classes
USER root

RUN python3 -m pip install ska-logging==0.3.0

# This is a temporary approach to install base classes from Gitlab.
# This will be reverted back in PI 12. 
RUN python3 -m pip install git+git://gitlab.com/ska-telescope/ska-tango-base@0.7.2

RUN python3 -m pip install cdm-shared-library==2.0.0 \
                           ska-telescope-model==0.3.0 \
                           ska-log-transactions \
                           skatmccommon==0.1.6+3aaa7bbe \
                           katpoint==1.0a1
# install all local TMC packages
RUN python3 -m pip install \
    /app/ska-tmc/centralnodelow \
    /app/ska-tmc/cspmasterleafnode \
    /app/ska-tmc/cspsubarrayleafnode \
    /app/ska-tmc/dishleafnode \
    /app/ska-tmc/dishmaster \
    /app/ska-tmc/sdpmasterleafnode \
    /app/ska-tmc/sdpsubarrayleafnode \
    /app/ska-tmc/mccsmasterleafnode \
    /app/ska-tmc/mccssubarrayleafnode \
    /app/ska-tmc/subarraynodelow 

USER tango

CMD ["/usr/local/bin/CentralNodeLowDS"]

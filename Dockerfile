FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:0.2.2 AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:0.2.2 AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#install lmc-base-classes
USER root
RUN python3 -m pip install https://nexus.engageska-portugal.pt/repository/pypi/packages/lmcbaseclasses/0.2.0+6bb55a6e/lmcbaseclasses-0.2.0+6bb55a6e.tar.gz

# install all local TMC packages
RUN python3 -m pip install \
    /app/tmcprototype/centralnode \
    /app/tmcprototype/cspmasterleafnode \
    /app/tmcprototype/CspSubarray \
    /app/tmcprototype/cspsubarrayleafnode \
    /app/tmcprototype/dishleafnode \
    /app/tmcprototype/dishmaster \
    /app/tmcprototype/SdpMaster \
    /app/tmcprototype/sdpmasterleafnode \
    /app/tmcprototype/SdpSubarray \
    /app/tmcprototype/sdpsubarrayleafnode \
    /app/tmcprototype/subarraynode

USER tango


CMD ["/venv/bin/python", "/app/tmcprototype/centralnode/src/centralnode/central_node.py"]

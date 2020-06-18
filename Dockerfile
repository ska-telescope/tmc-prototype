FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:9.3.2 AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:9.3.2 AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#install lmc-base-classes
USER root
RUN python3 -m pip install ska-logging==0.3.0
# install from state_machine branch, git hash 41626f0d03f3afa9c7112bbf5dfc960fa7e91a8a
RUN python3 -m pip install pip install https://gitlab.com/ska-telescope/lmc-base-classes/-/archive/41626f0d03f3afa9c7112bbf5dfc960fa7e91a8a/lmc-base-classes-41626f0d03f3afa9c7112bbf5dfc960fa7e91a8a.zip

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

CMD ["/usr/local/bin/CentralNodeDS"]

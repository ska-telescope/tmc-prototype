ARG CAR_OCI_REGISTRY_USERNAME
ARG CAR_OCI_REGISTRY_HOST
FROM artefact.skao.int/ska-tango-images-tango-cpp:9.3.5

USER root
RUN apt-get update && \
   apt-get install -y ca-certificates

RUN echo "deb http://deb.debian.org/debian buster-backports main contrib non-free" >> /etc/apt/sources.list && \
   more /etc/apt/sources.list && \
   apt-get update && \
   apt-get install -y \
       checkinstall \
       git \
       cmake \
       make \
       g++ \
       libomniorb4-dev \
       libzmq3-dev \
       libcos4-dev \
       default-libmysqlclient-dev \
       libboost-all-dev

RUN git clone http://github.com/ELETTRA-SincrotroneTrieste/makefiles.git
RUN git clone http://github.com/ELETTRA-SincrotroneTrieste/alarm-handler.git
COPY Make-9.3.3.in /makefiles
RUN cd alarm-handler && \
    TANGO_DIR=/usr/local/tango make

CMD ["/bin/bash", "-c", "/alarm-handler/bin/alarm-handler-srv 01"]

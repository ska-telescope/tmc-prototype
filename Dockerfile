ARG BUILD_IMAGE="artefact.skao.int/ska-tango-images-pytango-builder:9.5.0"
ARG BASE_IMAGE="artefact.skao.int/ska-tango-images-pytango-runtime:9.5.0"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

# Install Poetry
USER root
ENV SETUPTOOLS_USE_DISTUTILS=stdlib
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false
RUN pip install ipython
WORKDIR /app
COPY --chown=tango:tango . /app
# Install runtime dependencies and the app
RUN poetry install --only main
RUN rm /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python
RUN apt-get update && apt-get install git -y
USER tango

# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create
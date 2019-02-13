FROM ubuntu:16.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        libblitz0v5 \
        libsigc++-2.0-0v5 \
        libxml2 \
        libqtcore4 \
        zlib1g \
        python2.7 \
        python-sip \
        libpython2.7 \
        python-pip \
        python-six \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# We need to use the same version of numpy as casa-dev:ubuntu-16.04
# RUN pip install --disable-pip-version-check --no-cache-dir \
#     numpy==1.13.1

COPY install /usr/local
RUN ldconfig

# Make the BrainVISA Python packages visible to the system
RUN mkdir -p /usr/local/lib/python2.7/dist-packages \
    && cd /usr/local/lib/python2.7/dist-packages \
    && ln -s ../../../python/* .

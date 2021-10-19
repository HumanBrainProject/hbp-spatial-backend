FROM ubuntu:18.04

###############################
# 1. Install packages as root #
###############################

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        libsigc++-2.0-0v5 \
        libxml2 \
        libqtcore4 \
        zlib1g \
        python2.7 \
        python-sip \
        libpython2.7 \
        python-pip \
        python-six \
        wget \
        unzip \
        binutils make csh g++ sed gawk autoconf automake autotools-dev libtool \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Blitz++ is not provided anymore as an APT package in Debian/Ubuntu
# It now installs it from source
RUN cd /tmp \
    && wget https://github.com/blitzpp/blitz/archive/1.0.2.tar.gz \
    --no-verbose --show-progress \
    --progress=bar:force:noscrol \
    && tar -zxf 1.0.2.tar.gz \
    && mkdir blitz-1.0.2/build \
    && cd blitz-1.0.2 \
    && autoreconf -i \
    && ./configure \
    && make -j$(nproc) \
    && make install \
    && cd .. \
    && rm -rf 1.0.2.tar.gz blitz-1.0.2

##########################################
# 2. get brainvisa-aims installation     #
##########################################

# brainvisa-aims install directory has been generated using script.sh
COPY install /usr/local
RUN ldconfig

# Make the BrainVISA Python packages visible to the system
RUN mkdir -p /usr/local/lib/python2.7/dist-packages \
    && cd /usr/local/lib/python2.7/dist-packages \
    && ln -s ../../../python/* .

##########################################
# 3. get DISCO transformation files      #
##########################################

# File is accessible in neurospin network at:
# /neurospin/hbp/HBP_data_components/HBP_795/2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip

RUN mkdir -p /transformation-data
# COPY /neurospin/hbp/HBP_data_components/HBP_795/2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip \
#    -O /transformation-data/2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip
COPY 2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip \
     /transformation-data/2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip
RUN cd /transformation-data \
    && unzip 2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip \
    && rm -rf 2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip

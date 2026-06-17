FROM ubuntu:24.04

###############################
# 1. Install Pixi as root #
###############################

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        wget \
        python3 \
        python-is-python3 \
        ca-certificates \
        unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN (echo "export PIXI_HOME=/usr/local" && wget -qO- https://pixi.sh/install.sh) | sh

##########################################
# 2. get brainvisa-aims installation     #
##########################################

# brainvisa-aims install directory has been generated using script.sh
RUN cd /usr/local && pixi init -c https://brainvisa.info/neuro-forge -c conda-forge && pixi add soma && pixi run bv_update_bin_links && rm -rf /root/.cache
# temp: fix small bug
RUN touch /usr/local/activate.sh

##########################################
# 3. get DISCO transformation files      #
##########################################

# File is accessible in neurospin network at:
# /neurospin/hbp/HBP_data_components/HBP_795/2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip

# RUN mkdir -p /transformation-data
# COPY /neurospin/hbp/HBP_data_components/HBP_795/2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip \
#    -O /transformation-data/2021-07-29_DISCO_20181004_sigV30_DARTEL_20181004_reg_x4.zip
COPY DISCO_20181004_sigV30_DARTEL_20260422_reg_x5.zip \
     /transformation-data/DISCO_20181004_sigV30_DARTEL_20260422_reg_x5.zip
RUN cd /transformation-data \
    && unzip DISCO_20181004_sigV30_DARTEL_20260422_reg_x5.zip \
    && rm -rf DISCO_20181004_sigV30_DARTEL_20260422_reg_x5.zip

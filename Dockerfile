FROM jchavas/brainvisa-aims:latest

###############################
# 1. Install packages as root #
###############################

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        python3 \
	    python3-dev \
        python3-pip \
        python3-wheel \
        python3-venv \
        git \
        wget \
        lsof \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# # to deal with non-ASCII characters in source
ENV LANG=C.UTF-8

##################################
# 1. Install hbp-spatial-backend in virtualenv#
##################################

RUN git clone --branch dev \
    https://github.com/HumanBrainProject/hbp-spatial-backend.git \
    /opt/hbp-spatial-backend

RUN python3 -m venv /opt/venv
RUN . /opt/venv/bin/activate \
    && cd /opt/hbp-spatial-backend \
    && pip install -e .[dev]

RUN . /opt/venv/bin/activate \
    && pip install gunicorn \
    && pip install gevent==1.4

RUN apt-get update \
    && apt-get remove python3-dev \
      -y --no-install-recommends --no-install-suggests \
    && apt autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

######################
# 2. Configure paths #
######################
ENV INSTANCE_PATH /instance
ENV TRANSFORMATION_DATA_PATH /transformation-data

VOLUME ${INSTANCE_PATH}

###########################################################
# 3. Create an unprivileged user that will run the server #
###########################################################
#RUN useradd --create-home -G sudo -p "$(openssl passwd -1 user)" user
RUN mkdir -p ${TRANSFORMATION_DATA_PATH} && chown root:root ${TRANSFORMATION_DATA_PATH}
RUN mkdir -p ${INSTANCE_PATH} && chown root:root ${INSTANCE_PATH}
#USER user


###########################
# 4. Configure the server #
###########################
ENV FLASK_APP hbp_spatial_backend
EXPOSE 8080
CMD ln -sf \
    ${TRANSFORMATION_DATA_PATH}/DISCO_20181004_sigV30_DARTEL_20181004_reg_x4/* \
    ${INSTANCE_PATH} \
    && . /opt/venv/bin/activate \
    && gunicorn --access-logfile=- \
        --preload 'hbp_spatial_backend.wsgi:application' \
        --bind=:8080 --worker-class=gevent

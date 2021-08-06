FROM jchavas/brainvisa-aims:latest

###############################
# 1. Install packages as root #
###############################

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        python3 \
        python3-pip \
	wget \
	python3-dev \
	build-essential \
        git \
        sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip as recommended
RUN wget https://bootstrap.pypa.io/pip/3.5/get-pip.py -O ./get-pip.py \
    --no-verbose --show-progress \
    --progress=bar:force:noscrol
RUN python3 ./get-pip.py && rm ./get-pip.py

RUN python3 -m pip install p5py PEP517

# Setuptools is needed to import from source
# RUN python3 -m pip install --no-cache-dir setuptools wheel

RUN python3 -m pip install --no-cache-dir gunicorn[gevent]

# to deal with non-ASCII characters in source
ENV LANG=C.UTF-8

# Installs to run pytest
RUN python3 -m pip install --no-cache-dir pytest sip

COPY . /source
RUN python3 -m pip install --no-cache-dir /source


######################
# 2. Configure paths #
######################
ENV INSTANCE_PATH /instance
ENV TRANSFORMATION_DATA_PATH /transformation-data

VOLUME ${INSTANCE_PATH}

###########################################################
# 3. Create an unprivileged user that will run the server #
###########################################################
RUN useradd --create-home -G sudo -p "$(openssl passwd -1 user)" user
RUN mkdir -p ${INSTANCE_PATH}  && chown user:user ${INSTANCE_PATH}
RUN mkdir -p ${TRANSFORMATION_DATA_PATH} && chown user:user ${TRANSFORMATION_DATA_PATH}
USER user


###########################
# 4. Configure the server #
###########################
ENV FLASK_APP hbp_spatial_backend
EXPOSE 8080
CMD gunicorn --access-logfile=- --preload 'hbp_spatial_backend.wsgi:application' --bind=:8080 --worker-class=gevent

###########################
# 4. Launch tests         #
###########################

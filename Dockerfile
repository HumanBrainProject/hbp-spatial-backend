FROM ylep/brainvisa-aims:latest

###############################
# 1. Install packages as root #
###############################

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        python3 \
        python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Setuptools is needed to import from source
RUN python3 -m pip install --no-cache-dir setuptools

COPY . /source
RUN python3 -m pip install --no-cache-dir /source

RUN python3 -m pip install --no-cache-dir gunicorn


######################
# 2. Configure paths #
######################
ENV INSTANCE_PATH /instance
ENV TRANSFORMATION_DATA_PATH /transformation-data

VOLUME ${INSTANCE_PATH}


###########################################################
# 3. Create an unprivileged user that will run the server #
###########################################################
RUN groupadd -r user && useradd -r -g user user
RUN mkdir -p ${INSTANCE_PATH} && chown user:user ${INSTANCE_PATH}
RUN mkdir -p ${TRANSFORMATION_DATA_PATH} && chown user:user ${TRANSFORMATION_DATA_PATH}
USER user

###########################
# 4. Configure the server #
###########################
ENV FLASK_APP hbp_spatial_backend
EXPOSE 8080
CMD gunicorn --access-logfile=- 'hbp_spatial_backend:create_app()' --bind=:8080
An HTTP backend for transforming coordinates (and, in the future, data) between the HBP core template spaces

.. image:: https://api.travis-ci.com/HumanBrainProject/hbp-spatial-backend.svg?branch=master
   :target: https://travis-ci.com/HumanBrainProject/hbp-spatial-backend
   :alt: Travis Build Status

.. image:: https://codecov.io/gh/HumanBrainProject/hbp-spatial-backend/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/HumanBrainProject/hbp-spatial-backend
   :alt: Coverage Status

.. image:: https://img.shields.io/swagger/valid/3.0?label=OpenAPI&specUrl=https%3A%2F%2Fhbp-spatial-backend.apps.hbp.eu%2Fopenapi.json
   :target: https://hbp-spatial-backend.apps.hbp.eu/redoc
   :alt: Swagger Validator


Public deployments
==================

A production deployment (following the ``master`` branch) is deployed on https://hbp-spatial-backend.apps.hbp.eu. |uptime-prod|

The ``dev`` branch is deployed on https://hbp-spatial-backend.apps-dev.hbp.eu. |uptime-dev|

The public deployments are managed by OpenShift clusters, the relevant configuration is described in `<openshift-deployment/>`_.


Documentation
=============

The API is documented using the OpenAPI standard (a.k.a. Swagger): see `the ReDoc-generated documentation <https://hbp-spatial-backend.apps.hbp.eu/redoc>`_.

`A Swagger UI page <https://hbp-spatial-backend.apps.hbp.eu/swagger-ui>`_ is also available for trying out the API.

Tutorial on docker example
==========================

.. code-block:: shell

   # Commands to use docker as non-sudo user
   sudo groupadd docker
   sudo usermod -aG docker $USER
   sudo reboot # (or you can just login/logout)
   # To check that it works:
   docker ps

   # Command to run from the directory hbp-spatial-backend
   # This creates the container hbp-spatial-backend
   docker build -t hbp-spatial-backend .

   # Runs the container and mounts your data directory
   # containing your nii files into the container directory /Data
   # Change DATA_DIR to match your local data directory
   DATA_DIR=/volatile/Data
   docker run -t -i --rm -p 8080:8080 -v $DATA_DIR:/Data hbp-spatial-backend

   # From inside the container
   curl -X GET "http://0.0.0.0:8080/v1/graph.yaml" -H  "accept: */*"

   # From outside the container (here docker IP is 172.17.0.1)
   # Use the IP of your docker container (to know it, run ifconfig, and look for docker0 IP)
   DOCKER_IP=172.17.0.1
   curl -X GET "http://$DOCKER_IP:8080/v1/graph.yaml" -H  "accept: */*"

Development
===========

The backend needs to call ``AimsApplyTransform``, which is part of `the AIMS image processing toolkit <https://github.com/brainvisa/aims-free>`_. You can use `<docker-aims/script.sh>`_ to build a Docker image containing these tools (a pre-built image is available on Docker Hub: `ylep/brainvisa-aims <https://hub.docker.com/r/ylep/brainvisa-aims>`_).

Useful commands for development:

.. code-block:: shell

  git clone https://github.com/HumanBrainProject/hbp-spatial-backend.git

  # Install in a virtual environment
  cd hbp-spatial-backend
  python3 -m venv venv/
  . venv/bin/activate
  pip install -e .[dev]

  export FLASK_APP=hbp_spatial_backend
  flask run  # run a local development server

  # Tests
  pytest  # run tests
  pytest --cov=hbp_spatial_backend --cov-report=html  # detailed test coverage report
  tox  # run tests under all supported Python versions

  # Please install pre-commit if you intend to contribute
  pip install pre-commit
  pre-commit install  # install the pre-commit hook

  # Before a commit, you can launch the pre-commit:
  pre-commit run --all-files

Contributing
============

This repository uses `pre-commit`_ to ensure that all committed code follows minimal quality standards. Please install it and configure it to run as a pre-commit hook in your local repository (see above).


.. |uptime-prod| image:: https://img.shields.io/uptimerobot/ratio/7/m783468831-04ba4c898048519b8c7b5a2f?style=flat-square
   :alt: Weekly uptime ratio of the production instance
.. |uptime-dev| image:: https://img.shields.io/uptimerobot/ratio/7/m783468851-2872ab9d303cfa0973445798?style=flat-square
   :alt: Weekly uptime ratio of the development instance
.. _pre-commit: https://pre-commit.com/

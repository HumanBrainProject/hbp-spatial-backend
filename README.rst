An HTTP backend for transforming coordinates (and, in the future, data) between the HBP core template spaces

A production deployment (following the ``master`` branch) is deployed on https://hbp-spatial-backend.apps.hbp.eu.

The ``dev`` branch is deployed on https://hbp-spatial-backend.apps-dev.hbp.eu.


Running a local development server::

  pip install -e .
  export FLASK_APP=hbp_spatial_backend
  flask run


Contributing
============

This repository uses `pre-commit`_ to ensure that all committed code follows minimal quality standards. Please install it and configure it to run as a pre-commit hook in your local repository::

  pip install pre-commit
  pre-commit install


.. _pre-commit: https://pre-commit.com/

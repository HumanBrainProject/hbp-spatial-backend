#! /bin/sh -e

PYTHONPATH=$(dirname -- "$0")${PYTHONPATH+:}$PYTHONPATH
FLASK_APP=hbp_spatial_backend
FLASK_ENV=development
export PYTHONPATH FLASK_APP FLASK_ENV

HBP_SPATIAL_BACKEND_SETTINGS=$PWD/settings.cfg
export HBP_SPATIAL_BACKEND_SETTINGS

flask run "$@"

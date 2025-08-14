#! /bin/bash

helm install \
    --set envObj.HBP_SPATIAL_BACKEND_SETTINGS="/instance/config_v2.py" \
    --set replicaCount=1 \
    dev \
    ./.helm/hbp_spatial_backend
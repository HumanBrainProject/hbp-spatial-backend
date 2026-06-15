# Must be run from the directory that contains this script (docker-aims)

# This script

###################################
# 1. Creates docker image         #
###################################

DOCKER_IMAGE=brainvisa-aims:master_$(date -Id)
docker build -t $DOCKER_IMAGE --network=host .

docker save -o $DOCKER_IMAGE.tar $DOCKER_IMAGE

# Must be run from the directory that contains this script (docker-aims)

# This script

####################################
# 1. Downloads brainvisa dev image #
####################################

: ${CASA_BASE_REPOSITORY:=/volatile/bv/casa_distro_repo}  # set default value
export CASA_BASE_REPOSITORY
export IMAGE_VERSION=5.0-4
export IMAGE_NAME=aims-opensource-master-$IMAGE_VERSION

casa_distro \
    setup_dev \
    branch=master \
    url=https://brainvisa.info/download \
    image_version=$IMAGE_VERSION \
    output=$CASA_BASE_REPOSITORY/$IMAGE_NAME

# mv $CASA_BASE_REPOSITORY/opensource-master-$IMAGE_VERSION \
# $CASA_BASE_REPOSITORY/$IMAGE_NAME
export PATH="$CASA_BASE_REPOSITORY/$IMAGE_NAME/bin:$PATH"

###################################
# 2. Configures bv_maker          #
###################################

# Only aims dependencies will be installed
cat <<'EOF' > "$CASA_BASE_REPOSITORY"/$IMAGE_NAME/conf/bv_maker.cfg
[ source $CASA_SRC ]
  brainvisa brainvisa-cmake $CASA_BRANCH
  brainvisa soma-base $CASA_BRANCH
  brainvisa soma-io $CASA_BRANCH
  brainvisa aims-free $CASA_BRANCH

[ build $CASA_BUILD ]
  default_steps = configure build
  make_options = -j$NCPU
  build_type = Release
  packaging_thirdparty = OFF
  clean_config = ON
  clean_build = ON
  test_ref_data_dir = $CASA_TESTS/ref
  test_run_data_dir = $CASA_TESTS/test
  brainvisa brainvisa-cmake $CASA_BRANCH $CASA_SRC
  brainvisa soma-base $CASA_BRANCH $CASA_SRC
  brainvisa soma-io $CASA_BRANCH $CASA_SRC
  brainvisa aims-free $CASA_BRANCH $CASA_SRC
EOF

###################################
# 3. Installs aims in image       #
###################################

bv_maker

bv /bin/sh -c 'cd /casa/host/build && make install-runtime BRAINVISA_INSTALL_PREFIX=/casa/host/install'

rm -rf install && cp -a "$CASA_BASE_REPOSITORY"/"$IMAGE_NAME"/install .

###################################
# 4. Creates docker image         #
###################################

DOCKER_IMAGE=brainvisa-aims:master_$(date -Id)
docker build -t $DOCKER_IMAGE .

docker save -o $DOCKER_IMAGE.tar $DOCKER_IMAGE

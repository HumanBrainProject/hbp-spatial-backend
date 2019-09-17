# Run from the directory that contains this script (docker-aims)

: ${CASA_DEFAULT_REPOSITORY:=/volatile/bv/casa_distro_repo}  # set default value
export CASA_DEFAULT_REPOSITORY

casa_distro \
    create \
    distro_name=aims \
    distro_source=opensource \
    branch=bug_fix \
    system=ubuntu-16.04

cat <<'EOF' > "$CASA_DEFAULT_REPOSITORY"/aims/bug_fix_ubuntu-16.04/conf/bv_maker.cfg
[ source $CASA_SRC ]
  brainvisa brainvisa-cmake $CASA_BRANCH
  brainvisa soma-base $CASA_BRANCH
  brainvisa soma-io $CASA_BRANCH
  brainvisa aims-free $CASA_BRANCH

[ build $CASA_BUILD ]
  default_steps = configure build
  make_options = -j16
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

casa_distro \
    bv_maker \
    distro=aims \
    branch=bug_fix \
    system=ubuntu-16.04

casa_distro \
    run \
    distro=aims \
    branch=bug_fix \
    system=ubuntu-16.04 \
    /bin/sh -c 'cd /casa/build && make install-runtime BRAINVISA_INSTALL_PREFIX=/casa/install'

cp -a "$CASA_DEFAULT_REPOSITORY"/aims/bug_fix_ubuntu-16.04/install .

DOCKER_IMAGE=brainvisa-aims:bug_fix_$(date -Id)
docker build -t $DOCKER_IMAGE .

docker save -o $DOCKER_IMAGE.tar $DOCKER_IMAGE

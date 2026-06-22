FROM ghcr.io/prefix-dev/pixi:0.40.0

WORKDIR /usr/local

RUN pixi init -c https://brainvisa.info/neuro-forge -c conda-forge
RUN pixi add soma=6.0.17 && pixi run bv_update_bin_links

ENTRYPOINT /bin/bash

FROM ghcr.io/prefix-dev/pixi@sha256:a8b819b1ca32a3390655eea0a12d53999ca1e3e6ac5a20d39f2294cbc19b4d76

WORKDIR /usr/local

RUN pixi init -c https://brainvisa.info/neuro-forge -c conda-forge
RUN pixi add soma=6.0.19 && pixi run bv_update_bin_links

# start a shell in the pixi environment
ENTRYPOINT /bin/bash /usr/local/bin/bv /bin/bash

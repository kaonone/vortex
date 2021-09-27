FROM python:3.9
# TODO: use multi stage builds to reduce image size: 
# https://www.blogfoobar.com/post/2018/02/10/python-and-docker-multistage-build

# setup entrypoint that we will copy later
WORKDIR /root
# ENTRYPOINT ["/arbitrum-scripts/docker/entrypoint.sh"]

COPY docker/apt-install.sh /usr/sbin/

RUN apt-install.sh \
    libffi-dev \
    npm \
    python3-venv \
    python3-pip \ 
;

# setup python virtualenv
ENV PATH /venv/bin:/arbitrum-scripts/scripts:$PATH
RUN --mount=type=cache,target=/root/.cache { set -eux; \
    \
    python3.9 -m venv /venv; \
    pip install -U pip setuptools wheel; \
}

# ganache and hardhat for development
# TODO: install using package.json? install just one of these?
RUN --mount=type=cache,target=/root/.cache { set -eux; \
    \
    npm install -g hardhat ganache-cli yarn; \
}

# install the python dependencies
COPY requirements.txt /arbitrum-scripts/
RUN --mount=type=cache,target=/root/.cache { set -eux; \
    pip install \
        --use-feature=in-tree-build \
        --disable-pip-version-check \
        -r /arbitrum-scripts/requirements.txt \
    ; \
}

# install our code
COPY . /arbitrum-scripts/

# RUN /arbitrum-scripts/arb-deploy.sh 
# RUN rm -rf hardhat
RUN --mount=type=cache,target=/root/.cache { set -eux; \
    pip install \
        --use-feature=in-tree-build \
        --disable-pip-version-check \
        -r /arbitrum-scripts/requirements.txt -e /arbitrum-scripts/ \
    ; \
    build_dir=/arbitrum-scripts/build; \
    persist_dir=/root/build/arbitrum-scripts; \
    rm -rf "$build_dir"; \
    mkdir -p "$persist_dir"; \
    ln -sfv "$persist_dir" "$build_dir"; \
}

WORKDIR /arbitrum-scripts/

RUN  brownie networks import network-config.yaml True && brownie compile
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    file \
    git \
    make \
    procps \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash devuser \
    && echo "devuser ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/devuser \
    && chmod 0440 /etc/sudoers.d/devuser

USER devuser
WORKDIR /home/devuser

RUN NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

ENV PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:${PATH}"

COPY --chown=devuser:devuser . /home/devuser/dev-env
WORKDIR /home/devuser/dev-env

CMD make check && make bootstrap && WSL_DISTRO_NAME=Ubuntu CI=true make converge ANSIBLE_EXTRA="-e devenv_set_login_shell=false -e devenv_install_gui_casks=false" && WSL_DISTRO_NAME=Ubuntu CI=true fish -lc 'nvm use $devenv_node_default_version; make converge ANSIBLE_EXTRA="-e devenv_set_login_shell=false -e devenv_install_gui_casks=false"'

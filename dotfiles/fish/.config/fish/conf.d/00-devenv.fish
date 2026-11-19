# ============================================================================
# 00-devenv.fish -- version pins, OS detection and cross-machine defaults.
# fish sources conf.d/*.fish *before* config.fish, so the values defined here
# are available to config.fish (verified against fish 4.x, see README).
# ============================================================================

# --- version pins (source of truth; kept here so they are git-tracked) ------
set -g devenv_node_default_version 26.13.1

# --- OS detection (single source of truth for the rest of the config) -------
switch (uname)
    case Darwin
        set -gx devenv_os Darwin
    case Linux
        set -gx devenv_os Linux
    case '*'
        set -gx devenv_os other
        echo "dev-env: unsupported OS \""(uname)"\" -- package installation disabled" >&2
end
set -gx devenv_arch (uname -m)

# --- nvm.fish: XDG-based node state + pinned default ------------------------
set -q XDG_DATA_HOME || set -gx XDG_DATA_HOME "$HOME/.local/share"
set -g nvm_data $XDG_DATA_HOME/nvm/versions/node
set -gx nvm_mirror https://nodejs.org/dist
set -g  nvm_default_version $devenv_node_default_version

# Ensure unified version directory exists and maintain symlink parity with legacy paths
if test -d "$XDG_DATA_HOME/nvm"
    test -d "$XDG_DATA_HOME/nvm/versions/node" || mkdir -p "$XDG_DATA_HOME/nvm/versions/node"
    # Legacy ~/.local/share/nvm/v* -> unified ~/.local/share/nvm/versions/node/v*
    for legacy_ver in (command find "$XDG_DATA_HOME/nvm" -maxdepth 1 -name "v*" 2>/dev/null)
        if test -d "$legacy_ver"
            set -l vname (basename "$legacy_ver")
            if not test -e "$XDG_DATA_HOME/nvm/versions/node/$vname"
                test -L "$XDG_DATA_HOME/nvm/versions/node/$vname"; and command rm -f "$XDG_DATA_HOME/nvm/versions/node/$vname"
                ln -sfn "$legacy_ver" "$XDG_DATA_HOME/nvm/versions/node/$vname"
            end
        end
    end
    # Unified ~/.local/share/nvm/versions/node/v* -> legacy ~/.local/share/nvm/v* fallback
    for node_ver in (command find "$XDG_DATA_HOME/nvm/versions/node" -maxdepth 1 -name "v*" 2>/dev/null)
        if test -d "$node_ver"
            set -l vname (basename "$node_ver")
            if not test -e "$XDG_DATA_HOME/nvm/$vname"
                test -L "$XDG_DATA_HOME/nvm/$vname"; and command rm -f "$XDG_DATA_HOME/nvm/$vname"
                ln -sfn "$node_ver" "$XDG_DATA_HOME/nvm/$vname"
            end
        end
    end
end

fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"

if test -f "$HOME/.config/node/node-extra-ca.pem"
    set -gx NODE_EXTRA_CA_CERTS "$HOME/.config/node/node-extra-ca.pem"
end

# --- micromamba discovery and conda alias / hook integration ---
if not command -q conda
    if command -q micromamba
        alias conda=micromamba
    else if test -x /home/linuxbrew/.linuxbrew/bin/micromamba
        alias conda=/home/linuxbrew/.linuxbrew/bin/micromamba
    else if test -x "$HOME/.linuxbrew/bin/micromamba"
        alias conda="$HOME/.linuxbrew/bin/micromamba"
    end
end

if command -q micromamba
    if set -q MAMBA_ROOT_PREFIX; and test -d "$MAMBA_ROOT_PREFIX"
        micromamba shell hook --shell fish 2>/dev/null | source
    else if test -d "$HOME/.local/share/mamba"
        micromamba shell hook --shell fish 2>/dev/null | source
    else if test -d "$HOME/micromamba"
        micromamba shell hook --shell fish 2>/dev/null | source
    end
end

# --- Go toolchain PATH export ---
if test -d "$HOME/go/bin"
    fish_add_path -gPm "$HOME/go/bin"
end


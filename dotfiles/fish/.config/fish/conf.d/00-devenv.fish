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

# --- Multi-OS Homebrew / Linuxbrew Environment ------------------------------
switch "$devenv_os"
    case Darwin
        if test -x /opt/homebrew/bin/brew
            if not contains /opt/homebrew/bin $PATH
                /opt/homebrew/bin/brew shellenv | source
            end
        else if test -x /usr/local/bin/brew
            if not contains /usr/local/bin $PATH
                /usr/local/bin/brew shellenv | source
            end
        end
    case Linux
        if test -x /home/linuxbrew/.linuxbrew/bin/brew
            if not contains /home/linuxbrew/.linuxbrew/bin $PATH
                /home/linuxbrew/.linuxbrew/bin/brew shellenv | source
            end
        else if test -x "$HOME/.linuxbrew/bin/brew"
            if not contains "$HOME/.linuxbrew/bin" $PATH
                "$HOME/.linuxbrew/bin/brew" shellenv | source
            end
        else if test -d /home/linuxbrew/.linuxbrew/bin
            if not contains /home/linuxbrew/.linuxbrew/bin $PATH
                fish_add_path -gpP /home/linuxbrew/.linuxbrew/bin /home/linuxbrew/.linuxbrew/sbin
            end
        end
end

# --- nvm.fish: XDG-based node state + pinned default ------------------------
set -q XDG_DATA_HOME || set -gx XDG_DATA_HOME "$HOME/.local/share"
set -g nvm_data $XDG_DATA_HOME/nvm/versions/node
set -gx nvm_mirror https://nodejs.org/dist
set -g  nvm_default_version $devenv_node_default_version

# Ensure unified version directory exists and migrate legacy flat directories one-way
if test -d "$XDG_DATA_HOME/nvm"
    test -d "$nvm_data" || command mkdir -p "$nvm_data"
    if test -L "$nvm_data/versions"
        command rm -f "$nvm_data/versions"
    end
    for legacy_ver in (command find "$XDG_DATA_HOME/nvm" -maxdepth 1 -name "v[0-9]*" 2>/dev/null)
        set -l vname (basename "$legacy_ver")
        if test -L "$legacy_ver"
            command rm -f "$legacy_ver"
        else if test -d "$legacy_ver"
            if test -L "$nvm_data/$vname"
                command rm -f "$nvm_data/$vname"
                command mv "$legacy_ver" "$nvm_data/$vname"
            else if not test -e "$nvm_data/$vname"
                command mv "$legacy_ver" "$nvm_data/$vname"
            end
        end
    end
    if test -L "$XDG_DATA_HOME/nvm/current"; and not test -e "$XDG_DATA_HOME/nvm/current"
        if test -d "$nvm_data/v$devenv_node_default_version"
            ln -sfn "$nvm_data/v$devenv_node_default_version" "$XDG_DATA_HOME/nvm/current"
        end
    end
end

fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"

if test -f "$HOME/.config/node/node-extra-ca.pem"
    set -gx NODE_EXTRA_CA_CERTS "$HOME/.config/node/node-extra-ca.pem"
end

# --- Conda (Miniforge / Micromamba) Shell Hook Probe and Activation ---------
set -l conda_hook_activated 0
set -l conda_candidates
if set -q MAMBA_ROOT_PREFIX; and test -n "$MAMBA_ROOT_PREFIX"
    set -a conda_candidates "$MAMBA_ROOT_PREFIX"
end
set -a conda_candidates "$HOME/.local/share/mamba" "$HOME/micromamba" \
    "$HOME/miniforge3" "$HOME/miniforge" "$HOME/mambaforge"
switch "$devenv_os"
    case Darwin
        set -a conda_candidates /opt/homebrew/Caskroom/miniforge/base /usr/local/Caskroom/miniforge/base
end
set -a conda_candidates /opt/miniforge3 /opt/conda "$HOME/anaconda3" "$HOME/miniconda3"

for conda_root in $conda_candidates
    if test -n "$conda_root"; and test -x "$conda_root/bin/conda"
        "$conda_root/bin/conda" shell.fish hook 2>/dev/null | source
        set conda_hook_activated 1
        break
    end
end

# --- micromamba discovery and conda alias / hook integration ---
if test $conda_hook_activated -eq 0
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
    else if test -x /home/linuxbrew/.linuxbrew/bin/micromamba
        if set -q MAMBA_ROOT_PREFIX; and test -d "$MAMBA_ROOT_PREFIX"
            /home/linuxbrew/.linuxbrew/bin/micromamba shell hook --shell fish 2>/dev/null | source
        else if test -d "$HOME/.local/share/mamba"
            /home/linuxbrew/.linuxbrew/bin/micromamba shell hook --shell fish 2>/dev/null | source
        else if test -d "$HOME/micromamba"
            /home/linuxbrew/.linuxbrew/bin/micromamba shell hook --shell fish 2>/dev/null | source
        end
    else if test -x "$HOME/.linuxbrew/bin/micromamba"
        if set -q MAMBA_ROOT_PREFIX; and test -d "$MAMBA_ROOT_PREFIX"
            "$HOME/.linuxbrew/bin/micromamba" shell hook --shell fish 2>/dev/null | source
        else if test -d "$HOME/.local/share/mamba"
            "$HOME/.linuxbrew/bin/micromamba" shell hook --shell fish 2>/dev/null | source
        else if test -d "$HOME/micromamba"
            "$HOME/.linuxbrew/bin/micromamba" shell hook --shell fish 2>/dev/null | source
        end
    end
end

# --- Re-assert NVM and user local binary precedence after Homebrew/Conda ----
fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"
if test -d "$HOME/.local/bin"
    fish_add_path -gpPm "$HOME/.local/bin"
end

# --- Go toolchain PATH export ---
if test -d "$HOME/go/bin"
    fish_add_path -gPm "$HOME/go/bin"
end


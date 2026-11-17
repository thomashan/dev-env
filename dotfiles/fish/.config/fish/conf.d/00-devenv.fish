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
                ln -s "$legacy_ver" "$XDG_DATA_HOME/nvm/versions/node/$vname"
            end
        end
    end
    # Unified ~/.local/share/nvm/versions/node/v* -> legacy ~/.local/share/nvm/v* fallback
    for node_ver in (command find "$XDG_DATA_HOME/nvm/versions/node" -maxdepth 1 -name "v*" 2>/dev/null)
        if test -d "$node_ver"
            set -l vname (basename "$node_ver")
            if not test -e "$XDG_DATA_HOME/nvm/$vname"
                ln -s "$node_ver" "$XDG_DATA_HOME/nvm/$vname"
            end
        end
    end
end

fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"


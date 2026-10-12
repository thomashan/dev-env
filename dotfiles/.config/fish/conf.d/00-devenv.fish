# ============================================================================
# 00-devenv.fish -- version pins, OS detection and cross-machine defaults.
# fish sources conf.d/*.fish *before* config.fish, so the values defined here
# are available to config.fish (verified against fish 4.x, see README).
# ============================================================================

# --- version pins (source of truth; kept here so they are git-tracked) ------
set -g devenv_node_default_version 22.23.2

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
set -gx nvm_data "$HOME/.local/share/nvm"
set -gx nvm_mirror https://nodejs.org/dist
set -g  nvm_default_version $devenv_node_default_version

# --- editor / pager defaults -----------------------------------------------
set -g  fish_greeting
set -gx EDITOR nvim
set -gx VISUAL nvim
set -gx PAGER less
command -v delta >/dev/null 1>&2; and set -gx GIT_PAGER delta

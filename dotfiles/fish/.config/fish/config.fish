# ============================================================================
# dev-env fish configuration  --  this file is the source of truth.
# Managed by: dotfiles/fish/.config/fish/config.fish (symlinked via GNU Stow).
#
# Multi-OS rules: never hardcode /Users/... or /opt/homebrew/... absolute
# paths. Resolve everything from $HOME, $XDG_* or the OS detection in
# conf.d/00-devenv.fish so the same file works on macOS and Linux.
# ============================================================================

set -q XDG_DATA_HOME || set -gx XDG_DATA_HOME "$HOME/.local/share"
set -q XDG_CONFIG_HOME || set -gx XDG_CONFIG_HOME "$HOME/.config"

# Keep fisher payloads (plugin code, its completions) out of the repo working
# tree: everything it installs lands in ~/.config/fish/local, which is
# gitignored. Only config.fish, fish_plugins and conf.d/ are version controlled.
set -gx fisher_path "$__fish_config_dir/local"
fish_add_path -gaP "$fisher_path/bin"
set -gx fish_function_path $fish_function_path[1] "$fisher_path/functions" $fish_function_path[2..]
set -gx fish_complete_path $fish_complete_path[1] "$fisher_path/completions" $fish_complete_path[2..]

if status is-interactive
    # Commands to run in interactive sessions can go here
end

# --- PATH ------------------------------------------------------------------
fish_add_path -gaP "$HOME/.local/bin"                  # uv / pipx / user tools

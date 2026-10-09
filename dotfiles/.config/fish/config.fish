# ============================================================================
# dev-env fish configuration  --  this file is the source of truth.
# Managed by: dotfiles/.config/fish/config.fish (symlinked by ansible).
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
# nvm must come first: this host had three node binaries (brew node 26,
# ~/.local/bin/node -> ~/.hermes/node 22, nvm 24) and nvm is the one we manage.
# -g global, -p prepend, -P edit $PATH directly (not $fish_user_paths),
# -m move an existing entry to the front instead of leaving it stale.
fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"   # nvm-managed node (see ansible node role)

fish_add_path -gaP "$HOME/.local/bin"                  # uv / pipx / user tools

switch "$devenv_os"
    case Darwin
        # Apple Silicon /opt/homebrew, Intel /usr/local -- resolved by brew itself.
        if test -x /opt/homebrew/bin/brew
            brew shellenv | source
        else if test -x /usr/local/bin/brew
            /usr/local/bin/brew shellenv | source
        end
    case Linux
        for dir in /home/linuxbrew/.linuxbrew/bin /home/linuxbrew/.linuxbrew/sbin
            test -d "$dir"; and fish_add_path -gaP "$dir"
        end
end

# --- conda (miniforge): location differs per OS, so probe instead of hardcode
set -l conda_candidates \
    "$HOME/miniforge3" \
    "$HOME/miniforge" \
    "$HOME/mambaforge" \
    "$HOME/anaconda3" \
    /opt/homebrew/Caskroom/miniforge/base \
    /usr/local/Caskroom/miniforge/base \
    /opt/miniforge3 \
    /opt/conda
set -g devenv_conda_base ""
for root in $conda_candidates
    if test -f "$root/bin/conda"
        set devenv_conda_base "$root"
        break
    end
end

if test -n "$devenv_conda_base"
    eval "$($devenv_conda_base/bin/conda shell.fish hook)"
end

# --- tool paths that are user-installed and therefore OS-independent --------
for dir in "$HOME/.docker/bin" "$HOME/.lmstudio/bin" "$HOME/.antigravity-ide/antigravity-ide/bin"
    test -d "$dir"; and fish_add_path -gaP "$dir"
end

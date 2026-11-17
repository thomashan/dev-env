#!/usr/bin/env bash
# ============================================================================
# Reusable dev-env Shell Snippets
# Location: dotfiles/examples/devenv-shell-snippets.sh
#
# These modular snippets can be selectively copied into your interactive
# shell configuration (~/.bashrc, ~/.zshrc) or local overrides
# (~/.bashrc.local, ~/.zshrc.local) to opt in to specific toolchain integrations.
# ============================================================================

# ----------------------------------------------------------------------------
# Block A: NVM Managed Node PATH Prepend
# ----------------------------------------------------------------------------
# Prepends the nvm-managed node current symlink to PATH so the managed node
# runtime takes precedence over system or package manager binaries.
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
if [ -d "$XDG_DATA_HOME/nvm/current/bin" ]; then
    export PATH="$XDG_DATA_HOME/nvm/current/bin:$PATH"
fi

# ----------------------------------------------------------------------------
# Block B: Multi-OS Homebrew / Linuxbrew Environment
# ----------------------------------------------------------------------------
# Evaluates Homebrew / Linuxbrew shellenv depending on the operating system.
case "$(uname -s)" in
    Darwin)
        if [ -x /opt/homebrew/bin/brew ]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [ -x /usr/local/bin/brew ]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        ;;
    Linux)
        if [ -x /home/linuxbrew/.linuxbrew/bin/brew ]; then
            eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
        elif [ -d /home/linuxbrew/.linuxbrew/bin ]; then
            export PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH"
        fi
        ;;
esac

# ----------------------------------------------------------------------------
# Block C: Conda (Miniforge) Shell Hook Probe and Activation
# ----------------------------------------------------------------------------
# Probes common installation paths for Conda / Miniforge and initializes
# the shell hook for Bash or Zsh.
for conda_root in "$HOME/miniforge3" "$HOME/miniforge" "$HOME/mambaforge" "$HOME/anaconda3" \
    /opt/homebrew/Caskroom/miniforge/base /usr/local/Caskroom/miniforge/base /opt/miniforge3 /opt/conda; do
    if [ -x "$conda_root/bin/conda" ]; then
        if [ -n "$BASH_VERSION" ]; then
            eval "$("$conda_root/bin/conda" shell.bash hook 2>/dev/null)"
        elif [ -n "$ZSH_VERSION" ]; then
            eval "$("$conda_root/bin/conda" shell.zsh hook 2>/dev/null)"
        fi
        break
    fi
done

# ----------------------------------------------------------------------------
# Block D: Local Override Hook Loading
# ----------------------------------------------------------------------------
# Sources unversioned machine-local overrides for bash or zsh if present.
if [ -n "$BASH_VERSION" ]; then
    [ -f "$HOME/.bashrc.local" ] && . "$HOME/.bashrc.local"
elif [ -n "$ZSH_VERSION" ]; then
    [ -f "$HOME/.zshrc.local" ] && . "$HOME/.zshrc.local"
fi

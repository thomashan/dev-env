# ============================================================================
# dev-env bash configuration
# Managed by: dotfiles/bash/.bashrc (symlinked via GNU Stow)
# ============================================================================

# User-specific environment and paths
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

if [ -d "$HOME/.local/bin" ]; then
    case ":$PATH:" in
        *":$HOME/.local/bin:"*) ;;
        *) export PATH="$HOME/.local/bin:$PATH" ;;
    esac
fi

# Multi-OS Homebrew / Linuxbrew Environment
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
        elif [ -x "$HOME/.linuxbrew/bin/brew" ]; then
            eval "$("$HOME/.linuxbrew/bin/brew" shellenv)"
        elif [ -d /home/linuxbrew/.linuxbrew/bin ]; then
            export PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH"
        fi
        ;;
esac

# NVM and Node configuration
if [ -d "$HOME/.nvm" ] && [ ! -d "$XDG_DATA_HOME/nvm" ]; then
    export NVM_DIR="$HOME/.nvm"
else
    export NVM_DIR="$XDG_DATA_HOME/nvm"
fi

if [ -d "$NVM_DIR/current/bin" ]; then
    case ":$PATH:" in
        *":$NVM_DIR/current/bin:"*) ;;
        *) export PATH="$NVM_DIR/current/bin:$PATH" ;;
    esac
fi

# If not running interactively, don't do anything beyond environment and paths
case $- in
    *i*) ;;
      *) return;;
esac

# Source nvm.sh hook for interactive sessions if available
if [ -s "$NVM_DIR/nvm.sh" ]; then
    . "$NVM_DIR/nvm.sh"
elif [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then
    . "/opt/homebrew/opt/nvm/nvm.sh"
elif [ -s "/usr/local/opt/nvm/nvm.sh" ]; then
    . "/usr/local/opt/nvm/nvm.sh"
fi

# Conda (Miniforge) Shell Hook Probe and Activation
for conda_root in "$HOME/miniforge3" "$HOME/miniforge" "$HOME/mambaforge" \
    /opt/homebrew/Caskroom/miniforge/base /usr/local/Caskroom/miniforge/base /opt/miniforge3 /opt/conda \
    "$HOME/anaconda3" "$HOME/miniconda3"; do
    if [ -x "$conda_root/bin/conda" ]; then
        eval "$("$conda_root/bin/conda" shell.bash hook 2>/dev/null)"
        break
    fi
done

# --- Local override hook ---
[ -f "$HOME/.bashrc.local" ] && . "$HOME/.bashrc.local"

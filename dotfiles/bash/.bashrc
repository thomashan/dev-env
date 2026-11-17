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
            case ":$PATH:" in
                *":/opt/homebrew/bin:"*) ;;
                *) eval "$(/opt/homebrew/bin/brew shellenv)" ;;
            esac
        elif [ -x /usr/local/bin/brew ]; then
            case ":$PATH:" in
                *":/usr/local/bin:"*) ;;
                *) eval "$(/usr/local/bin/brew shellenv)" ;;
            esac
        fi
        ;;
    Linux)
        if [ -x /home/linuxbrew/.linuxbrew/bin/brew ]; then
            case ":$PATH:" in
                *":/home/linuxbrew/.linuxbrew/bin:"*) ;;
                *) eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" ;;
            esac
        elif [ -x "$HOME/.linuxbrew/bin/brew" ]; then
            case ":$PATH:" in
                *":$HOME/.linuxbrew/bin:"*) ;;
                *) eval "$("$HOME/.linuxbrew/bin/brew" shellenv)" ;;
            esac
        elif [ -d /home/linuxbrew/.linuxbrew/bin ]; then
            case ":$PATH:" in
                *":/home/linuxbrew/.linuxbrew/bin:"*) ;;
                *) export PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH" ;;
            esac
        fi
        ;;
esac

# NVM and Node configuration (canonical XDG convention)
export NVM_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/nvm"

# Re-assert NVM current bin and ~/.local/bin precedence ahead of Homebrew
if [ -d "$NVM_DIR/current/bin" ]; then
    case ":$PATH:" in
        ":$NVM_DIR/current/bin:"*) ;;
        *) export PATH="$NVM_DIR/current/bin:$PATH" ;;
    esac
fi

if [ -d "$HOME/.local/bin" ]; then
    case ":$PATH:" in
        ":$HOME/.local/bin:"*) ;;
        *) export PATH="$HOME/.local/bin:$PATH" ;;
    esac
fi

# If not running interactively, don't do anything beyond environment and paths
case $- in
    *i*) ;;
      *) return;;
esac

# Source nvm.sh hook and completion for interactive sessions if available
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

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

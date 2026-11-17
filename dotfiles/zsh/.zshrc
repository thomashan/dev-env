# ============================================================================
# dev-env zsh configuration
# Managed by: dotfiles/zsh/.zshrc (symlinked via GNU Stow)
# ============================================================================

export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

# --- PATH: prepend nvm first, then ~/.local/bin ---
if [ -d "$XDG_DATA_HOME/nvm/current/bin" ]; then
    export PATH="$XDG_DATA_HOME/nvm/current/bin:$HOME/.local/bin:$PATH"
else
    export PATH="$HOME/.local/bin:$PATH"
fi

# --- Multi-OS Homebrew / Linuxbrew ---
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

# --- Conda (miniforge): probe candidates for shell hook ---
for conda_root in "$HOME/miniforge3" "$HOME/miniforge" "$HOME/mambaforge" "$HOME/anaconda3" \
    /opt/homebrew/Caskroom/miniforge/base /usr/local/Caskroom/miniforge/base /opt/miniforge3 /opt/conda; do
    if [ -x "$conda_root/bin/conda" ]; then
        eval "$("$conda_root/bin/conda" shell.zsh hook 2>/dev/null)"
        break
    fi
done

# --- Local override hook ---
[ -f "$HOME/.zshrc.local" ] && . "$HOME/.zshrc.local"

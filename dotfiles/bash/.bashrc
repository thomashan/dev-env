# ============================================================================
# dev-env bash configuration
# Managed by: dotfiles/bash/.bashrc (symlinked via GNU Stow)
# ============================================================================

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# User-specific environment and paths
if [ -d "$HOME/.local/bin" ]; then
    case ":$PATH:" in
        *":$HOME/.local/bin:"*) ;;
        *) export PATH="$HOME/.local/bin:$PATH" ;;
    esac
fi

# --- Local override hook ---
[ -f "$HOME/.bashrc.local" ] && . "$HOME/.bashrc.local"

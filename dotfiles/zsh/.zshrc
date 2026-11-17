# ============================================================================
# dev-env zsh configuration
# Managed by: dotfiles/zsh/.zshrc (symlinked via GNU Stow)
# ============================================================================

# User-specific environment and paths
if [ -d "$HOME/.local/bin" ]; then
    case ":$PATH:" in
        *":$HOME/.local/bin:"*) ;;
        *) export PATH="$HOME/.local/bin:$PATH" ;;
    esac
fi

# --- Local override hook ---
[ -f "$HOME/.zshrc.local" ] && . "$HOME/.zshrc.local"

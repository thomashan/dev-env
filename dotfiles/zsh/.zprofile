# ============================================================================
# dev-env zsh profile
# Managed by: dotfiles/zsh/.zprofile (symlinked via GNU Stow)
# ============================================================================

if [[ ! -o interactive ]] && [ -f "$HOME/.zshrc" ]; then
    . "$HOME/.zshrc"
fi
[ -f "$HOME/.zprofile.local" ] && . "$HOME/.zprofile.local"

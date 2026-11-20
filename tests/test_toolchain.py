"""Toolchain, shell parity, and Makefile syntax invariants."""

from __future__ import annotations

import re

import pytest

from .conftest import REPO_ROOT, read

pytestmark = pytest.mark.manifest


def test_makefile_configure_python_fallback() -> None:
    """Makefile configure target probes Conda python3 then falls back to host python3."""
    makefile = read(REPO_ROOT / "Makefile")
    configure_target = makefile.split("\nconfigure:")[1].split("\ninstall:")[0]
    assert '[ -x "$(CONDA_DIR)/bin/python3" ]' in configure_target
    assert "command -v python3" in configure_target
    assert 'python3 "$(SELF_DIR)/scripts/devenv_wizard.py"' in configure_target
    assert "Error: Python 3 not found in $(CONDA_DIR)/bin/python3 or PATH." in configure_target


def test_makefile_galaxy_collection_install_isolated() -> None:
    """Ansible Galaxy collection install explicitly isolates to COLLECTIONS path."""
    makefile = read(REPO_ROOT / "Makefile")
    bootstrap_target = makefile.split("\nbootstrap:")[1].split("\nconfigure:")[0]
    assert '-p "$(COLLECTIONS)"' in bootstrap_target
    assert 'ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)"' in bootstrap_target


def test_ansible_cfg_collections_path_fallback() -> None:
    """ansible.cfg specifies primary and fallback collection directories."""
    ansible_cfg = read(REPO_ROOT / "ansible.cfg")
    assert re.search(
        r"collections_path\s*=\s*~/\.local/share/dev-env/collections:~/\.ansible/collections",
        ansible_cfg,
    ), "ansible.cfg missing collections_path fallback"


def test_multishell_micromamba_parity() -> None:
    """Bash, Zsh, and Fish dotfiles discover micromamba and provide conda alias or hook."""
    bashrc = read(REPO_ROOT / "dotfiles" / "bash" / ".bashrc")
    zshrc = read(REPO_ROOT / "dotfiles" / "zsh" / ".zshrc")
    fish_devenv = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")

    for shell_name, content in [("bash", bashrc), ("zsh", zshrc)]:
        assert "MAMBA_ROOT_PREFIX" in content, f"missing MAMBA_ROOT_PREFIX in {shell_name}"
        assert ".local/share/mamba" in content, f"missing .local/share/mamba probe in {shell_name}"
        assert "micromamba" in content, f"missing micromamba in {shell_name}"
        assert "alias conda=micromamba" in content, f"missing conda alias to micromamba in {shell_name}"
        assert f"micromamba shell hook --shell {shell_name}" in content, (
            f"missing micromamba shell hook in {shell_name}"
        )

    assert "command -q micromamba" in fish_devenv
    assert "alias conda=micromamba" in fish_devenv
    assert "micromamba shell hook --shell fish" in fish_devenv


def test_makefile_check_syntax_target() -> None:
    """Makefile defines check-syntax in .PHONY and executes --syntax-check."""
    makefile = read(REPO_ROOT / "Makefile")
    assert "check-syntax" in makefile.split(".PHONY:")[1].split("\n\n")[0]
    assert "check-syntax:" in makefile
    syntax_recipe = makefile.split("\ncheck-syntax:")[1].split("\n\n")[0]
    assert "--syntax-check" in syntax_recipe
    assert "$(ANSIBLE_ENV)" in syntax_recipe


def test_makefile_bootstrap_ca_injection() -> None:
    """Makefile bootstrap recipe checks and injects custom CA certificates."""
    makefile = read(REPO_ROOT / "Makefile")
    bootstrap_target = makefile.split("\nbootstrap:")[1].split("\nconfigure:")[0]
    assert "/usr/local/share/ca-certificates" in bootstrap_target
    assert "$(CONDA_DIR)/ssl/cacert.pem" in bootstrap_target
    assert "*.crt" in bootstrap_target
    assert "*.pem" in bootstrap_target
    assert "ANSIBLE MANAGED BLOCK: Custom CA" in bootstrap_target
    assert "grep -F -q" in bootstrap_target


def test_go_toolchain_declarations_and_skip(os_vars, group_vars) -> None:
    """Go toolchain package must be declared in core and skipped in apt on Linux."""
    assert "go" in group_vars.get("devenv_packages_core", []), "go missing from devenv_packages_core"
    assert "go" in os_vars["Linux"].get("devenv_pkg_skip", []), "go missing from Linux devenv_pkg_skip"


def test_fish_go_path_addition() -> None:
    """00-devenv.fish must export $HOME/go/bin via fish_add_path."""
    fish_conf = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    assert "$HOME/go/bin" in fish_conf, "missing $HOME/go/bin in 00-devenv.fish"
    assert "fish_add_path" in fish_conf, "missing fish_add_path in 00-devenv.fish"


def test_nvim_kickstart_markdownlint_auto_install_and_lint_guard() -> None:
    """Verify kickstart auto-installs markdownlint via mason-tool-installer and guards try_lint."""
    init_lua = read(REPO_ROOT / "dotfiles" / "nvim-kickstart" / ".config" / "nvim" / "init.lua")
    lint_lua = read(
        REPO_ROOT / "dotfiles" / "nvim-kickstart" / ".config" / "nvim" / "lua" / "kickstart" / "plugins" / "lint.lua"
    )

    match = re.search(r"vim\.list_extend\(ensure_installed,\s*\{([^}]*)\}\)", init_lua)
    assert match, "vim.list_extend(ensure_installed, { ... }) not found in kickstart init.lua"
    assert "'markdownlint'" in match.group(1), "markdownlint not in ensure_installed extension list"

    assert "lint.try_lint(nil, { ignore_errors = true })" in lint_lua


def test_node_ansible_role_ca_folding() -> None:
    """Node Ansible role folds custom CA certificates into node-extra-ca.pem."""
    node_tasks = read(REPO_ROOT / "ansible" / "roles" / "node" / "tasks" / "main.yml")
    assert "/usr/local/share/ca-certificates" in node_tasks
    assert "node-extra-ca.pem" in node_tasks
    assert "ansible.builtin.blockinfile" in node_tasks
    assert "recurse: true" in node_tasks or "recurse: yes" in node_tasks or "recurse: True" in node_tasks
    assert "# {mark} ANSIBLE MANAGED BLOCK: Custom CA" in node_tasks


def test_multishell_node_extra_ca_certs_parity() -> None:
    """Fish, Bash, Zsh, and snippet templates conditionally export NODE_EXTRA_CA_CERTS."""
    bashrc = read(REPO_ROOT / "dotfiles" / "bash" / ".bashrc")
    zshrc = read(REPO_ROOT / "dotfiles" / "zsh" / ".zshrc")
    fish_conf = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    snippets = read(REPO_ROOT / "dotfiles" / "examples" / "devenv-shell-snippets.sh")

    for file_content in (bashrc, zshrc, fish_conf, snippets):
        assert "NODE_EXTRA_CA_CERTS" in file_content
        assert ".config/node/node-extra-ca.pem" in file_content

    assert 'export NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"' in bashrc
    assert 'export NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"' in zshrc
    assert 'export NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"' in snippets
    assert 'set -gx NODE_EXTRA_CA_CERTS "$HOME/.config/node/node-extra-ca.pem"' in fish_conf


def test_tmux_pane_current_path_keybindings() -> None:
    """tmux configuration binds splits and new windows to current pane working directory."""
    tmux_conf = read(REPO_ROOT / "dotfiles" / "tmux" / ".tmux.conf")
    assert 'bind-key \'"\' split-window -v -c "#{pane_current_path}"' in tmux_conf
    assert 'bind-key % split-window -h -c "#{pane_current_path}"' in tmux_conf
    assert 'bind-key c new-window -c "#{pane_current_path}"' in tmux_conf


def test_gui_casks_and_linux_gui_apps_declarations(os_vars, group_vars) -> None:
    """GUI casks and Linux GUI application variable declarations adhere to OS isolation."""
    assert "docker-desktop" in os_vars["Darwin"]["devenv_casks"]
    assert "ghostty" in os_vars["Darwin"]["devenv_casks"]
    assert "warp" in os_vars["Darwin"]["devenv_casks"]
    assert os_vars["Linux"]["devenv_casks"] == []
    assert os_vars["Linux"]["devenv_linux_gui_apps"] == ["ghostty", "warp"]
    assert group_vars["devenv_linux_gui_apps"] == []


def test_ghostty_stow_config_and_links(group_vars) -> None:
    """Ghostty Stow config exists, unbinds Option+Arrow, and is registered in Stow packages and links."""
    ghostty_config_path = REPO_ROOT / "dotfiles" / "ghostty" / ".config" / "ghostty" / "config.ghostty"
    assert ghostty_config_path.exists(), "Ghostty config.ghostty missing"
    ghostty_config = read(ghostty_config_path)
    assert "keybind = alt+arrow_left=unbind" in ghostty_config
    assert "keybind = alt+arrow_right=unbind" in ghostty_config

    assert "ghostty" in group_vars.get("devenv_stow_packages", [])
    link_entries = group_vars.get("devenv_links", [])
    assert any(
        entry.get("src") == "dotfiles/ghostty/.config/ghostty/config.ghostty"
        and entry.get("dest") == "{{ devenv_home }}/.config/ghostty/config.ghostty"
        for entry in link_entries
    ), "Ghostty link missing from devenv_links"


def test_zsh_word_jump_keybindings() -> None:
    """Zsh configuration binds CSI word navigation key sequences inside interactive guard."""
    zshrc = read(REPO_ROOT / "dotfiles" / "zsh" / ".zshrc")
    assert "[[ -o interactive ]]" in zshrc
    assert 'bindkey "^[[1;3D" backward-word' in zshrc
    assert 'bindkey "^[[1;3C" forward-word' in zshrc
    assert 'bindkey "^[[1;5D" backward-word' in zshrc
    assert 'bindkey "^[[1;5C" forward-word' in zshrc


def test_linux_packages_gui_terminal_tasks() -> None:
    """Packages role defines check-mode safe, idempotent Linux tasks for Warp and Ghostty."""
    import yaml

    packages_tasks = yaml.safe_load(read(REPO_ROOT / "ansible" / "roles" / "packages" / "tasks" / "main.yml"))

    warp_probe = next((t for t in packages_tasks if t.get("name") == "Probe Warp terminal binary"), None)
    assert warp_probe is not None
    assert warp_probe.get("check_mode") is False
    assert warp_probe.get("failed_when") is False

    warp_keyring = next((t for t in packages_tasks if t.get("name") == "Ensure APT keyrings directory exists"), None)
    assert warp_keyring is not None
    assert warp_keyring.get("ansible.builtin.file", {}).get("path") == "/etc/apt/keyrings"

    warp_gpg = next((t for t in packages_tasks if t.get("name") == "Fetch and dearmor Warp GPG signing key"), None)
    assert warp_gpg is not None
    assert warp_gpg.get("ansible.builtin.command", {}).get("creates") == "/etc/apt/keyrings/warpdotdev.gpg"

    warp_repo = next((t for t in packages_tasks if t.get("name") == "Configure Warp APT repository"), None)
    assert warp_repo is not None
    assert warp_repo.get("ansible.builtin.copy", {}).get("dest") == "/etc/apt/sources.list.d/warpdotdev.list"
    content = warp_repo.get("ansible.builtin.copy", {}).get("content", "")
    assert "https://releases.warp.dev/linux/deb stable main" in content
    assert "x86_64" in content and "amd64" in content
    assert "arm64" in content

    ghostty_probe = next((t for t in packages_tasks if t.get("name") == "Probe Ghostty binary"), None)
    assert ghostty_probe is not None
    assert ghostty_probe.get("check_mode") is False
    assert ghostty_probe.get("failed_when") is False

    ghostty_apt_cache = next(
        (t for t in packages_tasks if t.get("name") == "Probe native Ghostty apt package availability"), None
    )
    assert ghostty_apt_cache is not None
    assert ghostty_apt_cache.get("check_mode") is False

    ghostty_snap = next((t for t in packages_tasks if t.get("name") == "Install Ghostty via snap"), None)
    assert ghostty_snap is not None
    assert "snap install ghostty --classic" in ghostty_snap.get("ansible.builtin.command", "")

    ghostty_ppa = next((t for t in packages_tasks if t.get("name") == "Add Ghostty PPA on Ubuntu"), None)
    assert ghostty_ppa is not None
    assert ghostty_ppa.get("ansible.builtin.apt_repository", {}).get("repo") == "ppa:mkasberg/ghostty-ubuntu"

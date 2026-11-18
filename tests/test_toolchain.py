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

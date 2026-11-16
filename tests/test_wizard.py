"""Unit tests for the host pre-Ansible interactive wizard (scripts/devenv_wizard.py).

Covers platform detection, variant discovery & resolution, dotfile conflict
detection, conflict resolution actions (diff, backup, local override, adopt),
YAML fallback serialization, and non-interactive execution.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.devenv_wizard import (
    adopt_file,
    backup_file,
    detect_platform,
    dump_yaml_fallback,
    extract_local_override,
    format_diff,
    get_available_variants,
    load_yaml_fallback,
    main,
    resolve_stow_packages,
    run_wizard,
    scan_dotfile_conflicts,
)

pytestmark = pytest.mark.manifest


def test_detect_platform_darwin(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "arm64")
    info = detect_platform()
    assert info["system"] == "Darwin"
    assert info["machine"] == "arm64"
    assert info["backend"] == "brew"
    assert info["distro"] == "macOS"


def test_detect_platform_linux(monkeypatch, tmp_path):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")

    os_release = tmp_path / "os-release"
    os_release.write_text('NAME="Ubuntu"\nPRETTY_NAME="Ubuntu 24.04 LTS"\n', encoding="utf-8")

    with patch("scripts.devenv_wizard.Path", side_effect=lambda p: os_release if p == "/etc/os-release" else Path(p)):
        info = detect_platform()
        assert info["system"] == "Linux"
        assert info["machine"] == "x86_64"
        assert info["backend"] == "apt"
        assert "Ubuntu" in info["distro"]


def test_get_available_variants(tmp_path):
    dotfiles = tmp_path / "dotfiles"
    dotfiles.mkdir()
    (dotfiles / "nvim-kickstart").mkdir()
    (dotfiles / "nvim-minimal").mkdir()
    (dotfiles / "nvim-lazyvim").mkdir()
    (dotfiles / "fish").mkdir()

    variants = get_available_variants(tmp_path)
    assert "nvim" in variants
    assert sorted(variants["nvim"]) == ["kickstart", "lazyvim", "minimal"]


def test_resolve_stow_packages():
    base = ["bash", "conda", "fish", "nvim", "tmux", "zsh"]
    resolved_kickstart = resolve_stow_packages(base, {"nvim": "kickstart"})
    assert "nvim-kickstart" in resolved_kickstart
    assert "nvim" not in resolved_kickstart

    resolved_minimal = resolve_stow_packages(base, {"nvim": "minimal"})
    assert "nvim-minimal" in resolved_minimal

    resolved_lazyvim = resolve_stow_packages(base, {"nvim": "lazyvim"})
    assert "nvim-lazyvim" in resolved_lazyvim


def test_scan_dotfile_conflicts(tmp_path):
    repo_root = tmp_path / "repo"
    home_dir = tmp_path / "home"

    # Setup repo structure
    bash_pkg = repo_root / "dotfiles" / "bash"
    bash_pkg.mkdir(parents=True)
    repo_bashrc = bash_pkg / ".bashrc"
    repo_bashrc.write_text("export REPO=1\n", encoding="utf-8")

    repo_profile = bash_pkg / ".bash_profile"
    repo_profile.write_text("export PROFILE=1\n", encoding="utf-8")

    # Setup home
    home_dir.mkdir(parents=True)
    home_bashrc = home_dir / ".bashrc"
    home_bashrc.write_text("export USER=1\n", encoding="utf-8")  # Conflict

    home_profile = home_dir / ".bash_profile"
    home_profile.write_text("export PROFILE=1\n", encoding="utf-8")  # Identical, no conflict

    conflicts = scan_dotfile_conflicts(repo_root, home_dir, ["bash"])
    assert len(conflicts) == 1
    assert conflicts[0]["rel_path"] == ".bashrc"
    assert conflicts[0]["src_path"] == repo_bashrc
    assert conflicts[0]["dest_path"] == home_bashrc


def test_format_diff(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.write_text("line A\nline B\n", encoding="utf-8")
    dest.write_text("line A\nline C\n", encoding="utf-8")

    diff = format_diff(src, dest)
    assert "-line C" in diff
    assert "+line B" in diff


def test_backup_file(tmp_path):
    home_dir = tmp_path / "home"
    target = home_dir / ".bashrc"
    target.parent.mkdir(parents=True)
    target.write_text("my custom content", encoding="utf-8")

    backed_up = backup_file(target, home_dir, timestamp="20261116120000")
    assert backed_up.exists()
    assert backed_up.read_text(encoding="utf-8") == "my custom content"
    assert "20261116120000" in str(backed_up)


def test_extract_local_override(tmp_path):
    home_dir = tmp_path / "home"
    target = home_dir / ".bashrc"
    target.parent.mkdir(parents=True)
    target.write_text("alias custom=true\n", encoding="utf-8")

    local_override = extract_local_override(target, home_dir, timestamp="20261116120000")
    assert local_override == home_dir / ".bashrc.local"
    assert local_override.exists()
    assert "alias custom=true" in local_override.read_text(encoding="utf-8")


def test_adopt_file(tmp_path):
    home_dir = tmp_path / "home"
    target = home_dir / ".tmux.conf"
    target.parent.mkdir(parents=True)
    target.write_text("set -g custom 1\n", encoding="utf-8")

    repo_dir = tmp_path / "repo" / "dotfiles" / "tmux"
    repo_file = repo_dir / ".tmux.conf"
    repo_file.parent.mkdir(parents=True)
    repo_file.write_text("set -g default 1\n", encoding="utf-8")

    adopt_file(target, repo_file, home_dir, timestamp="20261116120000")
    assert repo_file.read_text(encoding="utf-8") == "set -g custom 1\n"


def test_dump_and_load_yaml_fallback():
    data = {
        "devenv_pkg_backend": "apt",
        "devenv_selected_variants": {"nvim": "kickstart"},
        "devenv_stow_packages": ["bash", "conda", "fish"],
        "devenv_skip_links": [],
        "devenv_set_login_shell": False,
        "devenv_python_version": "3.13",
    }
    rendered = dump_yaml_fallback(data)
    assert "devenv_pkg_backend: apt" in rendered
    assert "devenv_set_login_shell: false" in rendered
    assert "- bash" in rendered

    parsed = load_yaml_fallback(rendered)
    assert parsed["devenv_pkg_backend"] == "apt"
    assert parsed["devenv_set_login_shell"] is False
    assert "bash" in parsed["devenv_stow_packages"]


def test_run_wizard_non_interactive(tmp_path):
    repo_root = tmp_path / "repo"
    home_dir = tmp_path / "home"
    choices_file = home_dir / ".config" / "dev-env" / "choices.yml"

    # Setup minimal repo
    dotfiles = repo_root / "dotfiles"
    (dotfiles / "bash").mkdir(parents=True)
    (dotfiles / "nvim-kickstart").mkdir(parents=True)

    choices = run_wizard(
        repo_root=repo_root,
        home_dir=home_dir,
        choices_file=choices_file,
        interactive=False,
    )

    assert choices_file.exists()
    assert (choices_file.stat().st_mode & 0o777) == 0o644
    assert choices["devenv_selected_variants"]["nvim"] == "kickstart"
    assert "nvim-kickstart" in choices["devenv_stow_packages"]
    assert choices["devenv_python_version"] == "3.13"


def test_main_cli_entrypoint(tmp_path):
    choices_file = tmp_path / "choices.yml"
    rc = main([
        "--non-interactive",
        "--choices-file",
        str(choices_file),
        "--home",
        str(tmp_path / "home"),
        "--repo-root",
        str(tmp_path / "repo"),
    ])
    assert rc == 0
    assert choices_file.exists()

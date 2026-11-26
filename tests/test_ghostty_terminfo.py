"""Hermetic tests for xterm-ghostty terminfo compilation, isolated tmux startup, and dotfiles task hygiene."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

import pytest
import yaml

from .conftest import REPO_ROOT, read

pytestmark = pytest.mark.manifest

TERMINFO_SOURCE = REPO_ROOT / "ansible" / "roles" / "dotfiles" / "files" / "xterm-ghostty.terminfo"
DOTFILES_TASKS = REPO_ROOT / "ansible" / "roles" / "dotfiles" / "tasks" / "main.yml"
TMUX_CONF = REPO_ROOT / "dotfiles" / "tmux" / ".tmux.conf"


def _require_binary(name: str) -> str:
    """Resolve a required binary (checking venv bin first) or fail closed in CI."""
    venv_candidate = Path(sys.executable).parent / name
    if venv_candidate.is_file() and os.access(venv_candidate, os.X_OK):
        return str(venv_candidate)
    resolved = shutil.which(name)
    if resolved is not None:
        return resolved
    if os.environ.get("CI") == "true" and os.environ.get("HOLON_IN_SANDBOX") != "1":
        pytest.fail(f"Required binary '{name}' is missing in CI")
    pytest.skip(f"{name} not installed in local/sandbox environment")


def _compile_ghostty_terminfo(tmp_path: Path) -> Path:
    """Compile the canonical xterm-ghostty terminfo source into an isolated temporary directory."""
    tic_bin = _require_binary("tic")
    terminfo_dir = tmp_path / "terminfo"
    terminfo_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [tic_bin, "-x", "-o", str(terminfo_dir), str(TERMINFO_SOURCE)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (
        f"tic failed to compile {TERMINFO_SOURCE} ({proc.returncode}).\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    return terminfo_dir


def test_terminfo_source_outside_dotfiles_and_compiles_cleanly(tmp_path: Path) -> None:
    """Verify xterm-ghostty.terminfo lives outside dotfiles/, compiles cleanly, and resolves via infocmp."""
    assert TERMINFO_SOURCE.is_file(), f"Missing canonical terminfo source: {TERMINFO_SOURCE}"
    dotfiles_root = (REPO_ROOT / "dotfiles").resolve()
    assert not TERMINFO_SOURCE.resolve().is_relative_to(dotfiles_root), (
        "xterm-ghostty.terminfo must live outside dotfiles/ so GNU Stow never symlinks raw terminfo text"
    )
    stray_terminfo = list(dotfiles_root.rglob("*.terminfo"))
    assert stray_terminfo == [], f"Unexpected raw terminfo files inside dotfiles/: {stray_terminfo}"

    terminfo_dir = _compile_ghostty_terminfo(tmp_path)
    infocmp_bin = _require_binary("infocmp")

    env = dict(os.environ)
    env["TERMINFO"] = str(terminfo_dir)
    env.pop("TERMINFO_DIRS", None)

    proc = subprocess.run(
        [infocmp_bin, "xterm-ghostty"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (
        f"infocmp xterm-ghostty failed ({proc.returncode}).\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    assert "xterm-ghostty" in proc.stdout, f"Expected xterm-ghostty entry in infocmp output:\n{proc.stdout}"


def test_isolated_tmux_starts_with_xterm_ghostty_terminfo(tmp_path: Path) -> None:
    """Verify an isolated tmux server starts cleanly under TERM=xterm-ghostty with compiled terminfo."""
    tmux_bin = _require_binary("tmux")
    terminfo_dir = _compile_ghostty_terminfo(tmp_path)

    env = dict(os.environ)
    env["TERM"] = "xterm-ghostty"
    env["TERMINFO"] = str(terminfo_dir)
    for var in ("TERMINFO_DIRS", "TMUX", "TMUX_PANE"):
        env.pop(var, None)

    socket_name = f"devenv-ghostty-ti-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    try:
        proc = subprocess.run(
            [
                tmux_bin,
                "-f",
                str(TMUX_CONF),
                "-L",
                socket_name,
                "new-session",
                "-d",
                "-s",
                "check",
                "sleep 5",
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, (
            f"tmux failed under TERM=xterm-ghostty ({proc.returncode}).\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
        assert "missing or unsuitable terminal" not in proc.stderr.lower(), (
            f"tmux reported missing/unsuitable terminal:\n{proc.stderr}"
        )
        assert proc.stderr.strip() == "", f"Unexpected tmux stderr output:\n{proc.stderr}"
    finally:
        subprocess.run(
            [tmux_bin, "-L", socket_name, "kill-server"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )


def _when_clauses(task: dict[str, Any]) -> list[str]:
    """Normalize a task's `when` attribute into a list of condition strings."""
    when_val = task.get("when")
    if when_val is None:
        return []
    if isinstance(when_val, str):
        return [when_val]
    return [str(item) for item in when_val]


def test_dotfiles_terminfo_tasks_hygiene_and_gating() -> None:
    """Verify dotfiles role terminfo tasks follow Ansible hygiene, check-mode, and non-WSL-gating invariants."""
    tasks: list[dict[str, Any]] = yaml.safe_load(read(DOTFILES_TASKS))
    assert isinstance(tasks, list)

    terminfo_tasks = [
        task
        for task in tasks
        if any(token in yaml.safe_dump(task) for token in ("which tic", "infocmp", "xterm-ghostty", ".terminfo"))
    ]
    assert len(terminfo_tasks) == 6, (
        f"Expected 6 terminfo tasks in {DOTFILES_TASKS}, found {len(terminfo_tasks)}: "
        f"{[t.get('name') for t in terminfo_tasks]}"
    )

    tic_probe = next((t for t in terminfo_tasks if "which tic" in yaml.safe_dump(t)), None)
    infocmp_probe = next(
        (t for t in terminfo_tasks if t.get("register") == "devenv_ghostty_terminfo_check"),
        None,
    )
    dir_task = next((t for t in terminfo_tasks if "ansible.builtin.file" in t), None)
    compile_task = next((t for t in terminfo_tasks if "tic -x -o" in yaml.safe_dump(t)), None)
    verify_task = next(
        (t for t in terminfo_tasks if t.get("register") == "devenv_ghostty_terminfo_verify"),
        None,
    )
    assert_task = next((t for t in terminfo_tasks if "ansible.builtin.assert" in t), None)

    assert tic_probe is not None, "Missing tic binary probe task"
    assert infocmp_probe is not None, "Missing pre-compile infocmp probe task"
    assert dir_task is not None, "Missing ~/.terminfo directory task"
    assert compile_task is not None, "Missing tic -x -o compile task"
    assert verify_task is not None, "Missing post-compile infocmp verify task"
    assert assert_task is not None, "Missing post-compile terminfo assert task"

    for task in terminfo_tasks:
        serialized = yaml.safe_dump(task)
        assert "role_path" not in serialized, f"Task '{task.get('name')}' must not use role_path"
        assert not task.get("become"), f"Task '{task.get('name')}' must not set become"

        when_joined = " ".join(_when_clauses(task))
        assert "devenv_is_wsl" not in when_joined, f"Task '{task.get('name')}' must not gate on devenv_is_wsl"
        assert "devenv_install_gui_casks" not in when_joined, (
            f"Task '{task.get('name')}' must not gate on devenv_install_gui_casks"
        )

        if "ansible.builtin.command" in task:
            cmd_block = task["ansible.builtin.command"]
            assert isinstance(cmd_block, dict) and "cmd" in cmd_block, (
                f"Task '{task.get('name')}' must use structured ansible.builtin.command with 'cmd'"
            )

    for probe in (tic_probe, infocmp_probe):
        assert probe.get("check_mode") is False, f"Probe '{probe.get('name')}' must set check_mode: false"
        assert probe.get("changed_when") is False, f"Probe '{probe.get('name')}' must set changed_when: false"
        assert probe.get("failed_when") is False, f"Probe '{probe.get('name')}' must set failed_when: false"

    compile_cmd = str(compile_task["ansible.builtin.command"]["cmd"])
    assert "{{ devenv_repo_root }}/ansible/roles/dotfiles/files/xterm-ghostty.terminfo" in compile_cmd, (
        f"Compile task must reference devenv_repo_root terminfo source, got: {compile_cmd}"
    )
    assert compile_task.get("changed_when") is True, "Compile task must set changed_when: true"
    assert any("not ansible_check_mode" in clause for clause in _when_clauses(compile_task)), (
        "Compile task must guard with `not ansible_check_mode`"
    )

    for post_task in (verify_task, assert_task):
        assert any("not ansible_check_mode" in clause for clause in _when_clauses(post_task)), (
            f"Task '{post_task.get('name')}' must guard with `not ansible_check_mode`"
        )

"""Static and live isolated-socket tmux regression tests for ``focus-events``.

Verifies that:
1. ``dotfiles/tmux/.tmux.conf`` actively enables ``set -g focus-events on`` and
   never comments it out or overrides it to ``off`` later in the file.
2. ``_require_binary("tmux")`` fails closed in CI when ``tmux`` is missing.
3. A live isolated-socket ``tmux`` server loaded with ``dotfiles/tmux/.tmux.conf``
   reports ``focus-events on`` via ``show-options -g focus-events`` with exit
   code 0, empty stderr, and deterministic ``kill-server`` teardown.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

from .conftest import REPO_ROOT, read

pytestmark = pytest.mark.manifest

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


def _clean_tmux_env(term: str = "xterm-256color") -> dict[str, str]:
    """Build a subprocess environment stripped of outer TMUX session variables."""
    env = os.environ.copy()
    env.pop("TMUX", None)
    env.pop("TMUX_PANE", None)
    env["TERM"] = term
    return env


def _strip_inline_comment(line: str) -> str:
    """Strip an unquoted trailing ``#`` comment from a tmux config line."""
    in_single = False
    in_double = False
    escaped = False
    for idx, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and not in_single:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:idx]
    return line


def _active_tmux_lines(text: str) -> list[str]:
    """Return stripped non-empty, non-comment directives from a tmux config."""
    active: list[str] = []
    for raw_line in text.splitlines():
        cleaned = _strip_inline_comment(raw_line).strip()
        if cleaned:
            active.append(cleaned)
    return active


def test_require_binary_fails_closed_in_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify _require_binary fails closed when CI=true outside the Holon sandbox."""
    monkeypatch.setattr(os, "access", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("HOLON_IN_SANDBOX", "0")

    with pytest.raises(pytest.fail.Exception, match="Required binary 'tmux' is missing in CI"):
        _require_binary("tmux")


def test_tmux_conf_enables_focus_events_without_override() -> None:
    """Verify dotfiles/tmux/.tmux.conf enables focus-events and never overrides it to off."""
    active_lines = _active_tmux_lines(read(TMUX_CONF))
    assert "set -g focus-events on" in active_lines, (
        f"Expected active 'set -g focus-events on' directive in {TMUX_CONF}"
    )

    effective_values: list[str] = []
    for line in active_lines:
        try:
            tokens = shlex.split(line)
        except ValueError:
            tokens = line.split()
        if not tokens or tokens[0] not in {"set", "set-option"}:
            continue
        if "focus-events" not in tokens:
            continue
        opt_idx = tokens.index("focus-events")
        value = tokens[opt_idx + 1].lower() if opt_idx + 1 < len(tokens) else ""
        assert value != "off", f"Conflicting focus-events override in {TMUX_CONF}: {line}"
        effective_values.append(value)

    assert effective_values, f"No active set/set-option focus-events directive found in {TMUX_CONF}"
    assert effective_values[-1] == "on", (
        f"Final effective focus-events value in {TMUX_CONF} is {effective_values[-1]!r}, expected 'on'"
    )


def test_tmux_live_focus_events_enabled_without_stderr() -> None:
    """Verify an isolated tmux server loads .tmux.conf with focus-events on and empty stderr."""
    tmux_bin = _require_binary("tmux")
    socket_name = f"devenv-focus-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    env = _clean_tmux_env("xterm-256color")

    try:
        start_proc = subprocess.run(
            [
                tmux_bin,
                "-f",
                str(TMUX_CONF),
                "-L",
                socket_name,
                "new-session",
                "-d",
                "-s",
                "focus-check",
                "sleep 5",
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert start_proc.returncode == 0, (
            f"tmux new-session failed ({start_proc.returncode}):\n"
            f"STDOUT:\n{start_proc.stdout}\nSTDERR:\n{start_proc.stderr}"
        )
        assert start_proc.stderr.strip() == "", f"tmux emitted stderr while loading {TMUX_CONF}:\n{start_proc.stderr}"

        show_proc = subprocess.run(
            [tmux_bin, "-L", socket_name, "show-options", "-g", "focus-events"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert show_proc.returncode == 0, (
            f"tmux show-options failed ({show_proc.returncode}):\n"
            f"STDOUT:\n{show_proc.stdout}\nSTDERR:\n{show_proc.stderr}"
        )
        assert show_proc.stderr.strip() == "", f"tmux show-options emitted stderr:\n{show_proc.stderr}"
        assert show_proc.stdout.strip() == "focus-events on", (
            f"Unexpected focus-events option output: {show_proc.stdout!r}"
        )
    finally:
        subprocess.run(
            [tmux_bin, "-L", socket_name, "kill-server"],
            env=env,
            capture_output=True,
            check=False,
        )

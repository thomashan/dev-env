"""Static and live real-tmux PTY regression tests for Shift+Enter extended keys.

Verifies that:
1. ``dotfiles/tmux/.tmux.conf`` configures ``extended-keys always``, quiet
   ``extended-keys-format csi-u`` (compatible with both tmux 3.4 on Ubuntu/WSL
   and tmux 3.5+ on macOS Homebrew), and ``xterm*:extkeys`` terminal features.
2. ``dotfiles/ghostty/.config/ghostty/config.ghostty`` preserves native
   extended-key reporting for ``shift+enter`` without rebinding it to a plain
   carriage return or raw newline.
3. ``dotfiles/tmux/.tmux.conf`` loads cleanly with exit code 0 and empty stderr.
4. Live real-tmux PTY sessions under both ``TERM=xterm-256color`` and
   ``TERM=xterm-ghostty`` forward CSI-u and modifyOtherKeys Shift+Enter
   sequences as distinct extended Shift+Enter sequences (never collapsing to
   plain ``\\r``), preserve ``ESC+CR`` without collapsing to plain ``\\r``, and
   keep plain Enter as ``\\r``.
"""

from __future__ import annotations

import os
import pty
import select
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

from .conftest import REPO_ROOT, read

pytestmark = pytest.mark.manifest

TMUX_CONF = REPO_ROOT / "dotfiles" / "tmux" / ".tmux.conf"
GHOSTTY_CONF = REPO_ROOT / "dotfiles" / "ghostty" / ".config" / "ghostty" / "config.ghostty"

EXTENDED_SHIFT_ENTER_SEQUENCES: frozenset[bytes] = frozenset({b"\x1b[13;2u", b"\x1b[27;2;13~"})

_PANE_READER_SCRIPT = """
import os, select, sys, time, tty
ready_path, out_path = sys.argv[1], sys.argv[2]
tmp_path = out_path + ".tmp"
tty.setraw(0)
with open(ready_path, "wb") as f:
    f.write(b"ready")
buf = bytearray()
deadline = time.monotonic() + 5.0
while time.monotonic() < deadline:
    timeout = 0.15 if buf else min(0.2, max(0.01, deadline - time.monotonic()))
    r, _, _ = select.select([0], [], [], timeout)
    if r:
        chunk = os.read(0, 4096)
        if not chunk:
            break
        buf.extend(chunk)
    elif buf:
        break
with open(tmp_path, "wb") as f:
    f.write(bytes(buf))
os.replace(tmp_path, out_path)
""".strip()


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


def _clean_tmux_env(term: str) -> dict[str, str]:
    """Build a subprocess environment stripped of outer TMUX session variables."""
    env = os.environ.copy()
    env.pop("TMUX", None)
    env.pop("TMUX_PANE", None)
    env["TERM"] = term
    return env


def _ensure_terminfo_env(term: str, tmp_path: Path) -> dict[str, str]:
    """Ensure terminfo exists for ``term`` (synthesizing ``xterm-ghostty`` if needed)."""
    env = _clean_tmux_env(term)
    if term != "xterm-ghostty":
        return env

    infocmp_bin = shutil.which("infocmp")
    if infocmp_bin is not None:
        probe = subprocess.run(
            [infocmp_bin, "xterm-ghostty"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode == 0:
            return env

    terminfo_dir = tmp_path / "terminfo"
    terminfo_dir.mkdir(parents=True, exist_ok=True)
    tic_bin = shutil.which("tic")
    if tic_bin is not None:
        src_path = tmp_path / "xterm-ghostty.ti"
        src_path.write_text(
            "xterm-ghostty|Ghostty terminal emulator (test shim),\n\tuse=xterm-256color,\n",
            encoding="utf-8",
        )
        compiled = subprocess.run(
            [tic_bin, "-o", str(terminfo_dir), str(src_path)],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if compiled.returncode == 0:
            env["TERMINFO"] = str(terminfo_dir)
            return env

    # Fallback when `tic` is unavailable: copy compiled xterm-256color entry.
    for root in (
        Path("/usr/share/terminfo"),
        Path("/lib/terminfo"),
        Path("/etc/terminfo"),
        Path("/opt/homebrew/share/terminfo"),
    ):
        for subdir in ("x", "78"):
            candidate = root / subdir / "xterm-256color"
            if candidate.is_file():
                dest = terminfo_dir / subdir / "xterm-ghostty"
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(candidate, dest)
                env["TERMINFO"] = str(terminfo_dir)
                return env

    return env


def _drain_fd(fd: int, max_duration: float, idle_window: float) -> None:
    """Drain readable bytes from a PTY master fd without blocking."""
    end_time = time.monotonic() + max_duration
    last_read = time.monotonic()
    while time.monotonic() < end_time:
        remaining = max(0.01, min(0.05, end_time - time.monotonic()))
        ready, _, _ = select.select([fd], [], [], remaining)
        if ready:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            last_read = time.monotonic()
        elif time.monotonic() - last_read >= idle_window:
            break


def _run_tmux_pty_capture(tmux_bin: str, term: str, payload: bytes, tmp_path: Path) -> bytes:
    """Attach a real tmux client over a PTY, feed raw bytes, and return bytes captured by the pane."""
    socket_name = f"devenv-test-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    case_dir = tmp_path / f"case-{uuid.uuid4().hex[:8]}"
    case_dir.mkdir(parents=True, exist_ok=True)
    ready_file = case_dir / "ready"
    out_file = case_dir / "captured.bin"

    env = _ensure_terminfo_env(term, tmp_path)
    pane_cmd = shlex.join([sys.executable, "-c", _PANE_READER_SCRIPT, str(ready_file), str(out_file)])

    master_fd: int | None = None
    slave_fd: int | None = None
    client_proc: subprocess.Popen[bytes] | None = None

    try:
        start_proc = subprocess.run(
            [
                tmux_bin,
                "-L",
                socket_name,
                "-f",
                str(TMUX_CONF),
                "new-session",
                "-d",
                "-s",
                "test",
                "-x",
                "80",
                "-y",
                "24",
                pane_cmd,
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

        ready_deadline = time.monotonic() + 5.0
        while not ready_file.exists() and time.monotonic() < ready_deadline:
            time.sleep(0.02)
        assert ready_file.exists(), f"Pane reader did not signal ready within 5s for TERM={term}"

        master_fd, slave_fd = pty.openpty()
        client_proc = subprocess.Popen(
            [tmux_bin, "-L", socket_name, "attach-session", "-t", "test"],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            env=env,
            start_new_session=True,
        )
        os.close(slave_fd)
        slave_fd = None

        # Drain initial attach redraw output so tmux completes client setup.
        _drain_fd(master_fd, max_duration=0.6, idle_window=0.15)
        assert client_proc.poll() is None, (
            f"tmux attach-session exited early ({client_proc.returncode}) for TERM={term}"
        )

        os.write(master_fd, payload)

        capture_deadline = time.monotonic() + 5.0
        while not out_file.exists() and time.monotonic() < capture_deadline:
            ready, _, _ = select.select([master_fd], [], [], 0.05)
            if ready:
                try:
                    os.read(master_fd, 4096)
                except OSError:
                    break

        assert out_file.exists(), f"Pane did not capture payload {payload!r} within 5s for TERM={term}"
        return out_file.read_bytes()
    finally:
        if client_proc is not None and client_proc.poll() is None:
            client_proc.terminate()
            try:
                client_proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                client_proc.kill()
                client_proc.wait(timeout=2.0)
        if master_fd is not None:
            try:
                os.close(master_fd)
            except OSError:
                pass
        if slave_fd is not None:
            try:
                os.close(slave_fd)
            except OSError:
                pass
        subprocess.run(
            [tmux_bin, "-L", socket_name, "kill-server"],
            env=env,
            capture_output=True,
            check=False,
        )


def test_require_binary_fails_closed_in_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify _require_binary fails closed when CI=true outside the Holon sandbox."""
    monkeypatch.setattr(os, "access", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("HOLON_IN_SANDBOX", "0")

    with pytest.raises(pytest.fail.Exception, match="Required binary 'tmux' is missing in CI"):
        _require_binary("tmux")


def test_tmux_conf_extended_keys_directives() -> None:
    """Verify dotfiles/tmux/.tmux.conf declares all required extended-keys directives."""
    active_lines = [
        line.strip() for line in read(TMUX_CONF).splitlines() if line.strip() and not line.lstrip().startswith("#")
    ]
    assert "set -s extended-keys always" in active_lines
    assert "set -sq extended-keys-format csi-u" in active_lines
    assert "set -as terminal-features 'xterm*:extkeys'" in active_lines


def test_ghostty_config_preserves_native_shift_enter() -> None:
    """Verify Ghostty config preserves native shift+enter reporting and Option+Arrow unbinds."""
    active_lines = [
        line.strip() for line in read(GHOSTTY_CONF).splitlines() if line.strip() and not line.lstrip().startswith("#")
    ]
    assert "keybind = alt+arrow_left=unbind" in active_lines
    assert "keybind = alt+arrow_right=unbind" in active_lines
    for line in active_lines:
        if line.lower().startswith("keybind"):
            assert "shift+enter" not in line.lower(), (
                f"Ghostty config must not override native shift+enter reporting: {line}"
            )


def test_tmux_conf_loads_cleanly_without_stderr() -> None:
    """Verify dotfiles/tmux/.tmux.conf loads with exit code 0 and empty stderr on real tmux."""
    tmux_bin = _require_binary("tmux")
    socket_name = f"devenv-load-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    env = _clean_tmux_env("xterm-256color")

    try:
        proc = subprocess.run(
            [
                tmux_bin,
                "-L",
                socket_name,
                "-f",
                str(TMUX_CONF),
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
        assert proc.returncode == 0, f"tmux exited {proc.returncode}:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        assert proc.stderr.strip() == "", f"tmux emitted stderr while loading {TMUX_CONF}:\n{proc.stderr}"
    finally:
        subprocess.run(
            [tmux_bin, "-L", socket_name, "kill-server"],
            env=env,
            capture_output=True,
            check=False,
        )


@pytest.mark.parametrize("term", ["xterm-256color", "xterm-ghostty"])
def test_tmux_pty_shift_enter_and_enter_sequences(tmp_path: Path, term: str) -> None:
    """Verify real tmux PTY sessions forward Shift+Enter without collapsing to plain Enter."""
    tmux_bin = _require_binary("tmux")

    csi_u_captured = _run_tmux_pty_capture(tmux_bin, term, b"\x1b[13;2u", tmp_path)
    assert csi_u_captured != b"\r", f"CSI-u Shift+Enter collapsed to plain CR for TERM={term}"
    assert csi_u_captured in EXTENDED_SHIFT_ENTER_SEQUENCES, (
        f"Unexpected CSI-u Shift+Enter capture {csi_u_captured!r} for TERM={term}"
    )

    modify_other_keys_captured = _run_tmux_pty_capture(tmux_bin, term, b"\x1b[27;2;13~", tmp_path)
    assert modify_other_keys_captured != b"\r", f"modifyOtherKeys Shift+Enter collapsed to plain CR for TERM={term}"
    assert modify_other_keys_captured in EXTENDED_SHIFT_ENTER_SEQUENCES, (
        f"Unexpected modifyOtherKeys Shift+Enter capture {modify_other_keys_captured!r} for TERM={term}"
    )

    esc_cr_captured = _run_tmux_pty_capture(tmux_bin, term, b"\x1b\r", tmp_path)
    assert esc_cr_captured != b"\r", f"ESC+CR collapsed to plain CR for TERM={term}"
    assert esc_cr_captured.startswith(b"\x1b"), f"ESC+CR lost leading ESC ({esc_cr_captured!r}) for TERM={term}"

    enter_captured = _run_tmux_pty_capture(tmux_bin, term, b"\r", tmp_path)
    assert enter_captured == b"\r", f"Plain Enter mutated to {enter_captured!r} for TERM={term}"

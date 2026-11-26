"""Static and live real-tmux PTY regression tests for Shift+Enter and C-j passthrough.

Verifies that:
1. ``dotfiles/tmux/.tmux.conf`` configures ``extended-keys always``, quiet
   ``extended-keys-format csi-u`` (compatible with both tmux 3.4 on Ubuntu/WSL
   and tmux 3.5+ on macOS Homebrew), and ``xterm*:extkeys`` terminal features.
2. ``dotfiles/ghostty/.config/ghostty/config.ghostty`` preserves native
   extended-key reporting for ``shift+enter`` without rebinding it to a plain
   carriage return or raw newline.
3. ``dotfiles/tmux/.tmux.conf`` loads cleanly with exit code 0 and empty stderr.
4. A universal cross-terminal real-tmux PTY matrix covering both Ghostty
   (``TERM=xterm-ghostty`` and ``TERM=xterm-256color``) and Warp
   (``TERM=xterm-256color``) delivers consistent Shift+Enter, Alt+Enter, and
   plain Enter sequences without swallowing ``0x0a`` or collapsing modified
   Enter to plain ``\\r``.
5. Vertical split-pane real-tmux PTY sessions preserve ``select-pane -D`` on
   plain non-agent top panes while forwarding ``0x0a`` (Warp Shift+Enter)
   intact without moving focus on coding-agent (``claude``) top panes.
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
    """Drain readable bytes from a PTY master fd without blocking.

    Waits for at least one byte to be read before applying ``idle_window`` so
    slow startup cannot exit early before initial output arrives.
    """
    end_time = time.monotonic() + max_duration
    last_read: float | None = None
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
        elif last_read is not None and time.monotonic() - last_read >= idle_window:
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
        _drain_fd(master_fd, max_duration=2.0, idle_window=0.15)
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


def test_tmux_conf_is_vim_or_agent_matches_args_cross_platform() -> None:
    """Verify is_vim_or_agent uses wide ps args and matches symlinked/long-path agents without false positives."""
    tmux_conf = read(TMUX_CONF)
    assert "ps -ww -o state= -o args= -t '#{pane_tty}'" in tmux_conf

    regex = (
        "^[^TXZ ]+ +([^[:space:]]+/)?"
        "(g?(view|l?n?vim?x?|diff)|claude|codex|agy|antigravity|opencode|pi|node)([[:space:]]|$)"
    )
    assert f"grep -iqE '{regex}'" in tmux_conf

    grep_bin = shutil.which("grep")
    if grep_bin is None:
        pytest.skip("grep not installed in local/sandbox environment")

    positive_samples = [
        "S+   claude",
        "Ss+  /Users/runner/.local/bin/claude --resume",
        (
            "S+   /private/var/folders/q2/p1t6rgxj5fj32g1dc7dmd49r0000gn/T/pytest-of-runner/"
            "pytest-0/test_tmux_pty_vertical_split_c0/agent-split-88f11d48/claude -c import sys"
        ),
        "S+   /opt/homebrew/bin/node /opt/homebrew/bin/codex",
        "S+   nvim dotfiles/tmux/.tmux.conf",
        "R+   /usr/local/bin/opencode",
    ]
    for sample in positive_samples:
        proc = subprocess.run(
            [grep_bin, "-iqE", regex],
            input=f"{sample}\n",
            text=True,
            capture_output=True,
            check=False,
        )
        assert proc.returncode == 0, f"Expected is_vim_or_agent regex to match {sample!r}"

    negative_samples = [
        "S+   sleep 30",
        "Ss   -zsh",
        "S+   /bin/cat claude.md",
        "S+   grep claude notes.txt",
        "S+   claude-helper --flag",
        "T+   claude",
        "Z    claude",
    ]
    for sample in negative_samples:
        proc = subprocess.run(
            [grep_bin, "-iqE", regex],
            input=f"{sample}\n",
            text=True,
            capture_output=True,
            check=False,
        )
        assert proc.returncode == 1, f"Expected is_vim_or_agent regex NOT to match {sample!r}"


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


@pytest.mark.parametrize(
    ("terminal_name", "term", "shift_enter_payloads"),
    [
        ("ghostty", "xterm-ghostty", (b"\x1b[13;2u", b"\x1b[27;2;13~")),
        ("ghostty", "xterm-256color", (b"\x1b[13;2u", b"\x1b[27;2;13~")),
        ("warp", "xterm-256color", (b"\x0a", b"\x1b[13;2u")),
    ],
)
def test_tmux_pty_cross_terminal_enter_matrix(
    tmp_path: Path,
    terminal_name: str,
    term: str,
    shift_enter_payloads: tuple[bytes, ...],
) -> None:
    """Verify Ghostty and Warp Shift+Enter, Alt+Enter, and Enter behave consistently in real tmux."""
    tmux_bin = _require_binary("tmux")

    for payload in shift_enter_payloads:
        captured = _run_tmux_pty_capture(tmux_bin, term, payload, tmp_path)
        assert captured != b"", f"{terminal_name} Shift+Enter ({payload!r}) was swallowed for TERM={term}"
        assert captured != b"\r", f"{terminal_name} Shift+Enter ({payload!r}) collapsed to plain CR for TERM={term}"
        if payload == b"\x0a":
            assert captured == b"\x0a", f"{terminal_name} Shift+Enter LF mutated to {captured!r} for TERM={term}"
        elif payload in EXTENDED_SHIFT_ENTER_SEQUENCES:
            assert captured in EXTENDED_SHIFT_ENTER_SEQUENCES, (
                f"Unexpected {terminal_name} Shift+Enter capture {captured!r} for TERM={term}"
            )

    for alt_payload in (b"\x1b\r", b"\x1b[13;3u"):
        alt_captured = _run_tmux_pty_capture(tmux_bin, term, alt_payload, tmp_path)
        assert alt_captured != b"", f"{terminal_name} Alt+Enter ({alt_payload!r}) was swallowed for TERM={term}"
        assert alt_captured != b"\r", (
            f"{terminal_name} Alt+Enter ({alt_payload!r}) collapsed to plain CR for TERM={term}"
        )
        assert alt_captured.startswith(b"\x1b"), (
            f"{terminal_name} Alt+Enter ({alt_payload!r}) lost leading ESC ({alt_captured!r}) for TERM={term}"
        )

    enter_captured = _run_tmux_pty_capture(tmux_bin, term, b"\r", tmp_path)
    assert enter_captured == b"\r", f"{terminal_name} plain Enter mutated to {enter_captured!r} for TERM={term}"


def _display_tmux_format(tmux_bin: str, socket_name: str, env: dict[str, str], fmt: str) -> str:
    """Query a tmux format string from the test session."""
    proc = subprocess.run(
        [tmux_bin, "-L", socket_name, "display-message", "-p", "-t", "test", fmt],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (
        f"tmux display-message failed ({proc.returncode}):\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    return proc.stdout.strip()


def _run_tmux_vertical_split_cj(
    tmux_bin: str,
    top_cmd: str,
    *,
    ready_file: Path | None = None,
    out_file: Path | None = None,
    expect_focus_move: bool,
) -> tuple[str, str, str, bytes | None]:
    """Send 0x0a (C-j) to the active top pane of a vertical split and return pane IDs and captured bytes."""
    socket_name = f"devenv-split-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    env = _clean_tmux_env("xterm-256color")

    master_fd: int | None = None
    slave_fd: int | None = None
    client_proc: subprocess.Popen[bytes] | None = None

    try:
        top_proc = subprocess.run(
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
                "-P",
                "-F",
                "#{pane_id}",
                top_cmd,
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert top_proc.returncode == 0, (
            f"tmux new-session failed ({top_proc.returncode}):\nSTDOUT:\n{top_proc.stdout}\nSTDERR:\n{top_proc.stderr}"
        )
        top_pane_id = top_proc.stdout.strip()

        remain_proc = subprocess.run(
            [tmux_bin, "-L", socket_name, "set-window-option", "-t", "test", "remain-on-exit", "on"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert remain_proc.returncode == 0, (
            f"tmux set-window-option remain-on-exit failed ({remain_proc.returncode}):\n"
            f"STDOUT:\n{remain_proc.stdout}\nSTDERR:\n{remain_proc.stderr}"
        )

        if ready_file is not None:
            ready_deadline = time.monotonic() + 5.0
            while not ready_file.exists() and time.monotonic() < ready_deadline:
                time.sleep(0.02)
            assert ready_file.exists(), "Top pane reader did not signal ready within 5s"

        split_proc = subprocess.run(
            [
                tmux_bin,
                "-L",
                socket_name,
                "split-window",
                "-v",
                "-t",
                "test",
                "-P",
                "-F",
                "#{pane_id}",
                "sleep 30",
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert split_proc.returncode == 0, (
            f"tmux split-window failed ({split_proc.returncode}):\n"
            f"STDOUT:\n{split_proc.stdout}\nSTDERR:\n{split_proc.stderr}"
        )
        bottom_pane_id = split_proc.stdout.strip()
        assert bottom_pane_id != top_pane_id, "split-window -v did not create a distinct bottom pane"

        focus_proc = subprocess.run(
            [tmux_bin, "-L", socket_name, "select-pane", "-t", top_pane_id],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert focus_proc.returncode == 0, (
            f"tmux select-pane failed ({focus_proc.returncode}):\n"
            f"STDOUT:\n{focus_proc.stdout}\nSTDERR:\n{focus_proc.stderr}"
        )

        pane_state = _display_tmux_format(tmux_bin, socket_name, env, "#{pane_id} #{pane_at_bottom}")
        assert pane_state == f"{top_pane_id} 0", f"Expected active top pane with pane_at_bottom=0, got {pane_state!r}"

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

        _drain_fd(master_fd, max_duration=2.0, idle_window=0.15)
        assert client_proc.poll() is None, f"tmux attach-session exited early ({client_proc.returncode})"

        os.write(master_fd, b"\x0a")

        captured: bytes | None = None
        if expect_focus_move:
            active_pane_id = top_pane_id
            deadline = time.monotonic() + 3.0
            while time.monotonic() < deadline:
                ready, _, _ = select.select([master_fd], [], [], 0.05)
                if ready:
                    try:
                        os.read(master_fd, 4096)
                    except OSError:
                        break
                active_pane_id = _display_tmux_format(tmux_bin, socket_name, env, "#{pane_id}")
                if active_pane_id == bottom_pane_id:
                    break
            return top_pane_id, bottom_pane_id, active_pane_id, captured

        assert out_file is not None
        deadline = time.monotonic() + 5.0
        while not out_file.exists() and time.monotonic() < deadline:
            ready, _, _ = select.select([master_fd], [], [], 0.05)
            if ready:
                try:
                    os.read(master_fd, 4096)
                except OSError:
                    break
        assert out_file.exists(), "Coding-agent top pane did not capture 0x0a within 5s"
        captured = out_file.read_bytes()
        active_pane_id = _display_tmux_format(tmux_bin, socket_name, env, "#{pane_id}")
        return top_pane_id, bottom_pane_id, active_pane_id, captured
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


def test_tmux_pty_vertical_split_cj_moves_focus_in_plain_top_pane() -> None:
    """Verify C-j (0x0a) in a plain non-agent top split pane still switches focus to the bottom pane."""
    tmux_bin = _require_binary("tmux")
    top_pane_id, bottom_pane_id, active_pane_id, _ = _run_tmux_vertical_split_cj(
        tmux_bin,
        "sleep 30",
        expect_focus_move=True,
    )
    assert active_pane_id == bottom_pane_id, (
        f"Expected C-j in plain top split pane {top_pane_id} to switch focus to {bottom_pane_id}, "
        f"but active pane remained {active_pane_id}"
    )


def test_tmux_pty_vertical_split_cj_passes_through_in_agent_top_pane(tmp_path: Path) -> None:
    """Verify Warp Shift+Enter (0x0a) in a coding-agent top split pane stays focused and delivers 0x0a."""
    tmux_bin = _require_binary("tmux")
    bash_bin = _require_binary("bash")
    case_dir = tmp_path / f"agent-split-{uuid.uuid4().hex[:8]}"
    case_dir.mkdir(parents=True, exist_ok=True)
    ready_file = case_dir / "ready"
    out_file = case_dir / "captured.bin"

    claude_bin = case_dir / "claude"
    os.symlink(bash_bin, claude_bin)
    reader_cmd = shlex.join([sys.executable, "-c", _PANE_READER_SCRIPT, str(ready_file), str(out_file)])
    # Keep the symlinked `claude` bash process alive on pane_tty instead of
    # symlinking `sys.executable` directly: on macOS framework Python builds,
    # `bin/python` is the `pythonw` stub which replaces argv[0] with
    # `Python.app/Contents/MacOS/Python`, hiding `claude` from `ps -o args=`.
    # The trailing `; rc=$?; exit "$rc"` prevents bash from exec-optimizing the
    # single command away before the reader exits.
    top_cmd = shlex.join([str(claude_bin), "-c", f'{reader_cmd}; rc=$?; exit "$rc"'])

    top_pane_id, _bottom_pane_id, active_pane_id, captured = _run_tmux_vertical_split_cj(
        tmux_bin,
        top_cmd,
        ready_file=ready_file,
        out_file=out_file,
        expect_focus_move=False,
    )
    assert captured == b"\x0a", f"Expected coding-agent top pane to receive 0x0a, got {captured!r}"
    assert active_pane_id == top_pane_id, (
        f"Expected focus to stay on coding-agent top pane {top_pane_id}, but moved to {active_pane_id}"
    )

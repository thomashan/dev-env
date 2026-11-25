"""Hermetic ansible-playbook integration tests and CI/Docker converge harness invariants.

Exercises real ``ansible-playbook`` execution against hermetic ``tmp_path`` homes for:
1. ``dotfiles`` role + ``ansible/playbooks/unlink.yml`` roundtrip with real GNU ``stow``
   and backup displacement of pre-existing unmanaged ``.bashrc`` and ``.zprofile``, plus
   ``xterm-ghostty`` terminfo converge, idempotence, and ``--check`` mode verification.
2. ``node`` role clean-environment login-shell verification probes and assertions under
   a polluted parent environment (simulating ``nvm.fish`` / ``nvm.sh`` active during
   re-converge) as well as ``--check`` mode on an unbootstrapped empty ``$HOME``.
3. ``fish`` role ``ansible.builtin.find`` with ``follow: true`` + ``fish -n`` syntax
   checking over stowed dotfile symlinks.
4. Structural and zero-``apt-get`` invariants for ``.github/workflows/test-converge.yml``,
   ``tests/docker/ubuntu.Dockerfile``, ``.dockerignore``, and ``Makefile`` ``test-ubuntu``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

from .conftest import REPO_ROOT, read
from .test_shell_hooks import _link_repo_dotfiles, _require_shell, _write_executable

pytestmark = pytest.mark.manifest


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


def test_ansible_dotfiles_stow_and_unlink_roundtrip(tmp_path: Path) -> None:
    """Run real ansible-playbook on dotfiles role and unlink.yml with GNU stow and backup displacement."""
    ansible_playbook_bin = _require_binary("ansible-playbook")
    _require_binary("stow")

    fake_home = tmp_path / "home"
    fake_home.mkdir(parents=True, exist_ok=True)

    # Seed pre-existing unmanaged regular files to verify backup displacement
    (fake_home / ".bashrc").write_text("# unmanaged pre-existing bashrc\n", encoding="utf-8")
    (fake_home / ".zprofile").write_text("# unmanaged pre-existing zprofile\n", encoding="utf-8")

    group_vars: dict[str, Any] = yaml.safe_load(read(REPO_ROOT / "ansible" / "group_vars" / "all.yml"))
    dotfiles_tasks: list[dict[str, Any]] = yaml.safe_load(
        read(REPO_ROOT / "ansible" / "roles" / "dotfiles" / "tasks" / "main.yml")
    )

    playbook_path = tmp_path / "run_dotfiles_role.yml"
    playbook_content = [
        {
            "name": "Run dotfiles role in hermetic HOME",
            "hosts": "localhost",
            "connection": "local",
            "gather_facts": True,
            "vars_files": [str(REPO_ROOT / "ansible" / "group_vars" / "all.yml")],
            "vars": {
                "devenv_repo_root": str(REPO_ROOT),
            },
            "tasks": dotfiles_tasks,
        }
    ]
    playbook_path.write_text(yaml.safe_dump(playbook_content, sort_keys=False), encoding="utf-8")

    env = {
        **os.environ,
        "HOME": str(fake_home),
        "ANSIBLE_CONFIG": str(REPO_ROOT / "ansible.cfg"),
        "ANSIBLE_LOCAL_TEMP": str(tmp_path / ".ansible_tmp"),
        "ANSIBLE_REMOTE_TEMP": str(tmp_path / ".ansible_remote_tmp"),
        "ANSIBLE_FORCE_COLOR": "0",
        "ANSIBLE_NOCOLOR": "1",
    }

    # First converge: displaces unmanaged files into backup dir and stows all packages
    proc1 = subprocess.run(
        [
            ansible_playbook_bin,
            "-i",
            "localhost,",
            "-c",
            "local",
            "-e",
            f"devenv_home={fake_home}",
            str(playbook_path),
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc1.returncode == 0, (
        f"dotfiles converge failed ({proc1.returncode}).\nSTDOUT:\n{proc1.stdout}\nSTDERR:\n{proc1.stderr}"
    )
    assert "[DEPRECATION WARNING]" not in proc1.stderr, f"Deprecation warning:\n{proc1.stderr}"

    # Verify every link in devenv_links (including .zprofile) is a symlink pointing into REPO_ROOT
    expected_links: list[dict[str, str]] = group_vars["devenv_links"]
    assert any(entry["src"] == "dotfiles/zsh/.zprofile" for entry in expected_links)
    for entry in expected_links:
        dest_rel = entry["dest"].replace("{{ devenv_home }}/", "")
        dest_path = fake_home / dest_rel
        expected_src = (REPO_ROOT / entry["src"]).resolve()
        assert dest_path.is_symlink(), f"Expected {dest_path} to be a stowed symlink"
        assert dest_path.resolve() == expected_src, f"{dest_path} resolved to {dest_path.resolve()} != {expected_src}"

    # Verify unmanaged .bashrc and .zprofile were backed up
    backup_root = fake_home / ".local" / "share" / "dev-env" / "backup"
    assert backup_root.is_dir(), "Expected backup directory to be created for displaced files"
    backed_up_files = list(backup_root.rglob("*"))
    assert any(p.is_file() and p.name.endswith("__.bashrc") for p in backed_up_files), (
        f"Displaced .bashrc not found in backup dir: {backed_up_files}"
    )
    assert any(p.is_file() and p.name.endswith("__.zprofile") for p in backed_up_files), (
        f"Displaced .zprofile not found in backup dir: {backed_up_files}"
    )

    # Second converge: verify idempotence
    proc2 = subprocess.run(
        [
            ansible_playbook_bin,
            "-i",
            "localhost,",
            "-c",
            "local",
            "-e",
            f"devenv_home={fake_home}",
            str(playbook_path),
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc2.returncode == 0, (
        f"dotfiles second converge failed ({proc2.returncode}).\nSTDOUT:\n{proc2.stdout}\nSTDERR:\n{proc2.stderr}"
    )
    assert "[DEPRECATION WARNING]" not in proc2.stderr

    # Run unlink.yml playbook using ansible/inventory/localhost.ini so `hosts: control` matches localhost
    unlink_proc = subprocess.run(
        [
            ansible_playbook_bin,
            "-i",
            str(REPO_ROOT / "ansible" / "inventory" / "localhost.ini"),
            "-e",
            f"devenv_home={fake_home}",
            str(REPO_ROOT / "ansible" / "playbooks" / "unlink.yml"),
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert unlink_proc.returncode == 0, (
        f"unlink.yml failed ({unlink_proc.returncode}).\nSTDOUT:\n{unlink_proc.stdout}\nSTDERR:\n{unlink_proc.stderr}"
    )
    assert "[DEPRECATION WARNING]" not in unlink_proc.stderr
    assert "Invoke stow to delete all declared variant packages" in unlink_proc.stdout

    # Verify all managed symlinks are removed while backups remain intact
    for entry in expected_links:
        dest_rel = entry["dest"].replace("{{ devenv_home }}/", "")
        dest_path = fake_home / dest_rel
        assert not dest_path.exists() and not dest_path.is_symlink(), (
            f"Expected {dest_path} to be unlinked by unlink.yml"
        )
    assert any(p.is_file() and p.name.endswith("__.bashrc") for p in backup_root.rglob("*"))
    assert any(p.is_file() and p.name.endswith("__.zprofile") for p in backup_root.rglob("*"))


def test_ansible_dotfiles_ghostty_terminfo_converge_and_check_mode(tmp_path: Path) -> None:
    """Run real ansible-playbook dotfiles role to verify xterm-ghostty terminfo converge, idempotence, and --check."""
    ansible_playbook_bin = _require_binary("ansible-playbook")
    _require_binary("stow")
    _require_binary("tic")
    infocmp_bin = _require_binary("infocmp")

    fake_home = tmp_path / "terminfo_home"
    fake_home.mkdir(parents=True, exist_ok=True)

    dotfiles_tasks: list[dict[str, Any]] = yaml.safe_load(
        read(REPO_ROOT / "ansible" / "roles" / "dotfiles" / "tasks" / "main.yml")
    )

    playbook_path = tmp_path / "run_dotfiles_terminfo.yml"
    playbook_content = [
        {
            "name": "Run dotfiles role for xterm-ghostty terminfo in hermetic HOME",
            "hosts": "localhost",
            "connection": "local",
            "gather_facts": True,
            "vars_files": [str(REPO_ROOT / "ansible" / "group_vars" / "all.yml")],
            "vars": {
                "devenv_repo_root": str(REPO_ROOT),
                "devenv_is_wsl": True,
                "devenv_install_gui_casks": False,
            },
            "tasks": dotfiles_tasks,
        }
    ]
    playbook_path.write_text(yaml.safe_dump(playbook_content, sort_keys=False), encoding="utf-8")

    env = {
        **os.environ,
        "HOME": str(fake_home),
        "ANSIBLE_CONFIG": str(REPO_ROOT / "ansible.cfg"),
        "ANSIBLE_LOCAL_TEMP": str(tmp_path / ".ansible_tmp"),
        "ANSIBLE_REMOTE_TEMP": str(tmp_path / ".ansible_remote_tmp"),
        "ANSIBLE_FORCE_COLOR": "0",
        "ANSIBLE_NOCOLOR": "1",
    }
    env.pop("TERMINFO", None)
    env.pop("TERMINFO_DIRS", None)

    pre_probe = subprocess.run(
        [infocmp_bin, "xterm-ghostty"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    host_had_system_terminfo = pre_probe.returncode == 0

    # First converge: compiles xterm-ghostty into fake_home/.terminfo (when absent system-wide)
    proc1 = subprocess.run(
        [
            ansible_playbook_bin,
            "-i",
            "localhost,",
            "-c",
            "local",
            "-e",
            f"devenv_home={fake_home}",
            str(playbook_path),
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc1.returncode == 0, (
        f"dotfiles terminfo converge failed ({proc1.returncode}).\nSTDOUT:\n{proc1.stdout}\nSTDERR:\n{proc1.stderr}"
    )
    assert "[DEPRECATION WARNING]" not in proc1.stderr, f"Deprecation warning:\n{proc1.stderr}"

    post_probe = subprocess.run(
        [infocmp_bin, "xterm-ghostty"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert post_probe.returncode == 0, (
        f"HOME={fake_home} infocmp xterm-ghostty failed ({post_probe.returncode}).\n"
        f"STDOUT:\n{post_probe.stdout}\nSTDERR:\n{post_probe.stderr}"
    )
    assert "xterm-ghostty" in post_probe.stdout

    compiled_stat_before: tuple[int, int] | None = None
    if not host_had_system_terminfo:
        terminfo_dir = fake_home / ".terminfo"
        assert terminfo_dir.is_dir(), f"Expected {terminfo_dir} to be created on converge"
        compiled_entries = [p for p in terminfo_dir.rglob("*") if p.is_file() and p.name == "xterm-ghostty"]
        assert compiled_entries, f"Expected compiled xterm-ghostty entry under {terminfo_dir}"
        st = compiled_entries[0].stat()
        compiled_stat_before = (st.st_ino, st.st_mtime_ns)

    # Second converge: verify terminfo tasks are strictly idempotent
    # (GNU Stow --restow on Ubuntu may still report changed=1 for symlink restow).
    proc2 = subprocess.run(
        [
            ansible_playbook_bin,
            "-i",
            "localhost,",
            "-c",
            "local",
            "-e",
            f"devenv_home={fake_home}",
            str(playbook_path),
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc2.returncode == 0, (
        f"dotfiles terminfo second converge failed ({proc2.returncode}).\n"
        f"STDOUT:\n{proc2.stdout}\nSTDERR:\n{proc2.stderr}"
    )
    assert "[DEPRECATION WARNING]" not in proc2.stderr
    assert "TASK [Locate tic terminfo compiler]" in proc2.stdout, (
        f"Expected terminfo tasks in second converge output:\n{proc2.stdout}"
    )
    terminfo_section = proc2.stdout.split("TASK [Locate tic terminfo compiler]", 1)[1].split("PLAY RECAP", 1)[0]
    assert "changed:" not in terminfo_section, (
        f"Expected terminfo tasks to be idempotent on second converge:\n{terminfo_section}"
    )
    assert "Ensure user terminfo directory exists for xterm-ghostty" not in terminfo_section, (
        f"Expected terminfo directory task to be skipped on second converge:\n{terminfo_section}"
    )
    assert "Compile xterm-ghostty terminfo into user terminfo directory" not in terminfo_section, (
        f"Expected terminfo compile task to be skipped on second converge:\n{terminfo_section}"
    )
    if compiled_stat_before is not None:
        compiled_after = [p for p in (fake_home / ".terminfo").rglob("*") if p.is_file() and p.name == "xterm-ghostty"]
        assert compiled_after, "Expected compiled xterm-ghostty entry to remain after second converge"
        st_after = compiled_after[0].stat()
        assert (st_after.st_ino, st_after.st_mtime_ns) == compiled_stat_before, (
            "Expected compiled xterm-ghostty terminfo file to remain untouched on second converge"
        )

    # --check mode against a fresh empty HOME must succeed without creating ~/.terminfo
    empty_home = tmp_path / "empty_terminfo_home"
    empty_home.mkdir(parents=True, exist_ok=True)
    check_env = {**env, "HOME": str(empty_home)}
    check_proc = subprocess.run(
        [
            ansible_playbook_bin,
            "--check",
            "-i",
            "localhost,",
            "-c",
            "local",
            "-e",
            f"devenv_home={empty_home}",
            str(playbook_path),
        ],
        cwd=REPO_ROOT,
        env=check_env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check_proc.returncode == 0, (
        f"dotfiles terminfo --check mode failed ({check_proc.returncode}).\n"
        f"STDOUT:\n{check_proc.stdout}\nSTDERR:\n{check_proc.stderr}"
    )
    assert "[DEPRECATION WARNING]" not in check_proc.stderr
    assert not (empty_home / ".terminfo").exists(), "--check mode must not create ~/.terminfo on disk"


def test_ansible_node_clean_env_shell_verification_playbook(tmp_path: Path) -> None:
    """Run real ansible-playbook on node role shell probes/assertions with polluted parent PATH and in --check mode."""
    ansible_playbook_bin = _require_binary("ansible-playbook")

    fake_home = tmp_path / "node_home"
    _link_repo_dotfiles(fake_home)

    node_ver = "26.13.1"
    nvm_root = fake_home / ".local" / "share" / "nvm"
    version_dir = nvm_root / "versions" / "node" / f"v{node_ver}"
    nvm_node_bin = version_dir / "bin" / "node"
    _write_executable(nvm_node_bin, f"#!/bin/sh\necho v{node_ver}\n")

    current_link = nvm_root / "current"
    current_link.symlink_to(version_dir)

    local_bin = fake_home / ".local" / "bin"
    local_bin.mkdir(parents=True, exist_ok=True)
    (local_bin / "node").symlink_to(current_link / "bin" / "node")

    # Simulate official nvm.sh prepending $NVM_DIR/versions/node/v<ver>/bin to PATH
    # (which previously broke narrow assertions that only allowed current/bin/node or .local/bin/node)
    (nvm_root / "nvm.sh").write_text(
        f'export PATH="$NVM_DIR/versions/node/v{node_ver}/bin:$PATH"\n',
        encoding="utf-8",
    )

    # Create a competing wrong node binary in parent PATH
    competing_dir = tmp_path / "competing_bin"
    _write_executable(competing_dir / "node", "#!/bin/sh\necho v18.0.0-wrong\n")

    node_tasks: list[dict[str, Any]] = yaml.safe_load(
        read(REPO_ROOT / "ansible" / "roles" / "node" / "tasks" / "main.yml")
    )
    start_idx = next(
        (idx for idx, t in enumerate(node_tasks) if t.get("name") == "Check if bash is available"),
        None,
    )
    end_idx = next(
        (idx for idx, t in enumerate(node_tasks) if t.get("name") == "Assert nvm-managed node wins on PATH"),
        None,
    )
    assert start_idx is not None and end_idx is not None and start_idx < end_idx
    shell_verify_tasks = node_tasks[start_idx : end_idx + 1]

    playbook_path = tmp_path / "verify_node_clean_shells.yml"
    playbook_content = [
        {
            "name": "Verify Node clean-shell tasks via ansible-playbook",
            "hosts": "localhost",
            "connection": "local",
            "gather_facts": True,
            "vars_files": [str(REPO_ROOT / "ansible" / "group_vars" / "all.yml")],
            "vars": {
                "devenv_node_version": node_ver,
            },
            "tasks": shell_verify_tasks,
        }
    ]
    playbook_path.write_text(yaml.safe_dump(playbook_content, sort_keys=False), encoding="utf-8")

    # Pollute parent PATH with both NVM versioned path and competing wrong node dir
    polluted_env = {
        **os.environ,
        "PATH": f"{version_dir / 'bin'}:{competing_dir}:{os.environ.get('PATH', '')}",
        "CONDA_DEFAULT_ENV": "POLLUTED_PARENT_ENV",
        "ANSIBLE_LOCAL_TEMP": str(tmp_path / ".ansible_tmp"),
        "ANSIBLE_REMOTE_TEMP": str(tmp_path / ".ansible_remote_tmp"),
        "ANSIBLE_FORCE_COLOR": "0",
        "ANSIBLE_NOCOLOR": "1",
    }

    proc = subprocess.run(
        [
            ansible_playbook_bin,
            "-i",
            "localhost,",
            "-c",
            "local",
            "-e",
            f"devenv_home={fake_home}",
            str(playbook_path),
        ],
        cwd=REPO_ROOT,
        env=polluted_env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (
        f"node shell verification playbook failed ({proc.returncode}).\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    assert "[DEPRECATION WARNING]" not in proc.stderr, f"Deprecation warning:\n{proc.stderr}"

    is_ci = os.environ.get("CI") == "true" and os.environ.get("HOLON_IN_SANDBOX") != "1"
    for shell_name, assert_header in [
        ("bash", "Assert nvm-managed node wins on PATH in Bash"),
        ("zsh", "Assert nvm-managed node wins on PATH in Zsh"),
        ("fish", "Assert nvm-managed node wins on PATH"),
    ]:
        if is_ci:
            _require_shell(shell_name)
        if shutil.which(shell_name) is not None or is_ci:
            assert assert_header in proc.stdout, f"Missing task header '{assert_header}' in stdout:\n{proc.stdout}"
            section = proc.stdout.split(assert_header, 1)[1].split("TASK [", 1)[0]
            assert "skipping:" not in section, f"Expected '{assert_header}' to execute without skipping:\n{section}"

    # Verify --check mode on an empty unbootstrapped HOME (no Node installed) succeeds cleanly
    empty_home = tmp_path / "empty_home"
    empty_home.mkdir(parents=True, exist_ok=True)
    check_proc = subprocess.run(
        [
            ansible_playbook_bin,
            "--check",
            "-i",
            "localhost,",
            "-c",
            "local",
            "-e",
            f"devenv_home={empty_home}",
            str(playbook_path),
        ],
        cwd=REPO_ROOT,
        env=polluted_env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check_proc.returncode == 0, (
        f"node shell verification --check mode failed ({check_proc.returncode}).\n"
        f"STDOUT:\n{check_proc.stdout}\nSTDERR:\n{check_proc.stderr}"
    )
    assert "[DEPRECATION WARNING]" not in check_proc.stderr


def test_ansible_fish_syntax_check_follows_stow_symlinks(tmp_path: Path) -> None:
    """Run real ansible-playbook on fish role find + fish -n tasks against stowed Fish symlinks."""
    ansible_playbook_bin = _require_binary("ansible-playbook")

    fake_home = tmp_path / "fish_home"
    _link_repo_dotfiles(fake_home)

    fish_tasks: list[dict[str, Any]] = yaml.safe_load(
        read(REPO_ROOT / "ansible" / "roles" / "fish" / "tasks" / "main.yml")
    )
    collect_task = next((t for t in fish_tasks if t.get("name") == "Collect linked fish files"), None)
    syntax_task = next((t for t in fish_tasks if t.get("name") == "Syntax-check every fish file now on disk"), None)
    assert collect_task is not None and syntax_task is not None

    assert_matched_task: dict[str, Any] = {
        "name": "Assert stowed fish symlinks were discovered",
        "ansible.builtin.assert": {
            "that": [
                "devenv_fish_files.matched >= 2",
            ],
            "fail_msg": "Expected ansible.builtin.find with follow: true to discover >= 2 symlinked .fish files",
        },
    }

    has_fish = shutil.which("fish") is not None
    if os.environ.get("CI") == "true" and os.environ.get("HOLON_IN_SANDBOX") != "1":
        _require_shell("fish")
        has_fish = True

    tasks_to_run = [collect_task, assert_matched_task]
    if has_fish:
        tasks_to_run.append(syntax_task)

    playbook_path = tmp_path / "verify_fish_symlinks.yml"
    playbook_content = [
        {
            "name": "Verify Fish find follow: true and syntax check over symlinks",
            "hosts": "localhost",
            "connection": "local",
            "gather_facts": False,
            "tasks": tasks_to_run,
        }
    ]
    playbook_path.write_text(yaml.safe_dump(playbook_content, sort_keys=False), encoding="utf-8")

    env = {
        **os.environ,
        "ANSIBLE_LOCAL_TEMP": str(tmp_path / ".ansible_tmp"),
        "ANSIBLE_REMOTE_TEMP": str(tmp_path / ".ansible_remote_tmp"),
        "ANSIBLE_FORCE_COLOR": "0",
        "ANSIBLE_NOCOLOR": "1",
    }

    proc = subprocess.run(
        [
            ansible_playbook_bin,
            "-i",
            "localhost,",
            "-c",
            "local",
            "-e",
            f"devenv_home={fake_home}",
            str(playbook_path),
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (
        f"fish symlink syntax check playbook failed ({proc.returncode}).\n"
        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    assert "[DEPRECATION WARNING]" not in proc.stderr
    assert "Assert stowed fish symlinks were discovered" in proc.stdout
    if has_fish:
        assert "config.fish" in proc.stdout, f"Expected config.fish to be syntax-checked:\n{proc.stdout}"
        assert "00-devenv.fish" in proc.stdout, f"Expected 00-devenv.fish to be syntax-checked:\n{proc.stdout}"


def test_ci_converge_workflow_and_docker_harness_invariants() -> None:
    """Validate .github/workflows/test-converge.yml, tests/docker/ubuntu.Dockerfile, .dockerignore, and Makefile."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "test-converge.yml"
    assert workflow_path.is_file(), ".github/workflows/test-converge.yml must exist"
    raw_workflow = read(workflow_path)
    assert "apt-get" not in raw_workflow, "test-converge.yml must never use apt-get"

    wf = yaml.safe_load(raw_workflow)
    triggers = wf.get("on") or wf.get(True)
    assert isinstance(triggers, dict)
    assert "push" in triggers and "pull_request" in triggers and "workflow_dispatch" in triggers
    assert wf.get("concurrency", {}).get("cancel-in-progress") is True

    job = wf["jobs"]["converge-ubuntu"]
    assert job["runs-on"] == "ubuntu-latest"
    assert job["timeout-minutes"] == 25

    runs = "\n".join(step.get("run", "") for step in job["steps"])
    assert "make check" in runs
    assert "make bootstrap" in runs
    assert (
        'WSL_DISTRO_NAME=Ubuntu CI=true make converge ANSIBLE_EXTRA="-e devenv_set_login_shell=false -e devenv_install_gui_casks=false"'
        in runs
    )
    assert (
        "WSL_DISTRO_NAME=Ubuntu CI=true fish -lc 'nvm use $devenv_node_default_version; make converge ANSIBLE_EXTRA=\"-e devenv_set_login_shell=false -e devenv_install_gui_casks=false\"'"
        in runs
    )
    for shell_check in ("bash -lc", "bash -lic", "zsh -lc", "zsh -lic", "fish -lc"):
        assert shell_check in runs, f"test-converge.yml smoke check missing {shell_check}"
    for tool_name in ("node", "conda", "uv", "ruff", "nvim", "stow", "tmux"):
        assert tool_name in runs, f"test-converge.yml smoke check missing {tool_name}"
    assert 'make check-mode ANSIBLE_EXTRA="-e devenv_set_login_shell=false -e devenv_install_gui_casks=false"' in runs

    # Validate .github/workflows/README.md documents test-converge.yml
    workflows_readme = read(REPO_ROOT / ".github" / "workflows" / "README.md")
    assert "test-converge.yml" in workflows_readme
    assert "converge-ubuntu (ubuntu-latest)" in workflows_readme

    # Validate tests/docker/ubuntu.Dockerfile
    dockerfile_path = REPO_ROOT / "tests" / "docker" / "ubuntu.Dockerfile"
    assert dockerfile_path.is_file(), "tests/docker/ubuntu.Dockerfile must exist"
    dockerfile = read(dockerfile_path)
    assert "apt-get" not in dockerfile, "tests/docker/ubuntu.Dockerfile must use apt, never apt-get"
    assert "FROM ubuntu:24.04" in dockerfile
    assert "devuser" in dockerfile
    assert "/home/linuxbrew/.linuxbrew" in dockerfile
    assert "make check" in dockerfile
    assert "make bootstrap" in dockerfile
    assert (
        'WSL_DISTRO_NAME=Ubuntu CI=true make converge ANSIBLE_EXTRA="-e devenv_set_login_shell=false -e devenv_install_gui_casks=false"'
        in dockerfile
    )
    assert (
        "WSL_DISTRO_NAME=Ubuntu CI=true fish -lc 'nvm use $devenv_node_default_version; make converge ANSIBLE_EXTRA=\"-e devenv_set_login_shell=false -e devenv_install_gui_casks=false\"'"
        in dockerfile
    )

    # Validate .dockerignore
    dockerignore_path = REPO_ROOT / ".dockerignore"
    assert dockerignore_path.is_file(), ".dockerignore must exist"
    dockerignore_entries = {
        line.strip()
        for line in read(dockerignore_path).splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    for required_ignore in (".git", ".venv", ".holon", ".pytest_cache", "__pycache__", ".ruff_cache"):
        assert required_ignore in dockerignore_entries, f".dockerignore missing {required_ignore}"

    # Validate Makefile test-ubuntu target
    makefile = read(REPO_ROOT / "Makefile")
    phony_block = makefile.split(".PHONY:")[1].split("\n\n")[0]
    assert "test-ubuntu" in phony_block, "Makefile .PHONY must include test-ubuntu"
    assert '"test-ubuntu"' in makefile, "Makefile help target must document test-ubuntu"
    assert "\ntest-ubuntu:" in makefile, "Makefile must define test-ubuntu target"
    test_ubuntu_recipe = makefile.split("\ntest-ubuntu:")[1].split("\n\n")[0]
    assert "command -v docker" in test_ubuntu_recipe
    assert "tests/docker/ubuntu.Dockerfile" in test_ubuntu_recipe
    assert "docker run --rm" in test_ubuntu_recipe

"""Multi-shell static parity and hermetic clean-environment runtime tests.

Verifies that Bash, Zsh, and Fish dotfiles:
1. Evaluate Homebrew / Linuxbrew ``brew shellenv`` inside multi-OS guards.
2. Probe all canonical Conda / Miniforge roots (with Darwin Caskroom paths
   guarded under ``case Darwin`` / ``Darwin)``) and evaluate the shell-specific
   Conda hook (``conda shell.<sh> hook``).
3. Gate the ``micromamba`` fallback behind ``conda_hook_activated == 0``.
4. Re-assert NVM's ``current/bin`` and ``~/.local/bin`` at the front of ``$PATH``
   after both Homebrew and Conda/Micromamba hooks so NVM-managed ``node`` always
   outranks Conda ``base/bin`` and Homebrew.
5. Execute cleanly inside real ``env -i`` login/interactive ``bash``, ``zsh``,
   and ``fish`` subprocesses against a hermetic fake ``$HOME`` that reproduces
   the macOS Homebrew ``/opt/homebrew/bin/conda -> .../condabin/conda`` symlink
   masking scenario.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from .conftest import REPO_ROOT, read

pytestmark = pytest.mark.manifest

CANONICAL_CONDA_CANDIDATES: tuple[str, ...] = (
    "MAMBA_ROOT_PREFIX",
    "$HOME/.local/share/mamba",
    "$HOME/micromamba",
    "$HOME/miniforge3",
    "$HOME/miniforge",
    "$HOME/mambaforge",
    "/opt/homebrew/Caskroom/miniforge/base",
    "/usr/local/Caskroom/miniforge/base",
    "/opt/miniforge3",
    "/opt/conda",
    "$HOME/anaconda3",
    "$HOME/miniconda3",
)


def _require_shell(shell_name: str) -> str:
    """Resolve a shell binary or fail closed in CI if missing."""
    resolved = shutil.which(shell_name)
    if resolved is not None:
        return resolved
    if os.environ.get("CI") == "true" and os.environ.get("HOLON_IN_SANDBOX") != "1":
        pytest.fail(f"Required shell '{shell_name}' is missing in CI")
    pytest.skip(f"{shell_name} not installed in local/sandbox environment")


def _write_executable(path: Path, content: str) -> None:
    """Create an executable script file inside tmp_path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _link_repo_dotfiles(fake_home: Path) -> None:
    """Symlink the repository's tracked shell dotfiles into a hermetic fake HOME."""
    fake_home.mkdir(parents=True, exist_ok=True)
    (fake_home / ".config" / "fish" / "conf.d").mkdir(parents=True, exist_ok=True)

    links = {
        fake_home / ".bashrc": REPO_ROOT / "dotfiles" / "bash" / ".bashrc",
        fake_home / ".bash_profile": REPO_ROOT / "dotfiles" / "bash" / ".bash_profile",
        fake_home / ".zshrc": REPO_ROOT / "dotfiles" / "zsh" / ".zshrc",
        fake_home / ".config" / "fish" / "config.fish": (
            REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "config.fish"
        ),
        fake_home / ".config" / "fish" / "conf.d" / "00-devenv.fish": (
            REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish"
        ),
    }
    for dest, src in links.items():
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        dest.symlink_to(src)

    # Ensure non-interactive login zsh (`zsh -lc`) also evaluates `.zshrc` in the
    # hermetic test home without tracking an extra dotfile outside devenv_links.
    zprofile = fake_home / ".zprofile"
    zprofile.write_text('[ -f "$HOME/.zshrc" ] && . "$HOME/.zshrc"\n', encoding="utf-8")


def _build_hermetic_conda_and_nvm_home(tmp_path: Path) -> tuple[Path, Path]:
    """Create a hermetic fake HOME with fake miniforge3, NVM node, and Homebrew conda symlink."""
    fake_home = tmp_path / "home"
    _link_repo_dotfiles(fake_home)

    conda_root = fake_home / "miniforge3"
    conda_script = f"""#!/bin/sh
if [ "$1" = "shell.bash" ] && [ "$2" = "hook" ]; then
    cat <<'EOF'
export CONDA_SHLVL=1
export CONDA_DEFAULT_ENV=base
export CONDA_PREFIX="{conda_root}"
export PATH="{conda_root}/bin:$PATH"
conda() {{
    :
}}
EOF
    exit 0
fi
if [ "$1" = "shell.zsh" ] && [ "$2" = "hook" ]; then
    cat <<'EOF'
export CONDA_SHLVL=1
export CONDA_DEFAULT_ENV=base
export CONDA_PREFIX="{conda_root}"
export PATH="{conda_root}/bin:$PATH"
conda() {{
    :
}}
EOF
    exit 0
fi
if [ "$1" = "shell.fish" ] && [ "$2" = "hook" ]; then
    cat <<'EOF'
set -gx CONDA_SHLVL 1
set -gx CONDA_DEFAULT_ENV base
set -gx CONDA_PREFIX "{conda_root}"
set -gx PATH "{conda_root}/bin" $PATH
function conda
end
EOF
    exit 0
fi
echo "raw-conda-binary"
"""
    _write_executable(conda_root / "bin" / "conda", conda_script)
    _write_executable(conda_root / "condabin" / "conda", conda_script)

    # Tool installed inside Conda base/bin (e.g., `conda install pipx`)
    _write_executable(
        conda_root / "bin" / "pipx",
        "#!/bin/sh\necho pipx-from-miniforge3\n",
    )

    # Competing node binary inside Conda base/bin that NVM must outrank
    _write_executable(
        conda_root / "bin" / "node",
        "#!/bin/sh\necho node-from-conda\n",
    )

    # NVM-managed node binary and ~/.local/bin symlink
    nvm_node = fake_home / ".local" / "share" / "nvm" / "current" / "bin" / "node"
    _write_executable(
        nvm_node,
        "#!/bin/sh\necho v26.13.1-nvm\n",
    )
    local_bin = fake_home / ".local" / "bin"
    local_bin.mkdir(parents=True, exist_ok=True)
    (local_bin / "node").symlink_to(nvm_node)

    # Reproduce macOS Homebrew's /opt/homebrew/bin/conda -> .../condabin/conda symlink
    fake_brew_bin = tmp_path / "fakebrew" / "bin"
    fake_brew_bin.mkdir(parents=True, exist_ok=True)
    (fake_brew_bin / "conda").symlink_to(conda_root / "condabin" / "conda")
    (local_bin / "conda").symlink_to(conda_root / "condabin" / "conda")

    return fake_home, fake_brew_bin


def test_require_shell_fails_closed_in_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify _require_shell fails closed when CI=true outside the Holon sandbox."""
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("HOLON_IN_SANDBOX", "0")

    with pytest.raises(pytest.fail.Exception, match="Required shell 'fish' is missing in CI"):
        _require_shell("fish")


def test_three_shell_static_parity() -> None:
    """Verify Bash, Zsh, and Fish dotfiles maintain static parity for Homebrew, Conda, and NVM."""
    bashrc = read(REPO_ROOT / "dotfiles" / "bash" / ".bashrc")
    zshrc = read(REPO_ROOT / "dotfiles" / "zsh" / ".zshrc")
    fish_devenv = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")

    shells = [
        ("bash", bashrc, "shell.bash hook", "$NVM_DIR/current/bin"),
        ("zsh", zshrc, "shell.zsh hook", "$NVM_DIR/current/bin"),
        ("fish", fish_devenv, "shell.fish hook", "$XDG_DATA_HOME/nvm/current/bin"),
    ]

    for shell_name, content, hook_token, nvm_bin_token in shells:
        # 1. OS-guarded Homebrew / Linuxbrew shellenv
        assert "brew shellenv" in content, f"{shell_name} missing brew shellenv evaluation"
        assert "/opt/homebrew/bin/brew" in content, f"{shell_name} missing /opt/homebrew/bin/brew probe"
        assert "/usr/local/bin/brew" in content, f"{shell_name} missing /usr/local/bin/brew probe"
        assert "/home/linuxbrew/.linuxbrew/bin/brew" in content, (
            f"{shell_name} missing /home/linuxbrew/.linuxbrew/bin/brew probe"
        )
        assert "$HOME/.linuxbrew/bin/brew" in content, f"{shell_name} missing $HOME/.linuxbrew/bin/brew probe"
        if shell_name == "fish":
            assert "case Darwin" in content and "case Linux" in content, (
                "00-devenv.fish must guard Homebrew/Linuxbrew under switch/case Darwin and case Linux"
            )
            assert "brew shellenv | source" in content, "00-devenv.fish must pipe brew shellenv to source"
        else:
            assert "Darwin)" in content and "Linux)" in content, (
                f"{shell_name} must guard Homebrew/Linuxbrew under case Darwin) and Linux)"
            )

        # 2. Canonical Conda candidate roots and Darwin Caskroom OS guard
        for candidate in CANONICAL_CONDA_CANDIDATES:
            assert candidate in content, f"{shell_name} missing Conda root candidate {candidate}"

        # Ensure Darwin Caskroom Conda candidate paths appear inside a Darwin case block
        cask_idx = content.find("/opt/homebrew/Caskroom/miniforge/base")
        assert cask_idx != -1
        preceding_window = content[max(0, cask_idx - 240) : cask_idx]
        assert "case Darwin" in preceding_window or "Darwin)" in preceding_window, (
            f"{shell_name} must guard /opt/homebrew/Caskroom/miniforge/base inside a Darwin OS case block"
        )

        # 3. Shell-specific Conda hook and guarded micromamba fallback
        assert hook_token in content, f"{shell_name} missing {hook_token}"
        assert "conda_hook_activated" in content, f"{shell_name} missing conda_hook_activated flag"
        assert f"micromamba shell hook --shell {shell_name}" in content, (
            f"{shell_name} missing micromamba shell hook fallback"
        )

        # 4. Post-hook NVM PATH precedence re-assertion after both Homebrew and Conda/Micromamba hooks
        brew_idx = content.rfind("brew shellenv")
        conda_hook_idx = content.rfind(hook_token)
        micromamba_hook_idx = content.rfind(f"micromamba shell hook --shell {shell_name}")
        last_nvm_idx = content.rfind(nvm_bin_token)
        last_local_bin_idx = content.rfind("$HOME/.local/bin")

        assert last_nvm_idx > brew_idx, f"{shell_name} must re-assert NVM PATH after brew shellenv"
        assert last_nvm_idx > conda_hook_idx, f"{shell_name} must re-assert NVM PATH after {hook_token}"
        assert last_nvm_idx > micromamba_hook_idx, (
            f"{shell_name} must re-assert NVM PATH after micromamba shell hook"
        )
        assert last_local_bin_idx > conda_hook_idx, (
            f"{shell_name} must re-assert ~/.local/bin PATH after {hook_token}"
        )


def test_conda_role_clean_env_shell_verification_tasks() -> None:
    """Verify ansible/roles/conda/tasks/main.yml defines read-only clean-env verification across shells."""
    conda_tasks: list[dict[str, Any]] = yaml.safe_load(
        read(REPO_ROOT / "ansible" / "roles" / "conda" / "tasks" / "main.yml")
    )

    for shell_name, probe_var, verify_var in [
        ("fish", "devenv_conda_has_fish", "devenv_conda_verify_fish"),
        ("zsh", "devenv_conda_has_zsh", "devenv_conda_verify_zsh"),
        ("bash", "devenv_conda_has_bash", "devenv_conda_verify_bash"),
    ]:
        which_task = next((t for t in conda_tasks if t.get("register") == probe_var), None)
        assert which_task is not None, f"Missing 'which {shell_name}' availability task ({probe_var})"
        assert which_task.get("changed_when") is False
        assert which_task.get("failed_when") is False
        assert which_task.get("check_mode") is False

        verify_task = next((t for t in conda_tasks if t.get("register") == verify_var), None)
        assert verify_task is not None, f"Missing clean-env verification task ({verify_var}) for {shell_name}"
        assert verify_task.get("changed_when") is False
        assert verify_task.get("check_mode") is False
        cmd = verify_task.get("ansible.builtin.command", {}).get("cmd", "")
        assert "env -i" in cmd, f"{verify_var} must run under env -i"
        when_clauses = verify_task.get("when", [])
        if isinstance(when_clauses, str):
            when_clauses = [when_clauses]
        assert "not ansible_check_mode" in when_clauses
        assert f"{probe_var}.rc == 0" in when_clauses

        assert_task = next(
            (
                t
                for t in conda_tasks
                if isinstance(t.get("ansible.builtin.assert"), dict)
                and any(verify_var in cond for cond in t["ansible.builtin.assert"].get("that", []))
            ),
            None,
        )
        assert assert_task is not None, f"Missing ansible.builtin.assert task for {verify_var}"
        that_conds = " ".join(assert_task["ansible.builtin.assert"].get("that", []))
        assert "function" in that_conds
        assert "ENV=base" in that_conds
        assert "devenv_conda_dir ~ '/bin'" in that_conds


def test_ci_unit_workflow_installs_fish_and_zsh() -> None:
    """Verify .github/workflows/test-unit.yml installs fish and zsh before running pytest."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "test-unit.yml"
    raw_content = read(workflow_path)
    assert "apt-get" not in raw_content, "test-unit.yml must use apt, never apt-get"

    workflow = yaml.safe_load(raw_content)
    steps: list[dict[str, Any]] = workflow["jobs"]["test-unit"]["steps"]
    runs = [s.get("run", "") for s in steps]

    ubuntu_idx = next(
        (i for i, r in enumerate(runs) if "sudo apt update && sudo apt install -y fish zsh" in r),
        -1,
    )
    macos_idx = next((i for i, r in enumerate(runs) if "brew install fish" in r), -1)
    pytest_idx = next((i for i, r in enumerate(runs) if "pytest" in r), -1)

    assert ubuntu_idx != -1, "test-unit.yml must install fish and zsh on Ubuntu via apt"
    assert macos_idx != -1, "test-unit.yml must install fish on macOS via brew"
    assert pytest_idx != -1, "test-unit.yml must run pytest"
    assert ubuntu_idx < pytest_idx and macos_idx < pytest_idx, (
        "Shell installation steps in test-unit.yml must run before pytest"
    )


def test_fish_syntax_check() -> None:
    """Verify fish -n passes with zero warnings/errors on config.fish and 00-devenv.fish."""
    fish_bin = _require_shell("fish")
    targets = [
        REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "config.fish",
        REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish",
    ]
    for target in targets:
        proc = subprocess.run(
            [fish_bin, "-n", str(target)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, f"fish -n failed on {target}: {proc.stderr}"
        assert proc.stderr.strip() == "", f"fish -n emitted warnings on {target}: {proc.stderr}"


@pytest.mark.parametrize(
    ("shell_name", "flags", "probe_script"),
    [
        (
            "bash",
            "-lic",
            (
                'echo "SHLVL=${CONDA_SHLVL:-}"; '
                'echo "ENV=${CONDA_DEFAULT_ENV:-}"; '
                'echo "TYPE=$(type -t conda)"; '
                'echo "PIPX_PATH=$(command -v pipx)"; '
                'echo "PIPX_OUT=$(pipx)"; '
                'echo "NODE_PATH=$(command -v node)"; '
                'echo "NODE_OUT=$(node)"'
            ),
        ),
        (
            "zsh",
            "-lic",
            (
                'echo "SHLVL=${CONDA_SHLVL:-}"; '
                'echo "ENV=${CONDA_DEFAULT_ENV:-}"; '
                'echo "TYPE=$(whence -w conda)"; '
                'echo "PIPX_PATH=$(command -v pipx)"; '
                'echo "PIPX_OUT=$(pipx)"; '
                'echo "NODE_PATH=$(command -v node)"; '
                'echo "NODE_OUT=$(node)"'
            ),
        ),
        (
            "zsh",
            "-lc",
            (
                'echo "SHLVL=${CONDA_SHLVL:-}"; '
                'echo "ENV=${CONDA_DEFAULT_ENV:-}"; '
                'echo "TYPE=$(whence -w conda)"; '
                'echo "PIPX_PATH=$(command -v pipx)"; '
                'echo "PIPX_OUT=$(pipx)"; '
                'echo "NODE_PATH=$(command -v node)"; '
                'echo "NODE_OUT=$(node)"'
            ),
        ),
        (
            "fish",
            "-lc",
            (
                'echo "SHLVL=$CONDA_SHLVL"; '
                'echo "ENV=$CONDA_DEFAULT_ENV"; '
                'echo "TYPE="(type -t conda); '
                'echo "PIPX_PATH="(command -s pipx); '
                'echo "PIPX_OUT="(pipx); '
                'echo "NODE_PATH="(command -s node); '
                'echo "NODE_OUT="(node)'
            ),
        ),
        (
            "fish",
            "-ic",
            (
                'echo "SHLVL=$CONDA_SHLVL"; '
                'echo "ENV=$CONDA_DEFAULT_ENV"; '
                'echo "TYPE="(type -t conda); '
                'echo "PIPX_PATH="(command -s pipx); '
                'echo "PIPX_OUT="(pipx); '
                'echo "NODE_PATH="(command -s node); '
                'echo "NODE_OUT="(node)'
            ),
        ),
    ],
)
def test_clean_env_runtime_conda_activation_and_nvm_precedence(
    tmp_path: Path,
    shell_name: str,
    flags: str,
    probe_script: str,
) -> None:
    """Run real clean-env (env -i) shells reproducing Homebrew conda symlink masking and NVM precedence."""
    shell_bin = _require_shell(shell_name)
    shell_dir = str(Path(shell_bin).resolve().parent)
    fake_home, fake_brew_bin = _build_hermetic_conda_and_nvm_home(tmp_path)

    initial_path = f"{fake_brew_bin}:{shell_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
    env_args = [
        "env",
        "-i",
        f"HOME={fake_home}",
        f"ZDOTDIR={fake_home}",
        "USER=testuser",
        "TERM=dumb",
        f"PATH={initial_path}",
        shell_bin,
        flags,
        probe_script,
    ]
    proc = subprocess.run(env_args, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, (
        f"{shell_name} {flags} exited {proc.returncode}.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )

    kv: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()

    assert kv.get("SHLVL") == "1", f"{shell_name} {flags} did not activate Conda (SHLVL): {proc.stdout}"
    assert kv.get("ENV") == "base", f"{shell_name} {flags} did not set CONDA_DEFAULT_ENV=base: {proc.stdout}"
    assert "function" in kv.get("TYPE", ""), (
        f"{shell_name} {flags} left conda as a binary instead of a shell function: {proc.stdout}"
    )
    assert kv.get("PIPX_PATH") == str(fake_home / "miniforge3" / "bin" / "pipx"), (
        f"{shell_name} {flags} did not expose miniforge3/bin/pipx on PATH: {proc.stdout}"
    )
    assert kv.get("PIPX_OUT") == "pipx-from-miniforge3"
    assert kv.get("NODE_PATH") in {
        str(fake_home / ".local" / "share" / "nvm" / "current" / "bin" / "node"),
        str(fake_home / ".local" / "bin" / "node"),
    }, f"{shell_name} {flags} did not resolve node to NVM ahead of Conda base/bin: {proc.stdout}"
    assert kv.get("NODE_OUT") == "v26.13.1-nvm"


@pytest.mark.parametrize(
    ("shell_name", "flags", "probe_script"),
    [
        (
            "bash",
            "-lic",
            'echo "ENV=${CONDA_DEFAULT_ENV:-}"; echo "TYPE=$(type -t conda)"',
        ),
        (
            "zsh",
            "-lic",
            'echo "ENV=${CONDA_DEFAULT_ENV:-}"; echo "TYPE=$(whence -w conda)"',
        ),
        (
            "fish",
            "-lc",
            'echo "ENV=$CONDA_DEFAULT_ENV"; echo "TYPE="(type -t conda)',
        ),
    ],
)
def test_clean_env_runtime_micromamba_fallback(
    tmp_path: Path,
    shell_name: str,
    flags: str,
    probe_script: str,
) -> None:
    """Verify micromamba shell hook and conda alias activate when no conda root binary is present."""
    shell_bin = _require_shell(shell_name)
    shell_dir = str(Path(shell_bin).resolve().parent)

    fake_home = tmp_path / "mamba_home"
    _link_repo_dotfiles(fake_home)
    mamba_root = fake_home / ".local" / "share" / "mamba"
    mamba_root.mkdir(parents=True, exist_ok=True)

    fake_bin = fake_home / ".local" / "bin"
    micromamba_script = f"""#!/bin/sh
if [ "$1" = "shell" ] && [ "$2" = "hook" ]; then
    if [ "$4" = "fish" ]; then
        cat <<'EOF'
set -gx CONDA_DEFAULT_ENV base
set -gx PATH "{mamba_root}/bin" $PATH
EOF
        exit 0
    else
        cat <<'EOF'
export CONDA_DEFAULT_ENV=base
export PATH="{mamba_root}/bin:$PATH"
EOF
        exit 0
    fi
fi
"""
    _write_executable(fake_bin / "micromamba", micromamba_script)

    initial_path = f"{fake_bin}:{shell_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
    env_args = [
        "env",
        "-i",
        f"HOME={fake_home}",
        f"ZDOTDIR={fake_home}",
        "USER=testuser",
        "TERM=dumb",
        f"PATH={initial_path}",
        shell_bin,
        flags,
        probe_script,
    ]
    proc = subprocess.run(env_args, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, (
        f"{shell_name} {flags} micromamba fallback failed.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )

    kv: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()

    assert kv.get("ENV") == "base", f"{shell_name} {flags} did not run micromamba shell hook: {proc.stdout}"
    assert any(token in kv.get("TYPE", "") for token in ("alias", "function")), (
        f"{shell_name} {flags} did not define conda alias/function for micromamba: {proc.stdout}"
    )

"""Unit tests for the Jinja the roles actually run.

Expressions are read out of the role YAML instead of being copied into this
file, so editing a role invalidates the test that covers it -- which is the
point. They are then evaluated with ansible-core's own templating engine, so
custom filters (extract, regex_replace, select('match'), map('split')) behave
exactly as they will during a converge.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import textwrap
import urllib.request
from pathlib import Path

import pytest
import yaml
from ansible.errors import AnsibleUndefinedVariable

from .conftest import REPO_ROOT, read

pytestmark = pytest.mark.templating


def task(role: str, name_fragment: str) -> dict:
    """Find a task inside a role by a fragment of its name."""
    path = REPO_ROOT / "ansible" / "roles" / role / "tasks" / "main.yml"
    for task_def in yaml.safe_load(read(path)):
        if name_fragment in task_def.get("name", ""):
            return task_def
    raise AssertionError(f"no task matching {name_fragment!r} in roles/{role}")


def playbook_task(playbook: str, name_fragment: str) -> dict:
    """Find a task inside a playbook by a fragment of its name."""
    path = REPO_ROOT / "ansible" / "playbooks" / playbook
    for play in yaml.safe_load(read(path)):
        for task_def in play.get("tasks", []):
            if name_fragment in task_def.get("name", ""):
                return task_def
    raise AssertionError(f"no task matching {name_fragment!r} in playbooks/{playbook}")


def set_fact_expression(role: str, name_fragment: str, key: str) -> str:
    fact_key = f"ansible.builtin.set_fact.{key}"
    found = task(role, name_fragment)
    try:
        return found["ansible.builtin.set_fact"][key]
    except KeyError:  # pragma: no cover - guards against refactors
        raise AssertionError(f"{role}: task {name_fragment!r} does not set_fact {key!r} ({fact_key})")


def stow_packages_expr() -> str:
    return set_fact_expression("bootstrap", "Resolve active stow packages", "devenv_stow_packages")


def wanted_expr() -> str:
    return set_fact_expression("bootstrap", "Build the wanted list", "devenv_packages_wanted")


def concrete_expr() -> str:
    return set_fact_expression("bootstrap", "Resolve logical names", "devenv_packages_concrete")


def node_pin_expr() -> str:
    return set_fact_expression("node", "Parse the pin", "devenv_node_version")


def nvim_brew_expr() -> str:
    return set_fact_expression("neovim", "Record Homebrew location", "devenv_brew_bin")


def nvim_asset_expr() -> str:
    return "nvim-{{ devenv_neovim_asset_os[devenv_system] }}-{{ devenv_neovim_asset_arch[devenv_system][devenv_arch] }}.tar.gz"


def test_wanted_list_drops_os_provided_packages(templar, group_vars):
    result = templar(
        wanted_expr(),
        {
            "devenv_packages_core": ["git", "unzip", "fzf"],
            "devenv_packages_extra": ["cURL"],
            "devenv_pkg_skip": ["unzip"],
        },
    )
    assert result == sorted(["cURL", "fzf", "git"])


def test_wanted_list_drops_linux_skipped_packages(templar, group_vars):
    """devenv_pkg_skip on Linux drops both neovim and go from wanted list."""
    result = templar(
        wanted_expr(),
        {
            "devenv_packages_core": ["git", "neovim", "go", "tmux"],
            "devenv_packages_extra": [],
            "devenv_pkg_skip": ["neovim", "go"],
        },
    )
    assert result == sorted(["git", "tmux"])


def test_wanted_list_survives_a_missing_skip_table(templar):
    """os_Linux.yml has devenv_pkg_skip, but the default([]) keeps it optional."""
    result = templar(
        wanted_expr(),
        {"devenv_packages_core": ["git"], "devenv_packages_extra": ["jq"]},
    )
    assert result == ["git", "jq"]


@pytest.mark.parametrize("backend", ["brew", "apt"])
def test_logical_names_resolve_on_every_backend(templar, group_vars, alias_tables, backend):
    wanted = [
        pkg
        for pkg in (group_vars["devenv_packages_core"] + group_vars["devenv_packages_extra"])
        if pkg in alias_tables[backend]
    ]
    variables = {
        "devenv_packages_wanted": wanted,
        "devenv_pkg_aliases": alias_tables[backend],
    }
    result = templar(concrete_expr(), variables)
    assert None not in result, f"{backend}: unresolved logical package"
    assert all(isinstance(name, str) and name for name in result)
    assert len(result) == len(set(result)), f"{backend}: two logical names collapsed onto one package"
    assert result == sorted(result)


def test_missing_alias_is_caught_by_the_guard_and_is_loud(templar, group_vars, alias_tables):
    """A missing alias must fail the pre-flight assert, then explode if bypassed.

    `extract` yields undefined for an unknown key, so the resolve task would
    carry a hole into `brew install`/`apt install` were the guard not there.
    """
    guard = task("bootstrap", "Fail when a logical package has no alias")["ansible.builtin.assert"]["that"][1]
    complete = {"devenv_packages_wanted": list(group_vars["devenv_packages_core"]),
                "devenv_pkg_aliases": alias_tables["apt"]}
    assert templar(guard, complete) is True

    broken_aliases = dict(alias_tables["apt"])
    dropped = broken_aliases.pop("fzf")
    broken = {"devenv_packages_wanted": list(group_vars["devenv_packages_core"]),
              "devenv_pkg_aliases": broken_aliases}
    assert templar(guard, broken) is False
    with pytest.raises(AnsibleUndefinedVariable):
        templar(concrete_expr(), broken)
    assert dropped == "fzf"


@pytest.mark.parametrize("backend", ["brew", "apt"])
def test_backend_guard_admits_only_configured_backends(templar, group_vars, backend):
    fail_when = task("bootstrap", "Fail early on an unsupported package backend")["when"]
    assert templar(fail_when, {"devenv_pkg_backend": backend,
                               "devenv_supported_backends": group_vars["devenv_supported_backends"]}) is False


@pytest.mark.parametrize("backend", ["dnf", "pacman", "port", "zypper", "unsupported"])
def test_backend_guard_rejects_the_rest(templar, group_vars, backend):
    fail_when = task("bootstrap", "Fail early on an unsupported package backend")["when"]
    assert templar(fail_when, {"devenv_pkg_backend": backend,
                               "devenv_supported_backends": group_vars["devenv_supported_backends"]}) is True


def test_node_pin_is_parsed_from_the_real_fish_config(templar):
    """The node pin is parsed from versions.json."""
    text = read(REPO_ROOT / "versions.json")
    rendered = templar(node_pin_expr(), {"devenv_versions_raw": {"content": base64.b64encode(text.encode())}})
    expected = json.loads(text)["node"]
    assert rendered == expected
    assert "\n" not in rendered and " " not in rendered, f"pin parse leaked surrounding text: {rendered!r}"


def test_node_pin_parse_fails_loudly_when_the_line_moves(templar):
    """If versions.json lacks a node pin, the role must assert rather than install ''."""
    rendered = templar(node_pin_expr(), {"devenv_versions_raw": {"content": base64.b64encode(b"{}")}})
    guard = task("node", "Assert a node pin was found")["ansible.builtin.assert"]["that"][0]
    assert templar(guard, {"devenv_node_version": rendered}) is False


def test_neovim_brew_lookup_resolution(templar):
    """Neovim role resolves Homebrew binary location when devenv_brew_bin is unset."""
    expr = nvim_brew_expr()
    missing = {"devenv_brew_stat": {"results": [{"stat": {"exists": False}, "item": "/opt/homebrew/bin/brew"}]}}
    assert templar(expr, missing) == ""
    found = {
        "devenv_brew_stat": {
            "results": [
                {"stat": {"exists": False}, "item": "/nope/brew"},
                {"stat": {"exists": True}, "item": "/home/linuxbrew/.linuxbrew/bin/brew"},
            ]
        }
    }
    assert templar(expr, found) == "/home/linuxbrew/.linuxbrew/bin/brew"


def test_neovim_homebrew_install_task_properties(templar):
    """Neovim install task uses community.general.homebrew conditioned on devenv_neovim_source: brew."""
    neovim_install = task("neovim", "Install Neovim via Homebrew")
    assert neovim_install["community.general.homebrew"]["name"] == "neovim"
    assert neovim_install["community.general.homebrew"]["state"] == "present"
    condition = neovim_install["when"]
    assert templar(condition, {"devenv_neovim_source": "brew"}) is True
    assert templar(condition, {"devenv_neovim_source": "github"}) is False


def test_packages_homebrew_go_install_task_properties(templar):
    """Packages role installs go via community.general.homebrew on Linux."""
    go_install = task("packages", "Install Go via Homebrew on Linux")
    assert go_install["community.general.homebrew"]["name"] == "go"
    assert go_install["community.general.homebrew"]["state"] == "present"
    conditions = go_install["when"]
    assert isinstance(conditions, list)

    def eval_when(vars_dict: dict) -> bool:
        return all(bool(templar(cond, vars_dict)) for cond in conditions)

    assert eval_when({"devenv_system": "Linux", "devenv_brew_bin": "/home/linuxbrew/.linuxbrew/bin/brew"}) is True
    assert eval_when({"devenv_system": "Darwin", "devenv_brew_bin": "/opt/homebrew/bin/brew"}) is False
    assert eval_when({"devenv_system": "Linux", "devenv_brew_bin": ""}) is False


@pytest.mark.parametrize(
    ("system", "arch", "expected"),
    [
        ("Darwin", "arm64", "nvim-macos-arm64.tar.gz"),
        ("Darwin", "x86_64", "nvim-macos-x86_64.tar.gz"),
        ("Linux", "x86_64", "nvim-linux-x86_64.tar.gz"),
        ("Linux", "aarch64", "nvim-linux-arm64.tar.gz"),
    ],
)
def test_neovim_release_asset_matches_platform(templar, group_vars, system, arch, expected):
    variables = {
        "devenv_system": system,
        "devenv_arch": arch,
        "devenv_neovim_asset_os": group_vars["devenv_neovim_asset_os"],
        "devenv_neovim_asset_arch": group_vars["devenv_neovim_asset_arch"],
    }
    assert templar(nvim_asset_expr(), variables) == expected


def test_brew_lookup_yields_empty_string_when_absent(templar):
    """The `+ ['']` tail is what lets the role's assert produce a clean failure."""
    expr = set_fact_expression("homebrew", "Record Homebrew location", "devenv_brew_bin")
    missing = {"devenv_brew_stat": {"results": [{"stat": {"exists": False}, "item": "/opt/homebrew/bin/brew"}]}}
    assert templar(expr, missing) == ""
    found = {
        "devenv_brew_stat": {
            "results": [
                {"stat": {"exists": False}, "item": "/nope/brew"},
                {"stat": {"exists": True}, "item": "/opt/homebrew/bin/brew"},
            ]
        }
    }
    assert templar(expr, found) == "/opt/homebrew/bin/brew"


def test_fish_binary_lookup_prefers_the_first_existing_path(templar):
    expr = set_fact_expression("fish", "Record the fish binary", "devenv_fish_bin")
    variables = {
        "devenv_fish_stat": {
            "results": [
                {"stat": {"exists": False}, "item": "/opt/homebrew/bin/fish"},
                {"stat": {"exists": True}, "item": "/usr/local/bin/fish"},
                {"stat": {"exists": True}, "item": "/usr/bin/fish"},
            ]
        }
    }
    assert templar(expr, variables) == "/usr/local/bin/fish"


def test_chsh_only_runs_when_the_shell_actually_changes(templar):
    """changed_when must not fire on every converge (idempotence requirement)."""
    chsh = task("fish", "Set fish as the login shell")
    condition = next(c for c in chsh["when"] if "SHELL" in c)
    same = templar(condition, {"ansible_facts": {"env": {"SHELL": "/usr/bin/fish"}}, "devenv_fish_bin": "/usr/bin/fish"})
    different = templar(condition, {"ansible_facts": {"env": {"SHELL": "/bin/zsh"}}, "devenv_fish_bin": "/usr/bin/fish"})
    assert same is False and different is True


def test_conda_dir_is_stable_across_platforms(templar, group_vars):
    rendered = templar(group_vars["devenv_conda_dir"], {"devenv_home": "/Users/anyone"})
    assert rendered == "/Users/anyone/miniforge3"
    assert templar(group_vars["devenv_conda_dir"], {"devenv_home": "/home/dev"}) == "/home/dev/miniforge3"


@pytest.mark.network
@pytest.mark.parametrize(
    ("system", "arch"),
    [("Darwin", "arm64"), ("Darwin", "x86_64"), ("Linux", "x86_64"), ("Linux", "aarch64")],
)
@pytest.mark.skipif(os.environ.get("DEVENV_NETWORK_TESTS") != "1", reason="set DEVENV_NETWORK_TESTS=1 (CI sets it)")
def test_miniforge_installer_names_exist_upstream(group_vars, system, arch):
    """Opt-in network check that the computed asset names are real (run in CI)."""
    os_name = group_vars["devenv_miniforge_asset_os"][system]
    arch_name = group_vars["devenv_miniforge_asset_arch"][system][arch]
    name = f"Miniforge3-{os_name}-{arch_name}.sh"
    url = f"https://github.com/conda-forge/miniforge/releases/latest/download/{name}"
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310 - fixed upstream host
        assert response.status == 200, f"{url} -> {response.status}"


def test_dotfiles_symlink_assertion_expression(templar):
    expr = task("dotfiles", "Assert the link manifest is fully satisfied")["ansible.builtin.assert"]["that"][1]
    repo_root_str = str(REPO_ROOT)
    vars_inside_abs = {
        "devenv_repo_root": repo_root_str,
        "item": {
            "stat": {"lnk_source": f"{repo_root_str}/dotfiles/tmux"},
            "item": {"dest": "/mock/dest"},
        },
    }
    assert templar(expr, vars_inside_abs) is True

    vars_inside_rel = {
        "devenv_repo_root": repo_root_str,
        "item": {
            "stat": {"lnk_source": "../tmux"},
            "item": {"dest": f"{repo_root_str}/dotfiles/other/dest"},
        },
    }
    assert templar(expr, vars_inside_rel) is True

    vars_outside_abs = {
        "devenv_repo_root": repo_root_str,
        "item": {
            "stat": {"lnk_source": "/etc/passwd"},
            "item": {"dest": "/mock/dest"},
        },
    }
    assert templar(expr, vars_outside_abs) is False

    vars_outside_rel = {
        "devenv_repo_root": repo_root_str,
        "item": {
            "stat": {"lnk_source": "../../../etc/passwd"},
            "item": {"dest": "/tmp/mock/dest"},
        },
    }
    assert templar(expr, vars_outside_rel) is False


def test_unlink_symlink_assertion_expression(templar):
    expr = playbook_task("unlink.yml", "Refuse to remove anything that is not our symlink")["ansible.builtin.assert"][
        "that"
    ][1]
    repo_root_str = str(REPO_ROOT)
    vars_inside_abs = {
        "devenv_repo_root": repo_root_str,
        "item": {
            "stat": {"lnk_source": f"{repo_root_str}/dotfiles/fish"},
            "item": {"dest": "/mock/dest"},
        },
    }
    assert templar(expr, vars_inside_abs) is True

    vars_inside_rel = {
        "devenv_repo_root": repo_root_str,
        "item": {
            "stat": {"lnk_source": "../fish"},
            "item": {"dest": f"{repo_root_str}/dotfiles/other/dest"},
        },
    }
    assert templar(expr, vars_inside_rel) is True

    vars_outside_abs = {
        "devenv_repo_root": repo_root_str,
        "item": {
            "stat": {"lnk_source": "/var/log"},
            "item": {"dest": "/mock/dest"},
        },
    }
    assert templar(expr, vars_outside_abs) is False

    vars_outside_rel = {
        "devenv_repo_root": repo_root_str,
        "item": {
            "stat": {"lnk_source": "../../var/log"},
            "item": {"dest": "/tmp/mock/dest"},
        },
    }
    assert templar(expr, vars_outside_rel) is False


# --- stale ~/.config/dev-env/choices.yml must not drop new repo stow packages ---

STALE_CHOICE_PACKAGES = ["bash", "conda", "fish", "nvim-kickstart", "tmux", "zsh"]
NVIM_VARIANT_PACKAGES = {"kickstart": "nvim-kickstart", "minimal": "nvim-minimal", "lazyvim": "nvim-lazyvim"}


def link_packages(links: list[dict]) -> set[str]:
    return {link["src"].split("/")[1] for link in links}


@pytest.mark.parametrize("variant", sorted(NVIM_VARIANT_PACKAGES))
def test_stow_packages_merges_repo_defaults_with_stale_choices(templar, group_vars, variant):
    repo_packages = group_vars["devenv_stow_packages"]
    assert "ghostty" in repo_packages and "ghostty" not in STALE_CHOICE_PACKAGES
    active = NVIM_VARIANT_PACKAGES[variant]
    result = templar(
        stow_packages_expr(),
        {
            "devenv_repo_stow_packages": repo_packages,
            "devenv_stow_packages": STALE_CHOICE_PACKAGES,
            "devenv_selected_variants": {"nvim": variant},
            "devenv_active_nvim_variant": variant,
            "devenv_inactive_packages": sorted(set(NVIM_VARIANT_PACKAGES.values()) - {active}),
        },
    )
    assert "ghostty" in result
    assert active in result
    assert not (set(NVIM_VARIANT_PACKAGES.values()) - {active}) & set(result)
    assert set(repo_packages) - set(NVIM_VARIANT_PACKAGES.values()) <= set(result)
    assert result == sorted(set(result))


def test_stow_packages_falls_back_without_repo_snapshot(templar):
    """An undefined snapshot degrades to the loaded list instead of erroring."""
    result = templar(
        stow_packages_expr(),
        {
            "devenv_stow_packages": ["zsh", "nvim-kickstart", "bash"],
            "devenv_active_nvim_variant": "minimal",
            "devenv_inactive_packages": ["nvim-kickstart", "nvim-lazyvim"],
        },
    )
    assert result == ["bash", "nvim-minimal", "zsh"]


def test_bootstrap_snapshots_stow_packages_before_loading_choices():
    names = [t.get("name", "") for t in yaml.safe_load(read(REPO_ROOT / "ansible/roles/bootstrap/tasks/main.yml"))]
    snapshot = names.index("Snapshot repository default stow packages")
    assert snapshot < names.index("Load choices.yml if present") < names.index("Resolve active stow packages")
    assert task("bootstrap", "Snapshot repository default")["ansible.builtin.set_fact"] == {
        "devenv_repo_stow_packages": "{{ devenv_stow_packages }}"
    }


def test_dotfiles_stow_coverage_assertion_catches_missing_packages(templar, link_manifest):
    expr = task("dotfiles", "Assert stow packages cover all active link manifest packages")["ansible.builtin.assert"][
        "that"
    ][0]
    links = [{"src": link["src"], "dest": link["dest"]} for link in link_manifest]
    assert templar(expr, {"devenv_links": links, "devenv_stow_packages": sorted(link_packages(links))}) is True
    assert templar(expr, {"devenv_links": links, "devenv_stow_packages": STALE_CHOICE_PACKAGES}) is False


@pytest.mark.parametrize("snapshot", [True, False])
def test_unlink_collects_repo_and_manifest_packages_despite_stale_choices(templar, group_vars, link_manifest, snapshot):
    expr = playbook_task("unlink.yml", "Collect all stow packages to unlink")["ansible.builtin.set_fact"][
        "devenv_all_stow_packages"
    ]
    links = [{"src": link["src"], "dest": link["dest"]} for link in link_manifest]
    variables = {"devenv_links": links, "devenv_stow_packages": STALE_CHOICE_PACKAGES}
    if snapshot:
        variables["devenv_repo_stow_packages"] = group_vars["devenv_stow_packages"]
    result = templar(expr, variables)
    assert "ghostty" in result
    assert link_packages(links) | set(NVIM_VARIANT_PACKAGES.values()) | set(STALE_CHOICE_PACKAGES) <= set(result)
    if snapshot:
        assert set(group_vars["devenv_stow_packages"]) <= set(result)
    assert result == sorted(set(result))


def test_unlink_snapshots_stow_packages_before_loading_choices():
    names = [t.get("name", "") for t in yaml.safe_load(read(REPO_ROOT / "ansible/playbooks/unlink.yml"))[0]["tasks"]]
    snapshot = names.index("Snapshot repository default stow packages")
    assert names.index("Load the manifest") < snapshot < names.index("Load user choices if present")
    assert playbook_task("unlink.yml", "Snapshot repository default")["ansible.builtin.set_fact"] == {
        "devenv_repo_stow_packages": "{{ devenv_stow_packages }}"
    }


def test_bootstrap_covers_every_manifest_package(templar, link_manifest):
    expr = set_fact_expression("bootstrap", "Cover every package referenced", "devenv_stow_packages")
    links = [{"src": link["src"], "dest": link["dest"]} for link in link_manifest]
    result = templar(expr, {"devenv_links": links, "devenv_stow_packages": STALE_CHOICE_PACKAGES})
    assert result == sorted(set(STALE_CHOICE_PACKAGES) | link_packages(links))


def test_dotfiles_omits_packages_whose_links_are_all_skipped(templar, link_manifest):
    expr = set_fact_expression("dotfiles", "Omit stow packages where all links", "devenv_stow_packages")
    links = [link for link in link_manifest if not link["src"].startswith("dotfiles/bash/")]
    result = templar(expr, {"devenv_links": links, "devenv_stow_packages": ["bash", "ghostty", "zsh"]})
    assert sorted(result) == ["ghostty", "zsh"]  # intersect order is hash-dependent


def test_dotfiles_stow_ignore_options_name_skipped_files(templar):
    expr = set_fact_expression("dotfiles", "Determine ignore arguments", "devenv_stow_ignore_opts")
    result = templar(expr, {"devenv_skip_links": ["/home/u/.bashrc", "/home/u/.config/fish/config.fish"]})
    assert result == '--ignore="^\\.bashrc$" --ignore="^config\\.fish$"'


@pytest.mark.parametrize(
    ("facts", "expected"),
    [
        (
            {"system": "Linux", "kernel": "5.15.153.1-microsoft-standard-WSL2", "env": {}},
            True,
        ),
        (
            {"system": "Linux", "kernel": "4.4.0-19041-Microsoft", "env": {}},
            True,
        ),
        (
            {"system": "Linux", "kernel": "6.6.0-custom", "env": {"WSL_DISTRO_NAME": "Ubuntu"}},
            True,
        ),
        (
            {"system": "Linux", "kernel": "6.6.0-custom", "env": {"WSL_INTEROP": "/run/WSL/12_interop"}},
            True,
        ),
        (
            {"system": "Linux", "kernel": "6.8.0-45-generic", "env": {}},
            False,
        ),
        (
            {"system": "Darwin", "kernel": "23.6.0", "env": {"WSL_DISTRO_NAME": "Ubuntu"}},
            False,
        ),
    ],
)
def test_bootstrap_devenv_is_wsl_classification(templar, facts: dict, expected: bool) -> None:
    """devenv_is_wsl evaluates True on WSL kernels/env vars and False on native Linux or macOS."""
    expr = set_fact_expression("bootstrap", "Classify host platform", "devenv_is_wsl")
    assert bool(templar(expr, {"ansible_facts": facts})) is expected


def test_packages_wsl_guards_and_winget_conditions(templar) -> None:
    """Linux GUI terminal tasks skip on WSL, while winget.exe tasks run only on WSL when GUI apps are enabled."""
    linux_probe = task("packages", "Probe Warp terminal binary")
    linux_when = linux_probe["when"]
    assert all(
        bool(templar(cond, {"devenv_pkg_backend": "apt", "devenv_install_gui_casks": True, "devenv_is_wsl": False}))
        for cond in linux_when
    )
    assert not all(
        bool(templar(cond, {"devenv_pkg_backend": "apt", "devenv_install_gui_casks": True, "devenv_is_wsl": True}))
        for cond in linux_when
    )

    winget_install = task("packages", "Install Warp on Windows host via winget.exe from WSL")
    winget_when = winget_install["when"]
    base_wsl_vars = {
        "devenv_is_wsl": True,
        "devenv_install_gui_casks": True,
        "devenv_wsl_winget_which": {"rc": 0, "stdout": "/mnt/c/Users/dev/AppData/Local/Microsoft/WindowsApps/winget.exe"},
        "devenv_wsl_warp_probe": {"rc": 1, "stdout": "No installed package found matching input criteria."},
    }
    assert all(bool(templar(cond, base_wsl_vars)) for cond in winget_when)
    assert not all(bool(templar(cond, {**base_wsl_vars, "devenv_is_wsl": False})) for cond in winget_when)
    assert not all(
        bool(templar(cond, {**base_wsl_vars, "devenv_wsl_warp_probe": {"rc": 0, "stdout": "Warp  Warp.Warp  v0.2025"}}))
        for cond in winget_when
    )


def test_playbooks_syntax_check_zero_deprecation_warnings(tmp_path: Path) -> None:
    """ansible-playbook --syntax-check passes with zero deprecation warnings on site.yml and unlink.yml."""
    playbook = ansible_playbook_bin()
    if playbook is None:
        pytest.skip("ansible-playbook not available in this environment")
    env = {
        **os.environ,
        "ANSIBLE_CONFIG": str(REPO_ROOT / "ansible.cfg"),
        "ANSIBLE_COLLECTIONS_PATH": collections_path(tmp_path / "collections-syntax"),
        "ANSIBLE_DEPRECATION_WARNINGS": "True",
        "ANSIBLE_FORCE_COLOR": "0",
        "ANSIBLE_NOCOLOR": "1",
    }
    for rel_playbook in ("ansible/site.yml", "ansible/playbooks/unlink.yml"):
        proc = subprocess.run(
            [playbook, str(REPO_ROOT / rel_playbook), "--syntax-check"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert proc.returncode == 0, f"{rel_playbook} syntax check failed:\n{proc.stdout}\n{proc.stderr}"
        assert "[DEPRECATION WARNING]" not in proc.stderr, (
            f"{rel_playbook} emitted deprecation warning:\n{proc.stderr}"
        )


# --- real ansible-playbook runs against an isolated $HOME -------------------

# Records every fact set during the run so tests can inspect what the roles
# actually resolved, without depending on callback plugins outside ansible-core.
FACTS_CALLBACK = textwrap.dedent(
    """
    import json
    import os

    from ansible.plugins.callback import CallbackBase


    class CallbackModule(CallbackBase):
        CALLBACK_VERSION = 2.0
        CALLBACK_TYPE = "aggregate"
        CALLBACK_NAME = "devenv_facts_dump"
        CALLBACK_NEEDS_ENABLED = True

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.facts = {}

        def v2_runner_on_ok(self, result):
            self.facts.update(result._result.get("ansible_facts", {}))

        def v2_playbook_on_stats(self, stats):
            with open(os.environ["DEVENV_FACTS_DUMP"], "w") as handle:
                json.dump(self.facts, handle, default=str)
    """
)


def ansible_playbook_bin() -> str | None:
    local = Path(sys.executable).parent / "ansible-playbook"
    return str(local) if local.is_file() else shutil.which("ansible-playbook")


def collections_path(scratch: Path) -> str:
    """Real collection paths, plus a fail-loud community.general stub as last resort.

    site.yml references community.general modules in roles that the tag filters
    below never execute, but ansible-playbook still resolves them at parse time.
    """
    real_home = Path.home()
    paths = [str(real_home / ".local/share/dev-env/collections"), str(real_home / ".ansible/collections")]
    modules = scratch / "ansible_collections" / "community" / "general" / "plugins" / "modules"
    modules.mkdir(parents=True)
    for name in ("homebrew", "homebrew_cask", "homebrew_tap"):
        (modules / f"{name}.py").write_text(
            "#!/usr/bin/python\nimport json\nprint(json.dumps({'failed': True, 'msg': 'community.general stub'}))\n"
        )
    return os.pathsep.join([*paths, str(scratch)])


def seed_stale_choices(home: Path, choices: dict) -> None:
    target = home / ".config" / "dev-env" / "choices.yml"
    target.parent.mkdir(parents=True)
    target.write_text(yaml.safe_dump(choices))


def run_site(tmp_path: Path, home: Path, tags: str, *extra: str) -> tuple[subprocess.CompletedProcess, dict]:
    playbook = ansible_playbook_bin()
    if playbook is None:
        pytest.skip("ansible-playbook not available in this environment")
    plugins = tmp_path / "callback_plugins"
    plugins.mkdir(exist_ok=True)
    (plugins / "devenv_facts_dump.py").write_text(FACTS_CALLBACK)
    facts_file = tmp_path / f"facts-{tags.replace(',', '-')}.json"
    env = {
        **os.environ,
        "HOME": str(home),
        "ANSIBLE_CONFIG": str(REPO_ROOT / "ansible.cfg"),
        "ANSIBLE_COLLECTIONS_PATH": collections_path(tmp_path / f"collections-{tags.replace(',', '-')}"),
        "ANSIBLE_CALLBACK_PLUGINS": str(plugins),
        "ANSIBLE_CALLBACKS_ENABLED": "devenv_facts_dump",
        "ANSIBLE_FORCE_COLOR": "0",
        "ANSIBLE_NOCOLOR": "1",
        "DEVENV_FACTS_DUMP": str(facts_file),
    }
    cmd = [playbook, str(REPO_ROOT / "ansible" / "site.yml"), "--tags", tags, "-e", f"devenv_home={home}", *extra]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=600, check=False)
    facts = json.loads(facts_file.read_text()) if facts_file.exists() else {}
    return proc, facts


@pytest.mark.parametrize(
    ("variant", "skip_basename"),
    [("minimal", None), ("kickstart", ".bashrc")],
)
def test_ansible_bootstrap_resolves_stow_packages_with_stale_choices(tmp_path, variant, skip_basename):
    home = tmp_path / "home"
    other_variant = "nvim-kickstart" if variant == "minimal" else "nvim-minimal"
    choices = {
        "devenv_selected_variants": {"nvim": variant},
        # Stale: written before ghostty existed, and still naming the other variant.
        "devenv_stow_packages": ["bash", "conda", "fish", other_variant, "tmux", "zsh"],
    }
    skipped = str(home / skip_basename) if skip_basename else None
    if skipped:
        choices["devenv_skip_links"] = [skipped]
    seed_stale_choices(home, choices)

    proc, facts = run_site(tmp_path, home, "bootstrap", "--check")
    assert proc.returncode == 0, proc.stdout + proc.stderr

    packages = facts["devenv_stow_packages"]
    links = facts["devenv_links"]
    assert "ghostty" in packages
    assert NVIM_VARIANT_PACKAGES[variant] in packages
    assert not (set(NVIM_VARIANT_PACKAGES.values()) - {NVIM_VARIANT_PACKAGES[variant]}) & set(packages)
    assert link_packages(links) <= set(packages)
    assert any(link["dest"] == str(home / ".config/ghostty/config.ghostty") for link in links)
    assert set(packages) <= {p.name for p in (REPO_ROOT / "dotfiles").iterdir() if p.is_dir()}
    if skipped:
        assert skipped not in {link["dest"] for link in links}
        assert "bash" in packages  # .bash_profile is still managed


@pytest.mark.skipif(shutil.which("stow") is None, reason="stow not available on PATH")
@pytest.mark.parametrize("skip_zshrc", [False, True])
def test_ansible_dotfiles_converge_with_stale_choices_and_stow(tmp_path, link_manifest, skip_zshrc):
    home = tmp_path / "stow_home"
    skipped = home / ".zshrc"
    seed_stale_choices(
        home,
        {
            "devenv_selected_variants": {"nvim": "kickstart"},
            "devenv_stow_packages": STALE_CHOICE_PACKAGES,
            "devenv_skip_links": [str(skipped)] if skip_zshrc else [],
        },
    )
    if skip_zshrc:
        skipped.write_text("# user-owned, must survive the converge\n")

    proc, facts = run_site(tmp_path, home, "dotfiles")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Assert the link manifest is fully satisfied" in proc.stdout

    # kickstart without skips never re-sets devenv_links, so fall back to the manifest.
    default_links = [{**link, "dest": link["dest"].replace("{{ devenv_home }}", str(home))} for link in link_manifest]
    links = facts.get("devenv_links", default_links)
    assert links
    for link in links:
        dest = Path(link["dest"])
        assert dest.is_symlink(), f"{dest} is not a symlink"
        assert dest.resolve() == (REPO_ROOT / link["src"]).resolve()

    if skip_zshrc:
        assert not skipped.is_symlink()
        assert skipped.read_text() == "# user-owned, must survive the converge\n"
        assert "zsh" not in facts["devenv_stow_packages"]

    ghostty = home / ".config" / "ghostty" / "config.ghostty"
    assert ghostty.is_symlink()
    assert ghostty.resolve() == (REPO_ROOT / "dotfiles/ghostty/.config/ghostty/config.ghostty").resolve()

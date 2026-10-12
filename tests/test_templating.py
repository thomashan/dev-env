"""Unit tests for the Jinja the roles actually run.

Expressions are read out of the role YAML instead of being copied into this
file, so editing a role invalidates the test that covers it -- which is the
point. They are then evaluated with ansible-core's own templating engine, so
custom filters (extract, regex_replace, select('match'), map('split')) behave
exactly as they will during a converge.
"""

from __future__ import annotations

import base64
import os
import re
import urllib.request

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


def set_fact_expression(role: str, name_fragment: str, key: str) -> str:
    fact_key = f"ansible.builtin.set_fact.{key}"
    found = task(role, name_fragment)
    try:
        return found["ansible.builtin.set_fact"][key]
    except KeyError:  # pragma: no cover - guards against refactors
        raise AssertionError(f"{role}: task {name_fragment!r} does not set_fact {key!r} ({fact_key})")


def wanted_expr() -> str:
    return set_fact_expression("bootstrap", "Build the wanted list", "devenv_packages_wanted")


def concrete_expr() -> str:
    return set_fact_expression("bootstrap", "Resolve logical names", "devenv_packages_concrete")


def node_pin_expr() -> str:
    return set_fact_expression("node", "Parse the pin", "devenv_node_version")


def conda_installer_expr() -> str:
    return set_fact_expression("conda", "Pick the Miniforge installer", "devenv_conda_installer")


def nvim_asset_expr() -> str:
    return set_fact_expression("neovim", "Compute the release asset name", "devenv_nvim_asset")


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
    """Regression: regex_search returns the whole match, so this must not use it."""
    text = read(REPO_ROOT / "dotfiles" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    rendered = templar(node_pin_expr(), {"devenv_fish_pins": {"content": base64.b64encode(text.encode())}})
    expected = re.search(r"^set -g devenv_node_default_version (\S+)$", text, re.MULTILINE).group(1)
    assert rendered == expected
    assert "\n" not in rendered and " " not in rendered, f"pin parse leaked surrounding text: {rendered!r}"


def test_node_pin_parse_fails_loudly_when_the_line_moves(templar):
    """If the fish file is reformatted, the role must assert rather than install ''."""
    rendered = templar(node_pin_expr(), {"devenv_fish_pins": {"content": base64.b64encode(b"set -g EDITOR nvim\n")}})
    guard = task("node", "Assert a node pin was found")["ansible.builtin.assert"]["that"][0]
    assert templar(guard, {"devenv_node_version": rendered}) is False


@pytest.mark.parametrize(
    ("system", "arch", "expected"),
    [
        ("Darwin", "arm64", "Miniforge3-MacOSX-arm64.sh"),
        ("Darwin", "aarch64", "Miniforge3-MacOSX-arm64.sh"),
        ("Darwin", "x86_64", "Miniforge3-MacOSX-x86_64.sh"),
        ("Linux", "x86_64", "Miniforge3-Linux-x86_64.sh"),
        ("Linux", "aarch64", "Miniforge3-Linux-aarch64.sh"),
        ("Linux", "amd64", "Miniforge3-Linux-x86_64.sh"),
    ],
)
def test_conda_installer_matches_platform(templar, system, arch, expected):
    assert templar(conda_installer_expr(), {"devenv_system": system, "devenv_arch": arch}) == expected


@pytest.mark.parametrize(
    ("system", "arch", "expected"),
    [
        ("Darwin", "arm64", "nvim-macos-arm64.tar.gz"),
        ("Darwin", "x86_64", "nvim-macos-x86_64.tar.gz"),
        ("Linux", "x86_64", "nvim-linux-x86_64.tar.gz"),
        ("Linux", "aarch64", "nvim-linux-arm64.tar.gz"),
    ],
)
def test_neovim_release_asset_matches_platform(templar, system, arch, expected):
    assert templar(nvim_asset_expr(), {"devenv_system": system, "devenv_arch": arch}) == expected


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
def test_miniforge_installer_names_exist_upstream(templar, system, arch):
    """Opt-in network check that the computed asset names are real (run in CI)."""
    name = templar(conda_installer_expr(), {"devenv_system": system, "devenv_arch": arch})
    url = f"https://github.com/conda-forge/miniforge/releases/latest/download/{name}"
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310 - fixed upstream host
        assert response.status == 200, f"{url} -> {response.status}"

"""Structural invariants of the declarative manifest.

These are the cheap, host-independent guarantees that a converge can be trusted:
package coverage on every supported backend, a link manifest that cannot clobber
something, and the rules that stop drift between the repo and a machine.
"""

from __future__ import annotations

import re
import subprocess

import pytest
import yaml

from .conftest import REPO_ROOT, VERSION_RE, read, role_task_files

pytestmark = pytest.mark.manifest

FORBIDDEN_MAKE = [".ONESHELL", "$(file", "!=", ".RECIPEPREFIX"]
MACHINE_LOCAL_FISH = [
    "fish_variables",
    "local",
    "completions",
    "functions",
    "__sdkman-noexport-init.sh",
]
# Plugin payloads installed by fisher, not authored by us.
FISHER_PAYLOADS = ["conf.d/sdk.fish", "conf.d/nvm.fish"]


def test_every_logical_package_has_an_alias_for_every_supported_os(group_vars, alias_tables, os_vars):
    """The multi-OS promise: one logical list, translated for every OS we support.

    A missing alias here means a wrong or absent package name on that OS. Names
    the OS already ships are exempt via devenv_pkg_skip, which is exactly why
    the check walks OS -> backend -> table rather than every table blindly.
    """
    logical = set(group_vars["devenv_packages_core"]) | set(group_vars["devenv_packages_extra"])
    assert alias_tables, "no alias tables found under ansible/vars/pkg_*.yml"
    for system, backend in group_vars["devenv_backend_for_system"].items():
        assert backend in alias_tables, f"{system} maps to backend '{backend}' with no pkg_{backend}.yml"
        skip = set(os_vars.get(system, {}).get("devenv_pkg_skip", []))
        missing = (logical - skip) - set(alias_tables[backend])
        assert not missing, f"ansible/vars/pkg_{backend}.yml ({system}) is missing aliases for: {sorted(missing)}"


def test_backend_and_asset_maps_cover_every_declared_os(group_vars, os_vars):
    """A new OS must come with a backend, an alias table and both asset maps."""
    for map_name in ("devenv_backend_for_system", "devenv_miniforge_asset_os", "devenv_neovim_asset_os"):
        assert set(group_vars[map_name]) == set(os_vars), f"{map_name} and ansible/vars/os_*.yml disagree"
    for map_name in ("devenv_miniforge_asset_arch", "devenv_neovim_asset_arch"):
        assert set(group_vars[map_name]) == set(os_vars), f"{map_name} is missing an entry for some OS"
        for system, arch_map in group_vars[map_name].items():
            assert {"arm64", "aarch64", "x86_64"} <= set(arch_map), f"{map_name}[{system}] lacks a common arch"


def test_no_orphan_aliases(group_vars, alias_tables):
    """Stale aliases hide renamed tools; every alias must be reachable."""
    logical = set(group_vars["devenv_packages_core"]) | set(group_vars["devenv_packages_extra"])
    for backend, aliases in alias_tables.items():
        orphans = set(aliases) - logical
        assert not orphans, f"ansible/vars/pkg_{backend}.yml declares unused logical names: {sorted(orphans)}"


def test_supported_backends_match_alias_tables(group_vars, alias_tables):
    supported = set(group_vars["devenv_supported_backends"])
    assert supported == set(alias_tables), "devenv_supported_backends and ansible/vars/pkg_*.yml disagree"


def test_unsupported_package_managers_have_no_table(group_vars):
    """dnf/pacman tables were deleted deliberately: unvalidated names must not ship."""
    present = {p.stem.removeprefix("pkg_") for p in (REPO_ROOT / "ansible" / "vars").glob("pkg_*.yml")}
    assert present == set(group_vars["devenv_supported_backends"])


def test_skip_list_only_names_logical_packages(os_vars, group_vars):
    logical = set(group_vars["devenv_packages_core"]) | set(group_vars["devenv_packages_extra"])
    for os_name, data in os_vars.items():
        for name in data.get("devenv_pkg_skip", []):
            assert name in logical, f"{os_name} skips '{name}', which is not a declared logical package"


def test_os_overrides_exist_for_supported_systems(os_vars):
    assert {"Darwin", "Linux"} <= set(os_vars), "each supported OS needs an ansible/vars/os_*.yml"


def test_link_sources_exist_and_are_files(link_manifest, repo_root):
    """Directory sources would displace third-party files in the same directory."""
    for entry in link_manifest:
        src = repo_root / entry["src"]
        assert src.exists(), f"devenv_links source missing: {entry['src']}"
        assert src.is_file(), f"devenv_links source must be a file, not a directory: {entry['src']}"


def test_link_destinations_are_absolute_home_paths_and_unique(link_manifest):
    dests = [entry["dest"] for entry in link_manifest]
    assert len(dests) == len(set(dests)), "duplicate destination in devenv_links"
    for dest in dests:
        assert dest.startswith("{{ devenv_home }}"), f"destination must be rooted at devenv_home: {dest}"
        assert ".." not in dest, f"destination must not traverse upwards: {dest}"


def test_no_link_is_nested_under_another_link(link_manifest):
    """Nesting would make the inner link unreachable once the outer one lands."""
    dests = sorted(entry["dest"] for entry in link_manifest)
    for outer in dests:
        for inner in dests:
            if inner == outer:
                continue
            assert not inner.startswith(outer + "/"), f"{inner} is nested under {outer}"


def test_no_shell_scripts_are_tracked(repo_root):
    """Orchestration lives in make recipes and Ansible tasks, never in .sh files.

    Scoped to tracked files: .venv and ~/.cache hold third-party scripts we
    neither own nor review, and .gitignore keeps them out of the repo anyway.
    """
    tracked = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-co", "--exclude-standard"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    offenders = [path for path in tracked if path.endswith(".sh")]
    assert not offenders, f"shell scripts are not allowed in this repository: {offenders}"


def test_no_single_source_of_truth_brewfile(repo_root):
    """ansible/group_vars/all.yml is the package manifest; a Brewfile would fork it."""
    assert not (repo_root / "Brewfile").exists()


def test_dotfiles_contain_no_machine_local_fish_state():
    fish_dir = REPO_ROOT / "dotfiles" / ".config" / "fish"
    present = {p.name for p in fish_dir.rglob("*")}
    for name in MACHINE_LOCAL_FISH:
        assert name not in present, f"{name} is generated or machine-local and must not be committed"
    for payload in FISHER_PAYLOADS:
        assert not (fish_dir / payload).exists(), f"{payload} is installed by fisher, not authored here"


def test_dotfiles_hardcode_no_per_user_paths():
    """Multi-OS rule: user homes are never literal; OS prefixes need an OS guard."""
    for path in (REPO_ROOT / "dotfiles").rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO_ROOT)
        # Comments legitimately name the paths the file avoids; only code counts.
        code = "\n".join(
            line for line in read(path).splitlines() if not line.lstrip().startswith("#")
        )
        assert "/Users/" not in code, f"{rel} hardcodes a macOS home path"
        # /home/linuxbrew is the fixed Linuxbrew prefix, not a user home.
        stray = re.findall(r"(?<![\w.])/home/(?!linuxbrew)[\w./-]+", code)
        assert not stray, f"{rel} hardcodes a Linux home path: {stray}"
        if "/opt/homebrew" in code or "/usr/local/bin/brew" in code:
            assert "case Darwin" in code, f"{rel} uses a macOS path without an OS switch"


def test_conda_path_parity_between_ansible_and_fish(group_vars):
    """The whole point of installing Miniforge to ~ on both OSes."""
    conda_dir = group_vars["devenv_conda_dir"]
    assert conda_dir == "{{ devenv_home }}/miniforge3"
    fish_cfg = read(REPO_ROOT / "dotfiles" / ".config" / "fish" / "config.fish")
    assert "$HOME/miniforge3" in fish_cfg, "config.fish must probe the same conda path Ansible installs"


def test_node_pin_is_declared_exactly_once_and_well_formed(group_vars):
    """Ansible parses this pin out of the fish config; two sources would drift."""
    pin_file = read(REPO_ROOT / "dotfiles" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    pins = re.findall(r"^set -g devenv_node_default_version (\S+)$", pin_file, flags=re.MULTILINE)
    assert len(pins) == 1, f"expected exactly one node pin, found {pins}"
    assert VERSION_RE.match(pins[0]), f"node pin is not an X.Y.Z version: {pins[0]}"
    assert "devenv_node_version" not in read(REPO_ROOT / "ansible" / "group_vars" / "all.yml")


def test_node_bin_is_first_on_path():
    """This host had three node binaries; nvm must win over ~/.local/bin."""
    fish_cfg = read(REPO_ROOT / "dotfiles" / ".config" / "fish" / "config.fish")
    nvm = fish_cfg.index("nvm/current/bin")
    local = fish_cfg.index('$HOME/.local/bin')
    assert nvm < local, "nvm's node must be prepended before ~/.local/bin"
    assert "-gpPm" in fish_cfg, "nvm path must use prepend (-p) so it wins over $fish_user_paths"


def test_python_pin_matches_the_world_ruleset(group_vars):
    ruleset = read(REPO_ROOT / "holon-config" / "world" / "ruleset.md")
    version = group_vars["devenv_python_version"]
    assert version == "3.13"
    assert f"`=={version}.*`" in ruleset, "ruleset.md no longer pins the python version the roles install"


def test_pyproject_declares_the_same_python(group_vars):
    """ruleset.md demands dependencies live in pyproject.toml, on one python."""
    pyproject = read(REPO_ROOT / "pyproject.toml")
    assert f'requires-python = "=={group_vars["devenv_python_version"]}.*"' in pyproject


def test_every_task_uses_a_fully_qualified_module_name():
    reserved = {
        "name", "when", "until", " retries", "loop", "loop_control", "register", "tags", "become",
        "become_user", "become_method", "vars", "vars_prompt", "notify", "changed_when",
        "failed_when", "unreachable_when", "ignore_errors", "ignore_unreachable", "run_once",
        "any_errors_fatal", "check_mode", "diff", "delegate_to", "delegation_facts",
        "environment", "retries", "delay", "poll", "timeout", "no_log", "local_action", "action",
        "args", "block", "rescue", "always", "listen", "throttle", "connection", "remote_user",
        "module_defaults", "label", "pause", "msg", "with_items", "with_dict", "with_fileglob",
    }
    offenders = []
    for path in role_task_files() + [REPO_ROOT / "ansible" / "playbooks" / "unlink.yml"]:
        for doc in yaml.safe_load_all(read(path)):
            for task in doc or []:
                if not isinstance(task, dict):
                    continue
                modules = [k for k in task if k not in reserved and not k.startswith("with_")]
                if len(modules) == 1 and "." not in modules[0]:
                    offenders.append(f"{path.name}: {modules[0]}")
    assert not offenders, f"non-FQCN module usage: {offenders}"


def test_every_role_is_wired_into_the_playbook():
    site = yaml.safe_load(read(REPO_ROOT / "ansible" / "site.yml"))
    wired = {next(iter(entry.values())) if isinstance(entry, dict) else entry
             for play in site for entry in play["roles"]}
    on_disk = {p.parent.parent.name for p in (REPO_ROOT / "ansible" / "roles").glob("*/tasks/main.yml")}
    assert on_disk <= wired, f"roles not reachable from site.yml: {sorted(on_disk - wired)}"


def test_bootstrap_role_always_runs():
    """Scoped runs (--tags dotfiles, node, ...) still need platform facts."""
    site = yaml.safe_load(read(REPO_ROOT / "ansible" / "site.yml"))
    bootstrap = next(entry for play in site for entry in play["roles"]
                     if isinstance(entry, dict) and entry.get("role") == "bootstrap")
    assert "always" in bootstrap["tags"]


def test_bootstrap_is_first():
    site = yaml.safe_load(read(REPO_ROOT / "ansible" / "site.yml"))
    first = site[0]["roles"][0]
    assert (first.get("role") if isinstance(first, dict) else first) == "bootstrap"


def test_makefile_stays_compatible_with_apple_gnu_make():
    """macOS ships GNU Make 3.81; 3.82+ features would break the cold start."""
    makefile = "\n".join(
        line for line in read(REPO_ROOT / "Makefile").splitlines() if not line.lstrip().startswith("#")
    )
    for token in FORBIDDEN_MAKE:
        assert token not in makefile, f"Makefile uses {token}, which GNU Make 3.81 lacks"
    assert "MAKE_VERSION" in makefile, "Makefile must refuse to run under a non-GNU make"


def test_makefile_recipes_are_tab_indented():
    """A space-indented recipe is a hard error in GNU Make; catch it in review."""
    lines = read(REPO_ROOT / "Makefile").splitlines()
    bad = []
    continued = False
    for lineno, line in enumerate(lines, start=1):
        if continued:
            continued = line.rstrip().endswith("\\")
            continue
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] == "\t":
            continued = line.rstrip().endswith("\\")
            continue
        # Not a recipe: must be a rule, assignment, conditional or directive.
        if re.match(
            r"^(?:ifeq|ifneq|ifdef|ifndef|else|endif|\$\(error\b|ifn?e?lse?|include|-?\.|[\w.\-/() $*]+\s*[:?+]?=|[\w./ ,@%()$-]+:)",
            line,
        ):
            continued = line.rstrip().endswith("\\")
            continue
        bad.append(lineno)
    assert not bad, f"unrecognised/un-indented lines (recipes need a TAB): lines {bad}"


def test_nvim_lockfile_covers_every_declared_plugin():
    """init.lua installs via vim.pack; an unlocked plugin is not reproducible."""
    init = read(REPO_ROOT / "dotfiles" / ".config" / "nvim" / "init.lua")
    lock = yaml.safe_load(read(REPO_ROOT / "dotfiles" / ".config" / "nvim" / "nvim-pack-lock.json"))
    declared = set(re.findall(r"'(https://github\.com/[^']+)'", init))
    locked = {entry["src"] for entry in lock["plugins"].values()}
    assert declared, "no vim.pack.add() sources found in init.lua"
    assert declared <= locked, f"plugins missing from nvim-pack-lock.json: {sorted(declared - locked)}"
    for name, entry in lock["plugins"].items():
        assert re.fullmatch(r"[0-9a-f]{40}", entry["rev"]), f"{name} is not pinned to a commit"


def test_tmux_config_uses_the_xdg_path(link_manifest):
    dests = [entry["dest"] for entry in link_manifest]
    assert any(d.endswith(".config/tmux/tmux.conf") for d in dests), (
        "tmux >= 3.1 reads ~/.config/tmux/tmux.conf; ~/.tmux.conf would be ignored"
    )


def test_ledger_files_exist_and_are_empty_or_append_only():
    """constraints.md forbids rewriting history; assert the files are present."""
    for name in ("intents.jsonl", "plans.jsonl", "executions.jsonl"):
        path = REPO_ROOT / "holon-knowledge" / "ledger" / name
        assert path.exists(), f"missing ledger: {name}"


def test_no_secrets_in_tracked_config(repo_root):
    """These files were imported from a live home directory; keep it that way."""
    pattern = re.compile(
        r"(api[_-]?key|secret|token|passw(?:ord)?|private[_-]?key"
        r"|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,})",
        re.IGNORECASE,
    )
    hits = []
    for path in (repo_root / "dotfiles").rglob("*"):
        if path.is_file() and pattern.search(read(path)):
            hits.append(str(path.relative_to(repo_root)))
    assert not hits, f"possible credentials committed in: {hits}"


def test_gitignore_protects_generated_fish_state(repo_root):
    gitignore = read(repo_root / ".gitignore")
    for token in ("fish_variables", "local/", "intents/*.json"):
        assert token in gitignore, f".gitignore no longer ignores {token}"

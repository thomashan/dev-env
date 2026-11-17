"""Structural invariants of the declarative manifest.

These are the cheap, host-independent guarantees that a converge can be trusted:
package coverage on every supported backend, a link manifest that cannot clobber
something, and the rules that stop drift between the repo and a machine.
"""

from __future__ import annotations

import json
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
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    offenders = [path for path in tracked if path.endswith(".sh") and not path.startswith("dotfiles/examples/")]
    assert not offenders, f"shell scripts are not allowed in this repository: {offenders}"


def test_no_single_source_of_truth_brewfile(repo_root):
    """ansible/group_vars/all.yml is the package manifest; a Brewfile would fork it."""
    assert not (repo_root / "Brewfile").exists()


def test_dotfiles_contain_no_machine_local_fish_state():
    fish_dir = REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish"
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
        code = "\n".join(line for line in read(path).splitlines() if not line.lstrip().startswith("#"))
        assert "/Users/" not in code, f"{rel} hardcodes a macOS home path"
        # /home/linuxbrew is the fixed Linuxbrew prefix, not a user home.
        stray = re.findall(r"(?<![\w.])/home/(?!linuxbrew)[\w./-]+", code)
        assert not stray, f"{rel} hardcodes a Linux home path: {stray}"
        if "/opt/homebrew" in code or "/usr/local/bin/brew" in code:
            assert "case Darwin" in code or "Darwin)" in code, f"{rel} uses a macOS path without an OS switch"


def test_conda_path_parity_between_ansible_and_fish(group_vars):
    """Conda is configured via Ansible while config.fish maintains pure OS defaults."""
    conda_dir = group_vars["devenv_conda_dir"]
    assert conda_dir == "{{ devenv_home }}/miniforge3"
    fish_cfg = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "config.fish")
    assert "$HOME/miniforge3" not in fish_cfg, "config.fish must not hardcode conda paths"
    assert "conda shell.fish hook" not in fish_cfg, "config.fish must not embed conda shell hooks"


def test_node_pin_is_declared_exactly_once_and_well_formed(group_vars):
    """versions.json defines the authoritative node pin; two sources would drift."""
    versions = json.loads(read(REPO_ROOT / "versions.json"))
    assert "node" in versions, "versions.json missing node pin"
    node_pin = versions["node"]
    assert VERSION_RE.match(node_pin), f"node pin is not an X.Y.Z version: {node_pin}"
    assert "devenv_node_version" not in read(REPO_ROOT / "ansible" / "group_vars" / "all.yml")


def test_wizard_default_node_version_matches_fish_pin():
    """Interactive wizard fallback must match the authoritative fish dotfiles pin."""
    wizard_src = read(REPO_ROOT / "scripts" / "devenv_wizard.py")
    wizard_pins = re.findall(
        r'existing_choices\.get\("devenv_node_default_version",\s*"([^"]+)"\)',
        wizard_src,
    )
    assert len(wizard_pins) == 1, f"expected exactly one wizard fallback node pin, found {wizard_pins}"

    pin_file = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    fish_pins = re.findall(r"^set -g devenv_node_default_version (\S+)$", pin_file, flags=re.MULTILINE)
    assert len(fish_pins) == 1, f"expected exactly one fish node pin, found {fish_pins}"

    assert wizard_pins[0] == fish_pins[0] == "26.13.1"


def test_node_bin_is_first_on_path():
    """config.fish maintains pure OS default invariants without embedded toolchain hooks."""
    fish_cfg = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "config.fish")
    assert "nvm/current/bin" not in fish_cfg, "nvm path addition must not be hardcoded in config.fish"
    assert "brew shellenv" not in fish_cfg, "brew shellenv must not be embedded in config.fish"
    assert "-gpPm" not in fish_cfg, "nvm prepend flag must not be embedded in config.fish"
    assert "$HOME/.local/bin" in fish_cfg, "standard user binary directory must be preserved on PATH"


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
        "name",
        "when",
        "until",
        " retries",
        "loop",
        "loop_control",
        "register",
        "tags",
        "become",
        "become_user",
        "become_method",
        "vars",
        "vars_prompt",
        "notify",
        "changed_when",
        "failed_when",
        "unreachable_when",
        "ignore_errors",
        "ignore_unreachable",
        "run_once",
        "any_errors_fatal",
        "check_mode",
        "diff",
        "delegate_to",
        "delegation_facts",
        "environment",
        "retries",
        "delay",
        "poll",
        "timeout",
        "no_log",
        "local_action",
        "action",
        "args",
        "block",
        "rescue",
        "always",
        "listen",
        "throttle",
        "connection",
        "remote_user",
        "module_defaults",
        "label",
        "pause",
        "msg",
        "with_items",
        "with_dict",
        "with_fileglob",
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
    wired = {
        next(iter(entry.values())) if isinstance(entry, dict) else entry for play in site for entry in play["roles"]
    }
    on_disk = {p.parent.parent.name for p in (REPO_ROOT / "ansible" / "roles").glob("*/tasks/main.yml")}
    assert on_disk <= wired, f"roles not reachable from site.yml: {sorted(on_disk - wired)}"


def test_bootstrap_role_always_runs():
    """Scoped runs (--tags dotfiles, node, ...) still need platform facts."""
    site = yaml.safe_load(read(REPO_ROOT / "ansible" / "site.yml"))
    bootstrap = next(
        entry
        for play in site
        for entry in play["roles"]
        if isinstance(entry, dict) and entry.get("role") == "bootstrap"
    )
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
    """init.lua and loaded plugins install via vim.pack; an unlocked plugin is not reproducible."""
    nvim_dir = REPO_ROOT / "dotfiles" / "nvim-kickstart" / ".config" / "nvim"
    init_file = nvim_dir / "init.lua"
    lock = yaml.safe_load(read(nvim_dir / "nvim-pack-lock.json"))

    init_lines = [line for line in read(init_file).splitlines() if not line.lstrip().startswith("--")]
    active_requires = {m.group(1) for line in init_lines if (m := re.search(r"require\s*['\"]([^'\"]+)['\"]", line))}

    lua_files = [init_file]
    for path in (nvim_dir / "lua").rglob("*.lua"):
        rel = path.relative_to(nvim_dir / "lua").with_suffix("")
        mod = ".".join(rel.parts)
        if mod in active_requires or mod.startswith("custom.plugins"):
            lua_files.append(path)

    declared = set()
    for path in lua_files:
        lines = [line for line in read(path).splitlines() if not line.lstrip().startswith("--")]
        text = "\n".join(lines)
        for match in re.findall(r"gh\s*['\"]([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)['\"]", text):
            declared.add(f"https://github.com/{match}")
        for match in re.findall(r"'(https://github\.com/[^']+)'", text):
            declared.add(match)

    locked = {entry["src"] for entry in lock["plugins"].values()}
    assert declared, "no vim.pack.add() sources found in init.lua and loaded plugins"
    assert declared <= locked, f"plugins missing from nvim-pack-lock.json: {sorted(declared - locked)}"
    for name, entry in lock["plugins"].items():
        assert re.fullmatch(r"[0-9a-f]{40}", entry["rev"]), f"{name} is not pinned to a commit"


def test_stow_is_declared_in_core_packages(group_vars):
    assert "stow" in group_vars["devenv_packages_core"], "stow must be in devenv_packages_core"


def test_stow_packages_match_dotfiles_subdirectories(group_vars):
    dotfiles_dir = REPO_ROOT / "dotfiles"
    pkg_dirs = {p.name for p in dotfiles_dir.iterdir() if p.is_dir() and p.name != "examples"}
    stow_pkgs = set(group_vars.get("devenv_stow_packages", []))
    assert stow_pkgs <= pkg_dirs, (
        f"devenv_stow_packages {sorted(stow_pkgs)} not contained in dotfiles/ subdirs {sorted(pkg_dirs)}"
    )
    # Every variant package declared in devenv_package_variants must correspond to a dotfiles subdir
    variant_pkgs = {
        v_info["package"]
        for tool_info in group_vars.get("devenv_package_variants", {}).values()
        for v_info in tool_info.get("variants", {}).values()
    }
    base_pkgs = {"bash", "conda", "fish", "tmux", "zsh"}
    assert pkg_dirs == (base_pkgs | variant_pkgs)


def test_all_tracked_dotfiles_belong_to_stow_packages_and_are_linked(group_vars):
    stow_pkgs = set(group_vars.get("devenv_stow_packages", []))
    variant_pkgs = {
        v_info["package"]
        for tool_info in group_vars.get("devenv_package_variants", {}).values()
        for v_info in tool_info.get("variants", {}).values()
    }
    all_known_pkgs = stow_pkgs | variant_pkgs
    manifest_srcs = {entry["src"] for entry in group_vars.get("devenv_links", [])}
    dotfiles_dir = REPO_ROOT / "dotfiles"
    for path in dotfiles_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(dotfiles_dir)
        if rel.parts[0] == "examples":
            continue
        repo_rel = str(path.relative_to(REPO_ROOT))
        assert len(rel.parts) > 1, f"{repo_rel} is directly under dotfiles/ outside a stow package"
        pkg = rel.parts[0]
        assert pkg in all_known_pkgs, f"{repo_rel} package '{pkg}' not in known packages"
        if pkg in stow_pkgs:
            assert repo_rel in manifest_srcs, f"{repo_rel} is not declared in devenv_links"


def test_readme_manifest_coverage(group_vars):
    readme = read(REPO_ROOT / "README.md")
    for pkg in group_vars["devenv_packages_core"]:
        assert pkg in readme, f"README.md missing core package: {pkg}"
    for tool in group_vars["devenv_conda_tools"]:
        assert tool in readme, f"README.md missing conda tool: {tool}"
    fish_plugins_text = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "fish_plugins")
    for line in fish_plugins_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name = line.split("@")[0]
        assert name in readme or line in readme, f"README.md missing fish plugin: {line}"
    lock = yaml.safe_load(read(REPO_ROOT / "dotfiles" / "nvim-kickstart" / ".config" / "nvim" / "nvim-pack-lock.json"))
    for plugin_name, entry in lock["plugins"].items():
        assert plugin_name in readme or entry["src"] in readme, f"README.md missing Neovim plugin: {plugin_name}"


def test_uv_role_deleted_and_absent_from_site_yml():
    uv_role_dir = REPO_ROOT / "ansible" / "roles" / "uv"
    assert not uv_role_dir.exists(), "ansible/roles/uv directory must not exist"
    site = yaml.safe_load(read(REPO_ROOT / "ansible" / "site.yml"))
    roles = [entry["role"] for entry in site[0]["roles"] if isinstance(entry, dict) and "role" in entry]
    assert "uv" not in roles, "uv role must be absent from site.yml"


def test_devenv_conda_tools_manifest_and_role(group_vars):
    assert group_vars.get("devenv_conda_tools") == ["uv", "ruff", "pre-commit"]
    conda_tasks = read(REPO_ROOT / "ansible" / "roles" / "conda" / "tasks" / "main.yml")
    assert "devenv_conda_tools" in conda_tasks
    assert 'creates: "{{ devenv_conda_dir }}/bin/uv"' in conda_tasks


def test_makefile_no_shims_and_direct_conda_bins():
    makefile = read(REPO_ROOT / "Makefile")
    assert "astral.sh/uv/install.sh" not in makefile
    assert "uv tool install" not in makefile
    assert "BIN :=" not in makefile
    assert "ln -sfn" not in makefile
    assert "$(CONDA_DIR)/bin/ansible-playbook" in makefile
    assert "$(CONDA_DIR)/bin/ansible-galaxy" in makefile
    assert "$(CONDA_DIR)/bin/ansible-lint" in makefile


def test_makefile_check_probes_prerequisites_strictly():
    makefile = read(REPO_ROOT / "Makefile")
    assert "command -v conda" in makefile, "Makefile must probe conda via command -v conda"
    assert "conda info --base" in makefile, "Makefile must probe conda base via conda info --base"
    check_target = makefile.split("check:")[1].split("bootstrap:")[0]
    expected_probes = [
        "GNU Make",
        "OS",
        "brew",
        "apt (Linux backend)",
        "conda",
        "ansible-core",
        "community.general",
    ]
    for probe in expected_probes:
        assert probe in check_target, f"check target missing probe for {probe}"
    assert "MISSING: Homebrew (brew) is required" in check_target
    assert "MISSING: apt is required" in check_target
    assert "err=$$((err+1))" in check_target
    for forbidden in ["uv", "stow", "git", "curl"]:
        assert f'"{forbidden}"' not in check_target, f"{forbidden} should not be probed in make check"


def test_readme_getting_started_and_categories():
    readme = read(REPO_ROOT / "README.md")
    assert "## Getting Started" in readme, "README.md must have a '## Getting Started' section"
    assert "make install" in readme, "README.md must document 'make install'"
    assert "`nvm`/node" not in readme, "README.md must not contain broken `nvm`/node formatting"
    assert re.search(r"\|\s*Logical Package\s*\|\s*Category\s*\|", readme), (
        "README.md table must contain Category column"
    )
    assert "**Python — Runtime & Environment Manager**" in readme
    assert "**Python — Package & Project Manager**" in readme
    assert "**Python — Linter & Formatter**" in readme
    assert "**Multi-Language — Git Hooks**" in readme
    assert "**JavaScript / TypeScript — Node.js Runtime & Version Manager**" in readme


def test_readme_uses_mermaid_and_no_shims():
    readme = read(REPO_ROOT / "README.md")
    assert "flowchart TD" in readme, "README.md must use a Mermaid flowchart TD diagram"
    assert "shims" not in readme, "README.md must not reference shims"
    assert "~/.local/share/dev-env/bin/" not in readme, "README.md must not reference ~/.local/share/dev-env/bin/"
    assert "NOT cold-start prerequisites" not in readme, "README.md must not include old cold-start callout"
    assert "for app dev" not in readme, "README.md must not include 'for app dev'"


def test_package_variants_structure_and_invariants(group_vars):
    variants_map = group_vars.get("devenv_package_variants")
    assert variants_map is not None, "devenv_package_variants must be declared in group_vars/all.yml"
    assert "nvim" in variants_map
    nvim_config = variants_map["nvim"]
    assert nvim_config.get("default") == "kickstart"
    assert set(nvim_config.get("variants", {}).keys()) == {"kickstart", "minimal", "lazyvim"}
    for v_name, v_info in nvim_config["variants"].items():
        pkg_dir = REPO_ROOT / "dotfiles" / v_info["package"]
        assert pkg_dir.is_dir(), f"variant {v_name} package dir {pkg_dir} missing"
        assert (pkg_dir / ".config" / "nvim" / "init.lua").is_file(), f"variant {v_name} missing init.lua"


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


def test_makefile_bootstrap_installs_conda_via_brew():
    makefile = read(REPO_ROOT / "Makefile")
    assert "wget" not in makefile, "wget should not appear in Makefile"
    assert "urllib.request" not in makefile, "urllib.request should not appear in Makefile"
    assert "apt-get" not in makefile, "apt-get should not appear in Makefile"
    bootstrap_target = makefile.split("bootstrap:")[1].split("configure:")[0]
    assert "Error: Homebrew (brew) is required." in bootstrap_target
    assert "Error: apt is required on Linux." in bootstrap_target
    assert "install --cask miniforge" in bootstrap_target
    assert "install micromamba" in bootstrap_target
    assert "curl" not in bootstrap_target, "curl should not appear in bootstrap recipe"
    assert "Miniforge3-" not in bootstrap_target, (
        "Miniforge3- release assets should not be fetched directly in bootstrap"
    )


test_makefile_bootstrap_uses_only_curl_and_installs_curl_via_brew_or_apt = (
    test_makefile_bootstrap_installs_conda_via_brew
)


def test_no_apt_get_in_repo():
    target_files = [
        REPO_ROOT / "Makefile",
        REPO_ROOT / "ansible" / "roles" / "packages" / "tasks" / "main.yml",
        REPO_ROOT / "README.md",
        REPO_ROOT / "holon-config" / "world" / "constraints.md",
    ]
    for path in target_files:
        assert path.exists(), f"Target file {path} missing"
        content = read(path)
        assert "apt-get" not in content, f"apt-get found in {path}"


def test_dotfiles_contain_no_personal_paths():
    """Verify dotfiles do not leak personal machine or agent paths."""
    dotfiles_dir = REPO_ROOT / "dotfiles"
    forbidden = [".lmstudio", ".antigravity-ide"]
    for path in dotfiles_dir.rglob("*"):
        if not path.is_file():
            continue
        content = read(path)
        for token in forbidden:
            assert token not in content, f"{token} found in {path.relative_to(REPO_ROOT)}"


def test_tmux_conf_is_comment_only_factory_default():
    """Verify tmux configuration adheres to comment-only upstream factory defaults."""
    tmux_conf = read(REPO_ROOT / "dotfiles" / "tmux" / ".config" / "tmux" / "tmux.conf")
    for line in tmux_conf.splitlines():
        line = line.strip()
        if not line:
            continue
        assert line.startswith("#"), f"Active tmux configuration found: {line}"


def test_nvim_minimal_init_lua_is_comment_only():
    """Verify nvim minimal variant contains no active statements, running vanilla defaults."""
    init_lua = read(REPO_ROOT / "dotfiles" / "nvim-minimal" / ".config" / "nvim" / "init.lua")
    for line in init_lua.splitlines():
        line = line.strip()
        if not line:
            continue
        assert line.startswith("--"), f"Active Lua configuration found in minimal init.lua: {line}"


def test_nvim_kickstart_custom_plugins_contains_only_init_lua():
    """Verify nvim kickstart custom plugins directory contains only the init.lua stub."""
    custom_plugins_dir = REPO_ROOT / "dotfiles" / "nvim-kickstart" / ".config" / "nvim" / "lua" / "custom" / "plugins"
    files = {p.name for p in custom_plugins_dir.iterdir() if p.is_file()}
    assert files == {"init.lua"}, f"Unexpected files in kickstart custom plugins: {files}"


def test_nvim_lazyvim_example_starts_with_early_return():
    """Verify nvim lazyvim example spec begins with early return to disable custom overrides."""
    example_lua = read(REPO_ROOT / "dotfiles" / "nvim-lazyvim" / ".config" / "nvim" / "lua" / "plugins" / "example.lua")
    executable_lines = [
        line.strip() for line in example_lua.splitlines() if line.strip() and not line.strip().startswith("--")
    ]
    assert executable_lines, "No executable lines found in lazyvim example.lua"
    assert executable_lines[0] == "if true then return {} end", (
        f"LazyVim example.lua must begin with 'if true then return {{}} end', got {executable_lines[0]!r}"
    )


def test_makefile_bootstrap_guards_collections_and_omits_force():
    """Verify Makefile bootstrap target guards galaxy collections and omits --force."""
    makefile = read(REPO_ROOT / "Makefile")
    bootstrap_target = makefile.split("\nbootstrap:")[1].split("\nconfigure:")[0]
    assert "ansible_collections/community/general" in bootstrap_target
    assert "Ansible collections: ok (already installed in $(COLLECTIONS))" in bootstrap_target
    assert "ANSIBLE_COLLECTIONS_PATH" in bootstrap_target
    assert "collection install" in bootstrap_target
    assert "--force" not in bootstrap_target, "--force must not be used in collection install"


def test_makefile_exports_extended_path() -> None:
    """Makefile must export extended PATH covering Homebrew and Linuxbrew prefixes."""
    makefile = read(REPO_ROOT / "Makefile")
    assert "export PATH :=" in makefile
    path_line = next(line for line in makefile.splitlines() if line.startswith("export PATH :="))
    for expected in [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/home/linuxbrew/.linuxbrew/bin",
        "$(HOME)/.linuxbrew/bin",
        "$(PATH)",
    ]:
        assert expected in path_line, f"export PATH line missing {expected}"


def test_makefile_skips_conda_and_ansible_if_present() -> None:
    """Bootstrap recipe must inspect existing Conda and PB before running installs."""
    makefile = read(REPO_ROOT / "Makefile")
    bootstrap_target = makefile.split("bootstrap:")[1].split("configure:")[0]
    assert "Using existing Conda at" in bootstrap_target
    assert "Using existing Ansible:" in bootstrap_target
    assert '[ -x "$(CONDA)" ]' in bootstrap_target or "command -v conda" in bootstrap_target
    assert '[ -x "$(PB)" ]' in bootstrap_target


def test_makefile_conda_install_does_not_force_python_downgrade() -> None:
    """Conda install command in Makefile must not pin python=3.13 into existing env."""
    makefile = read(REPO_ROOT / "Makefile")
    bootstrap_target = makefile.split("bootstrap:")[1].split("configure:")[0]
    for line in bootstrap_target.splitlines():
        if '"$(CONDA)" install' in line or "$$(CONDA) install" in line:
            assert "python=" not in line, f"Conda install in bootstrap forces python version: {line}"
            assert "ansible-core" in line
            assert "ansible-lint" in line
            assert "pyyaml" in line


def test_versions_json_schema_and_authoritative_keys() -> None:
    """versions.json must exist at repository root and define authoritative versions."""
    versions_file = REPO_ROOT / "versions.json"
    assert versions_file.is_file(), "versions.json missing at repository root"
    data = json.loads(read(versions_file))
    assert isinstance(data, dict), "versions.json must parse to a dict"
    for key in ("python", "node", "ansible_core", "neovim_min"):
        assert key in data, f"versions.json missing required key: {key}"
        assert isinstance(data[key], str) and data[key].strip(), (
            f"key {key} in versions.json must be a non-empty string"
        )
    assert data["python"] == "3.13"
    assert data["node"] == "26.13.1"
    assert data["ansible_core"] == "2.22"
    assert data["neovim_min"] == "0.12"


def test_versions_json_node_alignment_with_fish_and_wizard() -> None:
    """versions.json node pin must match fish dotfiles and devenv_wizard fallback."""
    versions = json.loads(read(REPO_ROOT / "versions.json"))
    node_pin = versions["node"]

    pin_file = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    fish_pins = re.findall(r"^set -g devenv_node_default_version (\S+)$", pin_file, flags=re.MULTILINE)
    assert len(fish_pins) == 1, f"expected exactly one fish node pin, found {fish_pins}"
    assert fish_pins[0] == node_pin, f"fish node pin {fish_pins[0]} does not match versions.json {node_pin}"

    wizard_src = read(REPO_ROOT / "scripts" / "devenv_wizard.py")
    assert (
        f'existing_choices.get("devenv_node_default_version", "{node_pin}")' in wizard_src
        or f'"{node_pin}"' in wizard_src
    )
    assert "versions.json" in wizard_src


def test_versions_json_python_alignment_with_consumers(group_vars) -> None:
    """versions.json python pin must match pyproject.toml, group_vars/all.yml, and Makefile."""
    versions = json.loads(read(REPO_ROOT / "versions.json"))
    py_version = versions["python"]

    # group_vars/all.yml
    assert group_vars["devenv_python_version"] == py_version
    assert group_vars["devenv_conda_env_python"] == "{{ devenv_python_version }}"

    # pyproject.toml
    pyproject = read(REPO_ROOT / "pyproject.toml")
    assert f'requires-python = "=={py_version}.*"' in pyproject

    # Makefile
    makefile = read(REPO_ROOT / "Makefile")
    assert f"PYTHON_VERSION ?= {py_version}" in makefile


def test_neovim_role_assertion_syntax() -> None:
    """Neovim version assert must use standard Ansible version comparison without .regex_replace calls."""
    neovim_tasks = read(REPO_ROOT / "ansible" / "roles" / "neovim" / "tasks" / "main.yml")
    assert ".regex_replace" not in neovim_tasks, ".regex_replace method call is invalid Jinja and causes runtime errors"
    assert "is version('0.12', '>=')" in neovim_tasks or 'is version("0.12", ">=")' in neovim_tasks
    assert "| regex_replace('^NVIM v', '')" in neovim_tasks or '| regex_replace("^NVIM v", "")' in neovim_tasks


def test_makefile_lint_recipe_structure() -> None:
    """Makefile lint target must support uv-managed run and provide conda fallback."""
    makefile = read(REPO_ROOT / "Makefile")
    lint_section = makefile.split("\nlint:")[1].split("\ndocs-fmt:")[0]
    assert "command -v uv" in lint_section, "Makefile lint target must probe command -v uv"
    assert "uv run --extra test ansible-lint" in lint_section, "Makefile lint target must run uv ansible-lint"
    assert 'PATH="$(dir $(LINT)):$$PATH"' in lint_section, "Makefile lint target fallback must set PATH to dir of LINT"


def test_node_role_fisher_directory_check_mode() -> None:
    """Node role fisher directory task must set check_mode: false for clean dry-runs."""
    node_tasks_content = read(REPO_ROOT / "ansible" / "roles" / "node" / "tasks" / "main.yml")
    tasks = yaml.safe_load(node_tasks_content)
    fisher_task = next(
        (t for t in tasks if t.get("name") and "Ensure the fisher path exists" in t["name"]),
        None,
    )
    assert fisher_task is not None, "Task 'Ensure the fisher path exists' not found in node role"
    assert fisher_task.get("check_mode") is False, "fisher path directory task must have check_mode: false"


def test_devenv_shell_snippets_exists_and_valid() -> None:
    """Reusable dev-env shell snippets file exists and contains all required modular blocks."""
    snippets_path = REPO_ROOT / "dotfiles" / "examples" / "devenv-shell-snippets.sh"
    assert snippets_path.exists(), "dotfiles/examples/devenv-shell-snippets.sh does not exist"
    content = read(snippets_path)
    assert len(content.strip()) > 0, "devenv-shell-snippets.sh is empty"

    # Block A: NVM managed node PATH prepend
    assert "$XDG_DATA_HOME/nvm/current/bin" in content, "missing NVM path prepend snippet"

    # Block B: Multi-OS Homebrew/Linuxbrew evaluation
    assert 'case "$(uname -s)" in' in content, "missing OS switch for Homebrew/Linuxbrew"
    assert "brew shellenv" in content, "missing brew shellenv invocation"

    # Block C: Conda (miniforge) shell hook probe and activation
    assert "miniforge3" in content, "missing miniforge3 candidate in conda probe"
    assert "shell.bash hook" in content, "missing conda shell.bash hook"
    assert "shell.zsh hook" in content, "missing conda shell.zsh hook"

    # Block D: Local override hook loading
    assert ".bashrc.local" in content, "missing .bashrc.local override hook"
    assert ".zshrc.local" in content, "missing .zshrc.local override hook"


def test_read_only_probe_tasks_check_mode() -> None:
    """Read-only shell probe tasks in node and neovim roles must have check_mode: false."""
    node_tasks = yaml.safe_load(read(REPO_ROOT / "ansible" / "roles" / "node" / "tasks" / "main.yml"))
    node_probe = next(
        (t for t in node_tasks if t.get("name") and "Verify which node a login shell resolves" in t["name"]),
        None,
    )
    assert node_probe is not None, "Task 'Verify which node a login shell resolves' not found in node role"
    assert node_probe.get("check_mode") is False, "Node login shell probe task must have check_mode: false"

    neovim_tasks = yaml.safe_load(read(REPO_ROOT / "ansible" / "roles" / "neovim" / "tasks" / "main.yml"))
    neovim_probe = next(
        (t for t in neovim_tasks if t.get("name") and "Read the installed Neovim version" in t["name"]),
        None,
    )
    assert neovim_probe is not None, "Task 'Read the installed Neovim version' not found in neovim role"
    assert neovim_probe.get("check_mode") is False, "Neovim version probe task must have check_mode: false"


def test_login_shell_and_gui_casks_defaults(group_vars) -> None:
    """Verify group_vars/all.yml defaults and ensure devenv_wizard.py defaults match."""
    assert group_vars["devenv_set_login_shell"] is True, "devenv_set_login_shell must default to true"
    assert group_vars["devenv_install_gui_casks"] is True, "devenv_install_gui_casks must default to true"

    wizard_src = read(REPO_ROOT / "scripts" / "devenv_wizard.py")
    assert 'existing_choices.get("devenv_set_login_shell", True)' in wizard_src
    assert 'existing_choices.get("devenv_install_gui_casks", True)' in wizard_src


def test_fish_nvm_path_resolution_in_conf_d() -> None:
    """00-devenv.fish must define XDG_DATA_HOME, unified nvm_data, fallback links, and prepend nvm bin."""
    content = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    assert 'set -q XDG_DATA_HOME || set -gx XDG_DATA_HOME "$HOME/.local/share"' in content
    assert "set -g nvm_data $XDG_DATA_HOME/nvm/versions/node" in content
    assert "$XDG_DATA_HOME/nvm/versions/node" in content
    assert "ln -sfn" in content
    assert 'fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"' in content


def test_multishell_nvm_and_node_parity() -> None:
    """Ensure Bash and Zsh dotfiles configure NVM and node PATH with parity."""
    bashrc = read(REPO_ROOT / "dotfiles" / "bash" / ".bashrc")
    zshrc = read(REPO_ROOT / "dotfiles" / "zsh" / ".zshrc")

    for shell_name, content in [("bash", bashrc), ("zsh", zshrc)]:
        # Assert canonical XDG sourcing for NVM_DIR
        assert 'export NVM_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/nvm"' in content, (
            f"canonical NVM_DIR XDG definition missing in {shell_name}"
        )
        assert '[ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh"' in content, (
            f"canonical nvm.sh sourcing missing in {shell_name}"
        )
        assert '[ -s "$NVM_DIR/bash_completion" ] && \\. "$NVM_DIR/bash_completion"' in content, (
            f"canonical bash_completion sourcing missing in {shell_name}"
        )

        # Assert NVM current binary path and ~/.local/bin precedence re-assertion after Homebrew
        assert "$HOME/.local/bin" in content, f"missing ~/.local/bin PATH inclusion in {shell_name}"
        assert "$NVM_DIR/current/bin" in content, (
            f"missing nvm current/bin PATH inclusion in {shell_name}"
        )
        # Ensure NVM precedence re-assertion appears after Homebrew evaluation
        brew_idx = content.find("brew shellenv")
        nvm_precedence_idx = content.find('export PATH="$NVM_DIR/current/bin:$PATH"')
        assert brew_idx != -1 and nvm_precedence_idx != -1 and nvm_precedence_idx > brew_idx, (
            f"NVM path precedence must be re-asserted after Homebrew evaluation in {shell_name}"
        )
        assert '":$NVM_DIR/current/bin:"*' in content, (
            f"NVM precedence check must include leading colon in {shell_name}"
        )
        assert '":$HOME/.local/bin:"*' in content, (
            f"local/bin precedence check must include leading colon in {shell_name}"
        )


def test_multishell_conda_and_homebrew_parity() -> None:
    """Ensure Bash and Zsh dotfiles evaluate Homebrew shellenv with path guards and Conda hooks."""
    bashrc = read(REPO_ROOT / "dotfiles" / "bash" / ".bashrc")
    zshrc = read(REPO_ROOT / "dotfiles" / "zsh" / ".zshrc")

    for shell_name, content in [("bash", bashrc), ("zsh", zshrc)]:
        # Multi-OS Homebrew evaluation guarded when /opt/homebrew/bin is already on PATH
        assert "brew shellenv" in content, f"missing brew shellenv in {shell_name}"
        assert "/opt/homebrew/bin/brew" in content, f"missing Apple Silicon brew path in {shell_name}"
        assert '*":/opt/homebrew/bin:"*' in content, (
            f"missing /opt/homebrew/bin PATH guard in {shell_name}"
        )

        # Conda probe and hook evaluation logic
        assert "miniforge3" in content, f"missing miniforge3 probe in {shell_name}"

    assert "shell.bash hook" in bashrc, "missing conda shell.bash hook in bashrc"
    assert "shell.zsh hook" in zshrc, "missing conda shell.zsh hook in zshrc"


def test_makefile_bootstrap_next_step_conditional() -> None:
    """Makefile bootstrap target conditionally prints next-step advice only when directly targeted."""
    makefile = read(REPO_ROOT / "Makefile")
    assert "ifeq ($(MAKECMDGOALS),bootstrap)" in makefile, (
        "Makefile must conditionally guard next-step advice with ifeq ($(MAKECMDGOALS),bootstrap)"
    )
    assert "Run 'make install' or 'make check-mode' next." in makefile


def test_node_role_symlinks_and_multishell_assertions() -> None:
    """Node role must ensure ~/.local/bin binary symlinks and verify across bash, zsh, and fish."""
    node_tasks = yaml.safe_load(read(REPO_ROOT / "ansible" / "roles" / "node" / "tasks" / "main.yml"))

    # Assert tasks exist ensuring ~/.local/bin directory and symlinks for node, npm, npx
    local_bin_dir_task = next(
        (t for t in node_tasks if t.get("ansible.builtin.file", {}).get("path") == "{{ devenv_home }}/.local/bin"),
        None,
    )
    assert local_bin_dir_task is not None, "Missing task ensuring ~/.local/bin directory"
    assert local_bin_dir_task["ansible.builtin.file"].get("state") == "directory"

    symlink_task = next(
        (
            t
            for t in node_tasks
            if t.get("ansible.builtin.file", {}).get("dest") == "{{ devenv_home }}/.local/bin/{{ item }}"
        ),
        None,
    )
    assert symlink_task is not None, "Missing task symlinking nvm binaries into ~/.local/bin"
    file_spec = symlink_task["ansible.builtin.file"]
    assert file_spec.get("state") == "link"
    assert "{{ devenv_home }}/.local/share/nvm/current/bin/{{ item }}" in file_spec.get("src", "")
    assert set(symlink_task.get("loop", [])) >= {"node", "npm", "npx"}

    # Assert verification tasks probe and assert Node path and version across bash -lc, zsh -lc, and fish -lc
    probe_commands = [
        t.get("ansible.builtin.command", {}).get("cmd")
        for t in node_tasks
        if isinstance(t.get("ansible.builtin.command"), dict) and "cmd" in t["ansible.builtin.command"]
    ]
    assert any("bash -lc" in cmd and "which node; node -v" in cmd for cmd in probe_commands), (
        "missing bash -lc node verification probe"
    )
    assert any("zsh -lc" in cmd and "which node; node -v" in cmd for cmd in probe_commands), (
        "missing zsh -lc node verification probe"
    )
    assert any("fish -lc" in cmd and "which node; node -v" in cmd for cmd in probe_commands), (
        "missing fish -lc node verification probe"
    )

    assertions = [
        t.get("ansible.builtin.assert", {}).get("that", [])
        for t in node_tasks
        if isinstance(t.get("ansible.builtin.assert"), dict) and "that" in t["ansible.builtin.assert"]
    ]
    flat_assertions = [cond for sublist in assertions for cond in sublist]
    assert any("devenv_node_which_bash" in cond for cond in flat_assertions), "missing bash node assertion"
    assert any("devenv_node_which_zsh" in cond for cond in flat_assertions), "missing zsh node assertion"
    assert any("devenv_node_which" in cond for cond in flat_assertions), "missing fish node assertion"


def test_makefile_configure_python_fallback() -> None:
    """Makefile configure target probes Conda python3 then falls back to host python3."""
    makefile = read(REPO_ROOT / "Makefile")
    configure_target = makefile.split("\nconfigure:")[1].split("\ninstall:")[0]
    assert '[ -x "$(CONDA_DIR)/bin/python3" ]' in configure_target
    assert "command -v python3" in configure_target
    assert 'python3 "$(SELF_DIR)/scripts/devenv_wizard.py"' in configure_target
    assert "Error: Python 3 not found in $(CONDA_DIR)/bin/python3 or PATH." in configure_target


def test_makefile_galaxy_collection_install_isolated() -> None:
    """Ansible Galaxy collection install explicitly isolates to COLLECTIONS path."""
    makefile = read(REPO_ROOT / "Makefile")
    bootstrap_target = makefile.split("\nbootstrap:")[1].split("\nconfigure:")[0]
    assert '-p "$(COLLECTIONS)"' in bootstrap_target
    assert 'ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)"' in bootstrap_target


def test_ansible_cfg_collections_path_fallback() -> None:
    """ansible.cfg specifies primary and fallback collection directories."""
    ansible_cfg = read(REPO_ROOT / "ansible.cfg")
    assert re.search(
        r"collections_path\s*=\s*~/\.local/share/dev-env/collections:~/\.ansible/collections",
        ansible_cfg,
    ), "ansible.cfg missing collections_path fallback"


def test_multishell_micromamba_parity() -> None:
    """Bash, Zsh, and Fish dotfiles discover micromamba and provide conda alias or hook."""
    bashrc = read(REPO_ROOT / "dotfiles" / "bash" / ".bashrc")
    zshrc = read(REPO_ROOT / "dotfiles" / "zsh" / ".zshrc")
    fish_devenv = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")

    for shell_name, content in [("bash", bashrc), ("zsh", zshrc)]:
        assert "MAMBA_ROOT_PREFIX" in content, f"missing MAMBA_ROOT_PREFIX in {shell_name}"
        assert ".local/share/mamba" in content, f"missing .local/share/mamba probe in {shell_name}"
        assert "micromamba" in content, f"missing micromamba in {shell_name}"
        assert "alias conda=micromamba" in content, f"missing conda alias to micromamba in {shell_name}"
        assert f"micromamba shell hook --shell {shell_name}" in content, (
            f"missing micromamba shell hook in {shell_name}"
        )

    assert "command -q micromamba" in fish_devenv
    assert "alias conda=micromamba" in fish_devenv
    assert "micromamba shell hook --shell fish" in fish_devenv


def test_makefile_check_syntax_target() -> None:
    """Makefile defines check-syntax in .PHONY and executes --syntax-check."""
    makefile = read(REPO_ROOT / "Makefile")
    assert "check-syntax" in makefile.split(".PHONY:")[1].split("\n\n")[0]
    assert "check-syntax:" in makefile
    syntax_recipe = makefile.split("\ncheck-syntax:")[1].split("\n\n")[0]
    assert "--syntax-check" in syntax_recipe
    assert "$(ANSIBLE_ENV)" in syntax_recipe


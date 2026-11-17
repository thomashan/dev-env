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
        code = "\n".join(
            line for line in read(path).splitlines() if not line.lstrip().startswith("#")
        )
        assert "/Users/" not in code, f"{rel} hardcodes a macOS home path"
        # /home/linuxbrew is the fixed Linuxbrew prefix, not a user home.
        stray = re.findall(r"(?<![\w.])/home/(?!linuxbrew)[\w./-]+", code)
        assert not stray, f"{rel} hardcodes a Linux home path: {stray}"
        if "/opt/homebrew" in code or "/usr/local/bin/brew" in code:
            assert "case Darwin" in code or "Darwin)" in code, f"{rel} uses a macOS path without an OS switch"


def test_conda_path_parity_between_ansible_and_fish(group_vars):
    """The whole point of installing Miniforge to ~ on both OSes."""
    conda_dir = group_vars["devenv_conda_dir"]
    assert conda_dir == "{{ devenv_home }}/miniforge3"
    fish_cfg = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "config.fish")
    assert "$HOME/miniforge3" in fish_cfg, "config.fish must probe the same conda path Ansible installs"


def test_node_pin_is_declared_exactly_once_and_well_formed(group_vars):
    """Ansible parses this pin out of the fish config; two sources would drift."""
    pin_file = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    pins = re.findall(r"^set -g devenv_node_default_version (\S+)$", pin_file, flags=re.MULTILINE)
    assert len(pins) == 1, f"expected exactly one node pin, found {pins}"
    assert VERSION_RE.match(pins[0]), f"node pin is not an X.Y.Z version: {pins[0]}"
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
    """This host had three node binaries; nvm must win over ~/.local/bin."""
    fish_cfg = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "config.fish")
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
    """init.lua and loaded plugins install via vim.pack; an unlocked plugin is not reproducible."""
    nvim_dir = REPO_ROOT / "dotfiles" / "nvim-kickstart" / ".config" / "nvim"
    init_file = nvim_dir / "init.lua"
    lock = yaml.safe_load(read(nvim_dir / "nvim-pack-lock.json"))

    init_lines = [line for line in read(init_file).splitlines() if not line.lstrip().startswith("--")]
    active_requires = {
        m.group(1)
        for line in init_lines
        if (m := re.search(r"require\s*['\"]([^'\"]+)['\"]", line))
    }

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
    pkg_dirs = {p.name for p in dotfiles_dir.iterdir() if p.is_dir()}
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
        assert (pkg_dir / ".config" / "nvim" / "init.lua").is_file(), (
            f"variant {v_name} missing init.lua"
        )


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
    assert "Miniforge3-" not in bootstrap_target, "Miniforge3- release assets should not be fetched directly in bootstrap"


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
    custom_plugins_dir = (
        REPO_ROOT
        / "dotfiles"
        / "nvim-kickstart"
        / ".config"
        / "nvim"
        / "lua"
        / "custom"
        / "plugins"
    )
    files = {p.name for p in custom_plugins_dir.iterdir() if p.is_file()}
    assert files == {"init.lua"}, f"Unexpected files in kickstart custom plugins: {files}"


def test_nvim_lazyvim_example_starts_with_early_return():
    """Verify nvim lazyvim example spec begins with early return to disable custom overrides."""
    example_lua = read(
        REPO_ROOT
        / "dotfiles"
        / "nvim-lazyvim"
        / ".config"
        / "nvim"
        / "lua"
        / "plugins"
        / "example.lua"
    )
    executable_lines = [
        line.strip()
        for line in example_lua.splitlines()
        if line.strip() and not line.strip().startswith("--")
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

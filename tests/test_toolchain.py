"""Toolchain, shell parity, and Makefile syntax invariants."""

from __future__ import annotations

import re

import pytest
import yaml

from .conftest import REPO_ROOT, read, role_task_files

pytestmark = pytest.mark.manifest


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
    """Makefile defines check-syntax in .PHONY and executes --syntax-check on site.yml and unlink.yml."""
    makefile = read(REPO_ROOT / "Makefile")
    assert "check-syntax" in makefile.split(".PHONY:")[1].split("\n\n")[0]
    assert "check-syntax:" in makefile
    syntax_recipe = makefile.split("\ncheck-syntax:")[1].split("\n\n")[0]
    assert "--syntax-check" in syntax_recipe
    assert "$(ANSIBLE_ENV)" in syntax_recipe
    assert '"$(SITE)"' in syntax_recipe
    assert '"$(SELF_DIR)/ansible/playbooks/unlink.yml"' in syntax_recipe


def test_makefile_bootstrap_ca_injection() -> None:
    """Makefile bootstrap recipe checks and injects custom CA certificates."""
    makefile = read(REPO_ROOT / "Makefile")
    bootstrap_target = makefile.split("\nbootstrap:")[1].split("\nconfigure:")[0]
    assert "/usr/local/share/ca-certificates" in bootstrap_target
    assert "$(CONDA_DIR)/ssl/cacert.pem" in bootstrap_target
    assert "*.crt" in bootstrap_target
    assert "*.pem" in bootstrap_target
    assert "ANSIBLE MANAGED BLOCK: Custom CA" in bootstrap_target
    assert "grep -F -q" in bootstrap_target


def test_go_toolchain_declarations_and_skip(os_vars, group_vars) -> None:
    """Go toolchain package must be declared in core and skipped in apt on Linux."""
    assert "go" in group_vars.get("devenv_packages_core", []), "go missing from devenv_packages_core"
    assert "go" in os_vars["Linux"].get("devenv_pkg_skip", []), "go missing from Linux devenv_pkg_skip"


def test_fish_go_path_addition() -> None:
    """00-devenv.fish must export $HOME/go/bin via fish_add_path."""
    fish_conf = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    assert "$HOME/go/bin" in fish_conf, "missing $HOME/go/bin in 00-devenv.fish"
    assert "fish_add_path" in fish_conf, "missing fish_add_path in 00-devenv.fish"


def test_nvim_kickstart_markdownlint_auto_install_and_lint_guard() -> None:
    """Verify kickstart auto-installs markdownlint via mason-tool-installer and guards try_lint."""
    init_lua = read(REPO_ROOT / "dotfiles" / "nvim-kickstart" / ".config" / "nvim" / "init.lua")
    lint_lua = read(
        REPO_ROOT / "dotfiles" / "nvim-kickstart" / ".config" / "nvim" / "lua" / "kickstart" / "plugins" / "lint.lua"
    )

    match = re.search(r"vim\.list_extend\(ensure_installed,\s*\{([^}]*)\}\)", init_lua)
    assert match, "vim.list_extend(ensure_installed, { ... }) not found in kickstart init.lua"
    assert "'markdownlint'" in match.group(1), "markdownlint not in ensure_installed extension list"

    assert "lint.try_lint(nil, { ignore_errors = true })" in lint_lua


def test_node_ansible_role_ca_folding() -> None:
    """Node Ansible role folds custom CA certificates into node-extra-ca.pem."""
    node_tasks = read(REPO_ROOT / "ansible" / "roles" / "node" / "tasks" / "main.yml")
    assert "/usr/local/share/ca-certificates" in node_tasks
    assert "node-extra-ca.pem" in node_tasks
    assert "ansible.builtin.blockinfile" in node_tasks
    assert "recurse: true" in node_tasks or "recurse: yes" in node_tasks or "recurse: True" in node_tasks
    assert "# {mark} ANSIBLE MANAGED BLOCK: Custom CA" in node_tasks


def test_multishell_node_extra_ca_certs_parity() -> None:
    """Fish, Bash, Zsh, and snippet templates conditionally export NODE_EXTRA_CA_CERTS."""
    bashrc = read(REPO_ROOT / "dotfiles" / "bash" / ".bashrc")
    zshrc = read(REPO_ROOT / "dotfiles" / "zsh" / ".zshrc")
    fish_conf = read(REPO_ROOT / "dotfiles" / "fish" / ".config" / "fish" / "conf.d" / "00-devenv.fish")
    snippets = read(REPO_ROOT / "dotfiles" / "examples" / "devenv-shell-snippets.sh")

    for file_content in (bashrc, zshrc, fish_conf, snippets):
        assert "NODE_EXTRA_CA_CERTS" in file_content
        assert ".config/node/node-extra-ca.pem" in file_content

    assert 'export NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"' in bashrc
    assert 'export NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"' in zshrc
    assert 'export NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"' in snippets
    assert 'set -gx NODE_EXTRA_CA_CERTS "$HOME/.config/node/node-extra-ca.pem"' in fish_conf


def test_tmux_pane_current_path_keybindings() -> None:
    """tmux configuration binds splits and new windows to current pane working directory."""
    tmux_conf = read(REPO_ROOT / "dotfiles" / "tmux" / ".tmux.conf")
    assert 'bind-key \'"\' split-window -v -c "#{pane_current_path}"' in tmux_conf
    assert 'bind-key % split-window -h -c "#{pane_current_path}"' in tmux_conf
    assert 'bind-key c new-window -c "#{pane_current_path}"' in tmux_conf


def test_gui_casks_and_linux_gui_apps_declarations(os_vars, group_vars) -> None:
    """GUI casks and Linux GUI application variable declarations adhere to OS isolation."""
    assert "docker-desktop" in os_vars["Darwin"]["devenv_casks"]
    assert "ghostty" in os_vars["Darwin"]["devenv_casks"]
    assert "warp" in os_vars["Darwin"]["devenv_casks"]
    assert os_vars["Linux"]["devenv_casks"] == []
    assert os_vars["Linux"]["devenv_linux_gui_apps"] == ["ghostty", "warp"]
    assert group_vars["devenv_linux_gui_apps"] == []


def test_ghostty_stow_config_and_links(group_vars) -> None:
    """Ghostty Stow config exists, unbinds Option+Arrow, and is registered in Stow packages and links."""
    ghostty_config_path = REPO_ROOT / "dotfiles" / "ghostty" / ".config" / "ghostty" / "config.ghostty"
    assert ghostty_config_path.exists(), "Ghostty config.ghostty missing"
    ghostty_config = read(ghostty_config_path)
    assert "keybind = alt+arrow_left=unbind" in ghostty_config
    assert "keybind = alt+arrow_right=unbind" in ghostty_config

    assert "ghostty" in group_vars.get("devenv_stow_packages", [])
    link_entries = group_vars.get("devenv_links", [])
    assert any(
        entry.get("src") == "dotfiles/ghostty/.config/ghostty/config.ghostty"
        and entry.get("dest") == "{{ devenv_home }}/.config/ghostty/config.ghostty"
        for entry in link_entries
    ), "Ghostty link missing from devenv_links"


def test_zsh_word_jump_keybindings() -> None:
    """Zsh configuration binds CSI word navigation key sequences inside interactive guard."""
    zshrc = read(REPO_ROOT / "dotfiles" / "zsh" / ".zshrc")
    assert "[[ -o interactive ]]" in zshrc
    assert 'bindkey "^[[1;3D" backward-word' in zshrc
    assert 'bindkey "^[[1;3C" forward-word' in zshrc
    assert 'bindkey "^[[1;5D" backward-word' in zshrc
    assert 'bindkey "^[[1;5C" forward-word' in zshrc


def test_linux_packages_gui_terminal_tasks() -> None:
    """Packages role defines check-mode safe, DEB822, WSL-excluded Linux tasks for Warp and Ghostty."""
    packages_raw = read(REPO_ROOT / "ansible" / "roles" / "packages" / "tasks" / "main.yml")
    packages_tasks = yaml.safe_load(packages_raw)

    assert "winget.exe" not in packages_raw
    assert "devenv_install_gui_on_wsl" not in packages_raw
    assert "devenv_install_gui_on_wsl" not in read(REPO_ROOT / "ansible" / "group_vars" / "all.yml")
    assert "devenv_install_gui_on_wsl" not in read(REPO_ROOT / "scripts" / "devenv_wizard.py")

    warp_probe = next((t for t in packages_tasks if t.get("name") == "Probe Warp terminal binary"), None)
    assert warp_probe is not None
    assert warp_probe.get("ansible.builtin.command", {}).get("cmd") == "which warp-terminal"
    assert warp_probe.get("check_mode") is False
    assert warp_probe.get("failed_when") is False

    warp_keyring = next((t for t in packages_tasks if t.get("name") == "Ensure APT keyrings directory exists"), None)
    assert warp_keyring is not None
    assert warp_keyring.get("ansible.builtin.file", {}).get("path") == "/etc/apt/keyrings"

    warp_gpg = next((t for t in packages_tasks if t.get("name") == "Fetch and dearmor Warp GPG signing key"), None)
    assert warp_gpg is not None
    assert warp_gpg.get("ansible.builtin.command", {}).get("creates") == "/etc/apt/keyrings/warpdotdev.gpg"

    warp_repo = next((t for t in packages_tasks if t.get("name") == "Configure Warp APT repository"), None)
    assert warp_repo is not None
    assert warp_repo.get("ansible.builtin.copy", {}).get("dest") == "/etc/apt/sources.list.d/warpdotdev.list"
    content = warp_repo.get("ansible.builtin.copy", {}).get("content", "")
    assert "https://releases.warp.dev/linux/deb stable main" in content
    assert "x86_64" in content and "amd64" in content
    assert "arm64" in content

    ghostty_probe = next((t for t in packages_tasks if t.get("name") == "Probe Ghostty binary"), None)
    assert ghostty_probe is not None
    assert ghostty_probe.get("ansible.builtin.command", {}).get("cmd") == "which ghostty"
    assert ghostty_probe.get("check_mode") is False
    assert ghostty_probe.get("failed_when") is False

    ghostty_apt_cache = next(
        (t for t in packages_tasks if t.get("name") == "Probe native Ghostty apt package availability"), None
    )
    assert ghostty_apt_cache is not None
    assert ghostty_apt_cache.get("ansible.builtin.command", {}).get("cmd") == "apt-cache show ghostty"
    assert ghostty_apt_cache.get("check_mode") is False

    snap_probe = next((t for t in packages_tasks if t.get("name") == "Probe snap command"), None)
    assert snap_probe is not None
    assert snap_probe.get("ansible.builtin.command", {}).get("cmd") == "which snap"
    assert snap_probe.get("check_mode") is False

    ghostty_snap = next((t for t in packages_tasks if t.get("name") == "Install Ghostty via snap"), None)
    assert ghostty_snap is not None
    assert ghostty_snap.get("ansible.builtin.command", {}).get("cmd") == "snap install ghostty --classic"

    ghostty_ppa = next((t for t in packages_tasks if t.get("name") == "Add Ghostty PPA on Ubuntu"), None)
    assert ghostty_ppa is not None
    assert "ansible.builtin.apt_repository" not in ghostty_ppa
    deb822 = ghostty_ppa.get("ansible.builtin.deb822_repository", {})
    assert deb822.get("name") == "ghostty-ubuntu"
    assert deb822.get("types") == ["deb"]
    assert deb822.get("uris") == ["https://ppa.launchpadcontent.net/mkasberg/ghostty-ubuntu/ubuntu"]
    assert deb822.get("suites") == ["{{ ansible_facts['distribution_release'] }}"]
    assert deb822.get("components") == ["main"]
    assert (
        deb822.get("signed_by")
        == "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x7981725F2B0C9E295E2C368B322003C4710E280B"
    )
    assert deb822.get("state") == "present"

    gui_terminal_task_names = [
        "Probe Warp terminal binary",
        "Ensure APT keyrings directory exists",
        "Fetch and dearmor Warp GPG signing key",
        "Configure Warp APT repository",
        "Install Warp terminal via apt",
        "Probe Ghostty binary",
        "Probe native Ghostty apt package availability",
        "Install Ghostty via native apt",
        "Probe snap command",
        "Install Ghostty via snap",
        "Add Ghostty PPA on Ubuntu",
        "Install Ghostty from PPA on Ubuntu",
    ]
    for task_name in gui_terminal_task_names:
        matched = next((t for t in packages_tasks if t.get("name") == task_name), None)
        assert matched is not None, f"missing task {task_name}"
        when_list = matched.get("when", [])
        assert isinstance(when_list, list)
        assert "not (devenv_is_wsl | default(false) | bool)" in when_list, f"{task_name} missing WSL skip guard"


def test_tmux_mouse_mode_enabled() -> None:
    """tmux configuration enables mouse mode by default for wheel scrolling."""
    tmux_conf = read(REPO_ROOT / "dotfiles" / "tmux" / ".tmux.conf")
    assert any(line.strip() == "set -g mouse on" for line in tmux_conf.splitlines())


def test_bootstrap_defines_devenv_is_wsl() -> None:
    """Bootstrap role sets devenv_is_wsl in Classify host platform and displays it in Show resolved plan."""
    bootstrap_tasks = yaml.safe_load(read(REPO_ROOT / "ansible" / "roles" / "bootstrap" / "tasks" / "main.yml"))
    classify = next((t for t in bootstrap_tasks if t.get("name") == "Classify host platform"), None)
    assert classify is not None
    assert "devenv_is_wsl" in classify.get("ansible.builtin.set_fact", {})

    show_plan = next((t for t in bootstrap_tasks if t.get("name") == "Show resolved plan"), None)
    assert show_plan is not None
    msgs = show_plan.get("ansible.builtin.debug", {}).get("msg", [])
    assert any("wsl: {{ devenv_is_wsl }}" in line for line in msgs)


def test_ansible_static_task_hygiene() -> None:
    """Every task across all roles and unlink.yml obeys command, check_mode, and APT module hygiene."""
    task_sources: list[tuple[str, list[dict]]] = []
    for path in role_task_files():
        rel = str(path.relative_to(REPO_ROOT))
        task_sources.append((rel, yaml.safe_load(read(path)) or []))

    unlink_path = REPO_ROOT / "ansible" / "playbooks" / "unlink.yml"
    for play in yaml.safe_load(read(unlink_path)) or []:
        task_sources.append(("ansible/playbooks/unlink.yml", play.get("tasks", [])))

    forbidden_modules = {
        "ansible.builtin.apt_repository",
        "apt_repository",
        "ansible.builtin.apt_key",
        "apt_key",
    }

    for source_name, tasks in task_sources:
        for task_def in tasks:
            task_name = task_def.get("name", "<unnamed>")
            label = f"{source_name} :: {task_name}"
            for mod in forbidden_modules:
                assert mod not in task_def, f"{label} uses deprecated module {mod}"

            if "ansible.builtin.command" in task_def:
                cmd_block = task_def["ansible.builtin.command"]
                assert isinstance(cmd_block, dict), f"{label} must use structured ansible.builtin.command mapping"
                cmd_str = cmd_block.get("cmd")
                assert isinstance(cmd_str, str) and cmd_str.strip(), f"{label} missing non-empty cmd string"
                cmd_no_jinja = re.sub(r"\{\{.*?\}\}", "", cmd_str, flags=re.DOTALL)
                if re.search(r"\$[A-Za-z_{]", cmd_no_jinja):
                    assert cmd_block.get("expand_argument_vars") is False, (
                        f"{label} references shell $VAR tokens in ansible.builtin.command.cmd and must set "
                        "expand_argument_vars: false so Ansible does not expand them from the parent environment"
                    )
                has_changed_when = "changed_when" in task_def
                has_creates = "creates" in cmd_block
                assert has_changed_when or has_creates, f"{label} must declare changed_when or creates"

                if task_def.get("changed_when") is False or "ansible_check_mode" in cmd_str:
                    assert task_def.get("check_mode") is False, f"{label} must declare check_mode: false"
                if "ansible_check_mode" in cmd_str:
                    when_cond = task_def.get("when", "")
                    when_str = " ".join(when_cond) if isinstance(when_cond, list) else str(when_cond)
                    assert "not ansible_check_mode or devenv_stow_bin.rc == 0" in when_str, (
                        f"{label} must guard stow dry-run execution when stow is absent in check mode"
                    )


def test_zsh_core_package_and_os_mapping(os_vars, group_vars, alias_tables) -> None:
    """Zsh must be declared in devenv_packages_core, aliased in apt, and skipped on Darwin."""
    assert "zsh" in group_vars.get("devenv_packages_core", []), "zsh missing from devenv_packages_core"
    assert alias_tables["apt"].get("zsh") == "zsh", "zsh missing or misaliased in pkg_apt.yml"
    assert "zsh" in os_vars["Darwin"].get("devenv_pkg_skip", []), "zsh must be skipped on Darwin (OS-provided)"
    assert "zsh" not in os_vars["Linux"].get("devenv_pkg_skip", []), "zsh must not be skipped on Linux"


def test_node_role_unified_nvm_versions_node_paths() -> None:
    """Node role must ensure versions/node directory and point creates and current symlink at versions/node."""
    node_tasks = yaml.safe_load(read(REPO_ROOT / "ansible" / "roles" / "node" / "tasks" / "main.yml"))

    versions_dir_task = next(
        (
            t
            for t in node_tasks
            if t.get("ansible.builtin.file", {}).get("path") == "{{ devenv_home }}/.local/share/nvm/versions/node"
        ),
        None,
    )
    assert versions_dir_task is not None, "Missing task ensuring ~/.local/share/nvm/versions/node directory"
    assert versions_dir_task["ansible.builtin.file"].get("state") == "directory"
    assert versions_dir_task["ansible.builtin.file"].get("mode") == "0755"

    install_task = next(
        (t for t in node_tasks if t.get("name") == "Install the pinned node through nvm"),
        None,
    )
    assert install_task is not None, "Missing 'Install the pinned node through nvm' task"
    assert (
        install_task.get("ansible.builtin.command", {}).get("creates")
        == "{{ devenv_home }}/.local/share/nvm/versions/node/v{{ devenv_node_version }}/bin/node"
    )

    current_task = next(
        (
            t
            for t in node_tasks
            if t.get("name") == "Point `current` at the pinned version (PATH entry for non-interactive shells)"
        ),
        None,
    )
    assert current_task is not None, "Missing task pointing current at the pinned version"
    current_file = current_task.get("ansible.builtin.file", {})
    assert current_file.get("src") == "{{ devenv_home }}/.local/share/nvm/versions/node/v{{ devenv_node_version }}"
    assert current_file.get("dest") == "{{ devenv_home }}/.local/share/nvm/current"
    assert current_file.get("state") == "link"


def test_node_role_clean_env_shell_probes_and_canonical_path_assertions() -> None:
    """Node role probes bash, zsh, and fish under clean env -i and accepts canonical versions/node/v paths."""
    node_tasks = yaml.safe_load(read(REPO_ROOT / "ansible" / "roles" / "node" / "tasks" / "main.yml"))

    for shell_name, probe_var, verify_var in [
        ("bash", "devenv_has_bash", "devenv_node_which_bash"),
        ("zsh", "devenv_has_zsh", "devenv_node_which_zsh"),
        ("fish", "devenv_has_fish", "devenv_node_which"),
    ]:
        which_task = next((t for t in node_tasks if t.get("register") == probe_var), None)
        assert which_task is not None, f"Missing 'which {shell_name}' availability task ({probe_var})"
        assert which_task.get("ansible.builtin.command", {}).get("cmd") == f"which {shell_name}"
        assert which_task.get("changed_when") is False
        assert which_task.get("failed_when") is False
        assert which_task.get("check_mode") is False

        verify_task = next((t for t in node_tasks if t.get("register") == verify_var), None)
        assert verify_task is not None, f"Missing node login-shell probe task ({verify_var})"
        assert verify_task.get("changed_when") is False
        assert verify_task.get("check_mode") is False
        cmd_block = verify_task.get("ansible.builtin.command", {})
        assert cmd_block.get("expand_argument_vars") is False
        cmd_str = cmd_block.get("cmd", "")
        assert "env -i" in cmd_str
        assert f"{shell_name} -lc" in cmd_str
        assert "which node; node -v" in cmd_str
        assert f"({probe_var}.stdout | trim) | dirname" in cmd_str
        assert verify_task.get("when") == ["not ansible_check_mode", f"{probe_var}.rc == 0"]

        assert_task = next(
            (
                t
                for t in node_tasks
                if isinstance(t.get("ansible.builtin.assert"), dict)
                and any(f"{verify_var}.stdout" in cond for cond in t["ansible.builtin.assert"].get("that", []))
            ),
            None,
        )
        assert assert_task is not None, f"Missing ansible.builtin.assert task for {verify_var}"
        assert assert_task.get("when") == ["not ansible_check_mode", f"{probe_var}.rc == 0"]
        that_conds = assert_task["ansible.builtin.assert"].get("that", [])
        path_cond = that_conds[0]
        assert f"'.local/share/nvm/current/bin/node' in {verify_var}.stdout" in path_cond
        assert f"'.local/bin/node' in {verify_var}.stdout" in path_cond
        assert (
            f"('.local/share/nvm/versions/node/v' ~ devenv_node_version ~ '/bin/node') in {verify_var}.stdout"
            in path_cond
        )
        assert f"'v' ~ devenv_node_version in {verify_var}.stdout" in that_conds[1]


def test_fish_role_find_follows_stow_symlinks() -> None:
    """Fish role Collect linked fish files task sets follow: true so GNU Stow symlinks are syntax-checked."""
    fish_tasks = yaml.safe_load(read(REPO_ROOT / "ansible" / "roles" / "fish" / "tasks" / "main.yml"))
    collect_task = next((t for t in fish_tasks if t.get("name") == "Collect linked fish files"), None)
    assert collect_task is not None, "Missing 'Collect linked fish files' task in fish role"
    assert collect_task.get("ansible.builtin.find", {}).get("follow") is True


def test_homebrew_module_tasks_pass_dirname_to_path() -> None:
    """Every community.general.homebrew* task across roles passes devenv_brew_bin | dirname to path."""
    role_names = ("homebrew", "packages", "conda", "neovim")
    brew_modules = (
        "community.general.homebrew",
        "community.general.homebrew_tap",
        "community.general.homebrew_cask",
    )
    checked_count = 0
    for role_name in role_names:
        role_path = REPO_ROOT / "ansible" / "roles" / role_name / "tasks" / "main.yml"
        tasks = yaml.safe_load(read(role_path)) or []
        for task_def in tasks:
            for mod_name in brew_modules:
                if mod_name in task_def:
                    checked_count += 1
                    path_param = task_def[mod_name].get("path", "")
                    assert "devenv_brew_bin | dirname" in path_param, (
                        f"{role_name} :: {task_def.get('name')} ({mod_name}) must pass "
                        f"devenv_brew_bin | dirname to path, got {path_param!r}"
                    )
    assert checked_count == 7, f"Expected 7 community.general.homebrew* tasks across roles, found {checked_count}"

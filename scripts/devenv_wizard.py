#!/usr/bin/env python3
"""Interactive host pre-Ansible configuration wizard for dev-env.

Collects user choices on platform backends, dotfile stow variants, dotfile
conflicts, runtime pins, and feature flags before Ansible executes, persisting
decisions to ~/.config/dev-env/choices.yml.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


def load_versions() -> dict[str, str]:
    """Load authoritative versions from versions.json at repository root."""
    versions_path = Path(__file__).resolve().parent.parent / "versions.json"
    if versions_path.exists():
        try:
            data = json.loads(versions_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def dump_yaml_fallback(data: dict[str, Any]) -> str:
    """Minimal YAML dumper fallback when PyYAML is not installed."""
    lines = ["---"]

    def _dump_val(v: Any, indent: int = 0) -> list[str]:
        pad = " " * indent
        res: list[str] = []
        if isinstance(v, bool):
            res.append(f"{'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            res.append(f"{v}")
        elif isinstance(v, str):
            res.append(f"\"{v}\"" if (":" in v or " " in v or not v) else v)
        elif isinstance(v, list):
            if not v:
                res.append("[]")
            else:
                for item in v:
                    val_lines = _dump_val(item, indent + 2)
                    res.append(f"\n{pad}- {val_lines[0]}")
                    for sub in val_lines[1:]:
                        res.append(f"\n{pad}  {sub}")
        elif isinstance(v, dict):
            if not v:
                res.append("{}")
            else:
                for k, sub_v in v.items():
                    val_lines = _dump_val(sub_v, indent + 2)
                    if isinstance(sub_v, (dict, list)) and sub_v:
                        res.append(f"\n{pad}{k}:{val_lines[0] if val_lines[0].startswith('\n') else ' ' + val_lines[0]}")
                        for sub in val_lines[1:]:
                            res.append(f"{sub}")
                    else:
                        res.append(f"\n{pad}{k}: {val_lines[0]}")
        return res

    for key, value in data.items():
        if isinstance(value, (dict, list)) and value:
            rendered = "".join(_dump_val(value, 2))
            lines.append(f"{key}:{rendered}")
        else:
            lines.append(f"{key}: {''.join(_dump_val(value, 0))}")

    return "\n".join(lines) + "\n"


def _parse_yaml_scalar(val: str) -> Any:
    val = val.strip()
    if (val.startswith('"') and val.endswith('"') and len(val) >= 2) or (
        val.startswith("'") and val.endswith("'") and len(val) >= 2
    ):
        val = val[1:-1]
    if val == "true":
        return True
    if val == "false":
        return False
    if val == "[]":
        return []
    if val == "{}":
        return {}
    return val


def load_yaml_fallback(text: str) -> dict[str, Any]:
    """Minimal YAML loader fallback for choices.yml."""
    if yaml is not None:
        loaded = yaml.safe_load(text)
        return loaded if isinstance(loaded, dict) else {}

    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line == "---":
            continue
        indent = len(raw_line) - len(raw_line.lstrip())
        if indent == 0 and ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if not val:
                current_key = key
                result[key] = {} if key == "devenv_selected_variants" else []
            else:
                result[key] = _parse_yaml_scalar(val)
                current_key = None
        elif current_key is not None and indent > 0:
            if line.startswith("- "):
                item = line[2:].strip()
                if not isinstance(result.get(current_key), list):
                    result[current_key] = []
                result[current_key].append(_parse_yaml_scalar(item))
            elif ":" in line:
                sub_k, sub_v = line.split(":", 1)
                sub_k = sub_k.strip()
                sub_v = sub_v.strip()
                if not isinstance(result.get(current_key), dict):
                    result[current_key] = {}
                result[current_key][sub_k] = _parse_yaml_scalar(sub_v)
    return result


def detect_platform() -> dict[str, str]:
    """Detect operating system, architecture, and package manager backend."""
    sys_name = platform.system()
    machine = platform.machine()
    distro = ""
    backend = "unsupported"

    if sys_name == "Darwin":
        backend = "brew"
        distro = "macOS"
    elif sys_name == "Linux":
        backend = "apt"
        os_release = Path("/etc/os-release")
        if os_release.exists():
            try:
                for line in os_release.read_text(encoding="utf-8").splitlines():
                    if line.startswith("PRETTY_NAME="):
                        distro = line.split("=", 1)[1].strip('"\'')
                        break
                    if line.startswith("NAME=") and not distro:
                        distro = line.split("=", 1)[1].strip('"\'')
            except OSError:
                pass
        if not distro:
            distro = "Linux"

    return {
        "system": sys_name,
        "machine": machine,
        "distro": distro,
        "backend": backend,
    }


def get_available_variants(repo_root: Path) -> dict[str, list[str]]:
    """Discover tool variants by inspecting dotfiles/ subdirectories."""
    variants: dict[str, list[str]] = {"nvim": ["kickstart", "minimal", "lazyvim"]}
    dotfiles = repo_root / "dotfiles"
    if dotfiles.exists():
        nvim_dirs = [p.name.removeprefix("nvim-") for p in dotfiles.glob("nvim-*") if p.is_dir()]
        if nvim_dirs:
            variants["nvim"] = sorted(nvim_dirs)
    return variants


def resolve_stow_packages(
    base_packages: list[str],
    variant_selections: dict[str, str],
) -> list[str]:
    """Resolve concrete stow packages replacing variant keys with their selection."""
    result: list[str] = []
    for pkg in base_packages:
        if pkg in variant_selections:
            variant = variant_selections[pkg]
            result.append(f"{pkg}-{variant}")
        else:
            result.append(pkg)
    return sorted(set(result))


def scan_dotfile_conflicts(
    repo_root: Path,
    home_dir: Path,
    active_packages: list[str],
) -> list[dict[str, Any]]:
    """Scan target paths in home directory for conflicts with active stow packages."""
    conflicts: list[dict[str, Any]] = []
    dotfiles = repo_root / "dotfiles"

    for pkg_name in active_packages:
        pkg_dir = dotfiles / pkg_name
        if not pkg_dir.is_dir():
            continue
        for src_path in pkg_dir.rglob("*"):
            if not src_path.is_file():
                continue
            rel_path = src_path.relative_to(pkg_dir)
            dest_path = home_dir / rel_path

            if not dest_path.exists() and not dest_path.is_symlink():
                continue

            # If dest_path is already a symlink pointing to src_path, no conflict
            if dest_path.is_symlink():
                try:
                    if dest_path.resolve() == src_path.resolve():
                        continue
                except OSError:
                    pass

            # If destination is regular file, compare contents
            if dest_path.is_file() and not dest_path.is_symlink():
                try:
                    src_content = src_path.read_bytes()
                    dest_content = dest_path.read_bytes()
                    if src_content == dest_content:
                        continue
                except OSError:
                    pass

            conflicts.append({
                "package": pkg_name,
                "rel_path": str(rel_path),
                "src_path": src_path,
                "dest_path": dest_path,
            })

    return conflicts


def format_diff(src_path: Path, dest_path: Path) -> str:
    """Return side-by-side or unified diff between repository package file and home file."""
    cols = shutil.get_terminal_size(fallback=(80, 24)).columns

    if shutil.which("delta"):
        try:
            result = subprocess.run(
                ["delta", "--side-by-side", "-w", str(cols), str(dest_path), str(src_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode in (0, 1) and result.stdout:
                return result.stdout
        except OSError:
            pass

    if shutil.which("diff"):
        try:
            result = subprocess.run(
                ["diff", "-y", "-W", str(cols), str(dest_path), str(src_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode in (0, 1) and result.stdout:
                return result.stdout
        except OSError:
            pass

    src_lines = src_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    dest_lines = dest_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    diff = difflib.unified_diff(
        dest_lines,
        src_lines,
        fromfile=f"target: {dest_path}",
        tofile=f"repo: {src_path}",
    )
    return "".join(diff)


def backup_file(target_path: Path, home_dir: Path, timestamp: str | None = None) -> Path:
    """Back up target file to ~/.local/share/dev-env/backup/<timestamp>/."""
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = home_dir / ".local" / "share" / "dev-env" / "backup" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    safe_name = str(target_path).lstrip("/").replace("/", "__")
    backup_target = backup_dir / safe_name
    shutil.copy2(target_path, backup_target, follow_symlinks=False)
    return backup_target


def extract_local_override(
    target_path: Path,
    home_dir: Path,
    timestamp: str | None = None,
) -> Path:
    """Extract destination file customizations to the corresponding .local file."""
    filename = target_path.name
    if filename in (".bashrc", "bashrc"):
        local_override = home_dir / ".bashrc.local"
    elif filename in (".bash_profile", "bash_profile"):
        local_override = home_dir / ".bash_profile.local"
    elif filename in (".zshrc", "zshrc"):
        local_override = home_dir / ".zshrc.local"
    elif "fish" in str(target_path):
        local_override = home_dir / ".config" / "fish" / "conf.d" / "99-local.fish"
    else:
        local_override = home_dir / f"{filename}.local"

    local_override.parent.mkdir(parents=True, exist_ok=True)
    backup_file(target_path, home_dir, timestamp=timestamp)

    content = target_path.read_text(encoding="utf-8", errors="replace")
    header = f"\n# --- Extracted from {target_path} on {datetime.date.today()} ---\n"
    with open(local_override, "a", encoding="utf-8") as f:
        f.write(header + content + "\n")

    return local_override


def adopt_file(
    target_path: Path,
    src_path: Path,
    home_dir: Path,
    timestamp: str | None = None,
) -> None:
    """Adopt target file into repo package directory and back up target."""
    backup_file(target_path, home_dir, timestamp=timestamp)
    src_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target_path, src_path)


def prompt_user(
    prompt_str: str,
    default: str | None = None,
    interactive: bool = True,
) -> str:
    """Prompt the user via /dev/tty or sys.stdin, returning default if non-interactive."""
    if not interactive:
        return default or ""
    display_prompt = f"{prompt_str} [{default}]: " if default else f"{prompt_str}: "

    try:
        with open("/dev/tty", "r") as tty_in, open("/dev/tty", "w") as tty_out:
            tty_out.write(display_prompt)
            tty_out.flush()
            line = tty_in.readline()
            if not line:
                return default or ""
            val = line.strip()
            return val if val else (default or "")
    except OSError:
        pass

    try:
        sys.stdout.write(display_prompt)
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line:
            return default or ""
        val = line.strip()
        return val if val else (default or "")
    except (OSError, EOFError):
        return default or ""


def run_wizard(
    repo_root: Path,
    home_dir: Path,
    choices_file: Path,
    interactive: bool = True,
) -> dict[str, Any]:
    """Execute the full 5-step wizard (A-E) and persist choices."""
    existing_choices: dict[str, Any] = {}
    if choices_file.exists():
        try:
            content = choices_file.read_text(encoding="utf-8")
            existing_choices = load_yaml_fallback(content)
        except (OSError, ValueError):
            pass

    # --- Step A: OS / Distro & Backend Confirmation ---
    plat_info = detect_platform()
    detected_backend = plat_info["backend"]
    if detected_backend not in ("brew", "apt"):
        detected_backend = "apt" if plat_info["system"] == "Linux" else "brew"

    chosen_backend = existing_choices.get("devenv_pkg_backend", detected_backend)
    if interactive:
        prompt_msg = (
            f"Detected {plat_info['distro']} ({plat_info['machine']}). "
            f"Package backend"
        )
        ans = prompt_user(prompt_msg, default=chosen_backend, interactive=True)
        if ans.lower() in ("brew", "apt"):
            chosen_backend = ans.lower()

    # --- Step B: Stow Package & Multi-Variant Selection ---
    base_stow_tools = ["bash", "conda", "fish", "nvim", "tmux", "zsh"]
    variants = get_available_variants(repo_root)
    selected_variants: dict[str, str] = existing_choices.get("devenv_selected_variants", {})
    if not isinstance(selected_variants, dict):
        selected_variants = {}

    nvim_default = selected_variants.get("nvim", "kickstart")
    if interactive:
        nvim_opts = variants.get("nvim", ["kickstart", "minimal", "lazyvim"])
        prompt_msg = f"Select Neovim variant ({', '.join(nvim_opts)})"
        ans = prompt_user(prompt_msg, default=nvim_default, interactive=True)
        if ans in nvim_opts:
            selected_variants["nvim"] = ans
        else:
            selected_variants["nvim"] = nvim_default
    else:
        selected_variants.setdefault("nvim", nvim_default)

    active_stow_packages = resolve_stow_packages(base_stow_tools, selected_variants)

    # --- Step C: Interactive Dotfile Conflict Resolution ---
    skip_links: list[str] = list(existing_choices.get("devenv_skip_links", []))
    conflicts = scan_dotfile_conflicts(repo_root, home_dir, active_stow_packages)

    for conflict in conflicts:
        dest_path: Path = conflict["dest_path"]
        src_path: Path = conflict["src_path"]
        dest_str = str(dest_path)

        if dest_str in skip_links:
            continue

        if not interactive:
            # Default to backup in non-interactive mode
            backup_file(dest_path, home_dir)
            continue

        print(f"\n[Conflict] File differs: {dest_path}")
        while True:
            choice = prompt_user(
                "Options: [d]iff, [m]erge, [l]ocal override, [a]dopt, [b]ackup & replace, [s]kip",
                default="b",
                interactive=True,
            ).lower()

            if choice == "d":
                diff_text = format_diff(src_path, dest_path)
                print(diff_text if diff_text else "(No visible differences)")
                continue
            elif choice == "m":
                editor = os.environ.get("EDITOR", "nvim")
                backup_file(dest_path, home_dir)
                subprocess.run([editor, "-d", str(dest_path), str(src_path)], check=False)
                break
            elif choice == "l":
                extracted = extract_local_override(dest_path, home_dir)
                print(f"Extracted customizations to {extracted}")
                break
            elif choice == "a":
                adopt_file(dest_path, src_path, home_dir)
                print(f"Adopted {dest_path} into {src_path}")
                break
            elif choice == "b":
                backed_up = backup_file(dest_path, home_dir)
                print(f"Backed up to {backed_up}")
                break
            elif choice == "s":
                skip_links.append(dest_str)
                print(f"Skipped {dest_str}")
                break
            else:
                print("Invalid option. Please enter d, m, l, a, b, or s.")

    # --- Step D: Host Feature Flags & Runtime Pins ---
    set_login_shell = bool(existing_choices.get("devenv_set_login_shell", True))
    install_gui_casks = bool(existing_choices.get("devenv_install_gui_casks", True))
    remove_unmanaged = bool(existing_choices.get("devenv_remove_unmanaged", False))
    versions = load_versions()
    py_version = str(existing_choices.get("devenv_python_version", "3.13"))
    if "python" in versions and "devenv_python_version" not in existing_choices:
        py_version = versions["python"]
    node_version = str(existing_choices.get("devenv_node_default_version", "26.13.1"))
    if "node" in versions and "devenv_node_default_version" not in existing_choices:
        node_version = versions["node"]

    if interactive:
        ans_shell = prompt_user(
            "Change login shell to Fish? (true/false)",
            default=str(set_login_shell).lower(),
            interactive=True,
        )
        set_login_shell = ans_shell.lower() in ("true", "1", "yes", "y")

        if chosen_backend == "brew":
            ans_casks = prompt_user(
                "Install GUI casks (docker-desktop, ghostty, warp)? (true/false)",
                default=str(install_gui_casks).lower(),
                interactive=True,
            )
            install_gui_casks = ans_casks.lower() in ("true", "1", "yes", "y")
        elif chosen_backend == "apt":
            ans_casks = prompt_user(
                "Install GUI terminal apps (ghostty, warp)? (true/false)",
                default=str(install_gui_casks).lower(),
                interactive=True,
            )
            install_gui_casks = ans_casks.lower() in ("true", "1", "yes", "y")

        py_version = prompt_user("Python version", default=py_version, interactive=True)
        node_version = prompt_user("Node.js default version", default=node_version, interactive=True)

    # --- Step E: Persist Choices ---
    choices: dict[str, Any] = {
        "devenv_pkg_backend": chosen_backend,
        "devenv_selected_variants": selected_variants,
        "devenv_stow_packages": active_stow_packages,
        "devenv_skip_links": sorted(set(skip_links)),
        "devenv_set_login_shell": set_login_shell,
        "devenv_install_gui_casks": install_gui_casks,
        "devenv_remove_unmanaged": remove_unmanaged,
        "devenv_python_version": py_version,
        "devenv_conda_env_python": py_version,
        "devenv_node_default_version": node_version,
    }

    choices_file.parent.mkdir(parents=True, exist_ok=True)
    yaml_content = dump_yaml_fallback(choices)
    temp_file = choices_file.with_suffix(".tmp")
    temp_file.write_text(yaml_content, encoding="utf-8")
    os.chmod(temp_file, 0o644)
    temp_file.replace(choices_file)

    return choices


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point for devenv_wizard.py."""
    parser = argparse.ArgumentParser(description="dev-env configuration wizard")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without prompting, using defaults or pre-existing choices",
    )
    parser.add_argument(
        "--choices-file",
        type=Path,
        default=Path(os.environ.get("HOME", str(Path.home()))) / ".config" / "dev-env" / "choices.yml",
        help="Path to output choices.yml",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path(os.environ.get("HOME", str(Path.home()))),
        help="User home directory",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Root directory of dev-env repository",
    )

    args = parser.parse_args(argv)

    is_interactive = not args.non_interactive
    if os.environ.get("CI") == "true" or (not sys.stdin.isatty() and not os.path.exists("/dev/tty")):
        is_interactive = False

    try:
        run_wizard(
            repo_root=args.repo_root,
            home_dir=args.home,
            choices_file=args.choices_file,
            interactive=is_interactive,
        )
        print(f"dev-env wizard configured successfully. Choices saved to {args.choices_file}")
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"dev-env wizard error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

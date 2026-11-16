# Plan for I-1794797329-wizard

- **Plan ID:** P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794797329-wizard
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-16T02:49:50Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent specifies a coherent, exceptionally high-value transformation:
  enforcing pure `make -> conda -> ansible` toolchain bootstrap (GNU Make as sole cold-start prerequisite; git/curl
  deferred to Ansible; uv installed via Conda for app dev), introducing multi-variant GNU Stow packages
  (`nvim-kickstart`, `nvim-minimal`, `nvim-lazyvim`), implementing a host pre-Ansible interactive wizard
  (`scripts/devenv_wizard.py` and `make configure`), completely overhauling `README.md` to make the execution chain and
  package inventory blindingly obvious, updating world rules/constraints, and adding comprehensive tests.
- **Exploration stance:** balanced with targeted empirical verification of Conda installer resolution across platforms,
  multi-variant unstow/restow logic, TTY and non-interactive wizard execution paths, and regex-driven documentation
  manifest verifications.
- **Safety priority level:** standard
- **Priority Justification:** Triggered by `holon-config/world/ruleset.md` §1 (Multi-OS Darwin/Linux parity, GNU Make
  3.81 compatibility, no shell scripts outside package managers, pure `make -> conda -> ansible` chain),
  `holon-config/world/ruleset.md` §2 (Coding conventions, static typing, Prettier markdown formatting with code-span
  arithmetic), `holon-config/world/ruleset.md` §3 (Testing constraints: pytest runner, explicit test modification
  declarations), `holon-config/world/constraints.md` §1 (Branch isolation and git flow),
  `holon-config/world/constraints.md` §3 (Environment mutation boundaries: converge through manifest, never write
  outside repo except through Ansible).

## Exploration

- **Proportion of steps that are exploratory:** 0.33
- **Justification:** Steps 2 and 3 incorporate exploratory validation of multi-variant GNU Stow symlink trees and
  interactive TTY dotfile conflict resolution flows (`fzf` / numbered prompt, diff, merge, local override, adopt,
  backup, skip).

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.94  |
| entropy_pred        | 0.65  |
| impact_pred         | 96.0  |
| cost_pred           | 14.5  |
| learning_value_pred | 6.0   |
| ev_pred             | 78.55 |

---

## Step 1: Pure `make -> conda -> ansible` Tool Chain and Prerequisite Decoupling

- **Sub‑intent recommendation:** NO
- **Reasoning:** Essential foundation for the entire repository lifecycle. Eliminating `git`, `curl`, and `uv` as
  cold-start prerequisites establishes GNU Make (`>= 3.81`) as the sole host requirement, while shifting bootstrap
  interpreter and Ansible provisioning cleanly onto Miniforge Conda.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Fetching the Miniforge3 installer using platform-native fetchers (`curl`, `wget`, or
  system Python `urllib.request`) and provisioning Ansible (`ansible-core`, `ansible-lint`, `pyyaml`,
  `community.general`) strictly through Conda completely decouples bootstrap from `uv` and host package managers, while
  deferring `git` and `curl` to Ansible's `packages` role.
- **Learning target:** Verify resilient cross-platform Miniforge installer resolution and Conda channel override
  behavior (`-c conda-forge --override-channels python=3.13 ansible-core ansible-lint pyyaml`) across Darwin and Linux
  architectures.
- **Maximum acceptable cost for this learning:** 2.5

### Intent & Git Integration

- **Step Intent:** Enforce pure `make -> conda -> ansible` toolchain bootstrap in `Makefile`, `ansible/site.yml`, and
  `ansible/roles/uv/tasks/main.yml`. Define `CONDA_DIR ?= $(HOME)/miniforge3` and `CONDA ?= $(CONDA_DIR)/bin/conda`.
  Resolve Darwin/Linux Miniforge3 installer dynamically. Install `python=3.13`, `ansible-core`, `ansible-lint`, `pyyaml`
  via Conda. Shim Ansible binaries into `~/.local/share/dev-env/bin/`. Update `make check` to probe `GNU Make` -> `OS`
  -> `apt` -> `conda` -> `ansible-core` -> `community.general` -> `stow` -> `brew` -> `git`/`curl` (informational only).
  Reorder `ansible/site.yml` so `conda` runs before `uv`. Remove `astral.sh/uv/install.sh` and `uv tool install` from
  `Makefile` and `uv` role; install `uv`, `ruff`, `pre-commit` via Conda.
- **Git branch:**
  `I-1794797329-wizard/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium/E-1-conda-bootstrap-chain/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Makefile Bootstrap & Shims:
   - Define `CONDA_DIR ?= $(HOME)/miniforge3` and `CONDA ?= $(CONDA_DIR)/bin/conda`.
   - In `make bootstrap` Step 1: check if `$(CONDA)` exists. If absent, detect OS (`Darwin` vs `Linux`) and machine
     architecture (`arm64`/`aarch64` vs `x86_64`/`amd64`). Select installer filename: `Miniforge3-MacOSX-arm64.sh` or
     `Miniforge3-MacOSX-x86_64.sh` on Darwin; `Miniforge3-Linux-aarch64.sh` or `Miniforge3-Linux-x86_64.sh` on Linux.
     Fetch into `$$HOME/.cache/dev-env/` using `curl -fsSL`, `wget -qO`, or `python3 -c "import urllib.request..."`.
     Execute installer with `-b -u -p "$(CONDA_DIR)"`.
   - In `make bootstrap` Step 2: run
     `"$(CONDA)" install -y -c conda-forge --override-channels python=3.13 ansible-core ansible-lint pyyaml`.
   - Link shims into `$(BIN)`: `$(CONDA_DIR)/bin/ansible-playbook` to `$(PB)`, `$(CONDA_DIR)/bin/ansible-galaxy` to
     `$(GALAXY)`, and `$(CONDA_DIR)/bin/ansible-lint` to `$(LINT)`.
   - Install `community.general` via
     `ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)" "$(GALAXY)" collection install -r "$(SELF_DIR)/ansible/requirements.yml" --force`.
   - Completely remove `curl https://astral.sh/uv/install.sh` and `uv tool install` from `Makefile`.
2. Makefile Prerequisite Probe (`check` target):
   - Probe `GNU Make >= 3.81` first (fatal if missing or `< 3.81`).
   - Probe `OS` (fatal if not `Darwin` or `Linux`).
   - Probe `apt` on Linux (fatal if missing `apt-get`).
   - Probe `conda` (`$(CONDA)`) (informational warning: will be installed by `make bootstrap`).
   - Probe `ansible-core` (`$(PB)`) (informational warning).
   - Probe `community.general` (`$(COLLECTIONS)`) (informational warning).
   - Probe `stow` (informational warning: will be installed by packages role).
   - Probe `brew` on macOS (informational warning).
   - Probe `git` and `curl` as deferred informational checks (report `ok` if found, or report
     `deferred: will be installed by Ansible packages role`, never incrementing fatal error count).
   - Preserve 100% GNU Make 3.81 compatibility. Keep `make test` and `make test-all` running smoothly.
3. Ansible Playbook Order & UV Role Refactoring:
   - In `ansible/site.yml`: reorder role execution to ensure `conda` executes before `uv`:
     `bootstrap -> homebrew -> packages -> dotfiles -> conda -> uv -> node -> neovim -> fish`.
   - In `ansible/roles/uv/tasks/main.yml`: remove all tasks downloading `https://astral.sh/uv/install.sh` or invoking
     `uv tool install`.
   - Install `uv` and `devenv_uv_tools` (`ruff`, `pre-commit`) through Conda via:
     `"{{ devenv_conda_dir }}/bin/conda" install -y -c conda-forge --override-channels uv {{ devenv_uv_tools | join(' ') }}`.
   - Assert `{{ devenv_conda_dir }}/bin/uv` exists and is executable.

### Dependencies & Criticality

- **Depends on:** NONE
- **Is Bottleneck:** YES (Downstream role execution and wizard commands rely on Conda Python and Ansible tooling)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS Darwin/Linux parity, GNU Make 3.81 compatibility,
  pure `make -> conda -> ansible` chain), `holon-config/world/constraints.md` §3 (Converge through the manifest).
- **Potential failure modes for this step:** Broken Miniforge download fallback when neither `curl` nor `wget` is
  installed (handled by Python 3 `urllib.request` fallback); stale shims in `~/.local/share/dev-env/bin/`.
- **Guardrails and early‑abort checks:** Validate installer sha256 or check return code; verify `test -x "$(PB)"`
  immediately after bootstrap shims are linked.

### Success & Discard Criteria

- **Success:** `make check` succeeds cleanly without requiring `git`, `curl`, or `uv`. `make bootstrap` provisions Conda
  and shims Ansible tools into `~/.local/share/dev-env/bin/`. `ansible/site.yml` runs `conda` before `uv`, and
  `ansible/roles/uv/tasks/main.yml` installs `uv` and tooling via Conda.
- **Discard:** Discard if GNU Make 3.81 compatibility is violated or if `make check` fails due to absent `git`/`curl`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.96  |
| entropy_pred        | 0.40  |
| impact_pred         | 92.0  |
| cost_pred           | 2.5   |
| learning_value_pred | 3.5   |
| ev_pred             | 87.45 |

### Step Metrics Rationale

Calculated via: `EV = 0.96 * 92.0 + 0.5 * 3.5 - 0.3 * 0.40 - 2.5 = 88.32 + 1.75 - 0.12 - 2.5 = 87.45`. High determinism
with minimal entropy, decoupling bootstrap dependencies cleanly.

---

## Step 2: Multi-Variant GNU Stow Architecture and Inactive Variant Management

- **Sub‑intent recommendation:** NO
- **Reasoning:** Modularizes dotfiles configuration into pluggable tool variants, enabling user customizability (such as
  Neovim kickstart vs minimal vs lazyvim) while maintaining strict idempotency through automated unlinking of inactive
  variants.
- **Step Type:** ARCHITECTURE
- **Exploration level:** EXPLORE
- **Hypothesis being tested:** Structuring `dotfiles/` into distinct variant packages (`nvim-kickstart`, `nvim-minimal`,
  `nvim-lazyvim`), dynamically computing active Stow packages while explicitly executing `stow --delete` for inactive
  variants, avoids symlink collisions and supports arbitrary user config choices without manual dotfile cleanup.
- **Learning target:** Confirm Stow behavior when deleting inactive packages whose target files share common parent
  directories (`~/.config/nvim/`) without removing shared parent directories.
- **Maximum acceptable cost for this learning:** 2.5

### Intent & Git Integration

- **Step Intent:** Migrate `dotfiles/nvim/` to `dotfiles/nvim-kickstart/`; create `dotfiles/nvim-minimal/` (lightweight
  `vim.pack` config) and `dotfiles/nvim-lazyvim/` (LazyVim starter config). Declare `devenv_package_variants` in
  `ansible/group_vars/all.yml` with `nvim` defaulting to `kickstart`. Declare `devenv_skip_links: []`. Update
  `ansible/roles/bootstrap/tasks/main.yml` to check for and load `~/.config/dev-env/choices.yml` if present. Update
  `ansible/roles/dotfiles/tasks/main.yml` and `ansible/playbooks/unlink.yml` to unstow inactive variants before stowing
  active packages, filtering out any paths in `devenv_skip_links`. Update `ansible/roles/neovim/tasks/main.yml` so
  plugin checks adapt to the active variant.
- **Git branch:**
  `I-1794797329-wizard/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium/E-2-multi-variant-stow/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Variant Directory Migration and Structure:
   - Move existing `dotfiles/nvim/` contents to `dotfiles/nvim-kickstart/` (`.config/nvim/...`).
   - Create `dotfiles/nvim-minimal/.config/nvim/init.lua` providing a lean, high-speed Neovim configuration leveraging
     built-in `vim.pack` with minimal plugins and standard settings.
   - Create `dotfiles/nvim-lazyvim/.config/nvim/` providing a canonical LazyVim starter structure (`init.lua`,
     `lua/config/lazy.lua`, `lua/config/keymaps.lua`, `lua/config/options.lua`, `lua/plugins/example.lua`).
2. Declarative Variant Manifest (`group_vars/all.yml`):
   - Declare `devenv_package_variants` defining tool mappings:
     - Key `nvim` mapped to `default: kickstart` and available variants: `kickstart` (`package: nvim-kickstart`),
       `minimal` (`package: nvim-minimal`), `lazyvim` (`package: nvim-lazyvim`).
   - Define `devenv_skip_links: []` in `group_vars/all.yml`.
   - Update `devenv_links` and `devenv_stow_packages` calculation so the active variant package (e.g. `nvim-kickstart`)
     is used, while ensuring invariant link definitions exist for testing and fallback.
3. Choices Loading in Bootstrap Role (`ansible/roles/bootstrap/tasks/main.yml`):
   - Inspect `~/.config/dev-env/choices.yml` using `ansible.builtin.stat`.
   - When the file exists, include it via `ansible.builtin.include_vars`.
   - Fall back smoothly to `group_vars/all.yml` defaults in CI and non-interactive runs.
   - Resolve active stow packages and identify inactive variant packages for all declared variant keys.
4. Dotfiles Role and Unlink Playbook Execution:
   - In `ansible/roles/dotfiles/tasks/main.yml`: identify inactive variant packages (e.g., if `nvim-kickstart` is
     active, inactive are `nvim-minimal` and `nvim-lazyvim`).
   - Run `stow --delete -d "{{ devenv_repo_root }}/dotfiles" -t "{{ devenv_home }}" <inactive_packages>` with
     `failed_when: false` to cleanly detach previous variant symlinks.
   - Filter `devenv_links` to exclude any paths present in `devenv_skip_links`.
   - Execute `stow --no-folding --restow` for active packages.
   - In `ansible/playbooks/unlink.yml`: ensure all declared variants (both active and inactive) are unlinked cleanly.
5. Neovim Role Plugin Checks:
   - In `ansible/roles/neovim/tasks/main.yml`: guard the `vim.pack` assertions and plugin sync tasks so they run when
     the active variant is `kickstart` (or `minimal`), avoiding irrelevant `nvim-pack-lock.json` sync failures when
     `lazyvim` is active.

### Dependencies & Criticality

- **Depends on:** Step 1 (Conda/Ansible environment operational)
- **Is Bottleneck:** NO (Stow variants are self-contained within dotfiles role and manifest)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Project layout, Stow packaging),
  `holon-config/world/constraints.md` §3 (Never write outside repo except through Ansible, Stow `--no-folding`).
- **Potential failure modes for this step:** Symlink collision when switching between variants if inactive variants are
  not unlinked first; missing target directories.
- **Guardrails and early‑abort checks:** Explicit unstow (`stow --delete`) step for all inactive variants before
  restowing active variant; verify `devenv_skip_links` filtering.

### Success & Discard Criteria

- **Success:** `nvim-kickstart`, `nvim-minimal`, and `nvim-lazyvim` packages are present and well-formed in `dotfiles/`.
  Active variant links cleanly via `stow --no-folding`. Inactive variants are unlinked without errors.
  `~/.config/dev-env/choices.yml` loads seamlessly when present.
- **Discard:** Discard if directory folding occurs or if variant switching leaves dangling or colliding symlinks.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.95  |
| entropy_pred        | 0.50  |
| impact_pred         | 90.0  |
| cost_pred           | 2.5   |
| learning_value_pred | 4.0   |
| ev_pred             | 84.85 |

### Step Metrics Rationale

Calculated via: `EV = 0.95 * 90.0 + 0.5 * 4.0 - 0.3 * 0.50 - 2.5 = 85.50 + 2.00 - 0.15 - 2.5 = 84.85`. Provides flexible
user customization with deterministic unlinking guarantees.

---

## Step 3: Host Interactive Pre-Ansible Wizard and Conflict Resolution Engine

- **Sub‑intent recommendation:** NO
- **Reasoning:** Central interactive orchestrator enabling smooth zero-surprise user onboarding. Captures user decisions
  on platform backends, variant packages, and dotfile conflict resolution prior to Ansible playbook execution.
- **Step Type:** FEATURE
- **Exploration level:** EXPLORE
- **Hypothesis being tested:** Providing an interactive Python wizard (`scripts/devenv_wizard.py`) with support for both
  TTY terminal interaction (`fzf`, `/dev/tty` menus, interactive diff/merge/adopt/local-extract) and `--non-interactive`
  batch mode enables flawless operation in both human interactive and CI/automated environments.
- **Learning target:** Evaluate TTY detection, interactive editor spawning (`nvim -d` / `$EDITOR -d`), and `.local`
  override extraction mechanisms across POSIX shells (`bash`, `zsh`, `fish`).
- **Maximum acceptable cost for this learning:** 3.5

### Intent & Git Integration

- **Step Intent:** Implement `scripts/devenv_wizard.py` in Python 3.13 supporting `--non-interactive`, `--choices-file`,
  `--home`, and `--repo-root` flags. Implement Step A (OS/backend detection & override), Step B (Stow package & variant
  selection via `fzf` or numbered menu), Step C (Dotfile conflict resolution: diff `[d]`, merge `[m]`, extract local
  override `[l]`, adopt `[a]`, backup `[b]`, skip `[s]`), Step D (Feature flags & runtime pins), and Step E (Persist
  choices to `~/.config/dev-env/choices.yml`). Add `make configure` in `Makefile` and invoke `configure` in
  `make install` when on interactive TTYs (`[ -t 0 ]` and `CI != true`) and choices file is absent.
- **Git branch:**
  `I-1794797329-wizard/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium/E-3-host-wizard/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. CLI Arguments and Architecture:
   - Create `scripts/devenv_wizard.py` using Python 3 standard library (`argparse`, `os`, `sys`, `subprocess`,
     `pathlib`, `shutil`, `difflib`).
   - Parse `--non-interactive`, `--choices-file` (default: `~/.config/dev-env/choices.yml`), `--home` (default:
     `$HOME`), and `--repo-root` (default: repo root resolved relative to script).
   - In non-interactive mode, load existing choices if present or emit defaults without blocking on stdin.
2. Step A: OS / Distro & Backend Confirmation:
   - Inspect `platform.system()`, `platform.machine()`, and `/etc/os-release` (on Linux).
   - Map platform to default backend (`Darwin` -> `brew`, `Linux` -> `apt`).
   - If interactive, prompt user to confirm or override detected backend.
3. Step B: Stow Package & Multi-Variant Selection:
   - List available Stow packages (`bash`, `conda`, `fish`, `nvim`, `tmux`, `zsh`).
   - For tools with variants (e.g. `nvim`), prompt selection between `kickstart`, `minimal`, and `lazyvim`.
   - Prefer `fzf` if installed on TTY; fall back to a clean numbered `/dev/tty` menu prompt.
4. Step C: Interactive Dotfile Conflict Resolution:
   - For all active package files, check corresponding destination in target `$HOME`.
   - If destination exists, is a regular file, is not a symlink to repo, and its content differs from the repo package
     file:
     - Prompt user with options:
       - `[d]`: diff contents using `delta` (if available) or Python `difflib`/`diff -u`.
       - `[m]`: interactive 3-way/2-way merge in `$EDITOR -d` (or `nvim -d`) using `/dev/tty`, then backup existing
         file.
       - `[l]`: extract local customizations into `.local` override file (`~/.bashrc.local`, `~/.bash_profile.local`,
         `~/.zshrc.local`, or `~/.config/fish/conf.d/99-local.fish`).
       - `[a]`: adopt destination file into repo package directory and back up original `$HOME` file.
       - `[b]`: back up `$HOME` file into `~/.local/share/dev-env/backup/` and allow Stow to link repo file.
       - `[s]`: skip linking this file (append destination path to `devenv_skip_links`).
5. Step D: Feature Flags and Runtime Pins:
   - Prompt confirmation for `devenv_set_login_shell` (default: `false`), `devenv_install_gui_casks` (default: `false`),
     and `devenv_remove_unmanaged` (default: `false`).
   - If conflicting packages are detected on host (e.g. `brew list node` or `brew list nvm`), highlight and recommend
     `devenv_remove_unmanaged: true`.
   - Confirm runtime version pins (`devenv_python_version: 3.13`, `devenv_conda_env_python: 3.13`,
     `devenv_node_default_version: 22`).
6. Step E: Persist Choices:
   - Serialize collected configuration to YAML in `~/.config/dev-env/choices.yml` with permissions `0600` (or `0644`).
   - Ensure parent directory `~/.config/dev-env` is created.
7. Makefile Integration:
   - Add target `configure` in `Makefile`: executes `$(CONDA_DIR)/bin/python3 scripts/devenv_wizard.py` with fallback to
     system `python3`.
   - In `make install`: check if `[ -t 0 ]` and `[ "$$CI" != "true" ]` and choices file does not exist; if so, trigger
     `configure` automatically before `bootstrap` and `converge`.

### Dependencies & Criticality

- **Depends on:** Step 1 (Makefile shims) and Step 2 (Variant structure)
- **Is Bottleneck:** NO (Wizard is pre-flight configuration step; playbook functions with default variables if wizard is
  bypassed)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (No shell scripts; Python 3.13 runtime),
  `holon-config/world/constraints.md` §3 (Destructive operations require explicit confirmation; never write outside repo
  except through Ansible, choices file is strictly user config).
- **Potential failure modes for this step:** Broken stdin handling when invoked in non-TTY environments (handled by
  `--non-interactive` flag and `os.isatty` checks); syntax errors in YAML output.
- **Guardrails and early‑abort checks:** Ensure `/dev/tty` is safely opened only when interactive; write choices file
  atomically using a temporary file and atomic rename.

### Success & Discard Criteria

- **Success:** `scripts/devenv_wizard.py` runs cleanly with `--non-interactive`, generating valid YAML choices. In
  interactive mode, all five steps (A-E) execute cleanly, correctly diffing, merging, backing up, or skipping dotfile
  conflicts. `make configure` runs properly from `Makefile`.
- **Discard:** Discard if wizard hangs on non-TTY runs or generates unparseable YAML.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.94  |
| entropy_pred        | 0.65  |
| impact_pred         | 95.0  |
| cost_pred           | 3.5   |
| learning_value_pred | 5.0   |
| ev_pred             | 88.11 |

### Step Metrics Rationale

Calculated via: `EV = 0.94 * 95.0 + 0.5 * 5.0 - 0.3 * 0.65 - 3.5 = 89.30 + 2.50 - 0.195 - 3.5 = 88.105 ~ 88.11`.
High-impact user experience upgrade containing exploratory interactive resolution options.

---

## Step 4: Comprehensive README Rework and Package Inventory Modernization

- **Sub‑intent recommendation:** NO
- **Reasoning:** Documentation is a first-class contract in this repository. Making the toolchain execution order,
  prerequisites, package inventory, and conflict resolution blindingly obvious guarantees clarity and prevents developer
  misconfiguration.
- **Step Type:** DOCS
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Placing an ASCII/Unicode flow diagram and stage-by-stage execution table at the top of
  `README.md` alongside exhaustive package tables satisfying `test_readme_manifest_coverage` provides clear, unambiguous
  guidance for new machine setups and day-to-day operations.
- **Learning target:** Ensure formatting meets strict single-pass Prettier constraints while incorporating exhaustive
  inventory tables (22 core packages, runtimes, Conda app-dev tools, variants, fish plugins, neovim plugins).
- **Maximum acceptable cost for this learning:** 2.0

### Intent & Git Integration

- **Step Intent:** Completely rework `README.md` to highlight the pure `make -> conda -> ansible` toolchain hierarchy,
  prerequisites by stage (sole prerequisite: `GNU Make >= 3.81`), bare-repo worktree clone instructions (`dev-env/.git`,
  `dev-env/main`), quick-start and day-to-day commands, full package tables (22 core packages, runtimes, Conda app-dev
  tools, Stow packages & variants, 3 fish plugins, 26 locked Neovim plugins, GUI casks, purged duplicates), interactive
  setup & merge walkthrough, and CI architecture.
- **Git branch:**
  `I-1794797329-wizard/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium/E-4-readme-rework/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Chain of Tools & Execution Order:
   - Place front-and-centre visual workflow diagram at the very top of `README.md`.
   - Provide a stage-by-stage table explaining the exact execution order:
     - **Sole Prerequisite (`GNU Make >= 3.81`):** Required for ANY action in `dev-env`. `git`, `curl`, and `uv` are NOT
       cold-start prerequisites. `git` and `curl` are deferred to Ansible's `packages` role; `uv` is installed via Conda
       purely as a user app-dev tool.
     - **Step 1 (`make bootstrap` -> Conda -> Ansible):** GNU Make installs Miniforge Conda into `~/miniforge3`, and
       Conda installs `python=3.13`, `ansible-core`, `ansible-lint`, `pyyaml`, and `community.general`.
     - **Step 2 (`make configure` -> Interactive Wizard):** Conda Python runs `scripts/devenv_wizard.py` to collect host
       settings, resolve dotfile conflicts, and write `~/.config/dev-env/choices.yml`.
     - **Step 3 (`make converge` -> Ansible):** Ansible converges the full system: `bootstrap` -> `homebrew`/`packages`
       (provisions 22 CLI packages including `git`, `curl`, `stow`) -> `dotfiles` (uses GNU Stow `--no-folding`) ->
       `conda` (`dev` environment) -> `uv` (installs `uv`, `ruff`, `pre-commit` via Conda) -> `node` -> `neovim` ->
       `fish`.
2. Repository Setup and Worktree Guide:
   - Document bare repository clone workflow: `git clone --bare <url> dev-env/.git` followed by worktree checkouts
     `git worktree add dev-env/main main` and subsequent branch worktrees `dev-env/<worktree>`.
3. Quick Start & Operational Commands:
   - Document `make check`, `make configure`, `make bootstrap`, `make install`, `make converge`, `make check-mode`,
     `make doctor`, `make dotfiles`, `make nvim-sync`, `make fisher`, `make unlink`, `make test`.
4. Complete Package Inventories:
   - Table of all 22 `devenv_packages_core` tools: logical name, macOS Homebrew formula, Linux APT package, and Stow
     status.
   - Table of language runtimes: Python (CPython 3.13 via Miniforge), Node.js (via nvm.fish).
   - Table of Conda-installed app-dev Python tools: `uv`, `ruff`, `pre-commit`.
   - Table of GNU Stow packages and variants: `bash`, `conda`, `fish`, `nvim` (`nvim-kickstart`, `nvim-minimal`,
     `nvim-lazyvim`), `tmux`, `zsh`.
   - Table of all 3 Fish plugins: `jorgebucaran/fisher`, `jorgebucaran/nvm.fish`, `pure-fish/pure`.
   - Table of all 26 locked Neovim plugins from `nvim-pack-lock.json`.
   - Table of macOS GUI casks (`devenv_casks`) and purged conflicting duplicates (`devenv_packages_remove`).
5. Interactive Wizard & Conflict Resolution Guide:
   - Walk through wizard steps A-E and explain all merge options (`[d]`, `[m]`, `[l]`, `[a]`, `[b]`, `[s]`).

### Dependencies & Criticality

- **Depends on:** Step 1, Step 2, and Step 3 (Documentation must accurately reflect finalized toolchain and packages)
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Markdown & Docs: backticks around code spans and arithmetic),
  `holon-config/world/ruleset.md` §3 (Test manifest coverage).
- **Potential failure modes for this step:** Prettier formatting failure or missing package name causing
  `test_readme_manifest_coverage` assertion failure.
- **Guardrails and early‑abort checks:** Run `npx prettier --check README.md` and `pytest tests/test_manifest.py`
  immediately after editing.

### Success & Discard Criteria

- **Success:** `README.md` displays the pure `make -> conda -> ansible` toolchain prominently. All tables are exhaustive
  and accurate. `test_readme_manifest_coverage` passes with zero assertion errors.
- **Discard:** Discard if any core package, runtime, plugin, or variant is omitted from `README.md`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.97  |
| entropy_pred        | 0.30  |
| impact_pred         | 92.0  |
| cost_pred           | 2.0   |
| learning_value_pred | 3.0   |
| ev_pred             | 88.65 |

### Step Metrics Rationale

Calculated via: `EV = 0.97 * 92.0 + 0.5 * 3.0 - 0.3 * 0.30 - 2.0 = 89.24 + 1.50 - 0.09 - 2.0 = 88.65`. High-certainty
documentation synchronization enforcing single-source-of-truth invariants.

---

## Step 5: World Documentation Synchronization and Comprehensive Test Automation

- **Sub‑intent recommendation:** NO
- **Reasoning:** Enforces strict adherence to repository invariants. Synchronizing world rules and expanding test
  coverage prevents regression, verifies wizard mechanics across edge cases, and solidifies architectural contracts.
- **Step Type:** TESTING
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Adding dedicated unit tests in `tests/test_wizard.py` combined with structural assertion
  updates in `tests/test_manifest.py` and `tests/test_templating.py` guarantees that no deprecated `astral.sh` or
  `uv tool install` patterns remain, role ordering is immutable, and all variant configurations remain valid.
- **Learning target:** Validate mock testing of TTY user input, sub-process diff/merge invocations, and choices file
  serialization in pytest.
- **Maximum acceptable cost for this learning:** 2.5

### Intent & Git Integration

- **Step Intent:** Update `holon-config/world/ruleset.md` and `holon-config/world/constraints.md` to reflect the pure
  `make -> conda -> ansible` bootstrap architecture, `scripts/devenv_wizard.py`, and `devenv_package_variants`. Create
  `tests/test_wizard.py` covering OS/distro detection, variant resolution, dotfile conflict detection, resolution flows
  (`[d]`, `[m]`, `[l]`, `[a]`, `[b]`, `[s]`), runtime pin overrides, choices persistence, and non-interactive execution.
  Update `tests/test_manifest.py` and `tests/test_templating.py` to assert: (a) absence of `astral.sh` and
  `uv tool install`, (b) `conda` runs before `uv` in `site.yml`, (c) `Makefile` `check` probes GNU Make and Conda
  non-fatally for `git`/`curl`/`uv`, (d) variant invariants, and (e) full README inventory coverage.
- **Git branch:**
  `I-1794797329-wizard/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium/E-5-tests-and-world-docs/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. World Model Documentation Updates:
   - In `holon-config/world/ruleset.md`:
     - §1: Replace references to `uv tool install --python 3.13` with Conda-managed Python and Ansible bootstrap
       tooling; document pure `make -> conda -> ansible` hierarchy; document multi-variant Stow packages
       (`devenv_package_variants`) and `scripts/devenv_wizard.py`.
   - In `holon-config/world/constraints.md`:
     - Update environment mutation boundaries to reflect Conda-based bootstrapping and multi-variant Stow package
       structures.
2. Wizard Test Suite (`tests/test_wizard.py`):
   - Test OS/distro and backend detection across Darwin and Linux (`/etc/os-release` parsing).
   - Test Stow package enumeration and variant resolution (e.g. `kickstart`, `minimal`, `lazyvim`).
   - Test dotfile conflict scanner (detect identical vs differing vs missing files).
   - Test conflict actions: diff formatting, merge triggering, local override extraction (`.bashrc.local`,
     `99-local.fish`), adopt into package directory, backup to `~/.local/share/dev-env/backup/`, and skip
     (`devenv_skip_links`).
   - Test runtime pin and flag prompts.
   - Test YAML serialization and permission setting (`0600`/`0644`) for `choices.yml`.
   - Test `--non-interactive` mode with and without pre-existing choices.
3. Manifest and Templating Invariants (`tests/test_manifest.py` & `tests/test_templating.py`):
   - Assert `astral.sh/uv/install.sh` and `uv tool install` do NOT appear anywhere in `Makefile` or
     `ansible/roles/uv/tasks/main.yml`.
   - Assert role order in `ansible/site.yml` executes `conda` before `uv`.
   - Assert `make check` recipe probes GNU Make as hard prerequisite, and does not fail on missing `git`, `curl`, or
     `uv`.
   - Assert all variants declared in `devenv_package_variants` correspond to real directories under `dotfiles/` and
     satisfy file linking rules.
   - Assert `README.md` documents every core package, runtime pin, Conda app-dev tool, Stow package & variant, Fish
     plugin, and Neovim plugin.

### Dependencies & Criticality

- **Depends on:** Steps 1, 2, 3, and 4
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (pytest runner, explicitly declared test modifications).
- **Potential failure modes for this step:** Test mocking leakage or unclosed temporary files during wizard tests.
- **Guardrails and early‑abort checks:** Use pytest `tmp_path` fixtures and `monkeypatch` for all filesystem and
  environment alterations.

### Success & Discard Criteria

- **Success:** All wizard unit tests pass. Manifest and templating tests verify all architectural invariants. World docs
  are up to date and match current repository behavior.
- **Discard:** Discard if any test assertion fails or if deprecated `uv tool install` rules linger in world docs.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.95  |
| entropy_pred        | 0.45  |
| impact_pred         | 94.0  |
| cost_pred           | 2.5   |
| learning_value_pred | 4.5   |
| ev_pred             | 88.92 |

### Step Metrics Rationale

Calculated via: `EV = 0.95 * 94.0 + 0.5 * 4.5 - 0.3 * 0.45 - 2.5 = 89.30 + 2.25 - 0.135 - 2.5 = 88.915 ~ 88.92`. High-EV
verification step guaranteeing enduring stability and adherence to world constraints.

---

## Step 6: End-to-End Verification, Code Quality Auditing, and Documentation Formatting

- **Sub‑intent recommendation:** NO
- **Reasoning:** Final gatekeeper step ensuring all linters, static analyzers, test suites, formatting rules, and make
  entrypoints pass with zero warnings or regressions.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Executing full test suites under pytest, running `ruff` across all Python code including
  `scripts/devenv_wizard.py` and `tests/test_wizard.py`, running `ansible-lint` against the reordered playbook,
  validating single-pass Prettier convergence on all markdown files, and probing `make check` guarantees complete
  repository health.
- **Learning target:** Confirm zero linting or formatting regressions across Python, YAML, and Markdown files.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:** Run complete verification suite: `uv run --extra test pytest -m "not network"`,
  `uv run ruff check .`, `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and
  `make check`. Fix any formatting or linting discrepancies.
- **Git branch:**
  `I-1794797329-wizard/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium/E-6-verification-and-audit/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Test Execution:
   - Run `uv run --extra test pytest -m "not network"`. Verify all tests in `tests/test_manifest.py`,
     `tests/test_templating.py`, and `tests/test_wizard.py` pass cleanly.
   - Verify compatibility when invoked with Conda Python or system Python.
2. Code Quality & Linting:
   - Run `uv run ruff check .` across the workspace. Resolve any formatting, import sorting, or typing issues.
   - Run `uv run --extra test ansible-lint ansible/site.yml` to verify Ansible tasks meet best practices.
3. Documentation Formatting:
   - Run `npx prettier --check "**/*.md"`. Format with `npx prettier --write "**/*.md"` if required, ensuring all
     formulas and metrics remain enclosed in backticks for single-pass stability.
4. Makefile Entrypoint Verification:
   - Execute `make check` to ensure cold-start probing exits with code 0 without failing on deferred tools.

### Dependencies & Criticality

- **Depends on:** Steps 1 through 5
- **Is Bottleneck:** YES (Final release gate)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1, §2, §3, `holon-config/world/constraints.md` §1, §3.
- **Potential failure modes for this step:** Residual lint warnings or markdown formatting discrepancies.
- **Guardrails and early‑abort checks:** Format before final check using `npx prettier --write` and `ruff check --fix`.

### Success & Discard Criteria

- **Success:** All test suites pass 100%; `ruff check .`, `ansible-lint`, `prettier --check`, and `make check` exit with
  code 0.
- **Discard:** Discard if any test or lint check fails.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.20  |
| impact_pred         | 90.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 2.0   |
| ev_pred             | 87.64 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 90.0 + 0.5 * 2.0 - 0.3 * 0.20 - 1.5 = 88.20 + 1.00 - 0.06 - 1.5 = 87.64`. Deterministic
audit step verifying complete delivery readiness.

---

## Strategy Rationale

The overall plan metrics were derived from individual step-level metrics as follows:

- **p_success_pred**: 0.94. Dictated by the bottleneck step (Step 3: 0.94), where interactive TTY prompts, `/dev/tty`
  input handling, editor subprocess launching, and multi-option conflict resolution logic must operate reliably across
  both interactive terminals and headless automated test environments.
- **entropy_pred**: 0.65. Evaluated as the maximum single-step risk profile (Step 3: 0.65), where the interactive wizard
  introduces new user-facing state transitions and conflict-handling options. The sum of predicted step entropies across
  all six steps is 2.50 (`0.40 + 0.50 + 0.65 + 0.30 + 0.45 + 0.20 = 2.50`), well within the allocated entropy budget of
  15.0.
- **impact_pred**: 96.0. Establishes a pure `make -> conda -> ansible` toolchain with GNU Make as the sole cold-start
  prerequisite, introduces extensible multi-variant GNU Stow packaging (`nvim-kickstart`, `nvim-minimal`,
  `nvim-lazyvim`), delivers an interactive pre-Ansible wizard (`make configure`) with comprehensive dotfile conflict
  resolution, elevates documentation clarity with top-level toolchain diagrams and full package inventories, and
  enforces invariants through automated tests.
- **cost_pred**: 14.5. Calculated as the direct sum of individual step costs
  (`2.5 + 2.5 + 3.5 + 2.0 + 2.5 + 1.5 = 14.5`).
- **learning_value_pred**: 6.0. Epistemic gain from mastering pure Conda-based bootstrap shimming, multi-variant Stow
  unlinking semantics, TTY-aware interactive Python conflict resolution, and single-pass documentation manifest
  verification.
- **ev_pred**: 78.55. Computed strictly via the config-driven Expected Value formula:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system constants `lambda = 0.3`
  and `mu = 0.5` loaded from `holon-config/metrics/ev_config.json`:
  `EV = 0.94 * 96.0 + 0.5 * 6.0 - 0.3 * 0.65 - 14.5 = 90.24 + 3.00 - 0.195 - 14.5 = 78.545 ~ 78.55`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: pure `make -> conda -> ansible` toolchain,
    GNU Make 3.81 compatibility, no shell scripts tracked, Python target `==3.13.*` via Miniforge Conda, multi-variant
    Stow packaging, Multi-OS Darwin/Linux parity).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8, static typing, single-pass Prettier
    formatting with code-span arithmetic).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, tests located in `tests/`, all test
    modifications explicitly declared during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow & Branch Constraints: branch prefix isolation
    `I-{timestamp}-{slug}/P-{timestamp}-{agent}-{model}/E-{timestamp}-{action}/_`, rebase discipline, commit
    boundaries).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment Tiers: process sandbox $< 10$ entropy).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: converge through manifest, never write
    outside repo except through Ansible, do not touch unmanaged state, two backends only, destructive operations require
    explicit human confirmation).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero modifications to historical ledger entries).
- **Potential violations or edge cases:**
  - Inactive Stow package collisions: Switching between Neovim variants without unlinking previous variant links could
    cause Stow collision errors. Mitigated by explicitly executing `stow --delete` on all inactive variants before
    stowing the active variant.
  - Wizard hanging in CI: An interactive prompt blocking on stdin in non-interactive CI runs. Mitigated by implementing
    `--non-interactive` flag, checking `os.isatty(0)`, and verifying `CI == 'true'` environment variables.
  - GNU Make 3.81 incompatibility: Using modern GNU Make features (`.ONESHELL`, `$(file)`, `!=`). Mitigated by strictly
    using standard POSIX shell constructs and variable assignments.
  - Dotfile clobbering: Overwriting user dotfiles during wizard merge/adopt actions. Mitigated by always generating
    backups in `~/.local/share/dev-env/backup/` before modifying or replacing any existing user dotfile.
- **Mitigations built into the plan:**
  - Strict adherence to `stow --no-folding --restow` and explicit inactive variant deletion.
  - Automated fallback to non-interactive defaults when no TTY is detected.
  - Robust Miniforge installer fetching supporting `curl`, `wget`, and `python3 urllib.request`.
  - Comprehensive unit test suite in `tests/test_wizard.py` validating all conflict resolution options using mock
    environments.
- **Residual risk accepted (and why):**
  - Dependency on network availability during `make bootstrap` to fetch the Miniforge3 installer from GitHub; accepted
    as fundamental for bootstrap, with cached installer reuse in `~/.cache/dev-env/`.
- **Allocated Entropy Budget:** 15.0
- **Predicted Plan Entropy:** 0.65
- **Budget Compliance:** The strategy fits comfortably within budget (`0.65 <= 15.0`).

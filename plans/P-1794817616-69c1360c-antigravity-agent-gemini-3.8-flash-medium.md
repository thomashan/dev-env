# Plan for I-1794817597-getting-started

- **Plan ID:** P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794817597-getting-started
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-16T08:27:03Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent delivers a comprehensive architectural unification: detecting
  existing Conda environments via `command -v conda` and `conda info --base`, bootstrapping Conda via `brew` when absent
  (miniforge cask on macOS, micromamba on Linux) exclusively during `make bootstrap` while Ansible preserves a single
  backend per OS (`brew` on macOS, `apt` on Linux), fixing the broken `` `nvm`/node `` inline-code formatting in
  `README.md`, adding a prominent `## Getting Started` section highlighting `make install`, categorizing every package
  and tool in `README.md`, updating world documentation, and updating the pytest suite invariants.
- **Exploration stance:** Focused exploit with deterministic verification across POSIX GNU Make 3.81 syntax, Ansible
  roles, documentation standards, and pytest assertions.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification, GNU Make 3.81 compatibility, pure `make -> conda -> ansible` toolchain, Multi-OS Darwin/Linux parity),
  `holon-config/world/ruleset.md` §2 (PEP 8, static typing, backtick arithmetic code spans for Prettier),
  `holon-config/world/ruleset.md` §3 (pytest suite verification), and `holon-config/world/constraints.md` §3 (Two
  backends only: `brew` and `apt`).

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic refactorings, documentation enhancements, role adaptations, and test
  suite assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.35  |
| impact_pred         | 95.0  |
| cost_pred           | 6.0   |
| learning_value_pred | 3.5   |
| ev_pred             | 88.75 |

---

## Step 1: Implement Dynamic Conda Detection and Brew-Based Conda Bootstrap in `Makefile`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Foundational refactoring of the entry point `Makefile`. Replaces static paths with dynamic Conda root
  resolution, requires `brew` across both Darwin and Linux for Conda bootstrap while maintaining `apt` as Linux backend,
  and eliminates direct shell downloads (`curl`/`Miniforge3-*.sh`) in favor of package-managed bootstrap
  (`brew install --cask miniforge` on macOS and `brew install micromamba` on Linux).
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Probing `command -v conda` and `conda info --base` first in GNU Make 3.81 syntax allows
  `dev-env` to seamlessly reuse existing Anaconda, Miniconda, Miniforge, or Homebrew Cask Conda environments without
  re-downloading or conflicting with existing user installations.
- **Learning target:** Verify GNU Make 3.81 compatibility (no `!=` syntax, using `$(shell ...)`) and POSIX shell
  variable resolution across both macOS and Linux environments.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:** In `Makefile`:
  1. Replace hardcoded `CONDA_DIR ?= $(HOME)/miniforge3` with a GNU Make 3.81-compatible shell evaluation:
     - Check `command -v conda >/dev/null 2>&1` and resolve `conda info --base` first.
     - Probe candidate paths: `/opt/homebrew/Caskroom/miniforge/base`, `/usr/local/Caskroom/miniforge/base`, and
       `$(HOME)/miniforge3`.
     - Fallback if Conda is absent: `/opt/homebrew/Caskroom/miniforge/base` (Apple Silicon when `/opt/homebrew` exists),
       `/usr/local/Caskroom/miniforge/base` (Intel macOS), or `$(HOME)/miniforge3` (Linux).
  2. Set `CONDA ?= $(shell command -v conda 2>/dev/null || echo $(CONDA_DIR)/bin/conda)`.
  3. Ensure `PB := $(CONDA_DIR)/bin/ansible-playbook`, `GALAXY := $(CONDA_DIR)/bin/ansible-galaxy`, and
     `LINT := $(CONDA_DIR)/bin/ansible-lint` resolve against the active `CONDA_DIR`.
  4. In `check:` target:
     - Probe `GNU Make`, `OS` (`Darwin|Linux`).
     - Probe `brew`: required on BOTH `Darwin` and `Linux` for Conda bootstrap. Check `/opt/homebrew/bin/brew`,
       `/usr/local/bin/brew`, `/home/linuxbrew/.linuxbrew/bin/brew`, `$$HOME/.linuxbrew/bin/brew`, and
       `command -v brew`. If missing, print `MISSING: Homebrew (brew) is required` and increment `err=$$((err+1))`.
     - Probe `apt (Linux backend)`: on Linux, require `command -v apt`; if missing, print `MISSING: apt is required` and
       increment `err=$$((err+1))`. On Darwin, print `n/a`.
     - Probe `conda`: check `command -v conda >/dev/null 2>&1 || [ -x "$(CONDA)" ]`.
     - Probe `ansible-core` and `community.general`.
  5. In `bootstrap:` target:
     - Resolve `brew_bin` across `/opt/homebrew/bin/brew`, `/usr/local/bin/brew`, `/home/linuxbrew/.linuxbrew/bin/brew`,
       `$$HOME/.linuxbrew/bin/brew`, or `command -v brew`. Fail with `Error: Homebrew (brew) is required.` and exit 1 if
       missing.
     - On Linux, verify `command -v apt >/dev/null 2>&1 || { echo "Error: apt is required on Linux." >&2; exit 1; }`.
     - Only install Conda when `if ! command -v conda >/dev/null 2>&1 && [ ! -x "$(CONDA)" ]; then`:
       - On Darwin: run `"$$brew_bin" install --cask miniforge || exit 1`.
       - On Linux: run `"$$brew_bin" install micromamba || exit 1`, resolve `mamba_bin`
         (`"$$(dirname "$$brew_bin")/micromamba"` or `command -v micromamba`), and run
         `"$$mamba_bin" create -y -p "$(CONDA_DIR)" -c conda-forge --override-channels conda python=3.13 ansible-core ansible-lint pyyaml || exit 1`.
     - Remove all `curl -fsSL`, `Miniforge3-*.sh` download URLs, and `brew install curl` / `apt install -y curl` blocks.
     - Run
       `"$(CONDA)" install -y -c conda-forge --override-channels python=3.13 ansible-core ansible-lint pyyaml || exit 1`
       and install `community.general`.
- **Git branch:**
  `I-1794817597-getting-started/P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium/E-1-makefile-conda-detection-bootstrap/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Dynamic Conda Detection in `Makefile`:
   - Structure `CONDA_DIR ?= $(shell ...)` using POSIX shell commands inside `$(shell)`:
     - Check `if command -v conda >/dev/null 2>&1; then conda info --base 2>/dev/null; ...`
     - Else check if directory `/opt/homebrew/Caskroom/miniforge/base` exists, then
       `/usr/local/Caskroom/miniforge/base`, then `$(HOME)/miniforge3`.
     - Else fallback to platform default: if `[ -d /opt/homebrew ]` echo `/opt/homebrew/Caskroom/miniforge/base`; elif
       `[ "$$(uname -s)" = "Darwin" ]` echo `/usr/local/Caskroom/miniforge/base`; else echo `$(HOME)/miniforge3`.
   - Update `CONDA ?= $(shell command -v conda 2>/dev/null || echo $(CONDA_DIR)/bin/conda)`.
   - Ensure `PB`, `GALAXY`, and `LINT` point to `$(CONDA_DIR)/bin/...`.
2. Refactor `check:` Target:
   - Output `brew` probe unconditionally on Darwin and Linux. Test the 4 fixed filesystem locations and
     `command -v brew`. If none match, print `MISSING: Homebrew (brew) is required` and increment `err`.
   - Output `apt (Linux backend)` probe: if `Linux`, test `command -v apt`; print `ok` or `MISSING: apt is required`
     (incrementing `err`). If not Linux, print `n/a`.
   - Output `conda` probe: check `command -v conda >/dev/null 2>&1 || [ -x "$(CONDA)" ]`. If present, report version;
     otherwise report will be installed by `make bootstrap` and increment `warn`.
   - Maintain `ansible-core` and `community.general` checks.
3. Refactor `bootstrap:` Target:
   - Early Homebrew check: detect `brew_bin` across candidate paths. If empty, print
     `"Error: Homebrew (brew) is required." >&2` and `exit 1`.
   - On Linux: verify `command -v apt >/dev/null 2>&1 || { echo "Error: apt is required on Linux." >&2; exit 1; }`.
   - Remove installer cache directory creation (`~/.cache/dev-env`), `curl` installation recipes, installer URL logic,
     and `Miniforge3-*.sh` execution.
   - Wrap Conda installation in `if ! command -v conda >/dev/null 2>&1 && [ ! -x "$(CONDA)" ]; then`:
     - Darwin: run `"$$brew_bin" install --cask miniforge || exit 1`.
     - Linux: run `"$$brew_bin" install micromamba || exit 1`, locate `micromamba`, and run
       `"$$mamba_bin" create -y -p "$(CONDA_DIR)" -c conda-forge --override-channels conda python=3.13 ansible-core ansible-lint pyyaml || exit 1`.
   - Execute
     `"$(CONDA)" install -y -c conda-forge --override-channels python=3.13 ansible-core ansible-lint pyyaml || exit 1`.
   - Install `community.general` via `$(GALAXY)`.

### Dependencies & Critical Path

- **Depends on:** None (Step 1).
- **Is Bottleneck:** YES (Build/bootstrap entry point for the repository).

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (GNU Make 3.81 compatibility, no `!=`, no `.ONESHELL`),
  `holon-config/world/constraints.md` §3 (Two backends only: `brew` and `apt`).
- **Potential failure modes for this step:** Make parsing errors with nested shell quotes or parentheses; failure to
  find Homebrew if installed under `/home/linuxbrew/.linuxbrew`.
- **Guardrails and early‑abort checks:** Validate with `make -n check`, `make -n bootstrap`, and `make check`.

### Success & Discard Criteria

- **Success:** `Makefile` contains dynamic Conda detection without `!=`, `make check` requires `brew` on all platforms
  and `apt` on Linux, `bootstrap` has no `curl -fsSL` or `.sh` download script, and installs Conda via `brew`.
- **Discard:** Discard if GNU Make 3.81 rejects variable assignments or shell syntax.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.20  |
| impact_pred         | 90.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 2.5   |
| ev_pred             | 87.89 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 90.0 + 0.5 * 2.5 - 0.3 * 0.20 - 1.5 = 88.20 + 1.25 - 0.06 - 1.5 = 87.89`.

---

## Step 2: Adapt Ansible Homebrew and Conda Roles to Reuse Existing Conda and Bootstrap via Homebrew

- **Sub‑intent recommendation:** NO
- **Reasoning:** Aligns Ansible role execution with the `Makefile` Conda discovery strategy. Guarantees that
  `make converge` idempotently detects and reuses any existing Conda installation (Miniforge, Miniconda, Anaconda,
  Mambaforge, or Homebrew cask), updates Homebrew search paths to cover standard Linuxbrew locations, and removes legacy
  shell installer tasks (`get_url` for `Miniforge3-*.sh`) in favor of declarative package manager tasks (`homebrew_cask`
  on macOS and `homebrew` on Linux) only when Conda is completely absent.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Discovering existing Conda installations via `which conda` / `conda info --base` and a
  broad list of standard candidate roots prevents destructive re-installation during Ansible convergence and maintains
  parity with system package managers.
- **Learning target:** Verify Ansible task syntax, `failed_when: false` probing logic, and idempotence under
  `ansible-lint`.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `ansible/roles/homebrew/tasks/main.yml`:
     - Add `/home/linuxbrew/.linuxbrew/bin/brew` to `devenv_brew_stat` and `devenv_brew_stat2` stat path loops alongside
       `/opt/homebrew/bin/brew`, `/usr/local/bin/brew`, and `{{ devenv_home }}/.linuxbrew/bin/brew`.
  2. In `ansible/roles/conda/tasks/main.yml`:
     - Remove the `Pick the Miniforge installer for this platform`, `Ensure the download cache exists`,
       `Download the Miniforge installer`, and `Install Miniforge into {{ devenv_conda_dir }}` tasks.
     - Probe existing conda executable: run `which conda` (or `command -v conda`) and `conda info --base` with
       `changed_when: false` and `failed_when: false`.
     - Stat candidate roots if no active conda command is found:
       - `/opt/homebrew/Caskroom/miniforge/base`
       - `/usr/local/Caskroom/miniforge/base`
       - `{{ devenv_home }}/miniforge3`
       - `{{ devenv_home }}/miniforge`
       - `{{ devenv_home }}/mambaforge`
       - `{{ devenv_home }}/miniconda3`
       - `{{ devenv_home }}/anaconda3`
       - `/opt/miniforge3`
       - `/opt/conda`
     - Resolve active `devenv_conda_dir` and `devenv_conda_bin` based on discovered path.
     - If no Conda is found anywhere:
       - On Darwin: install `miniforge` via `community.general.homebrew_cask`.
       - On Linux: install `micromamba` via `community.general.homebrew`, locate `micromamba`, and initialize the conda
         root environment into `{{ devenv_conda_dir }}`.
     - Retain downstream tasks: assert conda is runnable, inspect `~/.condarc`, create conda environments, install Conda
       development tools (`uv`, `ruff`, `pre-commit`), and optional local checkout installation.
- **Git branch:**
  `I-1794817597-getting-started/P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium/E-2-ansible-conda-reuse-brew-fallback/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Homebrew Path Discovery (`ansible/roles/homebrew/tasks/main.yml`):
   - Update `devenv_brew_stat` loop to include `/home/linuxbrew/.linuxbrew/bin/brew`.
   - Update `devenv_brew_stat2` loop to include `/home/linuxbrew/.linuxbrew/bin/brew`.
2. Conda Discovery & Bootstrap (`ansible/roles/conda/tasks/main.yml`):
   - Delete obsolete `set_fact` for `devenv_conda_installer` and `get_url` tasks downloading `.sh` scripts.
   - Add probe task executing `which conda` / `conda info --base` registering results.
   - Add stat tasks across candidate roots list (`/opt/homebrew/Caskroom/miniforge/base`,
     `/usr/local/Caskroom/miniforge/base`, `{{ devenv_home }}/miniforge3`, etc.).
   - Define fallback tasks when Conda is missing:
     - On macOS: invoke `community.general.homebrew_cask` with `name: miniforge`, `state: present`.
     - On Linux: invoke `community.general.homebrew` with `name: micromamba`, `state: present`, followed by a command
       creating `{{ devenv_conda_dir }}` with Python 3.13 and core packages.
   - Set `devenv_conda_bin` dynamically to resolved binary.
3. Ansible Lint Validation:
   - Run `ansible-lint` to verify proper FQCN module naming, task labels, and idempotence.

### Dependencies & Critical Path

- **Depends on:** Step 1
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Single manifest declarations, no shell scripts tracked),
  `holon-config/world/ruleset.md` §2 (Ansible FQCN style, idempotence, no unnecessary changes).
- **Potential failure modes for this step:** Jinja filter errors when resolving candidate roots; unquoted shell
  arguments.
- **Guardrails and early‑abort checks:** Run `uv run --extra test ansible-lint ansible/site.yml` and syntax-check the
  playbook.

### Success & Discard Criteria

- **Success:** Existing Conda environments are automatically detected and used by `ansible/roles/conda`; no `get_url` or
  Miniforge `.sh` tasks exist; `ansible-lint` succeeds with zero violations.
- **Discard:** Discard if Ansible playbook fails syntax or lint checks.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.15  |
| impact_pred         | 91.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 2.0   |
| ev_pred             | 90.05 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 91.0 + 0.5 * 2.0 - 0.3 * 0.15 - 1.0 = 90.09 + 1.0 - 0.045 - 1.0 = 90.045 ~ 90.05`.

---

## Step 3: Modernize `README.md`, Add Getting Started Section, Update World Docs, and Categorize Package Inventory

- **Sub‑intent recommendation:** NO
- **Reasoning:** User-facing and documentation core. Fixes broken code-span formatting, adds an onboarding
  `## Getting Started` guide emphasizing `make install`, updates Mermaid diagrams and world ruleset/constraint docs to
  reflect dynamic Conda detection and single-backend convergence, and enriches every section of
  `## Package & Tool Inventory` with precise Category and Programming Language attributions.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicitly categorizing every tool, providing an immediate 3-step getting started
  workflow, and fixing formatting issues makes the repository immediately operable for new developers and fully
  transparent about runtime dependencies.
- **Learning target:** Ensure Prettier single-pass formatting convergence for Markdown tables, lists, and quoted Mermaid
  diagram labels.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:**
  1. In `README.md`:
     - Fix line 5 inline formatting: replace broken `` `nvm`/node `` with proper code formatting and define the role of
       each core tool: `fish` (Terminal / Shell), `neovim` (Editor / IDE), `conda` (Python runtime & package manager),
       `nvm` (Node.js version manager).
     - Add a prominent `## Getting Started` section right after the intro paragraph (before
       `## Tool Chain & Execution Order`) featuring 3 steps:
       - **1. Prerequisites**: `brew` (required on macOS and Linux for Conda bootstrap; also macOS system package
         manager) and `apt` (required on Debian/Ubuntu Linux for system packages), plus installing `make` and `git` if
         absent (`brew install make git` on macOS; `sudo apt update && sudo apt install -y make git` on Linux).
       - **2. Clone the Repository**: `git clone --bare <repo-url> dev-env/.git`,
         `git --git-dir=dev-env/.git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"`,
         `git --git-dir=dev-env/.git fetch origin`, `git --git-dir=dev-env/.git worktree add dev-env/main main`,
         `cd dev-env/main`.
       - **3. Kick Off the Environment (`make install`)**: Explain clearly that **`make install`** is the single command
         that executes the entire pipeline (`make check` -> `make bootstrap` -> `make configure` -> `make converge`).
     - In Mermaid `flowchart TD` diagram and `Stage-by-Stage Execution` table:
       - Update nodes and descriptions to show Conda detection (`command -v conda` / `conda info --base`), brew-based
         Conda bootstrap in `make bootstrap` only, and single-backend Ansible convergence (`brew` on macOS, `apt` on
         Linux).
     - In `## Package & Tool Inventory`:
       - ### 1. Core CLI Packages (`devenv_packages_core`): Add `Category` column:
         `| Logical Package | Category | macOS (`brew`) Formula | Linux (`apt`) Package | Stow Status | Description |`
         for all 22 packages (`fish`, `neovim`, `tmux`, `git`, `gh`, `delta`, `stow`, `curl`, `aria2`, `autossh`,
         `openssh`, `iperf3`, `fd`, `ripgrep`, `fzf`, `ncdu`, `rsync`, `tree`, `jq`, `htop`, `watch`, `unzip`).
       - ### 2. Language Runtimes & Conda Tools: Convert into a Markdown table:
         `| Tool / Runtime | Category / Language | Provisioned Via | Description |` labeling `CPython 3.13` / `conda`
         (**Python — Runtime & Environment Manager**), `uv` (**Python — Package & Project Manager**), `ruff` (**Python —
         Linter & Formatter**), `pre-commit` (**Multi-Language — Git Hooks**), and `nvm.fish` + `Node.js 22.23.2`
         (**JavaScript / TypeScript — Node.js Runtime & Version Manager**).
       - ### 3. GNU Stow Packages & Config Variants (`devenv_package_variants`): Annotate category/language for `bash`,
         `conda`, `fish`, `tmux`, `zsh`, and `nvim-*` variants.
       - ### 4. Fish Shell Plugins (`fish_plugins`): Label `jorgebucaran/fisher` (**Terminal / Shell**),
         `reitzig/sdkman-for-fish@v2.1.0` (**Java / JVM**), and `jorgebucaran/nvm.fish` (**JavaScript / Node.js**).
       - ### 5. Neovim Plugins (`nvim-pack-lock.json`): Identify all 26 plugins as **Editor / IDE (Neovim / Lua)** with
         functional categories.
       - ### 6. macOS GUI Casks & Purged Unmanaged Packages: Label `docker-desktop` (**Containers / Virtualization**) and
         `nvm`, `node` (**JavaScript / Node.js**).
  2. In `holon-config/world/ruleset.md` and `holon-config/world/constraints.md`:
     - Update documentation to reflect dynamic Conda detection, `brew`-based Conda bootstrap, and single-backend Ansible
       convergence.
- **Git branch:**
  `I-1794817597-getting-started/P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium/E-3-readme-getting-started-categorization/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Intro & Getting Started in `README.md`:
   - Replace line 5 inline text to properly quote individual tools and specify roles: `fish` (Terminal / Shell),
     `neovim` (Editor / IDE), `conda` (Python runtime & package manager), and `nvm` (Node.js version manager).
   - Insert `## Getting Started` right before `## Tool Chain & Execution Order`. Include clear headings for 1.
     Prerequisites, 2. Clone the Repository, and 3. Kick Off the Environment (`make install`).
2. Architecture Diagram & Workflow Updates:
   - Update Mermaid `flowchart TD` nodes with double-quoted labels representing dynamic Conda detection and brew
     bootstrap.
   - Synchronize `Stage-by-Stage Execution` table.
3. Package & Tool Inventory Categorization:
   - Expand table headers and row cells for all 22 core packages with precise `Category` values.
   - Format section 2 tools into a clear markdown table with Category / Language column.
   - Add category and language descriptors to package variants, fish plugins, neovim plugins, and casks.
4. Synchronize World Ruleset & Constraints:
   - In `holon-config/world/ruleset.md` and `holon-config/world/constraints.md`, align environment specifications with
     Conda discovery via `command -v conda` and bootstrap via `brew`.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Prettier formatting, quoted Mermaid labels).
- **Potential failure modes for this step:** Broken Markdown table formatting; Prettier re-wrapping issues with unquoted
  labels in Mermaid.
- **Guardrails and early‑abort checks:** Run `npx prettier --check "**/*.md"` to verify formatting passes cleanly.

### Success & Discard Criteria

- **Success:** `README.md` contains `## Getting Started` highlighting `make install`, no `` `nvm`/node `` error, all 22
  core packages have a `Category` column, all tools have category/language attribution, and
  `npx prettier --check "**/*.md"` passes without error.
- **Discard:** Discard if Prettier reports syntax errors in Markdown or Mermaid.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.15  |
| impact_pred         | 93.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 2.0   |
| ev_pred             | 90.60 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 93.0 + 0.5 * 2.0 - 0.3 * 0.15 - 1.5 = 91.14 + 1.0 - 0.045 - 1.5 = 90.595 ~ 90.60`.

---

## Step 4: Update Test Invariants in `tests/test_manifest.py` and `tests/test_templating.py`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Invariant enforcement. Codifies the architectural promises into the automated test suite so regressions
  are immediately blocked. Asserts Conda detection, package manager requirements, absence of download tools in
  bootstrap, and documentation requirements.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating pytest assertions to match the new Makefile Conda detection/bootstrap and
  README.md sections ensures complete test coverage and prevents future regressions against these requirements.
- **Learning target:** Verify all modified test fixtures and assertions pass cleanly under pytest without network
  access.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `tests/test_manifest.py`:
     - Update `test_makefile_check_probes_prerequisites_strictly`:
       - Assert `Makefile` probes `command -v conda` and `conda info --base`.
       - Assert `make check` requires `brew` across both Darwin and Linux (`MISSING: Homebrew (brew) is required`).
       - Assert `make check` requires `apt` on Linux (`MISSING: apt is required`).
     - Update `test_makefile_bootstrap_uses_only_curl_and_installs_curl_via_brew_or_apt` (or refactor to
       `test_makefile_bootstrap_installs_conda_via_brew`):
       - Assert `make bootstrap` installs Conda via `brew` when missing (`brew install --cask miniforge` on Darwin,
         `brew install micromamba` on Linux).
       - Assert `curl`, `wget`, `urllib.request`, and `apt-get` do NOT appear in the Conda download or installation
         flow.
     - Add or update `test_readme_getting_started_and_categories`:
       - Assert `README.md` contains `## Getting Started`.
       - Assert `README.md` explicitly documents `make install`.
       - Assert `README.md` does not contain `` `nvm`/node ``.
       - Assert `README.md` table contains the `Category` column and category/language attributions.
  2. In `tests/test_templating.py`:
     - Since the old `get_url` Miniforge installer task was removed from `ansible/roles/conda/tasks/main.yml`, update or
       remove `conda_installer_expr()` and `test_conda_installer_matches_platform()` so the suite does not attempt to
       query a deleted task.
- **Git branch:**
  `I-1794817597-getting-started/P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium/E-4-test-suite-invariants-update/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Test Suite Refinement in `tests/test_manifest.py`:
   - Refactor Makefile inspection tests to check for `command -v conda`, `conda info --base`,
     `brew install --cask miniforge`, and `brew install micromamba`.
   - Update forbidden strings assertions to verify no `curl -fsSL` or `.sh` download patterns in bootstrap.
   - Assert `README.md` contains `## Getting Started`, `make install`, no broken code syntax, and the `Category` header.
2. Templating Suite Refinement in `tests/test_templating.py`:
   - Adjust `conda_installer_expr` and its test parameterizations to reflect the new Conda role structure.
3. Pytest Execution:
   - Run `uv run --extra test pytest -m "not network"` to confirm all tests pass.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2, Step 3
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Test modifications declared during planning),
  `holon-config/world/constraints.md` §3 (Two backends only).
- **Potential failure modes for this step:** Assertions failing on subtle whitespace or string matching discrepancies.
- **Guardrails and early‑abort checks:** Run pytest locally against target tests during development.

### Success & Discard Criteria

- **Success:** All pytest tests pass cleanly; all new Makefile and README requirements are asserted by automated tests.
- **Discard:** Discard if pytest tests fail or report regressions.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.15  |
| impact_pred         | 92.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 2.0   |
| ev_pred             | 91.04 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 2.0 - 0.3 * 0.15 - 1.0 = 91.08 + 1.0 - 0.045 - 1.0 = 91.035 ~ 91.04`.

---

## Step 5: Quality Gate & Verification Suite Execution

- **Sub‑intent recommendation:** NO
- **Reasoning:** Comprehensive end-to-end quality and compliance gate across all affected components. Ensures zero
  regressions in pytest, code linting with ruff, playbook validation with ansible-lint, markdown formatting with
  prettier, and dry-run readiness with `make check`.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Passing all five quality gates proves that the changes integrate cleanly, preserve all
  architectural invariants, and conform to the project's strict styling and static analysis standards.
- **Learning target:** Ensure clean zero-warning, zero-error status across the entire validation matrix.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. Run `uv run --extra test pytest -m "not network"` to verify all structural manifest, templating, and wizard tests.
  2. Run `uv run ruff check .` to verify PEP 8 compliance.
  3. Run `uv run --extra test ansible-lint ansible/site.yml` to verify Ansible collection and role syntax.
  4. Run `npx prettier --check "**/*.md"` to verify documentation formatting.
  5. Run `make check` to ensure read-only prerequisite verification works as expected on the host.
- **Git branch:**
  `I-1794817597-getting-started/P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium/E-5-full-quality-gate-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Pytest Suite Execution:
   - Execute pytest excluding network-dependent tests. Assert 100% test passing rate.
2. Python Linter Audit:
   - Execute `ruff check .` across the repository.
3. Ansible Linting:
   - Execute `ansible-lint` against `ansible/site.yml`.
4. Markdown Formatting Audit:
   - Execute `prettier` check over all markdown files.
5. Makefile Readiness Check:
   - Execute `make check` in the sandbox environment.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2, Step 3, Step 4
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1, §2, §3; `holon-config/world/constraints.md` §1, §2, §3.
- **Potential failure modes for this step:** Prettier reformatting differences or unhandled linter warnings.
- **Guardrails and early‑abort checks:** Remediate any formatting or lint issues immediately before declaring the step
  complete.

### Success & Discard Criteria

- **Success:** All 5 commands exit with status 0; no linting, testing, or formatting defects remain.
- **Discard:** Discard and fix any failure in the verification pipeline.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.10  |
| impact_pred         | 95.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 1.0   |
| ev_pred             | 93.52 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 95.0 + 0.5 * 1.0 - 0.3 * 0.10 - 1.0 = 94.05 + 0.50 - 0.03 - 1.0 = 93.52`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.98. Derived from the composite success probability of each step (Step 1: 0.98, Step 2: 0.99,
  Step 3: 0.98, Step 4: 0.99, Step 5: 0.99). The refactorings adhere strictly to existing GNU Make 3.81 patterns,
  Ansible collection modules, and Python pytest standards, giving high predictability.
- **entropy_pred**: 0.35. The maximum single-step entropy is 0.20 (Step 1, covering Makefile shell logic). The
  cumulative sum of step entropies across all five steps is 0.75 (`0.20 + 0.15 + 0.15 + 0.15 + 0.10 = 0.75`), remaining
  well within the process sandbox entropy limit of 10.0.
- **impact_pred**: 95.0. Unifies Conda discovery and bootstrap across platforms, eliminates raw shell downloads in favor
  of package manager-driven installation (`brew install --cask miniforge` on macOS, `brew install micromamba` on Linux),
  guarantees that existing Conda environments are automatically recognized and reused during `make converge`, fixes
  formatting in `README.md`, introduces a comprehensive `## Getting Started` section highlighting `make install`,
  categorizes every tool and plugin across the entire inventory, and codifies these guarantees in test suites.
- **cost_pred**: 6.0. Calculated as the direct sum of individual step costs (`1.5 + 1.0 + 1.5 + 1.0 + 1.0 = 6.0`).
- **learning_value_pred**: 3.5. Reflects the epistemic value of validating package-managed Conda bootstrap workflows,
  robust multi-path Conda root resolution in GNU Make 3.81, and complete tool categorization.
- **ev_pred**: 88.75. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.98 * 95.0 + 0.5 * 3.5 - 0.3 * 0.35 - 6.0 = 93.10 + 1.75 - 0.105 - 6.0 = 88.745 ~ 88.75`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: GNU Make 3.81 compatibility, pure
    `make -> conda -> ansible` flow, no tracked shell scripts, Python target `==3.13.*`, Multi-OS parity).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8 compliance, single-pass Prettier
    formatting with backtick code spans for arithmetic expressions, quoted Mermaid labels).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, tests located under `tests/`, all test
    modifications declared during planning).
  - `holon-config/world/constraints.md` §1 (Branch naming prefix:
    `I-{timestamp}-{slug}/P-{timestamp}-{agent}-{model}/E-{timestamp}-{action}/_`).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment Tiers: process sandbox $< 10$ entropy).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: converge through manifest, two backends
    only: `brew` and `apt`).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - GNU Make 3.81 incompatibility: Constructing Conda detection using GNU Make 4.x features like `!=` or `.ONESHELL`
    would break macOS system Make. Mitigated by using standard `$(shell ...)` compatible with Make 3.81.
  - Homebrew detection on Linux: Linuxbrew may reside at `/home/linuxbrew/.linuxbrew` or `~/.linuxbrew`. Mitigated by
    probing all candidate paths plus `command -v brew`.
  - Conda detection re-entrancy: Re-running `make converge` must not attempt to reinstall or overwrite an active Conda
    installation. Mitigated by probing `command -v conda` and `conda info --base` before falling back to filesystem
    paths.
  - Prettier table or Mermaid parsing: Unquoted labels in Mermaid diagrams or improper table column alignment can fail
    Prettier checks. Mitigated by wrapping Mermaid labels in double quotes and validating with `npx prettier --check`.
- **Mitigations built into the plan:**
  - Step-by-step verification commands after each structural change.
  - Targeted unit tests in `tests/test_manifest.py` verifying that Conda detection, package manager requirements, and
    prohibitions (no `curl -fsSL` or `.sh` download script) are strictly maintained.
  - Verification across `pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check` in Step 5.
- **Residual risk accepted (and why):**
  - Systems without `brew` (macOS and Linux) cannot bootstrap Conda, and Linux systems without `apt` cannot converge
    system packages; this is intentional per project constraints, making `brew` and `apt` explicit root prerequisites.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.35
- **Budget Compliance:** The strategy fits comfortably within budget (`0.35 <= 10.0`).

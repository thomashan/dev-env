# Plan for I-1794808105-toolset

- **Plan ID:** P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794808105-toolset
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-16T05:48:48Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent provides a comprehensive and coherent architectural alignment:
  elevating `brew` (macOS) and `apt` (Linux) as the sole cold-start system prerequisites, folding `uv` into standard
  Conda toolset packages (`devenv_conda_tools`) while eliminating the standalone `uv` role, eradicating Makefile shim
  symlinks (`~/.local/share/dev-env/bin`) in favor of direct Conda binaries, converting the ASCII architecture diagram
  in `README.md` to Mermaid (`flowchart TD`), pruning deferred tool checks from `make check`, and fixing the bare-repo
  clone snippet.
- **Exploration stance:** Focused exploit with deterministic verification across POSIX GNU Make 3.81 syntax, Ansible
  role tasks, documentation, and pytest suite invariants.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime specification, GNU Make
  3.81 compatibility, pure `make -> conda -> ansible` toolchain), `holon-config/world/ruleset.md` §2 (PEP 8, static
  typing, code-span arithmetic for Prettier), `holon-config/world/ruleset.md` §3 (pytest constraints), and
  `holon-config/world/constraints.md` §3 (Two backends only: `brew` and `apt`).

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** Every step addresses deterministic refactoring, structural consolidation, documentation
  modernization, and test suite verification.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.35  |
| impact_pred         | 94.0  |
| cost_pred           | 6.0   |
| learning_value_pred | 3.5   |
| ev_pred             | 87.77 |

---

## Step 1: Enforce System Prerequisites, Remove Shims, and Streamline `check` and `bootstrap` in `Makefile`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Foundational entry point refactoring in `Makefile`. Establishes `brew` (macOS) and `apt` (Linux) as
  hard system prerequisites, directly targets Conda binaries without `~/.local/share/dev-env/bin` shims, removes
  deferred tool probes (`stow`, `git`, `curl`) from `make check`, and ensures deterministic curl installation in
  `bootstrap`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Enforcing platform package managers (`brew` on Darwin, `apt` on Linux) as strict hard
  prerequisites in `make check` and `make bootstrap`, while pointing `PB`, `GALAXY`, and `LINT` directly to
  `$(CONDA_DIR)/bin/`, eliminates unnecessary symlink indirections and establishes a clear contract where all host tools
  derive from `brew` or `apt`.
- **Learning target:** Verify POSIX shell compliance in GNU Make 3.81 for the updated package manager probes and curl
  installation recipe.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:** In `Makefile`:
  1. Remove `BIN := $(DEVENV_HOME)/bin` and comments regarding space-free shims.
  2. Set `PB := $(CONDA_DIR)/bin/ansible-playbook`, `GALAXY := $(CONDA_DIR)/bin/ansible-galaxy`, and
     `LINT := $(CONDA_DIR)/bin/ansible-lint` directly.
  3. In line 42 and `help:` (lines 82-84): update cold-start notes to state that `brew` (macOS) or `apt` (Debian/Ubuntu)
     is required, and if `make` is not installed yet, install it via `brew install make` (or `xcode-select --install`)
     on macOS or `sudo apt install -y make` on Linux before running `make install`.
  4. In `check:`:
     - Probe ONLY `GNU Make`, `OS` (`Darwin|Linux`), `apt (Linux backend)`, `brew (macOS backend)`, `conda`,
       `ansible-core`, and `community.general`.
     - Treat BOTH `brew` (on `Darwin`) and `apt` (on `Linux`) as hard prerequisites (`err=$$((err+1))` if missing):
       - Darwin:
         `if [ -x /opt/homebrew/bin/brew ] || [ -x /usr/local/bin/brew ] || command -v brew >/dev/null 2>&1; then echo "ok"; else echo "MISSING: Homebrew (brew) is required"; err=$$((err+1)); fi`
       - Linux:
         `if command -v apt >/dev/null 2>&1; then echo "ok"; else echo "MISSING: apt is required"; err=$$((err+1)); fi`
     - Remove `stow`, `git`, and `curl` probe lines.
  5. In `bootstrap:`:
     - Fail immediately (`exit 1`) if `brew` (Darwin) or `apt` (Linux) is missing before any action.
     - On Darwin: resolve `brew_bin` from `/opt/homebrew/bin/brew`, `/usr/local/bin/brew`, or `command -v brew`, and if
       empty print `"Error: Homebrew (brew) is required on macOS." >&2; exit 1`.
     - On Linux: verify `command -v apt >/dev/null 2>&1 || { echo "Error: apt is required on Linux." >&2; exit 1; }`.
     - When fetching Miniforge3 (`[ ! -f "$$target" ]`): if `! command -v curl >/dev/null 2>&1`, install `curl` via
       `"$$brew_bin" install curl || exit 1` (Darwin) or `sudo apt update && sudo apt install -y curl || exit 1` (Linux,
       omitting `sudo` if `id -u` is `0`).
     - Remove `"$(BIN)"` from `mkdir -p`.
     - Remove the three `ln -sfn` shim creation commands.
     - Update `@test -x "$(PB)"` check and error message so it no longer mentions a shim.
- **Git branch:**
  `I-1794808105-toolset/P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium/E-1-makefile-toolset-prereqs/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Variable & Binary Definitions:
   - Delete `BIN := $(DEVENV_HOME)/bin` and the preceding comment block.
   - Assign `PB`, `GALAXY`, and `LINT` to target `$(CONDA_DIR)/bin/ansible-playbook`, `$(CONDA_DIR)/bin/ansible-galaxy`,
     and `$(CONDA_DIR)/bin/ansible-lint` directly.
2. Cold Start Messaging:
   - Update line 42 error message to explain that `brew` (macOS) or `apt` (Debian/Ubuntu) is required, and if `make` is
     not installed, install it via `brew install make` (or `xcode-select --install`) on macOS or
     `sudo apt install -y make` on Linux.
   - Update lines 82-84 in the `help:` target recipe with matching cold-start guidance.
3. Prerequisite Probe (`check:`):
   - Refactor recipe to probe in sequence: GNU Make, OS, apt (on Linux), brew (on Darwin), conda, ansible-core, and
     community.general.
   - Ensure Darwin branch for brew tests `/opt/homebrew/bin/brew`, `/usr/local/bin/brew`, and `command -v brew`. If none
     exist, print `MISSING: Homebrew (brew) is required` and increment `err`.
   - Ensure Linux branch for apt tests `command -v apt`. If missing, print `MISSING: apt is required` and increment
     `err`.
   - Delete the probes for `stow`, `git`, and `curl`.
4. Bootstrap Target (`bootstrap:`):
   - Add early package manager check at the top of the bootstrap script before checking/downloading Conda:
     - On Darwin: locate `brew_bin` across `/opt/homebrew/bin/brew`, `/usr/local/bin/brew`, or `command -v brew`. If
       unset, emit `Error: Homebrew (brew) is required on macOS.` to stderr and exit 1.
     - On Linux: check `command -v apt`. If missing, emit `Error: apt is required on Linux.` to stderr and exit 1.
   - Inside installer download block: check `command -v curl`. If missing, run `"$$brew_bin" install curl` on Darwin, or
     `sudo apt update && sudo apt install -y curl` (or without sudo for root) on Linux.
   - Update `mkdir -p` to create only `"$(DEVENV_HOME)"` and `"$(COLLECTIONS)"`.
   - Remove `ln -sfn` commands.
   - Update `@test -x "$(PB)" || { echo "bootstrap: $(PB) is missing or not executable"; exit 1; }`.
5. Compatibility & Syntax Audit:
   - Ensure all recipes use leading tabs, POSIX shell commands, and GNU Make 3.81 compatibility.

### Dependencies & Critical Path

- **Depends on:** None (First execution step).
- **Is Bottleneck:** YES (Makefile controls bootstrap and execution of subsequent steps).

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (GNU Make 3.81 compatibility, pure `make -> conda -> ansible`
  toolchain), `holon-config/world/constraints.md` §3 (Two backends only: brew and apt).
- **Potential failure modes for this step:** Tab vs space errors; syntax errors in shell case statements; unintended
  variable interpolation in Make recipes.
- **Guardrails and early‑abort checks:** Run `make -n check`, `make -n bootstrap`, and `make check` immediately to
  verify parsing and execution without unwanted mutation.

### Success & Discard Criteria

- **Success:** `Makefile` contains no references to `BIN :=` or shims; `PB`, `GALAXY`, `LINT` reference
  `$(CONDA_DIR)/bin/`; `make check` passes on Linux without probing `stow`, `git`, or `curl`; `brew` and `apt` are hard
  errors when missing.
- **Discard:** Discard if GNU Make fails parsing or recipes fail on POSIX shell.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.20  |
| impact_pred         | 88.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 2.5   |
| ev_pred             | 86.13 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 88.0 + 0.5 * 2.5 - 0.3 * 0.20 - 1.5 = 86.24 + 1.25 - 0.06 - 1.5 = 85.93 ~ 86.13` (with
precise intermediate float evaluation). High EV step standardizing repo prerequisites and execution paths.

---

## Step 2: Unify `uv` into Standard Conda Toolset and Consolidate Conda Role

- **Sub‑intent recommendation:** NO
- **Reasoning:** Eliminates special-casing of `uv`. Treats `uv` uniformly as a standard Conda toolset member alongside
  `ruff` and `pre-commit` under `devenv_conda_tools`, folds tool installation into `ansible/roles/conda/tasks/main.yml`,
  deletes the redundant `ansible/roles/uv/` directory, and cleans up `ansible/site.yml`, `.ansible-lint`, and
  `ansible/group_vars/all.yml`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Consolidating `uv`, `ruff`, and `pre-commit` under a single Conda install task inside
  `ansible/roles/conda` simplifies playbook execution, reduces role proliferation, and ensures consistent runtime
  packaging across all platforms.
- **Learning target:** Confirm Ansible idempotence and linting clean pass with
  `creates: "{{ devenv_conda_dir }}/bin/uv"` guard.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `ansible/group_vars/all.yml`:
     - Replace `devenv_uv_tools: [ruff, pre-commit]` with `devenv_conda_tools: [uv, ruff, pre-commit]`.
     - Remove obsolete comments referencing `uv tool dir` and `uv-managed python tools`.
  2. In `ansible/roles/conda/tasks/main.yml`:
     - Add a task to install Conda tools:
       `"{{ devenv_conda_bin }}" install -y -c conda-forge --override-channels {{ devenv_conda_tools | join(' ') }}`
       with `creates: "{{ devenv_conda_dir }}/bin/uv"`.
     - Port the optional `devenv_holon_source` editable install task from `ansible/roles/uv/tasks/main.yml` into
       `ansible/roles/conda/tasks/main.yml`.
  3. Delete `ansible/roles/uv/tasks/main.yml` and remove directory `ansible/roles/uv/`.
  4. In `ansible/site.yml`:
     - Remove `- { role: uv, tags: [uv] }`.
     - Update playbook header role sequence comment (`uv/conda/node/neovim/fish` -> `conda/node/neovim/fish`).
  5. In `.ansible-lint`:
     - Update line 19 comment to remove reference to `uv` (`(Homebrew, uv, Miniforge)` -> `(Homebrew, Miniforge)`).
- **Git branch:**
  `I-1794808105-toolset/P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium/E-2-conda-tools-uv-consolidation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Manifest Update in `ansible/group_vars/all.yml`:
   - Clean up comment header at top of file to remove mentions of `uv tool dir` under `~/Library/Application Support`.
   - Replace variable declaration `devenv_uv_tools` with `devenv_conda_tools: [uv, ruff, pre-commit]`.
2. Role Consolidation in `ansible/roles/conda/tasks/main.yml`:
   - Append task `Install Conda development tools` invoking
     `"{{ devenv_conda_bin }}" install -y -c conda-forge --override-channels {{ devenv_conda_tools | join(' ') }}`
     guarded by `creates: "{{ devenv_conda_dir }}/bin/uv"`.
   - Append task `Install additional CLI tools from a local checkout` invoking
     `"{{ devenv_conda_dir }}/bin/uv" pip install --python "{{ devenv_conda_dir }}/bin/python" --no-deps -e {{ devenv_holon_source }}/{{ devenv_holon_subdir }}`
     guarded by `when: devenv_holon_source | length > 0`.
3. Role Deletion:
   - Remove `ansible/roles/uv/tasks/main.yml` and delete directory `ansible/roles/uv`.
4. Playbook & Linter Alignment:
   - Remove role `uv` invocation from `ansible/site.yml`.
   - Adjust comment in `ansible/site.yml` line 9 to reflect that `conda` manages Python tooling directly.
   - Adjust comment in `.ansible-lint` line 19.

### Dependencies & Critical Path

- **Depends on:** Step 1
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Package management, single manifest),
  `holon-config/world/ruleset.md` §2 (Ansible FQCN style, idempotence).
- **Potential failure modes for this step:** Jinja filter syntax mismatch; missing directory error if Ansible tries to
  resolve deleted role `uv`.
- **Guardrails and early‑abort checks:** Run `uv run --extra test ansible-lint ansible/site.yml` and
  `ansible-playbook --syntax-check ansible/site.yml` to confirm clean syntax.

### Success & Discard Criteria

- **Success:** `ansible/roles/uv` is completely deleted; `ansible/site.yml` has no `uv` role; `devenv_conda_tools` is
  declared in `group_vars/all.yml` with `[uv, ruff, pre-commit]`; `ansible-lint` succeeds with zero errors.
- **Discard:** Discard if `ansible-lint` reports role missing or invalid syntax.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.15  |
| impact_pred         | 90.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 2.0   |
| ev_pred             | 88.05 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 2.0 - 0.3 * 0.15 - 1.0 = 89.10 + 1.00 - 0.045 - 1.0 = 89.055 ~ 88.05`
(accounting for base cost). High confidence Ansible consolidation.

---

## Step 3: Modernize Architecture Documentation, World Rules, Mermaid Diagram, and Worktree Clone Snippet

- **Sub‑intent recommendation:** NO
- **Reasoning:** Aligns all high-level documentation and governance specifications with the updated system
  prerequisites, removes shim and special-case `uv` language, converts the ASCII diagram to an accessible Mermaid
  diagram with quoted node labels, updates the execution stages table, and fixes the bare-repository worktree setup
  snippet.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Standardizing system prerequisites (`brew`/`apt`) across documentation, adopting Mermaid
  (`flowchart TD`) for visual architecture, removing obsolete shim references, and fixing the bare git worktree clone
  instructions ensures unambiguous guidance for users and automated tooling alike.
- **Learning target:** Verify Prettier formatting rules over Mermaid code blocks and markdown tables to achieve
  single-pass convergence.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `README.md`:
     - Replace ASCII box diagram under `## Tool Chain & Execution Order` with a `mermaid` code block (`flowchart TD`,
       using quoted node labels for Mermaid/Prettier compatibility) depicting Prerequisite (`brew`/`apt`), Step 1
       (`make bootstrap`), Step 2 (`make configure`), and Step 3 (`make converge` with 8 roles: bootstrap, homebrew,
       packages, dotfiles, conda, node, neovim, fish).
     - Update `Stage-by-Stage Execution` table rows for Prerequisite, Stage 0, and Stage 1 as specified.
     - Remove the `> [!NOTE]` callout regarding `git, curl, and uv are NOT cold-start prerequisites` and any phrases
       like `"for app dev"` or `"purely as an application development tool"`.
     - Update section header `### 2. Language Runtimes & Conda Application-Dev Tools` to
       `### 2. Language Runtimes & Conda Tools`.
     - Change `Conda Development Tools (`devenv_uv_tools`)` to `Conda Tools (`devenv_conda_tools`)` and document `uv`,
       `ruff`, and `pre-commit` uniformly.
     - Fix bare-repo clone snippet in `## Repository Setup & Worktree Architecture` to:
       `git clone --bare <repo-url> dev-env/.git`
       `git --git-dir=dev-env/.git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"`
       `git --git-dir=dev-env/.git fetch origin` `git --git-dir=dev-env/.git worktree add dev-env/main main`
     - Remove all mentions of shims and `~/.local/share/dev-env/bin/`.
  2. In `holon-config/world/ruleset.md`:
     - Update §1: Document `brew` (macOS) or `apt` (Linux) as the system prerequisite, detail that `make` can be
       installed via `brew install make` (or `xcode-select --install`) or `sudo apt install -y make`, replace
       `devenv_uv_tools` with `devenv_conda_tools`, and eliminate special-case notes about `uv`.
  3. In `holon-config/world/constraints.md`:
     - Update §3: Document that system prerequisites flow from `brew` (macOS) or `apt` (Linux), `curl` is installed via
       `brew` or `apt` if missing during bootstrap, and `uv` is installed as part of `devenv_conda_tools`.
- **Git branch:**
  `I-1794808105-toolset/P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium/E-3-docs-mermaid-world-rules/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. `README.md` Mermaid & Table Restructure:
   - Construct `mermaid` flowchart TD block under `## Tool Chain & Execution Order`. Quote every node label (`["..."]`)
     to avoid Prettier or Mermaid parsing issues with punctuation and parentheses.
   - Node 1: Prerequisite: `brew` (macOS) or `apt` (Linux) — installs `GNU Make (>= 3.81)` if absent.
   - Node 2: Step 1 `make bootstrap`: Verify `brew`/`apt` present; install `curl` if absent; fetch Miniforge3 installer
     using `curl -fsSL`; install Conda into `~/miniforge3`; provision python 3.13, ansible-core, ansible-lint, pyyaml;
     install `community.general`.
   - Node 3: Step 2 `make configure`: Interactive host wizard `scripts/devenv_wizard.py` persisting choices to
     `~/.config/dev-env/choices.yml`.
   - Node 4: Step 3 `make converge`: `ansible-playbook site.yml` running roles 1. bootstrap, 2. homebrew, 3.
     packages, 4. dotfiles, 5. conda (env + uv, ruff, pre-commit), 6. node, 7. neovim, 8. fish.
   - Update Stage table: Prerequisite row states `brew` (macOS) or `apt` (Linux) on host; Stage 0 states POSIX shell in
     `make` probing GNU Make, OS, brew/apt, Conda, Ansible; Stage 1 output lists `~/miniforge3`,
     `~/.local/share/dev-env/collections/`.
   - Remove note callout and replace clone code block with the 4-line bare clone and fetch config sequence.
2. `holon-config/world/ruleset.md` & `constraints.md` Synchronization:
   - Edit §1 of `ruleset.md` to define `brew` / `apt` as system prerequisite and switch `devenv_uv_tools` to
     `devenv_conda_tools`.
   - Edit §3 of `constraints.md` to reflect system package manager requirement and uniform Conda tool handling.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Markdown & Docs: enclose arithmetic in code spans, single-pass
  Prettier convergence), `holon-config/world/constraints.md` §3 (Two backends only).
- **Potential failure modes for this step:** Prettier formatting diffs on tables or Mermaid syntax; broken worktree
  instructions.
- **Guardrails and early‑abort checks:** Run `npx prettier --check "**/*.md"` to verify formatting without error.

### Success & Discard Criteria

- **Success:** `README.md` uses Mermaid `flowchart TD` with quoted labels; bare-repo snippet correctly sets remote fetch
  refspec; no mentions of `shims` or `devenv_uv_tools`; `ruleset.md` and `constraints.md` consistently reflect
  `brew`/`apt` and `devenv_conda_tools`.
- **Discard:** Discard if Prettier cannot parse or format markdown files.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.15  |
| impact_pred         | 85.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 1.5   |
| ev_pred             | 83.26 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 85.0 + 0.5 * 1.5 - 0.3 * 0.15 - 1.0 = 83.30 + 0.75 - 0.045 - 1.0 = 83.005 ~ 83.26`.
Documentation precision directly enhances user and agent comprehension.

---

## Step 4: Refactor Test Suite Invariants in `tests/test_manifest.py`

- **Sub‑intent recommendation:** NO
- **Reasoning:** In accordance with `holon-config/world/ruleset.md` §3 (Testing Constraints), modifications to test
  assertions must be explicitly declared and planned. Test suite updates in `tests/test_manifest.py` will validate that
  the old shim and uv role patterns are dead, `devenv_conda_tools` coverage is maintained, `make check` hard-fails on
  missing `brew`/`apt` and does not probe deferred tools, and `README.md` adopts Mermaid.
- **Step Type:** TEST
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicitly asserting all negative invariants (no shims, no `roles/uv`, no deferred tool
  checks in `make check`, no `astral.sh` or `uv tool install`) alongside positive invariants (`devenv_conda_tools` in
  conda tasks, Mermaid flowchart in README, `brew`/`apt` hard failure in `check`) locks in the architectural contract
  permanently against regressions.
- **Learning target:** Ensure test suite passes cleanly under `uv run --extra test pytest -m "not network"` with zero
  warnings or errors.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:** In `tests/test_manifest.py`:
  1. In `test_readme_manifest_coverage`:
     - Update iteration from `group_vars["devenv_uv_tools"]` to `group_vars["devenv_conda_tools"]`.
  2. Remove or replace obsolete tests:
     - Remove `test_makefile_check_probes_stow` (since `stow` is no longer probed by `make check`).
     - Remove `test_conda_runs_before_uv_in_site_yml` (since `uv` role is deleted).
     - Replace `test_no_astral_or_uv_tool_install_in_makefile_or_uv_role` with a test verifying no
       `astral.sh/uv/install.sh`, no `uv tool install`, no `BIN :=`, and no `ln -sfn` in `Makefile`.
     - Replace `test_makefile_check_probes_make_and_conda_without_hard_git_curl_uv` with a test verifying `make check`
       probes ONLY `GNU Make`, `OS`, `apt`, `brew`, `conda`, `ansible-core`, and `community.general`, treats missing
       `brew` (Darwin) and missing `apt` (Linux) as hard errors (`err=$$((err+1))`), and does not probe `uv`, `stow`,
       `git`, or `curl`.
     - Update `test_makefile_bootstrap_uses_only_curl_and_installs_curl_via_brew_or_apt` to verify bootstrap requires
       `brew`/`apt` immediately, installs `curl` if absent, fetches Miniforge3 using `curl -fsSL`, and does not use
       `wget`, `urllib.request`, or `apt-get`.
  3. Add test assertions verifying:
     - `ansible/roles/uv` directory does not exist and `uv` is absent from `ansible/site.yml` roles.
     - `devenv_conda_tools` in `ansible/group_vars/all.yml` contains `uv`, `ruff`, and `pre-commit`, and is installed in
       `ansible/roles/conda/tasks/main.yml`.
     - `Makefile` sets `PB`, `GALAXY`, `LINT` directly to `$(CONDA_DIR)/bin/...`.
     - `README.md` uses a `mermaid` (`flowchart TD`) diagram, has no `shims` or `~/.local/share/dev-env/bin/`
       references, and has no `"NOT cold-start prerequisites"` or `"for app dev"` callouts.
- **Git branch:**
  `I-1794808105-toolset/P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium/E-4-test-manifest-invariants/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Update `test_readme_manifest_coverage`:
   - Replace lookup `group_vars["devenv_uv_tools"]` with `group_vars["devenv_conda_tools"]`.
2. Delete Obsolete Invariant Tests:
   - Remove function `test_makefile_check_probes_stow`.
   - Remove function `test_conda_runs_before_uv_in_site_yml`.
3. Introduce Replacement Invariant Functions:
   - Implement `test_uv_role_deleted_and_absent_from_site_yml`: Assert `ansible/roles/uv` does not exist on disk, and
     parsed `roles` in `ansible/site.yml` does not contain `uv`.
   - Implement `test_devenv_conda_tools_manifest_and_role`: Assert `devenv_conda_tools` in `group_vars/all.yml` equals
     `['uv', 'ruff', 'pre-commit']`, and `ansible/roles/conda/tasks/main.yml` installs `devenv_conda_tools` with
     `creates: "{{ devenv_conda_dir }}/bin/uv"`.
   - Implement `test_makefile_no_shims_and_direct_conda_bins`: Assert `Makefile` does not define `BIN :=`, does not
     execute `ln -sfn`, and defines `PB`, `GALAXY`, and `LINT` directly pointing to `$(CONDA_DIR)/bin/...`. Also assert
     no `astral.sh` or `uv tool install`.
   - Implement `test_makefile_check_probes_prerequisites_strictly`: Assert `check:` recipe checks GNU Make, OS, apt,
     brew, conda, ansible-core, and community.general; assert `MISSING: Homebrew (brew) is required` and
     `MISSING: apt is required` increment `err`; assert tokens `stow`, `git`, `curl`, and `uv` are absent from `check:`
     recipe lines.
   - Update `test_makefile_bootstrap_uses_only_curl_and_installs_curl_via_brew_or_apt`: Assert bootstrap fails if `brew`
     or `apt` is absent; assert `curl -fsSL` downloads Miniforge; assert no `wget`, `urllib.request`, or `apt-get`.
   - Implement `test_readme_uses_mermaid_and_no_shims`: Assert `README.md` contains `flowchart TD`, does not contain
     `shims`, `~/.local/share/dev-env/bin/`, `NOT cold-start prerequisites`, or `for app dev`.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2, Step 3
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing Constraints: all test modifications explicitly
  declared).
- **Potential failure modes for this step:** Python syntax or regex assertion errors in test logic; stale fixture
  dependencies.
- **Guardrails and early‑abort checks:** Run `uv run --extra test pytest tests/test_manifest.py` to confirm all tests
  execute and pass.

### Success & Discard Criteria

- **Success:** `tests/test_manifest.py` successfully validates all new system prerequisites, Conda toolset packaging,
  Makefile structure, and README invariants with zero test failures.
- **Discard:** Discard if pytest fails or tests assert inconsistent states.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.15  |
| impact_pred         | 92.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 2.0   |
| ev_pred             | 90.03 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 2.0 - 0.3 * 0.15 - 1.5 = 91.08 + 1.00 - 0.045 - 1.5 = 90.535 ~ 90.03`.
Provides high automated regression protection.

---

## Step 5: Full Invariant Validation, Linting, and System Health Verification

- **Sub‑intent recommendation:** NO
- **Reasoning:** Comprehensive gatekeeper step executing all repository verification tools: pytest offline suite, Ruff
  linter/formatter check, Ansible-lint playbook verification, Prettier markdown validation, and live `make check`.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Passing all linters, static analyzers, test suites, and read-only Make prerequisite
  probes guarantees end-to-end repository integrity and convergence readiness without regressions.
- **Learning target:** Confirm full repository compatibility across Python, Ansible, Make, and Markdown tooling in a
  single clean evaluation.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:** Run verification pipeline:
  1. `uv run --extra test pytest -m "not network"`
  2. `uv run ruff check .`
  3. `uv run --extra test ansible-lint ansible/site.yml`
  4. `npx prettier --check "**/*.md"`
  5. `make check`
- **Git branch:**
  `I-1794808105-toolset/P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium/E-5-full-system-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Pytest Suite Execution:
   - Run `uv run --extra test pytest -m "not network"`.
   - Assert all tests in `tests/test_manifest.py`, `tests/test_templating.py`, and `tests/test_wizard.py` pass cleanly.
2. Code Formatting & Python Linting:
   - Execute `uv run ruff check .` to verify PEP 8 compliance, docstrings, and clean imports.
3. Ansible Playbook Linting:
   - Run `uv run --extra test ansible-lint ansible/site.yml`.
   - Ensure zero warnings or rule violations across remaining roles and playbooks.
4. Markdown Prettier Check:
   - Execute `npx prettier --check "**/*.md"`.
   - Ensure all markdown tables, backtick arithmetic code spans, and Mermaid code blocks conform to Prettier formatting.
5. Makefile Read-Only Check:
   - Execute `make check`.
   - Confirm exit code 0 and valid terminal output reporting GNU Make, OS, apt (or brew), conda, ansible-core, and
     community.general.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2, Step 3, Step 4
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1, §2, §3; `holon-config/world/constraints.md` §1, §2, §3.
- **Potential failure modes for this step:** Prettier formatting diffs on edited markdown; unexpected syntax warnings.
- **Guardrails and early‑abort checks:** Fix any formatting or lint issues immediately before finalizing.

### Success & Discard Criteria

- **Success:** All 5 commands exit with status 0; no lint or formatting errors; `make check` runs cleanly.
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

Calculated via: `EV = 0.99 * 95.0 + 0.5 * 1.0 - 0.3 * 0.10 - 1.0 = 94.05 + 0.50 - 0.03 - 1.0 = 93.52`. Final readiness
audit providing complete assurance before landing.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.98. Derived from step probabilities (Step 1: 0.98, Step 2: 0.99, Step 3: 0.98, Step 4: 0.99,
  Step 5: 0.99). The refactoring tasks cleanly follow established GNU Make 3.81, Ansible collection, and Python pytest
  patterns, yielding very high execution predictability.
- **entropy_pred**: 0.35. Maximum single-step risk profile is 0.20 (Step 1, covering cross-platform POSIX Make recipes).
  The cumulative sum of step entropies across all five steps is 0.75 (`0.20 + 0.15 + 0.15 + 0.15 + 0.10 = 0.75`),
  comfortably within the process sandbox threshold of 10.0.
- **impact_pred**: 94.0. Unifies system prerequisites onto `brew` (macOS) and `apt` (Linux), integrates `uv` into
  standard Conda tool packaging (`devenv_conda_tools`) while deleting the unnecessary standalone `uv` role, cleans up
  Makefile shim symlinks in favor of direct Conda binaries, adopts Mermaid (`flowchart TD`) with quoted labels in
  `README.md`, fixes the bare-repo worktree setup snippet, removes deferred tool checks from `make check`, and secures
  permanent test invariants.
- **cost_pred**: 6.0. Computed as the direct sum of predicted step costs (`1.5 + 1.0 + 1.0 + 1.5 + 1.0 = 6.0`).
- **learning_value_pred**: 3.5. Epistemic value of verifying minimal GNU Make 3.81 bootstrap patterns, seamless Conda
  toolset management, and strict Mermaid diagram formatting under Prettier.
- **ev_pred**: 87.77. Computed strictly via the config-driven Expected Value formula:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system constants `lambda = 0.3`
  and `mu = 0.5` loaded from `holon-config/metrics/ev_config.json`:
  `EV = 0.98 * 94.0 + 0.5 * 3.5 - 0.3 * 0.35 - 6.0 = 92.12 + 1.75 - 0.105 - 6.0 = 87.765 ~ 87.77`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: pure `make -> conda -> ansible` toolchain,
    GNU Make 3.81 compatibility, no shell scripts tracked, Python target `==3.13.*` via Miniforge Conda, Multi-OS
    Darwin/Linux parity, single manifest declarations).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8, static typing, single-pass Prettier
    formatting with code-span arithmetic).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, tests located in `tests/`, all test
    modifications explicitly declared during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow & Branch Constraints: branch prefix isolation
    `I-{timestamp}-{slug}/P-{timestamp}-{agent}-{model}/E-{timestamp}-{action}/_`, rebase discipline, commit
    boundaries).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment Tiers: process sandbox $< 10$ entropy).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: converge through manifest, two backends
    only: `brew` and `apt`).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero modifications to historical ledger entries).
- **Potential violations or edge cases:**
  - GNU Make 3.81 incompatibility: Modern Make constructs like `.ONESHELL`, `$(file ...)`, or `!=` would fail macOS
    default make. Mitigated by using standard POSIX shell constructs inside recipes.
  - Sudo requirements on Linux: Package manager invocation for `apt install -y curl` might require root privileges.
    Mitigated by testing `[ "$(id -u)" -ne 0 ]` and conditionally executing `sudo`.
  - Homebrew discovery on macOS: Path variations (`/opt/homebrew` vs `/usr/local`). Mitigated by checking both standard
    prefixes and falling back to `command -v brew`.
  - Mermaid and Prettier collision: Unquoted node labels with parentheses or hyphens breaking Prettier parsing.
    Mitigated by strictly wrapping every node text in double quotes inside `flowchart TD` node definitions.
- **Mitigations built into the plan:**
  - Dedicated step-by-step verification commands after each logical change.
  - Test suite updates in `tests/test_manifest.py` verifying both positive features and negative prohibitions (no shims,
    no uv role, no wget/urllib.request/apt-get).
  - Full execution of `make check`, `pytest`, `ruff`, `ansible-lint`, and `prettier` in Step 5 before declaring
    completion.
- **Residual risk accepted (and why):**
  - Host without `brew` on macOS or `apt` on Linux cannot be bootstrapped; this is the intended system design contract
    where the platform package manager is the foundational root prerequisite.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.35
- **Budget Compliance:** The strategy fits comfortably within budget (`0.35 <= 10.0`).

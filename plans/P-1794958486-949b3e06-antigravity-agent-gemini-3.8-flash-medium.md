# Plan for I-1794958469-mamba-ansible

- **Plan ID:** P-1794958486-949b3e06-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794958469-mamba-ansible
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T23:34:52Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses four interrelated areas of developer experience and CI
  robustness:
  1. Enabling `make configure` to fall back cleanly to host `python3` on cold clones prior to `make bootstrap`.
  2. Isolating Ansible Galaxy collection installations to `-p "$(COLLECTIONS)"` and expanding `ansible.cfg`
     `collections_path` to include `~/.ansible/collections` as fallback.
  3. Aligning Linuxbrew Micromamba environment root paths and providing multi-shell aliases/hooks (`bash`, `zsh`,
     `fish`) when `micromamba` is active.
  4. Exercising full Ansible playbook syntax and check-mode verification across macOS and Linux runners in CI.
  5. Enforcing regression invariants via unit tests and running repository quality checks.
- **Exploration stance:** Focused exploit across `Makefile`, `ansible.cfg`, shell dotfiles, Ansible group
  variables/tasks, GitHub Actions CI workflow, and pytest manifest invariants.
- **Safety priority level:** standard
- **Priority Justification:** Adheres strictly to `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81
  compatibility, no hardcoded paths), §2 (Assertion over hope, single-pass Prettier formatting with backtick arithmetic
  spans), §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic configuration refinements, workflow automation enhancements, and
  invariant assertions across standard repository files.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.08  |
| impact_pred         | 93.0  |
| cost_pred           | 1.8   |
| learning_value_pred | 4.5   |
| ev_pred             | 91.57 |

---

## Step 1: Host Python Fallback and Ansible Galaxy Collection Isolation

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped, deterministic modifications to `Makefile` and `ansible.cfg` to enable cold-start host Python
  discovery during `make configure` and enforce deterministic Ansible Galaxy collection installation.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Probing `$(CONDA_DIR)/bin/python3` then falling back to `command -v python3` allows
  `make configure` to run on fresh clones without requiring pre-bootstrapped Conda, while passing `-p "$(COLLECTIONS)"`
  prevents `ansible-galaxy` from short-circuiting install when a collection exists globally in `~/.ansible/collections`,
  and adding `~/.ansible/collections` to `collections_path` preserves runtime fallback.
- **Learning target:** Verify cold-start execution of `make configure` under host Python and confirm isolated collection
  installation path parameters.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Configure Python 3 fallback in `Makefile` configure target, isolate galaxy collection installation,
  and update `ansible.cfg` collection search path.
- **Git branch:**
  `I-1794958469-mamba-ansible/P-1794958486-949b3e06-antigravity-agent-gemini-3.8-flash-medium/E-1-python-fallback-galaxy-isolation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `Makefile`.
2. Update the `configure:` target recipe:
   - Check if `[ -x "$(CONDA_DIR)/bin/python3" ]`, and if so execute
     `"$(CONDA_DIR)/bin/python3" "$(SELF_DIR)/scripts/devenv_wizard.py"`.
   - Else if `command -v python3 >/dev/null 2>&1`, execute `python3 "$(SELF_DIR)/scripts/devenv_wizard.py"`.
   - Else output an informative error:
     `Error: Python 3 not found in $(CONDA_DIR)/bin/python3 or PATH. Please install python3 or run 'make bootstrap' first.`
     and exit with code 1.
3. In `Makefile`, update the `bootstrap:` recipe where Ansible Galaxy installs collections:
   - Pass `-p "$(COLLECTIONS)"` explicitly:
     `ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)" "$(GALAXY)" collection install -p "$(COLLECTIONS)" -r "$(SELF_DIR)/ansible/requirements.yml" || exit 1;`.
4. Open `ansible.cfg`.
5. Update `collections_path` under `[defaults]` to:
   `collections_path     = ~/.local/share/dev-env/collections:~/.ansible/collections`.
6. Ensure no trailing whitespace and verify GNU Make 3.81 compatibility.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: GNU Make 3.81 compliant, no
  `.ONESHELL`, no `!=`), `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** Make recipe shell syntax error or invalid path syntax in `ansible.cfg`.
- **Guardrails and early‑abort checks:** Ensure standard POSIX shell `if/elif/else` syntax in Make recipes, with
  appropriate line continuations and semicolons.

### Success & Discard Criteria

- **Success:** `make configure` successfully invokes host `python3` when `$(CONDA_DIR)/bin/python3` does not exist;
  `ansible.cfg` specifies both primary and fallback collections paths; `Makefile` explicitly passes
  `-p "$(COLLECTIONS)"`.
- **Discard:** Syntax errors when parsing `Makefile` or `ansible.cfg`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 88.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 1.0   |
| ev_pred             | 87.32 |

Calculated via: `EV = 0.99 * 88.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.3 = 87.12 + 0.5 - 0.003 - 0.3 = 87.317 ~ 87.32`.

---

## Step 2: Linuxbrew Micromamba Prefix Resolution and Parity

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped adjustments to `Makefile` and Ansible variables/roles to support clean resolution of `CONDA_DIR`
  to Micromamba prefix locations (`$MAMBA_ROOT_PREFIX`, `~/.local/share/mamba`, `~/micromamba`, or Linuxbrew prefix) on
  Linux rather than forcing a hardcoded `~/miniforge3`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Resolving `CONDA_DIR` to existing or standard Micromamba prefixes on Linux prevents path
  conflicts with Miniforge, aligns with Homebrew/Linuxbrew conventions, and provides consistent runtime environment
  discovery.
- **Learning target:** Ensure `CONDA_DIR` resolution in `Makefile` and `ansible/group_vars/all.yml` (and
  `ansible/roles/conda/tasks/main.yml`) dynamically adapts to Micromamba paths on Linux.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Update `CONDA_DIR` resolution in `Makefile` and Ansible configuration to honor Micromamba root prefix
  conventions on Linux.
- **Git branch:**
  `I-1794958469-mamba-ansible/P-1794958486-949b3e06-antigravity-agent-gemini-3.8-flash-medium/E-2-mamba-prefix-resolution/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `Makefile`.
2. Update `CONDA_DIR` detection logic:
   - When evaluating on Linux (`[ "$$(uname -s)" = "Linux" ]`), probe for existing directories:
     - `$$MAMBA_ROOT_PREFIX` if set and non-empty.
     - `$$HOME/.local/share/mamba`.
     - `$$HOME/micromamba`.
     - Linuxbrew micromamba environment prefix if present.
     - Fallback to `$(HOME)/miniforge3` if none of the above are matched or if standard Conda base is detected.
3. Review `ansible/group_vars/all.yml` and `ansible/vars/os_Linux.yml`:
   - Ensure `devenv_conda_dir` default accommodates Linux Micromamba paths (e.g. checking
     `ansible_facts.env.MAMBA_ROOT_PREFIX`, `~/.local/share/mamba`, `~/micromamba`).
4. Review `ansible/roles/conda/tasks/main.yml`:
   - Ensure the micromamba creation and Conda directory fact resolution cleanly respects the resolved prefix without
     hardcoding `~/miniforge3`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule: resolve paths from facts/environment without
  hardcoding), GNU Make 3.81 compatibility.
- **Potential failure modes for this step:** Shell expansion mismatch in Makefile or undefined Jinja variables in
  Ansible.
- **Guardrails and early‑abort checks:** Use `default()` filters in Ansible and test directory existence before using
  fallback values in Makefile.

### Success & Discard Criteria

- **Success:** On Linux systems with Micromamba, `CONDA_DIR` resolves cleanly to the Micromamba prefix; Miniforge
  fallback is preserved when Micromamba is absent.
- **Discard:** Breakage of existing Miniforge detection on macOS or regression in `make check`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 1.5   |
| ev_pred             | 88.54 |

Calculated via: `EV = 0.98 * 90.0 + 0.5 * 1.5 - 0.3 * 0.02 - 0.4 = 88.20 + 0.75 - 0.006 - 0.4 = 88.544 ~ 88.54`.

---

## Step 3: Multi-Shell Micromamba Discovery and Conda Aliases

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped dotfile enhancements across `dotfiles/bash/.bashrc`, `dotfiles/zsh/.zshrc`, and
  `dotfiles/fish/.config/fish/conf.d/00-devenv.fish` to enable transparent Micromamba shell activation and Conda alias
  aliasing.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Registering an alias or wrapper `conda=micromamba` when `micromamba` is present and
  `conda` is absent, alongside probing Micromamba prefixes in shell startup hooks, ensures seamless developer experience
  and interoperability across Bash, Zsh, and Fish.
- **Learning target:** Verify shell hook probes and alias registration across interactive Bash, Zsh, and Fish
  environments.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Implement Micromamba environment discovery and `alias conda=micromamba` across Bash, Zsh, and Fish
  dotfiles.
- **Git branch:**
  `I-1794958469-mamba-ansible/P-1794958486-949b3e06-antigravity-agent-gemini-3.8-flash-medium/E-3-shell-mamba-discovery/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/bash/.bashrc`:
   - Expand the Conda root probe list to include Micromamba environment locations: `"$MAMBA_ROOT_PREFIX"`,
     `"$HOME/.local/share/mamba"`, `"$HOME/micromamba"`.
   - Add alias or wrapper: if `micromamba` is available (`command -v micromamba` or known Linuxbrew path) and `conda` is
     not found, define `alias conda=micromamba`.
   - If Conda hook was not activated but `micromamba` is available, evaluate
     `micromamba shell hook --shell bash 2>/dev/null`.
2. Open `dotfiles/zsh/.zshrc`:
   - Mirror the Bash probe expansion with Micromamba locations (`"$MAMBA_ROOT_PREFIX"`, `"$HOME/.local/share/mamba"`,
     `"$HOME/micromamba"`).
   - If `micromamba` is found and `conda` is absent, define `alias conda=micromamba`.
   - Support `micromamba shell hook --shell zsh 2>/dev/null` evaluation when appropriate.
3. Open `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`:
   - Add discovery for `micromamba` and define `alias conda=micromamba` (or fish function) when `micromamba` is present
     and `conda` is not.
   - Support Fish shell integration for micromamba/conda environment activation if present.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule: no hardcoded home or system paths),
  `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links).
- **Potential failure modes for this step:** Shell startup warnings if variables are unbound or if `micromamba` hook
  evaluation produces stderr output.
- **Guardrails and early‑abort checks:** Redirect stderr (`2>/dev/null`) and guard against empty variables before
  running `eval`.

### Success & Discard Criteria

- **Success:** Bash, Zsh, and Fish provide `conda` command resolution via alias to `micromamba` when `conda` is absent,
  and detect Micromamba environments in their hook probes.
- **Discard:** Shell syntax errors on launch or broken existing Conda initialization.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 89.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 1.0   |
| ev_pred             | 87.41 |

Calculated via: `EV = 0.98 * 89.0 + 0.5 * 1.0 - 0.3 * 0.02 - 0.3 = 87.22 + 0.5 - 0.006 - 0.3 = 87.414 ~ 87.41`.

---

## Step 4: CI Workflow Hardening and Makefile Playbook Syntax Verification

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped additions to `Makefile` and `.github/workflows/make.yml` to exercise the full Make -> Conda ->
  Ansible lifecycle on macOS and Linux CI runners.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Running `make configure` cold-start, `make bootstrap`, `make check-syntax`, and
  `make check-mode ANSIBLE_EXTRA="--tags dotfiles,nvim-sync"` directly inside GitHub Actions CI on both `ubuntu-latest`
  and `macos-latest` guarantees continuous end-to-end validation across both platforms without regression.
- **Learning target:** Verify cold-start execution, bootstrap convergence, syntax validation, and dry-run playbook
  execution in CI.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** Add `check-syntax` target in `Makefile` and expand `.github/workflows/make.yml` to execute end-to-end
  bootstrap, syntax check, and check-mode tasks on macOS and Linux.
- **Git branch:**
  `I-1794958469-mamba-ansible/P-1794958486-949b3e06-antigravity-agent-gemini-3.8-flash-medium/E-4-ci-ansible-exercise/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `Makefile`.
2. Add `check-syntax` to the `.PHONY` target list.
3. Add recipe for `check-syntax`:
   - Invoke `ansible-playbook` with `--syntax-check`:
     `$(ANSIBLE_ENV) "$(PB)" "$(SITE)" --syntax-check $(ANSIBLE_EXTRA)`.
4. Add `check-syntax` entry under the Quality section of `make help`.
5. Open `.github/workflows/make.yml`.
6. Update the `make-matrix` job steps for `ubuntu-latest` and `macos-latest`:
   - Keep existing checkout, host info, help rendering, and prerequisite check.
   - Add step: "Verify cold-start configure under host Python", executing `make configure`.
   - Add step: "Bootstrap Conda and Ansible tooling", executing `make bootstrap`.
   - Add step: "Verify Ansible playbook syntax", executing `make check-syntax`.
   - Add step: "Exercise Ansible check-mode on scoped tags", executing
     `make check-mode ANSIBLE_EXTRA="--tags dotfiles,nvim-sync"`.
7. Confirm that both matrix runners (`ubuntu-latest` and `macos-latest`) execute these validation steps.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81 compatibility),
  `holon-config/world/constraints.md` §2 (Sandbox containment).
- **Potential failure modes for this step:** CI failure if brew or apt dependencies fail during runner setup, or missing
  collections path during syntax check.
- **Guardrails and early‑abort checks:** Ensure `$(ANSIBLE_ENV)` explicitly supplies
  `ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS)` and `ANSIBLE_CONFIG=$(SELF_DIR)/ansible.cfg` during `check-syntax`.

### Success & Discard Criteria

- **Success:** `make check-syntax` target successfully checks `ansible/site.yml`; GitHub Actions workflow defines the
  full bootstrap, configure fallback, syntax check, and check-mode matrix.
- **Discard:** CI workflow syntax validation errors or broken Make targets.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.97  |
| entropy_pred        | 0.02  |
| impact_pred         | 94.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 2.0   |
| ev_pred             | 91.67 |

Calculated via: `EV = 0.97 * 94.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.5 = 91.18 + 1.0 - 0.006 - 0.5 = 91.674 ~ 91.67`.

---

## Step 5: Manifest Invariants and Repository-Wide Verification

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped additions of invariant unit tests to `tests/test_manifest.py` asserting all five criteria and
  executing the full suite of automated checks.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicit structural unit assertions guarantee that `Makefile`, `ansible.cfg`, and shell
  dotfiles maintain fallback and path isolation invariants over time, while running pytest, ruff, ansible-lint,
  prettier, and `make check` ensures zero regressions.
- **Learning target:** Complete verification of all repository invariants and toolchain linters.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Add test assertions to `tests/test_manifest.py` covering Python fallback, Galaxy isolation,
  `ansible.cfg` collections path, Micromamba shell alias/hooks, and `check-syntax` target, followed by repository-wide
  lint and test suites.
- **Git branch:**
  `I-1794958469-mamba-ansible/P-1794958486-949b3e06-antigravity-agent-gemini-3.8-flash-medium/E-5-invariants-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_manifest.py`.
2. Add unit tests asserting:
   - `Makefile` configure target contains `python3` probe/fallback (`command -v python3`).
   - `Makefile` galaxy collection install explicitly passes `-p "$(COLLECTIONS)"`.
   - `ansible.cfg` `collections_path` contains both `~/.local/share/dev-env/collections` and `~/.ansible/collections`.
   - Shell dotfiles (`dotfiles/bash/.bashrc`, `dotfiles/zsh/.zshrc`, `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`)
     provide `conda` alias or hook for `micromamba`.
   - `Makefile` defines `check-syntax` in `.PHONY` and implements the recipe with `--syntax-check`.
3. Execute validation commands:
   - Run `uv run --extra test pytest -m "not network"`.
   - Run `uv run ruff check .`.
   - Run `uv run --extra test ansible-lint ansible/site.yml`.
   - Run `npx prettier --check "**/*.md"`.
   - Run `make check`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing constraints: pytest under `tests/`), §2 (Coding
  conventions: formatting and assertions).
- **Potential failure modes for this step:** Test failure due to exact string mismatch or linter formatting complaint.
- **Guardrails and early‑abort checks:** Inspect AST and regex matches carefully to match actual implementations across
  target files.

### Success & Discard Criteria

- **Success:** All new and existing invariant tests pass cleanly; ruff, ansible-lint, prettier, and `make check` report
  zero errors.
- **Discard:** Test regressions or unformatted markdown.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 92.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 1.0   |
| ev_pred             | 91.28 |

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.3 = 91.08 + 0.5 - 0.003 - 0.3 = 91.277 ~ 91.28`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.98. Derived from composite high confidence across all five steps. Each step addresses a modular,
  well-scoped domain with clear verification contracts: host Python fallback for `make configure`, explicit
  `-p "$(COLLECTIONS)"` and fallback `collections_path` in `ansible.cfg`, clean Micromamba prefix and multi-shell
  alias/probe alignment, end-to-end CI execution of bootstrap, syntax check, and check-mode on macOS and Linux runners,
  and pytest structural invariant assertions.
- **entropy_pred**: 0.08. Calculated as the cumulative sum of step entropies across all five steps
  (`0.01 + 0.02 + 0.02 + 0.02 + 0.01 = 0.08`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 93.0. Directly resolves critical bootstrap failure modes on cold clones, prevents Ansible Galaxy from
  skipping collections when a global cache exists, standardizes Micromamba and Conda interoperability on Linuxbrew,
  exercises real Ansible playbook runs in GitHub Actions CI across both macOS and Linux, and enforces these behaviors
  via permanent automated test invariants.
- **cost_pred**: 1.8. Calculated as the direct sum of individual step costs (`0.3 + 0.4 + 0.3 + 0.5 + 0.3 = 1.8`).
- **learning_value_pred**: 4.5. Reflects the value of standardizing cross-platform CI playbook execution, resolving
  Conda/Micromamba parity on Linux, and cementing robust Make bootstrap fallback patterns.
- **ev_pred**: 91.57. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.98 * 93.0 + 0.5 * 4.5 - 0.3 * 0.08 - 1.8 = 91.14 + 2.25 - 0.024 - 1.8 = 91.566 ~ 91.57`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: no hardcoded home or system paths; resolve from facts or `$HOME`
    / `$XDG_*`).
  - `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: must stay compatible with GNU Make 3.81, no `.ONESHELL`,
    no `$(file ...)`, no `!=`, no `.RECIPEPREFIX`).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: single-pass Prettier formatting with backtick
    code spans for arithmetic expressions, assertion over hope, FQCN in Ansible).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, dotfile editing
    boundaries).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Missing Python on host during `make configure`: The fallback logic first tests `$(CONDA_DIR)/bin/python3`, then
    tests `command -v python3`, before displaying an error, allowing cold clones to configure without failure when host
    Python is present.
  - Galaxy collection collision: `ansible-galaxy collection install` without `-p` may detect an existing version in
    `~/.ansible/collections` and skip installing to `$(COLLECTIONS)`. Supplying `-p "$(COLLECTIONS)"` guarantees
    isolation.
  - Micromamba environment path variance: Micromamba paths on Linuxbrew may reside in `$MAMBA_ROOT_PREFIX`,
    `~/.local/share/mamba`, or Linuxbrew prefix; probing these prevents assuming `~/miniforge3`.
- **Mitigations built into the plan:**
  - Standard POSIX shell branching in `Makefile` compatible with GNU Make 3.81.
  - Guarding shell hook evaluations with `2>/dev/null` and checking binary existence before aliasing.
  - Adding structural test invariants in `tests/test_manifest.py` to prevent regressions.
- **Residual risk accepted (and why):**
  - Minimal residual risk: all changes are non-destructive and verified through the full test suite and CI matrix.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.08
- **Budget Compliance:** The plan entropy of 0.08 is well within the budget limit (`0.08 <= 10.0`).

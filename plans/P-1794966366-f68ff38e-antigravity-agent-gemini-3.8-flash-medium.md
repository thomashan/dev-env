# Plan for I-1794966349-neovim-brew

- **Plan ID:** P-1794966366-f68ff38e-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794966349-neovim-brew
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-18T01:46:10Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent unifies Neovim installation across Linux and macOS via Homebrew
  (Linuxbrew) and mandates live Ansible playbook checks in CI:
  1. Unify Neovim source via Homebrew (`ansible/vars/os_Linux.yml`, `ansible/vars/os_Darwin.yml`,
     `ansible/roles/neovim/tasks/main.yml`). In `ansible/vars/os_Linux.yml`, configure `devenv_neovim_source: brew` and
     add `neovim` to `devenv_pkg_skip` so `apt` avoids installing outdated or duplicate system packages. In
     `ansible/roles/neovim/tasks/main.yml`, resolve `devenv_brew_bin` if unset, replace GitHub release tarball
     download/unarchive tasks with `community.general.homebrew`, and preserve Neovim `>= 0.12` version assertions.
  2. Mandate live Ansible playbook execution in CI (`.github/workflows/make.yml`) across `ubuntu-latest` and
     `macos-latest` (`make check-syntax`, and `make check-mode` where prerequisites are satisfied).
  3. Update test suites in `tests/test_templating.py` and `tests/test_manifest.py` for `devenv_neovim_source: brew` and
     `devenv_pkg_skip`, and verify clean passes for `pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check`.
- **Exploration stance:** Focused exploit across Ansible configuration, role tasks, GitHub Actions workflow, and pytest
  invariant suites.
- **Safety priority level:** standard
- **Priority Justification:** Adheres strictly to `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81
  compatibility), §2 (Assertion over hope, single-pass Prettier formatting with backtick arithmetic spans, idempotent
  package installations), §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic configuration refinements, declarative Ansible role tasks, CI workflow
  checks, and invariant assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.05  |
| impact_pred         | 92.0  |
| cost_pred           | 1.1   |
| learning_value_pred | 4.5   |
| ev_pred             | 91.30 |

---

## Step 1: Unify Neovim Source via Homebrew

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped, deterministic unification of Neovim installation across Linux and Darwin platforms using
  Homebrew / Linuxbrew rather than platform-specific GitHub release tarball unarchiving.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Setting `devenv_neovim_source: brew` and skipping `neovim` in `devenv_pkg_skip` on Linux,
  resolving Homebrew binary location across known Linux and Darwin paths (`/opt/homebrew/bin/brew`,
  `/usr/local/bin/brew`, `/home/linuxbrew/.linuxbrew/bin/brew`, and `{{ devenv_home }}/.linuxbrew/bin/brew`), and
  managing Neovim package state via `community.general.homebrew` eliminates brittle upstream release download failures
  and guarantees compatibility with `vim.pack` (>= 0.12).
- **Learning target:** Verify robust Homebrew binary discovery and package state convergence across both Debian/Ubuntu
  (Linuxbrew) and macOS environments.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Switch Neovim installation on Linux and Darwin to Homebrew and ensure proper skip lists.
- **Git branch:**
  `I-1794966349-neovim-brew/P-1794966366-f68ff38e-antigravity-agent-gemini-3.8-flash-medium/E-1-unify-neovim-source/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/vars/os_Linux.yml`.
   - Update `devenv_pkg_skip` to include `neovim` (`- neovim`).
   - Set `devenv_neovim_source: brew`.
2. Open `ansible/vars/os_Darwin.yml`.
   - Set `devenv_neovim_source: brew`.
3. Open `ansible/group_vars/all.yml`.
   - Update the description and default for `devenv_neovim_source` to document `brew` as the unified source across macOS
     and Linux.
4. Open `ansible/roles/neovim/tasks/main.yml`.
   - Add Homebrew path resolution logic when `devenv_brew_bin` is not defined or is empty:
     - Check candidate Homebrew binary paths using `ansible.builtin.stat`: `/opt/homebrew/bin/brew`,
       `/usr/local/bin/brew`, `/home/linuxbrew/.linuxbrew/bin/brew`, and `{{ devenv_home }}/.linuxbrew/bin/brew`.
     - Record the first existing path in `devenv_brew_bin` via `ansible.builtin.set_fact` (defaulting to empty string).
   - Replace the legacy `community.general.github_release`, release asset fact computation, download, unarchive, and
     symlink tasks with a declarative Homebrew package installation:
     - Task: Install Neovim via Homebrew using `community.general.homebrew` with `name: neovim`, `state: present`,
       `path: "{{ devenv_brew_bin | default(omit) }}"`, conditioned on `devenv_neovim_source == 'brew'`.
   - Maintain the Neovim version probe (`nvim --version` with `check_mode: false`) and version assertion
     (`is version('0.12', '>=')` for `vim.pack` and `nvim-pack-lock.json`).
   - Maintain the plugin sync and package count reporting tasks.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule), §2 (Ansible Style: FQCN, Idempotence,
  Assertion over Hope), `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** `devenv_brew_bin` unresolved if Linuxbrew is not installed or at a
  non-standard location; syntax errors or undefined variables during Jinja evaluation.
- **Guardrails and early‑abort checks:** Provide graceful fallback paths for `devenv_brew_bin` with `default(omit)` in
  the `homebrew` module task; ensure version assertion provides an explicit failure message.

### Success & Discard Criteria

- **Success:** `ansible/vars/os_Linux.yml`, `ansible/vars/os_Darwin.yml`, and `ansible/roles/neovim/tasks/main.yml` use
  Homebrew for Neovim installation with `devenv_neovim_source == 'brew'`, avoiding `apt` package conflicts.
- **Discard:** Syntax errors, unresolved variables, or broken idempotence.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 2.0   |
| ev_pred             | 90.75 |

Calculated via: `EV = 0.98 * 92.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.4 = 90.16 + 1.0 - 0.006 - 0.4 = 90.754 ~ 90.75`.

---

## Step 2: Mandate Live Ansible Playbook Check in CI

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped addition to `.github/workflows/make.yml` ensuring GitHub Actions exercises Ansible playbook
  syntax and execution checks on both Ubuntu and macOS matrices.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Incorporating `make check-syntax` (and `make check-mode` where environment prerequisites
  are met) in `.github/workflows/make.yml` on both `ubuntu-latest` and `macos-latest` validates Ansible task structures,
  Jinja templates, and runtime module parameter specifications prior to merging pull requests.
- **Learning target:** Verify CI runner compatibility with Ansible syntax and check-mode commands under GitHub Actions.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Add live Ansible playbook checks to the CI matrix in `.github/workflows/make.yml`.
- **Git branch:**
  `I-1794966349-neovim-brew/P-1794966366-f68ff38e-antigravity-agent-gemini-3.8-flash-medium/E-2-ci-playbook-checks/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `.github/workflows/make.yml`.
2. Review the steps in the `make-matrix` job across `ubuntu-latest` and `macos-latest`.
3. Add step(s) to execute Ansible checks:
   - Run `make check-syntax` to validate playbook syntax across both `ubuntu-latest` and `macos-latest`.
   - Where environment prerequisites (such as Conda / Ansible / collections) are present or can be probed, execute
     `make check-mode` to perform dry-run execution and catch module parameter regressions.
4. Ensure environment variables (e.g. `CI=true`) and paths are correctly passed to GNU Make.
5. Verify valid YAML formatting and Actions schema compliance.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule), §1 (GNU Make Compatibility),
  `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** Missing `ansible-playbook` binary on cold GitHub runner if not
  bootstrapped; failure in syntax check if collections are absent.
- **Guardrails and early‑abort checks:** Ensure step either runs after prerequisite tools are provisioned or guards
  `check-mode` execution based on environment readiness (`make check` or collection presence).

### Success & Discard Criteria

- **Success:** `.github/workflows/make.yml` contains explicit steps running `make check-syntax` (and conditional
  `make check-mode`) on both Ubuntu and macOS runners.
- **Discard:** Invalid GitHub Actions YAML or failed syntax checks.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 2.0   |
| ev_pred             | 88.89 |

Calculated via: `EV = 0.98 * 90.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.3 = 88.20 + 1.0 - 0.006 - 0.3 = 88.894 ~ 88.89`.

---

## Step 3: Tests & Quality Gate Verification

- **Sub‑intent recommendation:** NO
- **Reasoning:** Update existing pytest test suites in `tests/test_templating.py` and `tests/test_manifest.py` for
  `devenv_neovim_source: brew` and `devenv_pkg_skip`, then execute the mandatory repository quality gates.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Aligning unit tests in `tests/test_templating.py` and `tests/test_manifest.py` with the
  Homebrew-based Neovim role structure and `devenv_pkg_skip` ensures against regressions, and executing `pytest`,
  `ruff`, `ansible-lint`, `prettier`, and `make check` confirms complete codebase integrity.
- **Learning target:** Verify full test suite and linter convergence across all modified files.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Update unit tests and run all verification gates.
- **Git branch:**
  `I-1794966349-neovim-brew/P-1794966366-f68ff38e-antigravity-agent-gemini-3.8-flash-medium/E-3-tests-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_templating.py`.
   - Update or refactor helper `nvim_asset_expr()` and its test `test_neovim_release_asset_matches_platform()` to
     reflect the Homebrew-based Neovim role structure (or replace with templating tests for Neovim Homebrew task
     properties and `devenv_neovim_source: brew`).
   - Confirm `test_wanted_list_drops_os_provided_packages()` continues to pass with `devenv_pkg_skip` including
     `neovim`.
2. Open `tests/test_manifest.py`.
   - Update or add assertions confirming that `os_Linux.yml` defines `devenv_neovim_source: brew` and lists `neovim` in
     `devenv_pkg_skip`.
   - Confirm that `os_Darwin.yml` defines `devenv_neovim_source: brew`.
   - Verify that Neovim version assertions and probe tasks continue to satisfy `test_neovim_role_assertion_syntax()` and
     `test_read_only_probe_tasks_check_mode()`.
3. Execute the quality gates:
   - Run unit tests: `uv run --extra test pytest -m "not network"`.
   - Run Python linter: `uv run ruff check .`.
   - Run Ansible linter: `uv run --extra test ansible-lint ansible/site.yml`.
   - Run Markdown formatter check: `npx prettier --check "**/*.md"`.
   - Run repository prerequisite check: `make check`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Markdown & Docs: backtick spans for arithmetic), §3 (Testing
  Constraints).
- **Potential failure modes for this step:** Stale references to `devenv_nvim_asset` in tests causing test discovery or
  assertion errors; Prettier formatting discrepancies.
- **Guardrails and early‑abort checks:** Format all modified Markdown files with Prettier; ensure test suite covers both
  Linux and Darwin variables.

### Success & Discard Criteria

- **Success:** All unit tests pass, and all quality commands (`pytest`, `ruff`, `ansible-lint`, `prettier`,
  `make check`) exit cleanly with code 0.
- **Discard:** Test failures or linter violations.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 91.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 1.5   |
| ev_pred             | 90.44 |

Calculated via: `EV = 0.99 * 91.0 + 0.5 * 1.5 - 0.3 * 0.01 - 0.4 = 90.09 + 0.75 - 0.003 - 0.4 = 90.437 ~ 90.44`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.98. Derived from high confidence across all three modular steps: declarative Ansible role
  updates with Homebrew binary resolution and skip lists, deterministic GitHub Actions CI workflow updates for syntax
  checking, and explicit unit test assertion updates in `tests/test_templating.py` and `tests/test_manifest.py`.
- **entropy_pred**: 0.05. Calculated as the cumulative sum of step entropies across all three steps
  (`0.02 + 0.02 + 0.01 = 0.05`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 92.0. Eliminates fragile GitHub release tarball unarchive logic on Linux and unifies Neovim
  installation under Homebrew across Linux and Darwin, prevents `apt` package manager collisions, ensures runtime
  playbook syntax errors are caught in CI before merging, and provides solid regression test coverage.
- **cost_pred**: 1.1. Calculated as the direct sum of individual step costs (`0.4 + 0.3 + 0.4 = 1.1`).
- **learning_value_pred**: 4.5. Validates Homebrew resolution patterns across multi-OS Ansible roles and establishes
  live playbook syntax execution in GitHub Actions CI workflows.
- **ev_pred**: 91.30. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.98 * 92.0 + 0.5 * 4.5 - 0.3 * 0.05 - 1.1 = 90.16 + 2.25 - 0.015 - 1.1 = 91.295 ~ 91.30`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: support macOS and Linux consistently; resolve `devenv_brew_bin`
    across Apple Silicon, Intel, and Linuxbrew paths).
  - `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: ensure `make check-syntax` remains compatible with GNU
    Make 3.81).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: single-pass Prettier formatting with backtick
    code spans for arithmetic expressions, assertion over hope, FQCN in Ansible).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, no unauthorized
    writes).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - `devenv_brew_bin` not found on a machine without Linuxbrew: Mitigated by falling back to `omit` and reporting clear
    failure diagnostics via assertion.
  - Ansible syntax checks failing in CI if collections are not initialized: Mitigated by checking collection
    availability or ensuring `make check-syntax` uses proper collection search paths.
- **Mitigations built into the plan:**
  - Multi-path Homebrew resolution checking Apple Silicon (`/opt/homebrew`), Intel (`/usr/local`), standard Linuxbrew
    (`/home/linuxbrew/.linuxbrew`), and custom user Linuxbrew (`~/.linuxbrew`).
  - Declarative FQCN modules (`community.general.homebrew`, `ansible.builtin.set_fact`, `ansible.builtin.stat`).
  - Preserved Neovim version assertions for `vim.pack` and `nvim-pack-lock.json`.
- **Residual risk accepted (and why):**
  - Minimal residual risk: Homebrew is already established in the repository's toolchain and package models.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.05
- **Budget Compliance:** The plan entropy of 0.05 is well within the budget limit (`0.05 <= 10.0`).

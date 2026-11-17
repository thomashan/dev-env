# Plan for I-1794900732-pure-os-dotfiles

- **Plan ID:** P-1794900749-cbefe8f7-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794900732-pure-os-dotfiles
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T07:33:45Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses decoupling dotfiles from bespoke toolchain hooks,
  resetting bash, zsh, and fish configs to clean, pure OS defaults, extracting reusable shell snippets into
  `dotfiles/examples/devenv-shell-snippets.sh`, and updating Ansible node tasks and manifest tests to source versions
  from `versions.json`.
- **Exploration stance:** Focused exploit with deterministic dotfile simplification, modular shell script snippet
  extraction, Ansible task decoupling to `versions.json`, and comprehensive manifest invariant test updates.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification), §2 (Assertion over hope, single-pass Prettier formatting with code-span arithmetic), §3 (pytest
  verification under `tests/`, all test modifications declared in plan), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic dotfile resets, modular shell snippet extraction, Ansible task
  decoupling, and manifest invariant test updates.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.10  |
| impact_pred         | 95.0  |
| cost_pred           | 2.2   |
| learning_value_pred | 5.0   |
| ev_pred             | 94.32 |

---

## Step 1: Reset Shell Dotfiles to Pure Vanilla OS Defaults

- **Sub‑intent recommendation:** NO
- **Reasoning:** Resets `dotfiles/bash/.bashrc`, `dotfiles/bash/.bash_profile`, `dotfiles/zsh/.zshrc`, and
  `dotfiles/fish/.config/fish/config.fish` to pure vanilla OS skeletons without embedded toolchain hooks, while keeping
  `dotfiles/tmux/.config/tmux/tmux.conf` and `dotfiles/conda/.condarc` clean upstream defaults.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Stripping embedded toolchain hooks (Homebrew, Conda, NVM) from shell initialization
  dotfiles eliminates implicit environmental coupling and provides a clean, predictable OS default skeleton for all
  shells.
- **Learning target:** Verify that minimal skeleton files maintain full compatibility across interactive and
  non-interactive shell sessions without unexpected environment mutations.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Reset bash, zsh, and fish dotfiles to pure vanilla OS default skeletons free of embedded nvm, brew,
  and conda hooks, ensuring tmux and conda dotfiles remain upstream clean.
- **Git branch:**
  `I-1794900732-pure-os-dotfiles/P-1794900749-cbefe8f7-antigravity-agent-gemini-3.8-flash-medium/E-1-reset-shell-dotfiles/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/bash/.bashrc` and replace the existing content with a pure OS default skeleton stub:
   - Include standard interactive session guard check.
   - Set standard user binary PATH resolution (`$HOME/.local/bin`).
   - Source `$HOME/.bashrc.local` if present for local user overrides.
   - Remove all embedded NVM prepend logic, multi-OS Homebrew/Linuxbrew evaluation blocks, and Conda hook probe loops.
2. Verify `dotfiles/bash/.bash_profile` remains a pure vanilla skeleton that safely sources `.bashrc` and any
   `.bash_profile.local`.
3. Open `dotfiles/zsh/.zshrc` and reset it to a clean OS skeleton stub:
   - Ensure standard user binary PATH resolution (`$HOME/.local/bin`).
   - Source `$HOME/.zshrc.local` if present for local user overrides.
   - Remove embedded NVM paths, Homebrew shellenv evaluations, and Conda hook probe loops.
4. Open `dotfiles/fish/.config/fish/config.fish` and reset to a clean vanilla default skeleton:
   - Retain XDG directory variable defaults (`$HOME/.local/share`, `$HOME/.config`).
   - Retain Fisher plugin directory isolation paths (`$__fish_config_dir/local`).
   - Retain interactive session guard block.
   - Retain user tools path addition (`$HOME/.local/bin`).
   - Remove OS switch evaluation for Homebrew/Linuxbrew (`brew shellenv | source`).
   - Remove hardcoded NVM path prepend (`fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"`).
   - Remove Conda candidates probe loop and `eval ($devenv_conda_base/bin/conda shell.fish hook)`.
5. Inspect `dotfiles/tmux/.config/tmux/tmux.conf` and `dotfiles/conda/.condarc` to confirm they remain pristine upstream
   factory defaults.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification: no hardcoded user paths),
  `holon-config/world/ruleset.md` §2 (Assertion over hope), `holon-config/world/constraints.md` §3 (Environment mutation
  boundaries).
- **Potential failure modes for this step:** Accidental syntax errors in shell skeleton scripts or unintended omission
  of critical path definitions needed by standard CLI tools.
- **Guardrails and early‑abort checks:** Validate shell syntax using bash/zsh syntax check `-n` flags and verify no
  hardcoded home paths exist.

### Success & Discard Criteria

- **Success:** Shell dotfiles contain only clean OS default skeletons with zero references to nvm, brew, or conda hooks,
  and tmux and conda configs match upstream defaults.
- **Discard:** Lingering toolchain hooks or syntax errors in shell configs.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 1.00  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 2.0   |
| ev_pred             | 90.59 |

Calculated via: `EV = 1.00 * 90.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.4 = 90.0 + 1.0 - 0.006 - 0.4 = 90.594 ~ 90.59`.

---

## Step 2: Extract Reusable Modular Toolchain Snippets File

- **Sub‑intent recommendation:** NO
- **Reasoning:** Modularizes environment toolchain hooks previously scattered inside shell dotfiles into a reusable,
  copy-pasteable reference script under `dotfiles/examples/devenv-shell-snippets.sh`.
- **Step Type:** INFRASTRUCTURE
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Consolidating toolchain initialization blocks into a well-documented examples file allows
  developers to opt-in selectively via local overrides (`.bashrc.local`, `.zshrc.local`) without polluting default
  dotfile skeletons.
- **Learning target:** Ensure snippets are syntactically valid in POSIX/Bash/Zsh shells and contain clear demarcations
  for each toolchain integration.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Create `dotfiles/examples/devenv-shell-snippets.sh` containing modular snippets for NVM,
  Homebrew/Linuxbrew, Conda miniforge, and local override hooks.
- **Git branch:**
  `I-1794900732-pure-os-dotfiles/P-1794900749-cbefe8f7-antigravity-agent-gemini-3.8-flash-medium/E-2-extract-shell-snippets/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Create directory `dotfiles/examples/` if not already present.
2. Create script file `dotfiles/examples/devenv-shell-snippets.sh` with executable permissions (`0755`) and bash shebang
   (`#!/usr/bin/env bash`).
3. Add explanatory top-level documentation describing usage: users can copy relevant blocks into `.bashrc`, `.zshrc`, or
   local overrides (`~/.bashrc.local`, `~/.zshrc.local`).
4. Implement Block A: NVM managed node PATH prepend:
   - Export fallback for `$XDG_DATA_HOME` (`$HOME/.local/share`).
   - Check directory existence of `$XDG_DATA_HOME/nvm/current/bin` and prepend to `$PATH`.
5. Implement Block B: Multi-OS Homebrew/Linuxbrew `brew shellenv` evaluation:
   - Use `uname -s` case statement matching `Darwin` and `Linux`.
   - On `Darwin`, test `/opt/homebrew/bin/brew` or `/usr/local/bin/brew` and run `eval "$(... brew shellenv)"`.
   - On `Linux`, test `/home/linuxbrew/.linuxbrew/bin/brew` and run `eval "$(... brew shellenv)"` or fallback to
     appending linuxbrew `bin` and `sbin` to `$PATH`.
6. Implement Block C: Conda (Miniforge) shell hook probe and activation:
   - Iterate over candidate directories (`$HOME/miniforge3`, `$HOME/miniforge`, `$HOME/mambaforge`, `$HOME/anaconda3`,
     `/opt/homebrew/Caskroom/miniforge/base`, `/usr/local/Caskroom/miniforge/base`, `/opt/miniforge3`, `/opt/conda`).
   - If `$conda_root/bin/conda` is executable, evaluate `shell.bash hook` (for Bash) or `shell.zsh hook` (for Zsh) and
     break.
7. Implement Block D: Local override hook loading:
   - Guard and source `$HOME/.bashrc.local` when in Bash.
   - Guard and source `$HOME/.zshrc.local` when in Zsh.
8. Validate syntax via `bash -n dotfiles/examples/devenv-shell-snippets.sh`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS Darwin/Linux parity, no hardcoded user paths),
  `holon-config/world/ruleset.md` §2 (Coding conventions), `holon-config/world/constraints.md` §3 (Environment mutation
  boundaries).
- **Potential failure modes for this step:** Introduction of unescaped personal home directories or syntax that triggers
  shell parsing errors under strict POSIX/Bash modes.
- **Guardrails and early‑abort checks:** Ensure all user home paths use `$HOME` and Homebrew macOS paths are enclosed
  within an OS switch block (`case "$(uname -s)" in Darwin)`).

### Success & Discard Criteria

- **Success:** `dotfiles/examples/devenv-shell-snippets.sh` exists, is syntactically valid, and includes all 4 modular
  blocks (NVM, Homebrew, Conda, Local overrides).
- **Discard:** Missing snippets file or syntax validation errors.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 1.00  |
| entropy_pred        | 0.01  |
| impact_pred         | 85.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 2.0   |
| ev_pred             | 85.70 |

Calculated via: `EV = 1.00 * 85.0 + 0.5 * 2.0 - 0.3 * 0.01 - 0.3 = 85.0 + 1.0 - 0.003 - 0.3 = 85.697 ~ 85.70`.

---

## Step 3: Decouple Node Ansible Role from Fish Dotfiles

- **Sub‑intent recommendation:** NO
- **Reasoning:** Replaces the legacy parsing of `dotfiles/fish/.config/fish/conf.d/00-devenv.fish` in
  `ansible/roles/node/tasks/main.yml` with direct loading from repository authoritative manifest `versions.json`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Reading the Node version pin directly from root `versions.json` decouples the Ansible
  provisioner from shell-specific dotfiles, eliminating fragile string regex scraping and ensuring robust multi-OS
  provisioning.
- **Learning target:** Confirm Ansible `from_json` cleanly decodes `versions.json` content and binds
  `devenv_node_version` and `devenv_node_default_version` consistently.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Update `ansible/roles/node/tasks/main.yml` to slurp and parse `versions.json` instead of
  `00-devenv.fish`.
- **Git branch:**
  `I-1794900732-pure-os-dotfiles/P-1794900749-cbefe8f7-antigravity-agent-gemini-3.8-flash-medium/E-3-decouple-node-role/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/roles/node/tasks/main.yml`.
2. Locate the first task currently slurping `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
3. Update the task to read `{{ devenv_repo_root }}/versions.json` using `ansible.builtin.slurp` and register the result
   in `devenv_versions_raw`.
4. Replace the regex-based `ansible.builtin.set_fact` task with a structured JSON parser task:
   - Decode the slurped content using `b64decode | from_json`.
   - Extract the `node` key into `devenv_node_default_version` and `devenv_node_version`.
5. Update the assertion task to verify that `devenv_node_version` is non-empty, with an updated failure message
   indicating `versions.json`.
6. Ensure subsequent tasks in `ansible/roles/node/tasks/main.yml` continue to reference `devenv_node_version`
   seamlessly.
7. Run `ansible-lint ansible/site.yml` to verify task syntax and idempotency attributes remain compliant.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Version parity, single source of truth),
  `holon-config/world/ruleset.md` §2 (Ansible FQCN, no unquoted templating), `holon-config/world/constraints.md` §3
  (Mutation boundaries).
- **Potential failure modes for this step:** Misspelled dictionary key or failure when parsing JSON string.
- **Guardrails and early‑abort checks:** Ensure the assert task explicitly checks `devenv_node_version | length > 0`.

### Success & Discard Criteria

- **Success:** Node tasks cleanly load Node pin from `versions.json`, passing `ansible-lint` without errors or warnings.
- **Discard:** Retained dependency on `00-devenv.fish` or broken Ansible playbook execution.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 2.0   |
| ev_pred             | 89.69 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.4 = 89.1 + 1.0 - 0.006 - 0.4 = 89.694 ~ 89.69`.

---

## Step 4: Update Manifest Invariant Tests and Add Snippets Coverage

- **Sub‑intent recommendation:** NO
- **Reasoning:** Updates manifest tests to assert pure OS defaults for shell dotfiles, updates node pin assertions to
  reference `versions.json`, exempts `dotfiles/examples/` from Stow package discovery, and adds automated invariant
  testing for `dotfiles/examples/devenv-shell-snippets.sh`.
- **Step Type:** TEST
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicitly encoding pure OS default invariants and snippet structure checks into the
  manifest test suite prevents regressions, ensuring future changes do not re-introduce toolchain hooks into skeleton
  dotfiles.
- **Learning target:** Verify how pytest assertions capture both negative invariants (absence of toolchain injections in
  dotfiles) and positive invariants (presence of modular hooks in examples).
- **Maximum acceptable cost for this learning:** 0.6

### Intent & Git Integration

- **Step Intent:** Update `tests/test_manifest.py` for pure OS dotfile invariants, node pin verification from
  `versions.json`, Stow package exemption for `examples`, and validation of
  `dotfiles/examples/devenv-shell-snippets.sh`.
- **Git branch:**
  `I-1794900732-pure-os-dotfiles/P-1794900749-cbefe8f7-antigravity-agent-gemini-3.8-flash-medium/E-4-update-manifest-tests/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_manifest.py`.
2. Update `test_conda_path_parity_between_ansible_and_fish`:
   - Change assertion from requiring `$HOME/miniforge3` in `config.fish` to asserting that `config.fish` contains no
     hardcoded conda paths or conda hook invocations, maintaining pure OS default invariants.
   - Assert that `devenv_conda_dir` in `group_vars` remains cleanly configured as `{{ devenv_home }}/miniforge3`.
3. Update `test_node_bin_is_first_on_path`:
   - Refactor to verify pure OS default invariants in `config.fish`: assert that `nvm/current/bin`, `brew shellenv`, and
     nvm prepends are absent from `config.fish`.
   - Verify that standard user binary directory `$HOME/.local/bin` is preserved.
4. Update `test_node_pin_is_declared_exactly_once_and_well_formed`:
   - Update docstring and assertion to verify that `versions.json` defines a valid semantic version under key `node`.
   - Confirm Ansible `group_vars/all.yml` does not declare a conflicting hardcoded `devenv_node_version`.
5. Update `test_stow_packages_match_dotfiles_subdirectories` and
   `test_all_tracked_dotfiles_belong_to_stow_packages_and_are_linked`:
   - Ensure `dotfiles/examples/` is recognized as a non-stowed examples directory and excluded from the requirement that
     every subdirectory in `dotfiles/` must be a Stow package linked into `$HOME`.
6. Add `test_devenv_shell_snippets_exists_and_valid`:
   - Assert `dotfiles/examples/devenv-shell-snippets.sh` exists and is a non-empty file.
   - Assert the file contains the NVM managed node PATH prepend (`$XDG_DATA_HOME/nvm/current/bin`).
   - Assert the file contains multi-OS Homebrew/Linuxbrew evaluation (`brew shellenv` with `case "$(uname -s)" in`).
   - Assert the file contains Conda (miniforge) shell hook probe and activation loop (`miniforge3`, `shell.bash hook`,
     `shell.zsh hook`).
   - Assert the file contains local override hook loading (`.bashrc.local`, `.zshrc.local`).
7. Run `uv run --extra test pytest tests/test_manifest.py` to confirm all tests pass.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Assertion over hope), `holon-config/world/ruleset.md` §3 (All
  test modifications declared in plan), `holon-config/world/constraints.md` §3 (Environment mutation boundaries).
- **Potential failure modes for this step:** Broken regex assertions or test failures in unrelated manifest tests due to
  unhandled `examples/` directory.
- **Guardrails and early‑abort checks:** Run `pytest tests/test_manifest.py` in test environment to immediately identify
  and correct assertion mismatches.

### Success & Discard Criteria

- **Success:** All test manifest checks pass, including newly added snippet invariants and pure OS default assertions.
- **Discard:** Test assertion failures or unhandled edge cases in dotfiles tree traversal.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.03  |
| impact_pred         | 95.0  |
| cost_pred           | 0.6   |
| learning_value_pred | 3.0   |
| ev_pred             | 93.99 |

Calculated via: `EV = 0.98 * 95.0 + 0.5 * 3.0 - 0.3 * 0.03 - 0.6 = 93.1 + 1.5 - 0.009 - 0.6 = 93.991 ~ 93.99`.

---

## Step 5: Full Test Suite and Quality Assurance Verification

- **Sub‑intent recommendation:** NO
- **Reasoning:** Executes end-to-end linting, test suites, ansible verification, formatting checks, and make
  prerequisites to guarantee repository integrity.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Comprehensive verification across unit tests, Python linters, Ansible linter, Markdown
  prettier checks, and Makefile prerequisites ensures zero regression across the codebase.
- **Learning target:** Verify complete test suite execution clean across all linters without deprecations or formatting
  errors.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** Execute comprehensive quality checks: pytest, ruff, ansible-lint, prettier, and make check.
- **Git branch:**
  `I-1794900732-pure-os-dotfiles/P-1794900749-cbefe8f7-antigravity-agent-gemini-3.8-flash-medium/E-5-full-validation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Run `uv run --extra test pytest -m "not network"` to ensure the full test suite passes without errors.
2. Run `uv run ruff check .` to verify all Python code conforms to style and quality rules.
3. Run `uv run --extra test ansible-lint ansible/site.yml` to verify Ansible playbooks and roles satisfy Ansible best
   practices.
4. Run `npx prettier --check "**/*.md"` to guarantee single-pass markdown formatting convergence without syntax or code
   block corruption.
5. Execute `make check` or evaluate prerequisite assertions to verify repository-level health.
6. Verify `git status` reports clean or expected changes only.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Coding conventions, single-pass Prettier formatting),
  `holon-config/world/ruleset.md` §3 (pytest runner), `holon-config/world/constraints.md` §2 (Sandbox containment).
- **Potential failure modes for this step:** Prettier formatting discrepancies or unexpected lint warnings.
- **Guardrails and early‑abort checks:** Fix formatting or linting issues immediately using standard linters before
  declaring step completion.

### Success & Discard Criteria

- **Success:** All test suites and linters pass cleanly with exit code 0.
- **Discard:** Lingering test failures or linter errors.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 2.0   |
| ev_pred             | 89.59 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.5 = 89.1 + 1.0 - 0.006 - 0.5 = 89.594 ~ 89.59`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from composite high confidence across all five steps. Each step addresses a modular,
  well-scoped change with clear boundaries: stripping hooks from dotfiles, creating a standalone snippet script,
  updating an Ansible role to read JSON, updating manifest test assertions, and running standard QA linters.
- **entropy_pred**: 0.10. Calculated as the cumulative sum of step entropies across all steps
  (`0.02 + 0.01 + 0.02 + 0.03 + 0.02 = 0.10`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 95.0. Decouples core shell dotfiles from implicit toolchain dependencies, resets dotfiles to clean OS
  defaults, provides users with clear reusable snippets for opt-in toolchain activation, eliminates fragile file
  slurping in Ansible in favor of structured `versions.json`, and solidifies repository invariant test guarantees.
- **cost_pred**: 2.2. Calculated as the direct sum of individual step costs (`0.4 + 0.3 + 0.4 + 0.6 + 0.5 = 2.2`).
- **learning_value_pred**: 5.0. Reflects the value of decoupling shell initialization from deployment automation,
  establishing clear patterns for modular snippet extraction and non-stowed example file handling in manifest
  invariants.
- **ev_pred**: 94.32. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 95.0 + 0.5 * 5.0 - 0.3 * 0.10 - 2.2 = 94.05 + 2.5 - 0.03 - 2.2 = 94.32`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: version parity across environments, no
    hardcoded user paths).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: Ansible FQCN conventions, assertion over hope,
    PEP 8, single-pass Prettier formatting with backtick code spans for arithmetic expressions).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, dotfile editing
    boundaries).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Non-stowed directory discovery: `dotfiles/examples/` must not trigger failures in
    `test_stow_packages_match_dotfiles_subdirectories` or
    `test_all_tracked_dotfiles_belong_to_stow_packages_and_are_linked`. Explicitly exempting `dotfiles/examples/`
    preserves strict stow invariants while accommodating documentation/snippet resources.
  - Hardcoded user paths: All shell snippets must reference `$HOME` and `$XDG_DATA_HOME` rather than literal user
    directories, and multi-OS brew paths must remain guarded by `uname -s` switches.
  - Jinja / Ansible syntax: Using `from_json` on slurped `versions.json` avoids custom regex extraction fragile to
    whitespace changes.
- **Mitigations built into the plan:**
  - Clear separation of concerns between OS default skeleton stubs and reusable toolchain snippets.
  - Unit tests updated to test pure OS default invariants rather than hardcoded path probes.
  - Multi-tier validation via `pytest`, `ruff`, `ansible-lint`, and `prettier`.
- **Residual risk accepted (and why):**
  - Minimal residual risk: all changes are strictly additive or simplifying, removing unnecessary couplings without
    altering core provisioning capabilities.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.10
- **Budget Compliance:** The plan entropy of 0.10 is well below the budget limit (`0.10 <= 10.0`).

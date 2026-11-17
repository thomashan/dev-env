# Plan for I-1794887131-conda-detect

- **Plan ID:** P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794887131-conda-detect
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T03:48:10Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses critical robustness issues in Conda and Ansible
  discovery across Makefile and Ansible roles, preventing unwanted environment rebuilds, duplicate package manager
  installations, and python downgrade corruption in existing Conda base environments.
- **Exploration stance:** Focused exploit with deterministic verification across Makefile recipes, Ansible Conda
  discovery tasks, and automated pytest manifest assertions.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification, Make -> Conda -> Ansible bootstrap, GNU Make >= 3.81 compatibility, no shell scripts),
  `holon-config/world/ruleset.md` §2 (Coding conventions, single-pass Prettier convergence via backtick code spans for
  arithmetic expressions), `holon-config/world/ruleset.md` §3 (pytest verification under `tests/`), and
  `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic refinements to path exports, executable probing logic, conditional
  skipping, and regression test assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.14  |
| impact_pred         | 90.0  |
| cost_pred           | 4.0   |
| learning_value_pred | 4.0   |
| ev_pred             | 87.06 |

---

## Step 1: Makefile Robust Path, Executable Probing, and Conditional Bootstrap

- **Sub‑intent recommendation:** NO
- **Reasoning:** Makefile modifications provide immediate benefits across all targets without architectural changes or
  external dependencies.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Exporting an extended PATH and robustly probing existing Conda, ansible-playbook,
  ansible-galaxy, and ansible-lint executables prevents redundant tool installations, avoids homebrew cask/micromamba
  executions on machines with existing environments, and protects pre-existing base Python versions from forced
  downgrades.
- **Learning target:** Confirm GNU Make 3.81 compatibility when exporting PATH and evaluating dynamic shell probe
  assignments for Conda and Ansible tools.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:**
  1. Add
     `export PATH := /opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/home/linuxbrew/.linuxbrew/bin:$(HOME)/.linuxbrew/bin:$(PATH)`
     near the top of `Makefile`.
  2. Implement robust probing for `CONDA`:
     - Probe `command -v conda` followed by candidate paths `/opt/homebrew/bin/conda`, `/usr/local/bin/conda`,
       `/opt/homebrew/Caskroom/miniforge/base/condabin/conda`, `/opt/homebrew/Caskroom/miniforge/base/bin/conda`,
       `/home/linuxbrew/.linuxbrew/bin/conda`, `$$HOME/.linuxbrew/bin/conda`, and `$(HOME)/miniforge3/bin/conda`.
  3. Resolve `CONDA_DIR` dynamically via `$$CONDA info --base 2>/dev/null` if `CONDA` is executable, falling back to
     standard directory checks.
  4. Probe Ansible executables (`PB`, `GALAXY`, `LINT`):
     - If executable in `$(CONDA_DIR)/bin/`, reuse it.
     - Else if available on PATH via `command -v <tool>` (e.g. `~/.local/bin/ansible-playbook`), reuse it.
     - Else fall back to `$(CONDA_DIR)/bin/<tool>`.
  5. Refine `bootstrap:` target:
     - Check `[ -x "$(CONDA)" ]` or `command -v conda >/dev/null 2>&1`. If present, output `Using existing Conda at ...`
       and skip Homebrew cask/micromamba installation.
     - Check `[ -x "$(PB)" ]`. If present, output `Using existing Ansible: ...` and skip `conda install ...`.
     - When `$(PB)` is missing, invoke
       `"$(CONDA)" install -y -c conda-forge --override-channels ansible-core ansible-lint pyyaml` without pinning
       `python=3.13`.
  6. Update `check:` target to cleanly report ok when `command -v conda` or `$(CONDA)` exists, and report ok when
     `$(PB)` exists.
- **Git branch:**
  `I-1794887131-conda-detect/P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium/E-1-makefile-detection/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. In `Makefile`, place the `export PATH := ...` declaration immediately after `SELF_DIR`.
2. Restructure variable definitions for `CONDA`, `CONDA_DIR`, `PB`, `GALAXY`, and `LINT`:
   - Evaluate candidates in a POSIX shell snippet within Make variable assignment.
   - Guard each candidate check with `test -x` or `command -v`.
3. In `bootstrap:`, wrap the Conda installation block in a check verifying Conda is absent; if already present, echo the
   discovered location and skip package manager installs.
4. In `bootstrap:`, wrap the Ansible installation block in a check verifying Ansible (`PB`) is absent; if present, log
   Ansible version and skip `conda install`. If absent, run `conda install` for `ansible-core ansible-lint pyyaml`
   without forcing `python=3.13`.
5. Ensure `check:` target displays status ok for conda and ansible-core based on the probed executables.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (GNU Make >= 3.81 compatibility, no `.ONESHELL`, no `!=`
  operator, no shell scripts).
- **Potential failure modes for this step:** Shell quoting errors or non-standard syntax in `$(shell ...)` calls failing
  on older GNU Make versions.
- **Guardrails and early‑abort checks:** Run `make -n check` and `make check` to verify syntax validity without side
  effects.

### Success & Discard Criteria

- **Success:** `Makefile` contains the extended PATH export, dynamically detects existing Conda and Ansible tools, skips
  installation when tools are present, and never pins `python=3.13` during Ansible installation into an existing Conda
  environment.
- **Discard:** Syntax error in Makefile, break in GNU Make 3.81 compatibility, or failure in `make check`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.05  |
| impact_pred         | 90.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 1.0   |
| ev_pred             | 88.09 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.0 - 0.3 * 0.05 - 1.5 = 89.1 + 0.5 - 0.015 - 1.5 = 88.085 ~ 88.09`.

---

## Step 2: Ansible Conda Role Binary Discovery and Cask/Micromamba Skip Hardening

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped directly to `ansible/roles/conda/tasks/main.yml`, ensuring idempotence and alignment with
  Ansible facts and execution conditions.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Probing candidate Conda binaries directly and querying `conda info --base` using the
  discovered binary guarantees that existing Conda environments (such as custom base paths or non-PATH Conda
  installations) are detected before any Homebrew cask or micromamba task is triggered.
- **Learning target:** Confirm Ansible task ordering and stat registers properly resolve base prefixes without
  triggering unnecessary package manager operations.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `ansible/roles/conda/tasks/main.yml`:
     - Expand candidate checks by probing candidate Conda binary paths:
       - `/opt/homebrew/bin/conda`
       - `/opt/homebrew/Caskroom/miniforge/base/bin/conda`
       - `/opt/homebrew/Caskroom/miniforge/base/condabin/conda`
       - `/usr/local/bin/conda`
       - `/home/linuxbrew/.linuxbrew/bin/conda`
       - `{{ devenv_home }}/.linuxbrew/bin/conda`
       - `{{ devenv_home }}/miniforge3/bin/conda`
       - `/opt/conda/bin/conda`
     - Stat the candidate binaries alongside existing candidate directories.
     - Select discovered binary if `which conda` succeeds or any candidate binary stat exists.
     - When a Conda binary is discovered, invoke `{{ devenv_discovered_conda_bin }} info --base` to resolve root prefix.
     - Condition Homebrew cask (`miniforge`) on macOS and Homebrew (`micromamba`) on Linux to skip if
       `devenv_discovered_conda_bin | length > 0` or `devenv_discovered_conda_dir | length > 0`.
- **Git branch:**
  `I-1794887131-conda-detect/P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium/E-2-ansible-conda-probe/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Modify `ansible/roles/conda/tasks/main.yml`:
   - Add a stat task checking the list of candidate Conda binary locations.
   - Set fact `devenv_discovered_conda_bin` based on `which conda` or the first existing candidate binary.
   - Run `{{ devenv_discovered_conda_bin }} info --base` when a binary is found, registering the resolved base path.
   - Set fact `devenv_discovered_conda_dir` from the base query output if available, else from candidate root stats.
   - Update conditional `when:` guards on Miniforge cask installation (macOS), micromamba installation (Linux), and
     micromamba environment initialization to require both `devenv_discovered_conda_bin | length == 0` and
     `devenv_discovered_conda_dir | length == 0`.
2. Verify task syntax with `ansible-lint` to ensure fully-qualified collection names and style compliance.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Ansible role conventions), `holon-config/world/ruleset.md` §2
  (Ansible style, fully qualified collection names, `changed_when: false` on probes).
- **Potential failure modes for this step:** Undefined variable error if `devenv_discovered_conda_bin` is empty when
  running `info --base`.
- **Guardrails and early‑abort checks:** Add `when: devenv_discovered_conda_bin | length > 0` guard to the `info --base`
  task.

### Success & Discard Criteria

- **Success:** `ansible/roles/conda/tasks/main.yml` discovers candidate binaries, resolves base directory, and skips all
  bootstrap tasks if any Conda installation exists.
- **Discard:** Lint errors from `ansible-lint`, or failures to detect existing Conda binary paths.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.04  |
| impact_pred         | 90.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 1.0   |
| ev_pred             | 88.59 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.0 - 0.3 * 0.04 - 1.0 = 89.1 + 0.5 - 0.012 - 1.0 = 88.588 ~ 88.59`.

---

## Step 3: Manifest Unit Tests for Makefile Probing, PATH Export, and Non-Downgrade Invariants

- **Sub‑intent recommendation:** NO
- **Reasoning:** Codifies structural invariants in `tests/test_manifest.py` so any future regressions in Makefile PATH
  exports or Conda bootstrap behavior are caught automatically by pytest.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicitly asserting that `Makefile` exports an extended PATH, skips installation when
  Conda/Ansible are present, and never forces `python=3.13` during Conda package installation protects developer
  environments from regression across subsequent edits.
- **Learning target:** Confirm pytest coverage verifies both positive and negative structural rules for Makefile and
  role definitions.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `tests/test_manifest.py`:
     - Add `test_makefile_exports_extended_path()`: asserts `export PATH :=` includes Homebrew and Linuxbrew standard
       paths (`/opt/homebrew/bin`, `/usr/local/bin`, `/home/linuxbrew/.linuxbrew/bin`, `$(HOME)/.linuxbrew/bin`,
       `$(PATH)`).
     - Add `test_makefile_skips_conda_and_ansible_if_present()`: asserts bootstrap recipe inspects existing Conda and
       existing `PB` before running installations.
     - Add `test_makefile_conda_install_does_not_force_python_downgrade()`: asserts `conda install` in Makefile does not
       pin `python=3.13`.
  2. Format code and ensure PEP 8 compliance.
- **Git branch:**
  `I-1794887131-conda-detect/P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium/E-3-manifest-tests/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_manifest.py` and implement unit test functions:
   - Check `read(REPO_ROOT / "Makefile")` for `export PATH :=` containing Homebrew and Linuxbrew prefixes.
   - Inspect the `bootstrap:` recipe in `Makefile` to assert skip checks for Conda and Ansible.
   - Inspect the `conda install` command string in `Makefile` to verify `ansible-core ansible-lint pyyaml` are installed
     without `python=3.13`.
2. Run pytest targeting `test_manifest.py` to confirm the new assertions pass cleanly.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (pytest test location and declared modifications).
- **Potential failure modes for this step:** Fragile string matching if Makefile recipes use slightly different
  whitespace.
- **Guardrails and early‑abort checks:** Use robust substring assertions matching essential flags and paths.

### Success & Discard Criteria

- **Success:** New test functions pass cleanly under `uv run --extra test pytest -m "not network"`.
- **Discard:** Test failures or brittle assertions breaking standard Makefile execution.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.03  |
| impact_pred         | 90.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 1.5   |
| ev_pred             | 88.84 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.5 - 0.3 * 0.03 - 1.0 = 89.1 + 0.75 - 0.009 - 1.0 = 88.841 ~ 88.84`.

---

## Step 4: End-to-End Suite Verification and Toolchain Validation

- **Sub‑intent recommendation:** NO
- **Reasoning:** Executes complete end-to-end integration and quality checks across the entire repo.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Running all automated linters, syntax checks, pytest suites, Prettier formatters, and
  `make check` confirms that the entire codebase maintains 100% compliance with zero regressions.
- **Learning target:** Validate that all modified files pass strict linters (`ruff`, `ansible-lint`, `prettier`) and
  make prerequisite checks.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:**
  1. Execute unit and manifest tests: `uv run --extra test pytest -m "not network"`.
  2. Execute Python code linter: `uv run ruff check .`.
  3. Execute Ansible linter: `uv run --extra test ansible-lint ansible/site.yml`.
  4. Verify markdown documentation formatting: `npx prettier --check "**/*.md"`.
  5. Validate Makefile target execution: `make check`.
- **Git branch:**
  `I-1794887131-conda-detect/P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium/E-4-full-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Run `uv run --extra test pytest -m "not network"` to confirm all manifest tests pass.
2. Run `uv run ruff check .` and fix any linting or formatting defects.
3. Run `uv run --extra test ansible-lint ansible/site.yml` to ensure YAML and role syntax are clean.
4. Run `npx prettier --check "**/*.md"` to verify markdown compliance.
5. Execute `make check` to ensure GNU Make prerequisite probe runs successfully and reports status ok.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (PEP 8, Ansible style, Prettier markdown formatting),
  `holon-config/world/ruleset.md` §3 (pytest runner).
- **Potential failure modes for this step:** Discrepancies between local Prettier version and markdown files.
- **Guardrails and early‑abort checks:** Fix formatting with `npx prettier --write` if Prettier flags unformatted
  markdown spans.

### Success & Discard Criteria

- **Success:** All five quality and verification checks succeed with return code 0.
- **Discard:** Any linting error, test failure, or syntax break.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 0.5   |
| ev_pred             | 88.84 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 0.5 - 0.3 * 0.02 - 0.5 = 89.1 + 0.25 - 0.006 - 0.5 = 88.844 ~ 88.84`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from high confidence in POSIX Makefile syntax, standard Ansible task structures, and
  deterministic pytest assertions.
- **entropy_pred**: 0.14. Calculated as the cumulative sum of step entropies across all four steps
  (`0.05 + 0.04 + 0.03 + 0.02 = 0.14`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 90.0. Eliminates redundant package installations, prevents accidental base Python downgrades, and
  ensures seamless detection of existing Conda and Ansible binaries across both macOS and Linux.
- **cost_pred**: 4.0. Calculated as the direct sum of individual step costs (`1.5 + 1.0 + 1.0 + 0.5 = 4.0`).
- **learning_value_pred**: 4.0. Captures the architectural value of hardening Conda/Ansible detection logic and
  embedding continuous verification tests in `tests/test_manifest.py`.
- **ev_pred**: 87.06. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 90.0 + 0.5 * 4.0 - 0.3 * 0.14 - 4.0 = 89.1 + 2.0 - 0.042 - 4.0 = 87.058 ~ 87.06`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: Make -> Conda -> Ansible bootstrap, GNU
    Make >= 3.81 compatibility, no shell scripts).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8 compliance, single-pass Prettier
    formatting with backtick code spans for arithmetic expressions, Ansible fully-qualified collection names).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, all test modifications explicitly declared
    during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: never touch unmanaged state or run
    destructive operations).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Breakage of GNU Make 3.81 compatibility by using forbidden syntax: mitigated by adhering strictly to standard POSIX
    `$(shell ...)` and variable definitions.
  - Python version downgrade in pre-existing Conda environments: mitigated by removing `python=3.13` from
    `conda install ansible-core ansible-lint pyyaml` in `Makefile`.
  - Double-running Homebrew cask or micromamba when Conda exists under non-standard paths: mitigated by checking both
    `command -v conda` and candidate paths directly in Makefile and Ansible tasks.
- **Mitigations built into the plan:**
  - Structured probing sequence from PATH to standard system locations.
  - Comprehensive unit test assertions in `tests/test_manifest.py`.
  - Strict linting and end-to-end verification via `make check`, `pytest`, `ruff`, `ansible-lint`, and `prettier`.
- **Residual risk accepted (and why):**
  - Systems with corrupt or unexecutable Conda binaries at probed paths will fail early with clear diagnostic output,
    which is the desired behavior over silent fallback.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.14
- **Budget Compliance:** The plan entropy of 0.14 is well below the budget limit (`0.14 <= 10.0`).

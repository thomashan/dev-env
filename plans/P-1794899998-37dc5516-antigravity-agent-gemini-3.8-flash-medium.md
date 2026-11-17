# Plan for I-1794899982-python-prompt

- **Plan ID:** P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794899982-python-prompt
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T07:20:07Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent directly addresses consolidating redundant Python version
  prompts in the interactive host wizard (`scripts/devenv_wizard.py`), updating Ansible group defaults
  (`ansible/group_vars/all.yml`) so `devenv_conda_env_python` cleanly references `{{ devenv_python_version }}`, adding
  `check_mode: false` to read-only shell probes in Neovim and Node Ansible roles to support dry-run check-mode
  verification, and validating via targeted unit and manifest tests.
- **Exploration stance:** Focused exploit with deterministic configuration refactoring, Ansible task check-mode flags,
  and comprehensive pytest and linter verification.
- **Safety priority level:** standard
- **Priority Justification:** Fully adheres to `holon-config/world/ruleset.md` §1 (Runtime & environment specification),
  `holon-config/world/ruleset.md` §2 (Ansible style, assertion over hope, single-pass Prettier formatting with code-span
  arithmetic), `holon-config/world/ruleset.md` §3 (Testing constraints under `tests/`), and
  `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic, high-confidence refactoring and testing operations without open-ended
  research requirements.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.08  |
| impact_pred         | 95.0  |
| cost_pred           | 1.1   |
| learning_value_pred | 4.0   |
| ev_pred             | 94.93 |

---

## Step 1: Consolidate Wizard Python Prompt in `scripts/devenv_wizard.py`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Consolidating user prompts in `scripts/devenv_wizard.py` reduces prompt fatigue while ensuring the
  single chosen Python version propagates consistently to both `devenv_python_version` and `devenv_conda_env_python`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Consolidating `Python runtime version` and `Conda dev environment Python version` into a
  single `Python version` prompt in `run_wizard()` eliminates redundant user interaction and guarantees synchronization
  between the host runtime pin and the dev Conda environment pin in `choices.yml`.
- **Learning target:** Verify interactive prompt consolidation behavior and persistence to `choices.yml`.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** In `scripts/devenv_wizard.py`, replace the two separate prompts with a single
  `prompt_user("Python version", default=py_version, interactive=True)` and set both
  `choices["devenv_python_version"] = py_version` and `choices["devenv_conda_env_python"] = py_version`.
- **Git branch:**
  `I-1794899982-python-prompt/P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium/E-1-consolidate-wizard-python-prompt/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `scripts/devenv_wizard.py`.
2. In `run_wizard()`, locate Step D where runtime pins are initialized. Ensure `py_version` resolution inspects
   `existing_choices.get("devenv_python_version")` and `versions.get("python")`, and initialize `conda_py = py_version`
   (or existing choice if specified).
3. In the interactive prompt block of Step D, remove the separate prompt for `Conda dev environment Python version`
   (`conda_py = prompt_user(...)`) and update the Python version prompt string from `"Python runtime version"` to
   `"Python version"`.
4. In Step E (Persist Choices), assign `py_version` to both `choices["devenv_python_version"]` and
   `choices["devenv_conda_env_python"]`.
5. Run Python syntax check (`python3 -m py_compile scripts/devenv_wizard.py`) to verify script validity.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Host interactive wizard specification),
  `holon-config/world/ruleset.md` §2 (PEP 8 compliance, assertion over hope), `holon-config/world/constraints.md` §3
  (Host wizard configuration boundaries).
- **Potential failure modes for this step:** Regressions in non-interactive behavior or missing
  `devenv_conda_env_python` key in output dictionary.
- **Guardrails and early‑abort checks:** Ensure that both non-interactive execution and interactive execution write
  identical valid keys to `choices.yml`.

### Success & Discard Criteria

- **Success:** `scripts/devenv_wizard.py` contains a single `"Python version"` prompt in interactive mode, and assigns
  the resulting value to both `choices["devenv_python_version"]` and `choices["devenv_conda_env_python"]`.
- **Discard:** Retaining two separate prompts or omitting either Python key from persisted choices.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 1.00  |
| entropy_pred        | 0.02  |
| impact_pred         | 85.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 1.0   |
| ev_pred             | 85.19 |

Calculated via: `EV = 1.00 * 85.0 + 0.5 * 1.0 - 0.3 * 0.02 - 0.3 = 85.0 + 0.5 - 0.006 - 0.3 = 85.194 ~ 85.19`.

---

## Step 2: Update Ansible Defaults in `ansible/group_vars/all.yml`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Pointing `devenv_conda_env_python` directly to `"{{ devenv_python_version }}"` enforces
  single-source-of-truth semantics in the group variable declarations.
- **Step Type:** CONFIGURATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Setting `devenv_conda_env_python: "{{ devenv_python_version }}"` eliminates static
  duplication in Ansible group defaults, ensuring downstream tasks and conda environment provisioning automatically
  track `devenv_python_version` without manual multi-point updates.
- **Learning target:** Verify Jinja variable templating resolution for Conda environment definitions in Ansible.
- **Maximum acceptable cost for this learning:** 0.1

### Intent & Git Integration

- **Step Intent:** In `ansible/group_vars/all.yml`, update `devenv_conda_env_python` to `"{{ devenv_python_version }}"`.
- **Git branch:**
  `I-1794899982-python-prompt/P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium/E-2-update-ansible-defaults/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/group_vars/all.yml`.
2. Locate the line defining `devenv_conda_env_python: "3.13"`.
3. Update the definition to `devenv_conda_env_python: "{{ devenv_python_version }}"`.
4. Validate that `devenv_conda_envs` continues to reference `{{ devenv_conda_env_python }}` properly.
5. Verify YAML syntax using a YAML parser or linter.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Python runtime specification), `holon-config/world/ruleset.md`
  §2 (Ansible style & conventions), `holon-config/world/constraints.md` §3 (Converge through manifest).
- **Potential failure modes for this step:** Jinja syntax error or circular reference in group variables.
- **Guardrails and early‑abort checks:** Ensure Jinja templating is clean with standard double quotes around template
  braces (`"{{ devenv_python_version }}"`).

### Success & Discard Criteria

- **Success:** `ansible/group_vars/all.yml` defines `devenv_conda_env_python: "{{ devenv_python_version }}"`.
- **Discard:** Retaining hardcoded literal `"3.13"` for `devenv_conda_env_python`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 1.00  |
| entropy_pred        | 0.01  |
| impact_pred         | 80.0  |
| cost_pred           | 0.1   |
| learning_value_pred | 1.0   |
| ev_pred             | 80.40 |

Calculated via: `EV = 1.00 * 80.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.1 = 80.0 + 0.5 - 0.003 - 0.1 = 80.397 ~ 80.40`.

---

## Step 3: Support Check-Mode in Read-Only Probe Tasks

- **Sub‑intent recommendation:** NO
- **Reasoning:** In Ansible dry-run / check-mode execution (`ansible-playbook --check`, invoked via `make check-mode` or
  `make doctor`), read-only commands that inspect state are skipped by default unless annotated with
  `check_mode: false`. When skipped, the registered output is omitted or marked skipped, which causes downstream
  assertion tasks to fail erroneously.
- **Step Type:** FIX
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Adding `check_mode: false` to read-only shell probes
  (`Verify which node a login shell resolves` in `ansible/roles/node/tasks/main.yml` and
  `Read the installed Neovim version` in `ansible/roles/neovim/tasks/main.yml`) enables non-mutating inspection during
  dry-runs so downstream assertions receive valid registered output without failing.
- **Learning target:** Ensure Ansible dry-run execution succeeds without false assertion failures on existing
  environments.
- **Maximum acceptable cost for this learning:** 0.2

### Intent & Git Integration

- **Step Intent:** Add `check_mode: false` to `ansible/roles/node/tasks/main.yml` under task
  `Verify which node a login shell resolves` and to `ansible/roles/neovim/tasks/main.yml` under task
  `Read the installed Neovim version`.
- **Git branch:**
  `I-1794899982-python-prompt/P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium/E-3-support-check-mode-probes/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/roles/node/tasks/main.yml`.
2. Locate the task named `Verify which node a login shell resolves`
   (`ansible.builtin.command: cmd: fish -lc "which node; node -v"`).
3. Add `check_mode: false` attribute alongside `register: devenv_node_which` and `changed_when: false`.
4. Open `ansible/roles/neovim/tasks/main.yml`.
5. Locate the task named `Read the installed Neovim version` (`ansible.builtin.command: cmd: nvim --version`).
6. Add `check_mode: false` attribute alongside `register: devenv_nvim_version` and `changed_when: false`.
7. Verify YAML indentation and formatting across both task files.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule), `holon-config/world/ruleset.md` §2 (Ansible
  style, idempotence, assertion over hope), `holon-config/world/constraints.md` §3 (Mutation boundaries).
- **Potential failure modes for this step:** Indentation error in Ansible task files.
- **Guardrails and early‑abort checks:** Ensure tasks pass Ansible linting and YAML parsing checks.

### Success & Discard Criteria

- **Success:** Both `Verify which node a login shell resolves` in `ansible/roles/node/tasks/main.yml` and
  `Read the installed Neovim version` in `ansible/roles/neovim/tasks/main.yml` explicitly specify `check_mode: false`.
- **Discard:** Missing `check_mode: false` on either probe task.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 1.00  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.2   |
| learning_value_pred | 2.0   |
| ev_pred             | 90.79 |

Calculated via: `EV = 1.00 * 90.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.2 = 90.0 + 1.0 - 0.006 - 0.2 = 90.794 ~ 90.79`.

---

## Step 4: Update Unit & Manifest Tests and Run Full Verification Suite

- **Sub‑intent recommendation:** NO
- **Reasoning:** Tests validate that the unified Python prompt behaves correctly in `scripts/devenv_wizard.py`, that
  `ansible/group_vars/all.yml` references `{{ devenv_python_version }}`, and that probe tasks enforce
  `check_mode: false`.
- **Step Type:** TESTING
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Regression tests in `tests/test_wizard.py` and `tests/test_manifest.py` confirm the
  unified prompt logic and prevent accidental configuration drift or omission of `check_mode: false`.
- **Learning target:** Verify complete test coverage for wizard prompt consolidation and check-mode probe invariants.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** Update `tests/test_wizard.py` and `tests/test_manifest.py` to test the consolidated
  `"Python version"` prompt and `devenv_conda_env_python` template reference, and run `make test`, `make lint`, and
  `make check`.
- **Git branch:**
  `I-1794899982-python-prompt/P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium/E-4-tests-and-validation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_wizard.py`.
2. Add a test function (e.g. `test_run_wizard_interactive_python_prompt`) that patches `prompt_user` or inputs,
   verifying that when prompted for `"Python version"` with a custom value (e.g. `"3.13"` or `"3.12"`), both
   `choices["devenv_python_version"]` and `choices["devenv_conda_env_python"]` are set to that chosen version, and that
   only a single Python prompt was invoked.
3. Open `tests/test_manifest.py`.
4. In `test_versions_json_python_alignment_with_consumers(group_vars)`, update the assertion for
   `devenv_conda_env_python`: since `group_vars["devenv_conda_env_python"]` raw value is
   `"{{ devenv_python_version }}"`, assert `group_vars["devenv_conda_env_python"] == "{{ devenv_python_version }}"`.
5. In `tests/test_manifest.py`, add assertions or a test ensuring that the probe tasks
   `Verify which node a login shell resolves` in `ansible/roles/node/tasks/main.yml` and
   `Read the installed Neovim version` in `ansible/roles/neovim/tasks/main.yml` have `check_mode: false`.
6. Run `uv run pytest tests/test_wizard.py tests/test_manifest.py`.
7. Run `make test`.
8. Run `make lint` and `make check`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Installation contract, Python runtime),
  `holon-config/world/ruleset.md` §2 (Assertion over hope), `holon-config/world/ruleset.md` §3 (Testing constraints:
  pytest under `tests/`), `holon-config/world/constraints.md` §3 (Mutation boundaries).
- **Potential failure modes for this step:** Test failure due to assertion mismatch on raw vs templated values, or
  linter complaints.
- **Guardrails and early‑abort checks:** Execute `pytest` directly to ensure all test suites pass cleanly.

### Success & Discard Criteria

- **Success:** All unit and manifest tests pass, `make test`, `make lint`, and `make check` succeed with 0 exit code.
- **Discard:** Any test or linter failure.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.03  |
| impact_pred         | 95.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 3.0   |
| ev_pred             | 95.04 |

Calculated via: `EV = 0.99 * 95.0 + 0.5 * 3.0 - 0.3 * 0.03 - 0.5 = 94.05 + 1.5 - 0.009 - 0.5 = 95.041 ~ 95.04`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from composite high confidence across all four deterministic steps. Each step
  addresses a localized and unambiguous configuration or test adjustment with well-understood semantics.
- **entropy_pred**: 0.08. Calculated as the cumulative sum of step entropies across all steps
  (`0.02 + 0.01 + 0.02 + 0.03 = 0.08`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 95.0. Consolidating the wizard prompts streamlines interactive host setup, aligning
  `devenv_conda_env_python` to `{{ devenv_python_version }}` eliminates duplicate pins, and configuring
  `check_mode: false` on shell probes enables reliable dry-run execution (`make check-mode`, `make doctor`) across all
  targets.
- **cost_pred**: 1.1. Calculated as the direct sum of individual step costs (`0.3 + 0.1 + 0.2 + 0.5 = 1.1`).
- **learning_value_pred**: 4.0. Reinforces manifest invariants and establishes reliable check-mode support for read-only
  Ansible probes across the repository.
- **ev_pred**: 94.93. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 95.0 + 0.5 * 4.0 - 0.3 * 0.08 - 1.1 = 94.05 + 2.0 - 0.024 - 1.1 = 94.926 ~ 94.93`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: Python runtime version pin `==3.13.*`, host
    interactive wizard specification in `scripts/devenv_wizard.py`).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: Ansible style, idempotence, assertion over hope,
    PEP 8, single-pass Prettier formatting with code-span arithmetic).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest test runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: host wizard configuration boundaries,
    converge through manifest).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Breaking `tests/test_manifest.py`: Updating `devenv_conda_env_python` to `"{{ devenv_python_version }}"` requires
    updating manifest assertion tests that previously checked for literal version strings.
  - Wizard prompt regression: Ensure non-interactive execution (`--non-interactive`) continues to correctly populate
    both `devenv_python_version` and `devenv_conda_env_python`.
  - Check-mode behavior: Read-only probes with `check_mode: false` must not make mutations so that dry-run integrity is
    preserved.
  - Markdown formatting drift: Arithmetic expressions enclosed in backticks ensure single-pass Prettier formatting
    convergence.
- **Mitigations built into the plan:**
  - Synchronous updates to `scripts/devenv_wizard.py`, `ansible/group_vars/all.yml`, and `tests/test_manifest.py`.
  - Comprehensive unit test additions in `tests/test_wizard.py`.
  - Verification via `make test`, `make lint`, and `make check`.
- **Residual risk accepted (and why):**
  - Residual risk is negligible because changes simplify user interaction and configuration flow while aligning with
    standard Ansible best practices for dry-run probes.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.08
- **Budget Compliance:** The plan entropy of 0.08 is well within the budget limit (`0.08 <= 10.0`).

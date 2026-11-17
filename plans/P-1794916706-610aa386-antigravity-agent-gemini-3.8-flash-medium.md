# Plan for I-1794916689-clean-wizard-prompts

- **Plan ID:** P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794916689-clean-wizard-prompts
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T11:59:58Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent directly addresses streamlining wizard prompt UX by removing
  letter prefixes, setting modern user-centric defaults (fish login shell and GUI casks set to true) across the wizard
  and Ansible group variables, fixing nvm PATH prepending in fish conf.d, and enforcing strict invariant test coverage.
- **Exploration stance:** Focused exploit with deterministic prompt cleaning, default flag updates, fish PATH precedence
  resolution in `00-devenv.fish`, and regression test additions across `tests/test_wizard.py` and
  `tests/test_manifest.py`.
- **Safety priority level:** standard
- **Priority Justification:** Adheres strictly to `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification), §2 (Assertion over hope, single-pass Prettier formatting with code-span arithmetic), §3 (Testing
  constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All modifications involve deterministic refactoring of prompt strings, configuration flag defaults,
  fish environment PATH resolution, and test assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.07  |
| impact_pred         | 92.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 4.0   |
| ev_pred             | 91.56 |

---

## Step 1: Remove Step Letter Prefixes from Wizard Prompts

- **Sub‑intent recommendation:** NO
- **Reasoning:** Straightforward interactive UX prompt text cleanup within `scripts/devenv_wizard.py` that strips
  archaic letter prefixes.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Eliminating rigid step letter prefixes ('Step A: ', 'Step B: ', 'Step D: ') from
  interactive wizard prompts produces a more modern, cohesive CLI user experience while preserving argument passing and
  prompt options.
- **Learning target:** Verify all interactive prompts display cleanly without letter prefixes while retaining full
  option clarity and default indicators.
- **Maximum acceptable cost for this learning:** 0.2

### Intent & Git Integration

- **Step Intent:** Remove 'Step A: ', 'Step B: ', and 'Step D: ' letter prefixes from wizard prompts in
  `scripts/devenv_wizard.py`.
- **Git branch:**
  `I-1794916689-clean-wizard-prompts/P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium/E-1-clean-wizard-prompts/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `scripts/devenv_wizard.py` and navigate to `run_wizard()`.
2. Locate the package backend prompt in the OS detection block:
   - Change `prompt_msg = f"Step A: Detected {plat_info['distro']} ({plat_info['machine']}). Package backend"`
   - To `prompt_msg = f"Detected {plat_info['distro']} ({plat_info['machine']}). Package backend"`.
3. Locate the Neovim variant prompt:
   - Change `prompt_msg = f"Step B: Select Neovim variant ({', '.join(nvim_opts)})"`
   - To `prompt_msg = f"Select Neovim variant ({', '.join(nvim_opts)})"`.
4. Locate the login shell prompt:
   - Change `prompt_user("Step D: Change login shell to Fish? (true/false)", ...)`
   - To `prompt_user("Change login shell to Fish? (true/false)", ...)`.
5. Ensure comment headers (`# --- Step A: ...`) remain clear or are adjusted for clarity without altering runtime
   behavior.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Assertion over hope, PEP 8 style guidelines).
- **Potential failure modes for this step:** Accidental modification of prompt option keywords or breaking prompt
  matching regex in tests.
- **Guardrails and early‑abort checks:** Inspect diffs to ensure only string prefix characters are removed and parameter
  defaults remain intact.

### Success & Discard Criteria

- **Success:** Wizard interactive prompts no longer display `Step [A-Z]:` prefixes.
- **Discard:** Regression in prompt wording causing user options or default value presentations to become obscured.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 80.0  |
| cost_pred           | 0.2   |
| learning_value_pred | 1.0   |
| ev_pred             | 79.50 |

Calculated via: `EV = 0.99 * 80.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.2 = 79.2 + 0.5 - 0.003 - 0.2 = 79.497 ~ 79.50`.

---

## Step 2: Update Login Shell and GUI Casks Defaults

- **Sub‑intent recommendation:** NO
- **Reasoning:** Coordinated default value alignment between the Python pre-configuration wizard and Ansible group
  variables.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Setting default fallbacks for `devenv_set_login_shell` and `devenv_install_gui_casks` to
  `True` in both `scripts/devenv_wizard.py` and `ansible/group_vars/all.yml` aligns the out-of-the-box developer
  experience with modern defaults (Fish as login shell, GUI casks enabled on macOS).
- **Learning target:** Verify that default invocations of both the wizard and Ansible playbooks without prior
  configuration files automatically enable Fish login shell and GUI cask installation.
- **Maximum acceptable cost for this learning:** 0.2

### Intent & Git Integration

- **Step Intent:** Update default fallbacks for `devenv_set_login_shell` and `devenv_install_gui_casks` to `true` in
  `scripts/devenv_wizard.py` and `ansible/group_vars/all.yml`.
- **Git branch:**
  `I-1794916689-clean-wizard-prompts/P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium/E-2-update-defaults/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `scripts/devenv_wizard.py` and locate the initialization of host feature flags in `run_wizard()`:
   - Change `set_login_shell = bool(existing_choices.get("devenv_set_login_shell", False))` to default to `True`.
   - Change `install_gui_casks = bool(existing_choices.get("devenv_install_gui_casks", False))` to default to `True`.
2. Open `ansible/group_vars/all.yml`:
   - Locate `devenv_install_gui_casks: false` and update it to `devenv_install_gui_casks: true`.
   - Locate `devenv_set_login_shell: false` and update it to `devenv_set_login_shell: true`.
3. Verify that non-interactive runs and interactive prompts offer `true` as the default value when no existing choices
   file exists.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification),
  `holon-config/world/ruleset.md` §2 (Ansible conventions).
- **Potential failure modes for this step:** Inconsistent defaults between wizard and Ansible variables causing drifted
  behaviors depending on whether the wizard was run.
- **Guardrails and early‑abort checks:** Confirm both files declare `true` for these defaults and verify YAML syntax
  using `ansible-lint` and Python syntax with `ruff`.

### Success & Discard Criteria

- **Success:** Default resolution in `scripts/devenv_wizard.py` and `ansible/group_vars/all.yml` yields `true` for both
  `devenv_set_login_shell` and `devenv_install_gui_casks`.
- **Discard:** Discrepancy between wizard and Ansible default values.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 85.0  |
| cost_pred           | 0.2   |
| learning_value_pred | 1.5   |
| ev_pred             | 84.70 |

Calculated via: `EV = 0.99 * 85.0 + 0.5 * 1.5 - 0.3 * 0.01 - 0.2 = 84.15 + 0.75 - 0.003 - 0.2 = 84.697 ~ 84.70`.

---

## Step 3: Fix NVM Path Resolution for Fish in conf.d

- **Sub‑intent recommendation:** NO
- **Reasoning:** Targets fish shell initialization order specifically in
  `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Placing `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"` inside
  `conf.d/00-devenv.fish` guarantees that login shells resolve the nvm-managed Node.js binary before any system or
  Homebrew-installed Node binary (`/opt/homebrew/bin/node`), while leaving `config.fish` a pure OS default
  configuration.
- **Learning target:** Confirm that fish shell startup automatically prepends the nvm binary path globally and
  persistently across login shell sessions.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Ensure `$XDG_DATA_HOME/nvm/current/bin` is prepended to `PATH` via `fish_add_path -gpPm` in
  `00-devenv.fish`.
- **Git branch:**
  `I-1794916689-clean-wizard-prompts/P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium/E-3-fish-nvm-path/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
2. Ensure `XDG_DATA_HOME` is defined with fallback:
   - Check if `XDG_DATA_HOME` is set; if not, export `XDG_DATA_HOME "$HOME/.local/share"`.
3. Ensure `nvm_data` is defined using `$XDG_DATA_HOME/nvm`.
4. Prepend the nvm current bin directory to `PATH` using fish path manipulation:
   - Add `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"`.
   - The flags ensure global scope (`-g`), prepending (`-p`), direct PATH mutation (`-P`), and moving existing entries
     to the front (`-m`).
5. Confirm `dotfiles/fish/.config/fish/config.fish` remains clean and does not duplicate this hook.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification: no hardcoded absolute
  user home paths, cross-machine portability).
- **Potential failure modes for this step:** Variable expansion failure if `XDG_DATA_HOME` is unset when conf.d
  executes.
- **Guardrails and early‑abort checks:** Guard `XDG_DATA_HOME` with fallback to `"$HOME/.local/share"` prior to path
  invocation.

### Success & Discard Criteria

- **Success:** `00-devenv.fish` contains `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"`, ensuring nvm path
  resolution precedes `/opt/homebrew/bin/node`.
- **Discard:** Missing path flags or failure to evaluate `XDG_DATA_HOME` safely.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 2.0   |
| ev_pred             | 89.79 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.3 = 89.1 + 1.0 - 0.006 - 0.3 = 89.794 ~ 89.79`.

---

## Step 4: Update Automated Tests in tests/test_wizard.py and tests/test_manifest.py

- **Sub‑intent recommendation:** NO
- **Reasoning:** Enforces strict unit and manifest test coverage to guarantee regressions are immediately caught by CI.
- **Step Type:** TEST
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating `tests/test_wizard.py` and `tests/test_manifest.py` to assert new defaults
  (login shell true, GUI casks true), verify the absence of `Step [A-Z]:` prompt prefixes, and validate fish nvm path
  prepending creates an unbreakable regression barrier.
- **Learning target:** Ensure test suites rigorously validate prompt strings, configuration flag invariants, and shell
  environment initializations.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Update `tests/test_wizard.py` and `tests/test_manifest.py` with test coverage for prefix-free
  prompts, new default flags, and nvm fish PATH resolution.
- **Git branch:**
  `I-1794916689-clean-wizard-prompts/P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium/E-4-update-tests/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_wizard.py`:
   - Update `test_run_wizard_non_interactive`: Assert `choices["devenv_set_login_shell"] is True`. Assert
     `choices["devenv_install_gui_casks"] is True`.
   - Add a test `test_wizard_prompts_have_no_step_letter_prefixes`: Inspect `scripts/devenv_wizard.py` or mock
     interactive wizard prompts and assert that no prompt string contains the pattern `Step [A-Z]:`.
   - Update any existing mocks or assertions that relied on the old `Step D: ...` prompt string to match
     `Change login shell to Fish? (true/false)`.
2. Open `tests/test_manifest.py`:
   - Add a test verifying `group_vars/all.yml` defaults: Assert `devenv_set_login_shell: true` and
     `devenv_install_gui_casks: true` in `ansible/group_vars/all.yml`.
   - Add a test verifying `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`: Assert
     `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"` is present in `00-devenv.fish`. Assert `XDG_DATA_HOME`
     fallback definition is present.
   - Assert `scripts/devenv_wizard.py` defaults match `group_vars/all.yml` defaults for login shell and GUI casks.
3. Run `uv run --extra test pytest -m "not network"` to confirm all updated and new tests pass cleanly.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing Constraints: all test modifications declared in plan;
  pytest test paths; maintain high assertion density).
- **Potential failure modes for this step:** Brittle regex patterns that fail on unrelated prompt formatting changes.
- **Guardrails and early‑abort checks:** Use robust regex assertions (`r"Step [A-Z]:"`) and assert specific semantic
  substrings.

### Success & Discard Criteria

- **Success:** All tests in `tests/test_wizard.py` and `tests/test_manifest.py` pass cleanly, verifying new defaults,
  prompt prefix removal, and nvm path configuration.
- **Discard:** Test failures or unvalidated edge cases in wizard execution.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 3.0   |
| ev_pred             | 92.17 |

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 3.0 - 0.3 * 0.02 - 0.4 = 91.08 + 1.5 - 0.006 - 0.4 = 92.174 ~ 92.17`.

---

## Step 5: Full Verification and Quality Gate Validation

- **Sub‑intent recommendation:** NO
- **Reasoning:** Executes end-to-end repository test runners and linters to ensure complete codebase integrity.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Running all static linters, formatters, and dynamic test runners verifies zero
  regressions and guarantees that changes meet all repository world rules and constraints.
- **Learning target:** Verify complete test suite execution clean across all linters without deprecations or formatting
  errors.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Execute comprehensive quality checks: pytest, ruff, ansible-lint, prettier, and make check.
- **Git branch:**
  `I-1794916689-clean-wizard-prompts/P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium/E-5-full-validation/_`
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
| entropy_pred        | 0.01  |
| impact_pred         | 90.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 1.5   |
| ev_pred             | 89.45 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.5 - 0.3 * 0.01 - 0.4 = 89.1 + 0.75 - 0.003 - 0.4 = 89.447 ~ 89.45`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from composite high confidence across all five steps. Each step addresses a modular,
  well-scoped change with clear boundaries: removing letter prefixes from prompts, setting default booleans to `true`
  across wizard and group variables, prepending nvm path in fish conf.d, adding strict unit and manifest test
  assertions, and running standard QA linters.
- **entropy_pred**: 0.07. Calculated as the cumulative sum of step entropies across all steps
  (`0.01 + 0.01 + 0.02 + 0.02 + 0.01 = 0.07`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 92.0. Delivers clean wizard prompt UX without noisy step prefixes, aligns out-of-the-box defaults to
  Fish login shell and Docker Desktop GUI casks, resolves nvm Node binary priority in Fish login shells without
  compromising pure OS default dotfiles, and strengthens repository test invariants.
- **cost_pred**: 1.5. Calculated as the direct sum of individual step costs (`0.2 + 0.2 + 0.3 + 0.4 + 0.4 = 1.5`).
- **learning_value_pred**: 4.0. Reflects the value of clarifying prompt design patterns, establishing consistent
  configuration flag fallbacks across pre-flight scripts and Ansible manifests, and establishing robust fish path
  precedence patterns in `conf.d`.
- **ev_pred**: 91.56. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 92.0 + 0.5 * 4.0 - 0.3 * 0.07 - 1.5 = 91.08 + 2.0 - 0.021 - 1.5 = 91.559 ~ 91.56`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: version parity across environments, no
    hardcoded user paths).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: Ansible conventions, assertion over hope, PEP 8,
    single-pass Prettier formatting with backtick code spans for arithmetic expressions).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, dotfile editing
    boundaries).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - `conf.d/00-devenv.fish` PATH precedence: `fish_add_path -gpPm` must be used so that `$XDG_DATA_HOME/nvm/current/bin`
    is prepended to the global PATH and moves to the front even if already present in fish user paths or system
    defaults.
  - Undefined variable risk in Fish: Before evaluating `$XDG_DATA_HOME/nvm/current/bin`, verify `XDG_DATA_HOME` is set
    or default to `"$HOME/.local/share"`.
  - Invariant test drift: New tests must assert both the absence of `Step [A-Z]:` prefixes and the exact defaults
    (`devenv_set_login_shell: true` and `devenv_install_gui_casks: true`).
- **Mitigations built into the plan:**
  - Safe evaluation of `XDG_DATA_HOME` in `00-devenv.fish`.
  - Exact synchronization of default values across `scripts/devenv_wizard.py` and `ansible/group_vars/all.yml`.
  - Multi-tier validation via `pytest`, `ruff`, `ansible-lint`, and `prettier`.
- **Residual risk accepted (and why):**
  - Minimal residual risk: all modifications are simplifying or refining existing behavior with full automated
    regression testing.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.07
- **Budget Compliance:** The plan entropy of 0.07 is well below the budget limit (`0.07 <= 10.0`).

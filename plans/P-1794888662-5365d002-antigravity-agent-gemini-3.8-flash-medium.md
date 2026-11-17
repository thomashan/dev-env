# Plan for I-1794888646-node-26-lts

- **Plan ID:** P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794888646-node-26-lts
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T04:11:07Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent directly and cleanly updates the default Node.js LTS version
  across the fish dotfiles pin, the interactive configuration wizard fallback, the primary project documentation, and
  validates all invariants across pytest, Ruff, Prettier, and Make.
- **Exploration stance:** Focused exploit with deterministic verification across dotfiles, wizard fallback,
  documentation, and the full test suite.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification, single source of truth for version pins, GNU Stow packaging), `holon-config/world/ruleset.md` §2
  (Coding conventions, PEP 8, single-pass Prettier formatting with backtick arithmetic spans),
  `holon-config/world/ruleset.md` §3 (pytest suite verification), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic version pin updates, fallback synchronizations, documentation updates,
  and test suite validations.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.10  |
| impact_pred         | 85.0  |
| cost_pred           | 2.5   |
| learning_value_pred | 1.5   |
| ev_pred             | 82.37 |

---

## Step 1: Update Node.js Default Version Pin in Fish Dotfiles

- **Sub‑intent recommendation:** NO
- **Reasoning:** Updates the authoritative single source of truth for the default Node.js version in
  `dotfiles/fish/.config/fish/conf.d/00-devenv.fish` to `26.13.1` (Node.js 26 LTS Lithium). Both fish shell runtime
  (`nvm_default_version`) and Ansible's `node` role parse this pin directly.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating the version string in `00-devenv.fish` to `26.13.1` preserves regex parsing in
  `ansible/roles/node/tasks/main.yml`, passes `test_node_pin_is_declared_exactly_once_and_well_formed` in
  `tests/test_manifest.py`, and correctly renders in `test_node_pin_is_parsed_from_the_real_fish_config` in
  `tests/test_templating.py`.
- **Learning target:** Confirm that semantic version format `26.13.1` cleanly satisfies the regex pattern
  `^[0-9]+\.[0-9]+\.[0-9]+$` without requiring any Ansible parsing task changes.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:**
  1. In `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`, locate the line
     `set -g devenv_node_default_version 22.23.2`.
  2. Change it to `set -g devenv_node_default_version 26.13.1`.
  3. Ensure surrounding comments, OS detection, and `nvm` variables (`nvm_data`, `nvm_mirror`, `nvm_default_version`)
     remain intact.
- **Git branch:**
  `I-1794888646-node-26-lts/P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium/E-1-fish-pin-update/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
2. Replace `set -g devenv_node_default_version 22.23.2` with `set -g devenv_node_default_version 26.13.1`.
3. Verify that the line matches `^set -g devenv_node_default_version (\S+)$`.
4. Validate that `uv run --extra test pytest tests/test_manifest.py -k test_node_pin` and
   `uv run --extra test pytest tests/test_templating.py -k test_node_pin` pass.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Version pin source of truth in git-tracked dotfiles),
  `holon-config/world/constraints.md` §3 (Environment mutation boundaries; no loose files in dotfiles).
- **Potential failure modes for this step:** Typo in version pin format or accidentally modifying neighboring lines like
  `set -g nvm_default_version $devenv_node_default_version`.
- **Guardrails and early‑abort checks:** Run `pytest tests/test_manifest.py -k test_node_pin` immediately after editing
  to verify the pin format and single declaration.

### Success & Discard Criteria

- **Success:** `00-devenv.fish` declares `set -g devenv_node_default_version 26.13.1` and passes manifest pin checks.
- **Discard:** Retaining `22.23.2` or introducing syntax errors into fish dotfiles.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 80.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 0.5   |
| ev_pred             | 78.94 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 80.0 + 0.5 * 0.5 - 0.3 * 0.02 - 0.5 = 79.2 + 0.25 - 0.006 - 0.5 = 78.944 ~ 78.94`.

---

## Step 2: Update Fallback Node.js Default Version in Interactive Wizard

- **Sub‑intent recommendation:** NO
- **Reasoning:** Aligns the host configuration wizard fallback in `scripts/devenv_wizard.py` with the updated pin. When
  `make configure` is executed on a clean host lacking `~/.config/dev-env/choices.yml`, it defaults
  `devenv_node_default_version` to `26.13.1`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating the fallback string to `26.13.1` ensures that interactive and non-interactive
  wizard runs generate choices with `26.13.1` without breaking Python 3.13 typing or CLI argument handling.
- **Learning target:** Confirm that `scripts/devenv_wizard.py` passes `ruff check` and maintains strict typing
  conventions.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:**
  1. In `scripts/devenv_wizard.py`, locate the assignment:
     `node_version = str(existing_choices.get("devenv_node_default_version", "22.23.2"))`.
  2. Update it to: `node_version = str(existing_choices.get("devenv_node_default_version", "26.13.1"))`.
  3. Ensure no trailing whitespace or linting regressions are introduced.
- **Git branch:**
  `I-1794888646-node-26-lts/P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium/E-2-wizard-fallback-update/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `scripts/devenv_wizard.py`.
2. Locate `node_version = str(existing_choices.get("devenv_node_default_version", "22.23.2"))` under
   `# --- Step D: Host Feature Flags & Runtime Pins ---`.
3. Replace `"22.23.2"` with `"26.13.1"`.
4. Validate with `uv run ruff check scripts/devenv_wizard.py` and run existing wizard unit tests via
   `uv run --extra test pytest tests/test_wizard.py`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Host interactive wizard contract),
  `holon-config/world/ruleset.md` §2 (PEP 8, docstrings, typing).
- **Potential failure modes for this step:** Misspelling the dictionary key or modifying adjacent flags (`py_version`,
  `conda_py`).
- **Guardrails and early‑abort checks:** Run `ruff check scripts/devenv_wizard.py` and run
  `pytest tests/test_wizard.py`.

### Success & Discard Criteria

- **Success:** `scripts/devenv_wizard.py` contains `"26.13.1"` as the fallback for `devenv_node_default_version` and
  passes all linter checks.
- **Discard:** Retaining `"22.23.2"` or causing syntax/type errors in the wizard.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 80.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 0.5   |
| ev_pred             | 78.94 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 80.0 + 0.5 * 0.5 - 0.3 * 0.02 - 0.5 = 79.2 + 0.25 - 0.006 - 0.5 = 78.944 ~ 78.94`.

---

## Step 3: Update Node.js Version References in Documentation

- **Sub‑intent recommendation:** NO
- **Reasoning:** Keeps user-facing and architectural documentation in `README.md` in sync with the codebase runtime
  defaults. Updates the Language Runtimes table to state `Node.js 26.13.1`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating the documentation table line satisfies single-pass Prettier convergence
  (`npx prettier --check README.md`) and preserves table alignment.
- **Learning target:** Ensure no stale references to `22.23.2` remain in `README.md`.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:**
  1. In `README.md`, find `| \`nvm.fish\` + \`Node.js 22.23.2\` |`.
  2. Update it to `| \`nvm.fish\` + \`Node.js 26.13.1\` |`.
  3. Format with Prettier to ensure column widths and backtick spans adhere to repo markdown conventions.
- **Git branch:**
  `I-1794888646-node-26-lts/P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium/E-3-docs-update/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `README.md`.
2. Locate the table under `### 2. Language Runtimes & Conda Tools`.
3. Replace `Node.js 22.23.2` with `Node.js 26.13.1`.
4. Run `npx prettier --check README.md` (or format with `npx prettier --write README.md`) and confirm zero warnings.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Markdown & Docs: single-pass Prettier formatting with code
  spans).
- **Potential failure modes for this step:** Prettier formatting diffs due to markdown table realignment.
- **Guardrails and early‑abort checks:** Run `npx prettier --check README.md` directly after modifying the file.

### Success & Discard Criteria

- **Success:** `README.md` references `Node.js 26.13.1` and passes Prettier check cleanly.
- **Discard:** Retaining `22.23.2` in `README.md` or causing Prettier formatting failures.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 80.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 0.5   |
| ev_pred             | 78.94 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 80.0 + 0.5 * 0.5 - 0.3 * 0.02 - 0.5 = 79.2 + 0.25 - 0.006 - 0.5 = 78.944 ~ 78.94`.

---

## Step 4: Augment Invariant Tests and Execute Full Test Validation Suite

- **Sub‑intent recommendation:** NO
- **Reasoning:** Codifies a regression test invariant in the test suite asserting that the wizard fallback matches the
  fish dotfiles pin, guaranteeing that the two sources never drift in future releases. Runs the full test and
  verification suite specified in the intent.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** The test suite passes with 0 failures, all linting and formatting pass cleanly, and
  Ansible templating accurately parses `26.13.1`.
- **Learning target:** Verify complete test coverage across `test_manifest.py`, `test_templating.py`, and
  `test_wizard.py` for Node version synchronization.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `tests/test_manifest.py`, verify `test_node_pin_is_declared_exactly_once_and_well_formed` passes.
  2. In `tests/test_manifest.py` or `tests/test_wizard.py`, add a test
     `test_wizard_default_node_version_matches_fish_pin` ensuring `scripts/devenv_wizard.py` fallback equals
     `devenv_node_default_version` in `00-devenv.fish`.
  3. Execute the full test and linting pipeline:
     - `uv run --extra test pytest -m "not network"`
     - `uv run ruff check .`
     - `uv run --extra test ansible-lint ansible/site.yml`
     - `npx prettier --check "**/*.md"`
     - `make check`
- **Git branch:**
  `I-1794888646-node-26-lts/P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium/E-4-test-validation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. In `tests/test_manifest.py`:
   - Add unit test `test_wizard_default_node_version_matches_fish_pin`:
     - Reads `scripts/devenv_wizard.py` and extracts the fallback argument from
       `existing_choices.get("devenv_node_default_version", "...")`.
     - Reads `dotfiles/fish/.config/fish/conf.d/00-devenv.fish` and extracts `devenv_node_default_version`.
     - Asserts that both values are identical and equal to `26.13.1`.
2. Format Python files with `uv run ruff format .` and check with `uv run ruff check .`.
3. Format Markdown files with `npx prettier --write "**/*.md"` and verify with `npx prettier --check "**/*.md"`.
4. Run `uv run --extra test pytest -m "not network"`.
5. Run `uv run --extra test ansible-lint ansible/site.yml` (ensuring collections path is satisfied).
6. Run `make check`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (All test modifications explicitly declared during planning;
  standard pytest runner), `holon-config/world/constraints.md` §2 (Process sandbox entropy limits).
- **Potential failure modes for this step:** Prettier failure on modified markdown files or unhandled regex mismatch in
  test assertions.
- **Guardrails and early‑abort checks:** Run `pytest -m "not network"` locally before committing step changes.

### Success & Discard Criteria

- **Success:** All pytest tests pass; `ruff check .` passes; Prettier check passes; wizard and fish pin remain
  permanently coupled.
- **Discard:** Any test assertion failure or regression in templating parsing.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.04  |
| impact_pred         | 85.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 1.0   |
| ev_pred             | 83.64 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 85.0 + 0.5 * 1.0 - 0.3 * 0.04 - 1.0 = 84.15 + 0.5 - 0.012 - 1.0 = 83.638 ~ 83.64`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from the composite success probability across all four steps (each step evaluated at
  0.99). The modifications involve standardizing configuration pins to the latest Node.js 26 LTS (v26.13.1 Lithium),
  keeping the interactive wizard fallback aligned, updating documentation tables, and adding a regression invariant test
  to prevent drift.
- **entropy_pred**: 0.10. Calculated as the cumulative sum of step entropies across all four steps
  (`0.02 + 0.02 + 0.02 + 0.04 = 0.10`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 85.0. Modernizes the default Node.js LTS runtime to 26.13.1 (Lithium), ensuring access to modern
  JavaScript/TypeScript runtime capabilities, security updates, and performance enhancements across the managed
  development environment.
- **cost_pred**: 2.5. Calculated as the direct sum of individual step costs (`0.5 + 0.5 + 0.5 + 1.0 = 2.5`).
- **learning_value_pred**: 1.5. Reflects the value of codifying cross-file synchronization invariants into
  `test_manifest.py`, guaranteeing that `scripts/devenv_wizard.py` and `00-devenv.fish` remain in lockstep.
- **ev_pred**: 82.37. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 85.0 + 0.5 * 1.5 - 0.3 * 0.10 - 2.5 = 84.15 + 0.75 - 0.03 - 2.5 = 82.37`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: single source of truth for version pins in
    git-tracked dotfiles, GNU Stow packaging, zero loose dotfiles).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8 compliance, single-pass Prettier
    formatting with backtick arithmetic spans).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, all test modifications explicitly declared
    during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, no touching unmanaged
    state).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Version parse failure in Ansible role: `ansible/roles/node/tasks/main.yml` extracts the pin using
    `select('match', 'set -g devenv_node_default_version [0-9]')`. If the variable name or leading digit were altered,
    Ansible would fail with "Could not parse devenv_node_default_version". Validated in Step 4 via
    `tests/test_templating.py`.
  - Drift between wizard defaults and dotfiles: If a user executes `make configure` without existing choices, having
    mismatched defaults would create inconsistent environments. Mitigated by updating `scripts/devenv_wizard.py` and
    adding an invariant test in Step 4.
  - Markdown formatting drift: Tables or arithmetic notation in documentation or plans must not fail Prettier checks.
    Mitigated by wrapping all arithmetic expressions in backticks and verifying with `npx prettier --check`.
- **Mitigations built into the plan:**
  - Step-by-step verification of each pin and fallback value.
  - Adding an automated invariant test in `tests/test_manifest.py` ensuring the fish pin and wizard fallback stay
    synchronized.
  - Running the complete test and linting pipeline: `pytest`, `ruff`, `prettier`, and `make check`.
- **Residual risk accepted (and why):**
  - Existing workstations that already have `devenv_node_default_version: 22.23.2` saved in
    `~/.config/dev-env/choices.yml` will preserve their chosen version unless they re-run `make configure` or edit their
    choices file; this is by design to avoid mutating user-selected versions without prompt.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.10
- **Budget Compliance:** The plan entropy of 0.10 is well below the budget limit (`0.10 <= 10.0`).

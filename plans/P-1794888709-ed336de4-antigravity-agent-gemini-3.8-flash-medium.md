# Plan for I-1794888693-dotfiles-syntax-fix

- **Plan ID:** P-1794888709-ed336de4-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794888693-dotfiles-syntax-fix
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T04:12:00Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses a critical Jinja2 expression syntax error in the
  dotfiles role and unlink playbook assertions where `.startswith(...)` was invoked as an infix operator without
  parentheses, causing runtime template evaluation errors during symlink verification.
- **Exploration stance:** Focused exploit with deterministic syntax correction, Jinja templating test additions, and
  verification across test and lint suites.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification), `holon-config/world/ruleset.md` §2 (Ansible style, assertion over hope, backtick arithmetic code spans
  for Prettier), `holon-config/world/ruleset.md` §3 (pytest verification under `tests/`), and
  `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic syntax fixes, unit test assertions, and automated verification checks.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.08  |
| impact_pred         | 88.0  |
| cost_pred           | 2.0   |
| learning_value_pred | 4.0   |
| ev_pred             | 87.10 |

---

## Step 1: Fix Jinja2 Symlink Assertion in `ansible/roles/dotfiles/tasks/main.yml`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Directly fixes the Jinja2 method call syntax error in the assertion condition of the dotfiles role,
  converting `((...) | realpath) startswith devenv_repo_root` to `(((...) | realpath).startswith(devenv_repo_root))`.
- **Step Type:** BUGFIX
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Invoking `.startswith(...)` as a Python/Jinja2 string method call instead of an infix
  operator resolves the Jinja2 syntax error during symlink target verification in `ansible.builtin.assert`.
- **Learning target:** Confirm that Jinja2 evaluates method calls on pipeline expressions correctly when enclosed in
  proper parentheses.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** In `ansible/roles/dotfiles/tasks/main.yml`, lines 170-172:
  1. Replace the invalid infix expression
     `((item.stat.lnk_source if (item.stat.lnk_source | default('')).startswith('/') else (item.item.dest | dirname ~ '/' ~ (item.stat.lnk_source | default('')))) | realpath) startswith devenv_repo_root`
     with valid method invocation:
     `(((item.stat.lnk_source if (item.stat.lnk_source | default('')).startswith('/') else (item.item.dest | dirname ~ '/' ~ (item.stat.lnk_source | default('')))) | realpath).startswith(devenv_repo_root))`.
  2. Maintain YAML multiline folded scalar formatting (`>-`) and indentation matching surrounding tasks.
- **Git branch:**
  `I-1794888693-dotfiles-syntax-fix/P-1794888709-ed336de4-antigravity-agent-gemini-3.8-flash-medium/E-1-fix-dotfiles-assertion/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/roles/dotfiles/tasks/main.yml`.
2. Locate the task named "Assert the link manifest is fully satisfied".
3. Under the `that:` list, update the second expression from infix `startswith` to `.startswith(devenv_repo_root)` with
   enclosing parentheses around the piped realpath expression.
4. Verify YAML syntax and indentation integrity.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (project layout and dotfiles role specification),
  `holon-config/world/ruleset.md` §2 (Ansible style, assertion over hope), `holon-config/world/constraints.md` §3
  (environment mutation boundaries).
- **Potential failure modes for this step:** Mismatched parentheses in Jinja2 string or invalid YAML indentation in
  folded scalar block.
- **Guardrails and early‑abort checks:** Inspect YAML formatting and ensure parentheses match exactly:
  `(((...) | realpath).startswith(devenv_repo_root))`.

### Success & Discard Criteria

- **Success:** `ansible/roles/dotfiles/tasks/main.yml` contains syntactically valid Jinja2 method invocation
  `.startswith(devenv_repo_root)`.
- **Discard:** Retaining infix `startswith` or introducing YAML syntax errors.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 85.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 1.0   |
| ev_pred             | 84.14 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 85.0 + 0.5 * 1.0 - 0.3 * 0.02 - 0.5 = 84.15 + 0.5 - 0.006 - 0.5 = 84.144 ~ 84.14`.

---

## Step 2: Fix Jinja2 Symlink Assertion in `ansible/playbooks/unlink.yml`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Directly fixes the matching Jinja2 method call syntax error in the assertion condition of the unlink
  playbook, converting `((...) | realpath) startswith devenv_repo_root` to
  `(((...) | realpath).startswith(devenv_repo_root))`.
- **Step Type:** BUGFIX
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Changing infix `startswith` to method call `.startswith(...)` on the resolved realpath in
  `unlink.yml` prevents runtime crashes during `make unlink` symlink validation.
- **Learning target:** Ensure assertion logic in `unlink.yml` is identical to `ansible/roles/dotfiles/tasks/main.yml`,
  ensuring symmetric behavior between link creation and destruction.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** In `ansible/playbooks/unlink.yml`, lines 60-62:
  1. Replace the invalid infix expression
     `((item.stat.lnk_source if (item.stat.lnk_source | default('')).startswith('/') else (item.item.dest | dirname ~ '/' ~ (item.stat.lnk_source | default('')))) | realpath) startswith devenv_repo_root`
     with valid method invocation:
     `(((item.stat.lnk_source if (item.stat.lnk_source | default('')).startswith('/') else (item.item.dest | dirname ~ '/' ~ (item.stat.lnk_source | default('')))) | realpath).startswith(devenv_repo_root))`.
  2. Maintain YAML multiline folded scalar formatting (`>-`) and indentation matching surrounding tasks.
- **Git branch:**
  `I-1794888693-dotfiles-syntax-fix/P-1794888709-ed336de4-antigravity-agent-gemini-3.8-flash-medium/E-2-fix-unlink-assertion/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/playbooks/unlink.yml`.
2. Locate the task named "Refuse to remove anything that is not our symlink".
3. Under the `that:` list, update the second expression from infix `startswith` to `.startswith(devenv_repo_root)` with
   enclosing parentheses around the piped realpath expression.
4. Verify YAML syntax and indentation integrity.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (installation contract and symlink safety),
  `holon-config/world/ruleset.md` §2 (Ansible style, assertion over hope), `holon-config/world/constraints.md` §3
  (destructive operations and unlink safety).
- **Potential failure modes for this step:** Mismatched parentheses in Jinja2 string or invalid YAML indentation in
  folded scalar block.
- **Guardrails and early‑abort checks:** Inspect YAML formatting and verify that parentheses and quotes balance
  properly.

### Success & Discard Criteria

- **Success:** `ansible/playbooks/unlink.yml` contains syntactically valid Jinja2 method invocation
  `.startswith(devenv_repo_root)`.
- **Discard:** Retaining infix `startswith` or introducing YAML syntax errors.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 85.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 1.0   |
| ev_pred             | 84.14 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 85.0 + 0.5 * 1.0 - 0.3 * 0.02 - 0.5 = 84.15 + 0.5 - 0.006 - 0.5 = 84.144 ~ 84.14`.

---

## Step 3: Add Templating Tests for Assertions and Execute Full Verification Suite

- **Sub‑intent recommendation:** NO
- **Reasoning:** In accordance with `holon-config/world/ruleset.md` §3, test updates must be explicitly declared in the
  plan. Adding Jinja templating unit tests in `tests/test_templating.py` directly validates that Ansible's templating
  engine parses and evaluates both dotfiles and unlink symlink assertion expressions correctly without syntax errors.
  Running the complete verification suite confirms system integrity.
- **Step Type:** TEST
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** The updated Jinja2 assertion expressions evaluate without syntax errors under
  ansible-core's templating engine for both valid repo paths (returning `True`) and paths outside `devenv_repo_root`
  (returning `False`).
- **Learning target:** Ensure ongoing regression protection so future modifications cannot accidentally reintroduce
  invalid infix syntax.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `tests/test_templating.py`:
     - Add a unit test `test_dotfiles_symlink_assertion_expression(templar)` that reads the assertion condition from
       `ansible/roles/dotfiles/tasks/main.yml` and evaluates it against mock relative and absolute symlink items
       pointing inside and outside `devenv_repo_root`.
     - Add a unit test `test_unlink_symlink_assertion_expression(templar)` that reads the assertion condition from
       `ansible/playbooks/unlink.yml` and evaluates it similarly.
  2. Execute the full verification suite:
     - `uv run --extra test pytest -m "not network"`
     - `uv run ruff check .`
     - `uv run --extra test ansible-lint ansible/site.yml`
     - `npx prettier --check "**/*.md"`
     - `make check`
- **Git branch:**
  `I-1794888693-dotfiles-syntax-fix/P-1794888709-ed336de4-antigravity-agent-gemini-3.8-flash-medium/E-3-templating-tests-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Modify `tests/test_templating.py`:
   - Import necessary helpers or helper functions to locate the tasks in `ansible/roles/dotfiles/tasks/main.yml` and
     `ansible/playbooks/unlink.yml`.
   - Assert that evaluating the second expression in `that:` with `item.stat.lnk_source` pointing inside
     `devenv_repo_root` returns `True`.
   - Assert that evaluating with a path outside `devenv_repo_root` returns `False`.
2. Format python files with `uv run ruff format .` and check with `uv run ruff check .`.
3. Format markdown files with `npx prettier --write "**/*.md"` or verify with `npx prettier --check "**/*.md"`.
4. Run `uv run --extra test pytest -m "not network"`.
5. Run `uv run --extra test ansible-lint ansible/site.yml`.
6. Run `make check`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (PEP 8 compliance, single-pass Prettier formatting),
  `holon-config/world/ruleset.md` §3 (all test modifications declared in plan), `holon-config/world/constraints.md` §2
  (process sandbox entropy limit `< 10`).
- **Potential failure modes for this step:** Prettier failure on markdown formatting or test failure due to missing
  collection in ansible-lint environment.
- **Guardrails and early‑abort checks:** Format files prior to checking and verify all commands succeed with exit
  code 0.

### Success & Discard Criteria

- **Success:** All unit tests pass, `ruff` reports zero errors, `prettier` checks pass, and `make check` succeeds.
- **Discard:** Any test assertion failure, lint error, or formatting divergence.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.04  |
| impact_pred         | 88.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 2.0   |
| ev_pred             | 87.11 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 88.0 + 0.5 * 2.0 - 0.3 * 0.04 - 1.0 = 87.12 + 1.0 - 0.012 - 1.0 = 87.108 ~ 87.11`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from composite high confidence across all three steps. The root cause is a
  straightforward Jinja2 expression syntax error where Python's `.startswith(...)` method was used as an infix operator
  without method invocation syntax. Replacing this with proper method syntax on the realpath string is deterministic.
- **entropy_pred**: 0.08. Calculated as the cumulative sum of step entropies across all three steps
  (`0.02 + 0.02 + 0.04 = 0.08`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 88.0. Unblocks critical Ansible assertions in `ansible/roles/dotfiles/tasks/main.yml` and
  `ansible/playbooks/unlink.yml`, ensuring that both dotfile symlink convergence and symlink unlinking operate safely
  without crashing due to template evaluation syntax errors.
- **cost_pred**: 2.0. Calculated as the direct sum of individual step costs (`0.5 + 0.5 + 1.0 = 2.0`).
- **learning_value_pred**: 4.0. Reflects the value of implementing regression unit test coverage in
  `tests/test_templating.py` to prevent future reintroduction of invalid Jinja syntax in Ansible assertions.
- **ev_pred**: 87.10. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 88.0 + 0.5 * 4.0 - 0.3 * 0.08 - 2.0 = 87.12 + 2.0 - 0.024 - 2.0 = 87.096 ~ 87.10`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: GNU Stow multi-variant dotfile packaging,
    symlink verification, safe bootstrap chain).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: Ansible style, assertion over hope, PEP 8,
    single-pass Prettier formatting with backtick code spans for arithmetic expressions).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, all test modifications explicitly declared
    during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, safe unlinking).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Syntax errors in Jinja2 templating: mismatched parentheses or improper escaping in folded block scalars (`>-`).
    Mitigated by strictly applying parentheses
    `(((item.stat.lnk_source if ... else ...) | realpath).startswith(devenv_repo_root))` and verifying with Jinja
    templating unit tests in Step 3.
  - Markdown formatting drift: arithmetic expressions unquoted causing Prettier formatting failures. Mitigated by
    wrapping all arithmetic derivations in backtick code spans.
- **Mitigations built into the plan:**
  - Step-by-step modification and verification of each affected file.
  - Inclusion of Jinja2 templating unit tests in `tests/test_templating.py` to assert correct evaluation under both
    matching and non-matching conditions.
  - Comprehensive multi-tool verification suite (`pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check`).
- **Residual risk accepted (and why):**
  - Residual risk is near zero because the change directly corrects an invalid Jinja2 syntax to standard Python/Jinja2
    string method syntax and verifies it with automated unit tests.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.08
- **Budget Compliance:** The plan entropy of 0.08 is well below the budget limit (`0.08 <= 10.0`).

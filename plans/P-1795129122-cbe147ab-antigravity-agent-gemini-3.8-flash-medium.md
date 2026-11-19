# Plan for I-1795129105-tmux-pane-cwd

- **Plan ID:** P-1795129122-cbe147ab-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1795129105-tmux-pane-cwd
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-19T22:58:46Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent directly addresses developer ergonomics in tmux sessions by
  configuring new split panes and new windows to inherit the current pane's active working directory:
  1. Add keybindings in `dotfiles/tmux/.tmux.conf` for split-window (`"`, `%`) and new-window (`c`) with
     `-c "#{pane_current_path}"`.
  2. Add unit test assertions in `tests/test_toolchain.py` (keeping `tests/test_manifest.py` under the 1,000-line limit)
     verifying keybinding presence and syntax.
  3. Execute standard repository test and linting gates (`pytest`, `ruff`, `ansible-lint`, `prettier`, `make check`).
- **Exploration stance:** Focused exploit configuring declarative tmux keybindings and unit assertions.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Multi-Variant Stow Packaging:
  `dotfiles/tmux/.tmux.conf`), §2 (Assertion over hope, single-pass Prettier formatting with backtick arithmetic spans),
  §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All tasks are deterministic dotfile configuration updates and automated verification test
  assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.45  |
| learning_value_pred | 2.0   |
| ev_pred             | 89.64 |

---

## Step 1: Add Working Directory Preservation Keybindings to tmux Configuration

- **Sub‑intent recommendation:** NO
- **Reasoning:** Direct, well-scoped dotfile configuration change in `dotfiles/tmux/.tmux.conf`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Binding `'"'`, `%`, and `c` with `-c "#{pane_current_path}"` instructs tmux to spawn
  vertical splits, horizontal splits, and new windows within the working directory of the currently focused pane rather
  than defaulting to `$HOME`.
- **Learning target:** Verify clean tmux configuration syntax without conflicting with standard Vim-tmux navigator
  bindings.
- **Maximum acceptable cost for this learning:** 0.20

### Intent & Git Integration

- **Step Intent:** Configure tmux split and new window keybindings to preserve `#{pane_current_path}`.
- **Git branch:**
  `I-1795129105-tmux-pane-cwd/P-1795129122-cbe147ab-antigravity-agent-gemini-3.8-flash-medium/E-1-tmux-pane-cwd-keybindings/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/tmux/.tmux.conf`.
2. Add a dedicated section for working directory preservation:
   - Bind `'"'` to `split-window -v -c "#{pane_current_path}"`.
   - Bind `%` to `split-window -h -c "#{pane_current_path}"`.
   - Bind `c` to `new-window -c "#{pane_current_path}"`.
3. Preserve existing configuration lines, upstream default comments, and vim-tmux-navigator integration blocks intact.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-Variant Stow Packaging),
  `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: edits restricted to declared dotfile package
  paths under `dotfiles/tmux/`).
- **Potential failure modes for this step:** Syntax error in tmux config due to incorrect quoting around double quotes
  or string parameters; unintended conflict with existing navigator bindings.
- **Guardrails and early‑abort checks:** Use exact quoting conventions: single-quote `'\"'` for the split-window key,
  double-quote `"-c \"#{pane_current_path}\""`, and verify file readability.

### Success & Discard Criteria

- **Success:** `dotfiles/tmux/.tmux.conf` contains the three required `bind-key` directives referencing
  `#{pane_current_path}`.
- **Discard:** Missing keybinding, incorrect path variable name, or malformed tmux configuration syntax.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 88.0  |
| cost_pred           | 0.20  |
| learning_value_pred | 1.0   |
| ev_pred             | 87.42 |

Calculated via: `EV = 0.99 * 88.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.20 = 87.12 + 0.50 - 0.003 - 0.20 = 87.417 ~ 87.42`.

---

## Step 2: Implement Unit Tests and Execute Verification Suite

- **Sub‑intent recommendation:** NO
- **Reasoning:** Invariant assertions added directly to `tests/test_toolchain.py` and execution of standard repository
  verification targets.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Adding a unit test in `tests/test_toolchain.py` (keeping `tests/test_manifest.py` below
  the 1,000-line limit) confirms the presence and correctness of the new tmux keybindings, while running the
  verification suite (`pytest`, `ruff`, `ansible-lint`, `prettier`, `make check`) validates overall repository
  stability.
- **Learning target:** Codify regression testing for tmux configuration keybindings and verify suite integrity.
- **Maximum acceptable cost for this learning:** 0.25

### Intent & Git Integration

- **Step Intent:** Add test function to `tests/test_toolchain.py` and run quality verification gates.
- **Git branch:**
  `I-1795129105-tmux-pane-cwd/P-1795129122-cbe147ab-antigravity-agent-gemini-3.8-flash-medium/E-2-tests-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_toolchain.py`.
2. Add a new test function `test_tmux_pane_current_path_keybindings()`:
   - Read `dotfiles/tmux/.tmux.conf` using `REPO_ROOT / "dotfiles" / "tmux" / ".tmux.conf"`.
   - Assert `bind-key '"' split-window -v -c "#{pane_current_path}"` is present.
   - Assert `bind-key % split-window -h -c "#{pane_current_path}"` is present.
   - Assert `bind-key c new-window -c "#{pane_current_path}"` is present.
3. Ensure `tests/test_manifest.py` remains untouched and below the 1,000-line limit.
4. Run comprehensive repository verification commands:
   - `uv run --extra test pytest -m "not network"`
   - `uv run ruff check .`
   - `uv run --extra test ansible-lint ansible/site.yml`
   - `npx prettier --check "**/*.md"`
   - `make check`

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing Constraints: all test modifications explicitly
  declared in plan), `holon-config/world/ruleset.md` §2 (Assertion over hope).
- **Potential failure modes for this step:** Test assertion mismatch due to quote escaping; linter warnings on
  formatting or style.
- **Guardrails and early‑abort checks:** Use precise string matching matching the exact keybinding definitions; run
  linters locally before finalizing.

### Success & Discard Criteria

- **Success:** The new test passes cleanly under pytest; ruff, ansible-lint, prettier, and make check exit with code 0.
- **Discard:** Any test assertion failure, lint error, or unformatted markdown.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 90.0  |
| cost_pred           | 0.25  |
| learning_value_pred | 1.5   |
| ev_pred             | 89.60 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.5 - 0.3 * 0.01 - 0.25 = 89.10 + 0.75 - 0.003 - 0.25 = 89.597 ~ 89.60`.

---

## Strategy Rationale

The overall plan metrics are synthesized from the step-level metrics and system objectives as follows:

- **p_success_pred**: 0.99. Very high probability of success across both steps: modifying declarative keybindings in
  `dotfiles/tmux/.tmux.conf` and adding regression unit test assertions in `tests/test_toolchain.py`.
- **entropy_pred**: 0.02. Calculated as the cumulative sum of step entropies across both steps (`0.01 + 0.01 = 0.02`).
  This is well within the allocated budget limit of 10.0.
- **impact_pred**: 90.0. Significantly improves developer workflow and ergonomics by ensuring new tmux panes and windows
  open directly in the current working directory rather than reverting to `$HOME`.
- **cost_pred**: 0.45. Calculated as the direct sum of individual step costs (`0.20 + 0.25 = 0.45`).
- **learning_value_pred**: 2.0. Formalizes testing conventions for tmux configuration within `tests/test_toolchain.py`
  while respecting repository file length constraints.
- **ev_pred**: 89.64. Computed using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 90.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.45 = 89.10 + 1.00 - 0.006 - 0.45 = 89.644 ~ 89.64`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Project Layout & Multi-Variant Stow Packaging: edits scoped strictly to
    `dotfiles/tmux/.tmux.conf`).
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: configuration behaves identically across Linux and macOS).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: single-pass Prettier formatting with backtick
    code spans for arithmetic expressions, assertion over hope).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: test additions explicitly declared in plan, placing new
    tests in `tests/test_toolchain.py` keeping `tests/test_manifest.py` below the 1,000-line limit).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: zero unauthorized writes outside
    workspace).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Keybinding clashes or quote escaping issues in tmux: Addressed by using canonical tmux quoting syntax
    (`bind-key '"' ...`).
  - Test file bloat: Addressed by placing unit test in `tests/test_toolchain.py` instead of `tests/test_manifest.py`
    (which is already at 990 lines).
- **Mitigations built into the plan:**
  - Automated assertions validating all three keybindings (`'"'`, `%`, `c`) and their path flag.
  - Comprehensive verification pass running `pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check`.
- **Residual risk accepted (and why):**
  - Minimal residual risk: changes are declarative configuration entries and non-intrusive unit tests.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.02
- **Budget Compliance:** The plan entropy of 0.02 is well within the budget limit (`0.02 <= 10.0`).

# Plan for I-1794988615-nvim-markdownlint

- **Plan ID:** P-1794988632-ef2415b3-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794988615-nvim-markdownlint
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-18T07:57:30Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent directly addresses automatic tool provisioning and asynchronous
  error resilience in Neovim:
  1. Add `'markdownlint'` to `ensure_installed` passed to `require('mason-tool-installer').setup` in
     `dotfiles/nvim-kickstart/.config/nvim/init.lua` so `mason-tool-installer.nvim` automatically downloads and
     configures `markdownlint` on startup when missing.
  2. Guard `lint.try_lint()` inside the autocmd callback (`BufEnter`, `BufWritePost`, `InsertLeave`) in
     `dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/lint.lua` by invoking
     `lint.try_lint(nil, { ignore_errors = true })` so opening a Markdown file while Mason is still downloading
     `markdownlint` will not throw unhandled `ENOENT` runtime errors.
  3. Add explicit unit test assertions in `tests/test_manifest.py` verifying both settings and execute quality
     verification commands (`pytest`, `ruff`, `ansible-lint`, `prettier`, `make check`).
- **Exploration stance:** Focused exploit implementing exact configuration parameters and unit tests.
- **Safety priority level:** standard
- **Priority Justification:** Adheres to `holon-config/world/ruleset.md` §1 (Project Layout & Multi-Variant Stow
  Packaging), §2 (Assertion over hope, single-pass Prettier formatting with backtick arithmetic spans), §3 (Testing
  constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic configuration additions and unit test assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.03  |
| impact_pred         | 90.0  |
| cost_pred           | 0.50  |
| learning_value_pred | 2.0   |
| ev_pred             | 89.59 |

---

## Step 1: Add markdownlint to Mason Tool Installer in Kickstart init.lua

- **Sub‑intent recommendation:** NO
- **Reasoning:** Straightforward configuration change in `dotfiles/nvim-kickstart/.config/nvim/init.lua`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Declaring `'markdownlint'` within `ensure_installed` triggers `mason-tool-installer.nvim`
  to automatically download and configure `markdownlint` whenever Neovim starts up and the binary is not present in
  stdpath.
- **Learning target:** Verify clean Lua table extension syntax in `dotfiles/nvim-kickstart/.config/nvim/init.lua`
  without syntax errors.
- **Maximum acceptable cost for this learning:** 0.15

### Intent & Git Integration

- **Step Intent:** Add `'markdownlint'` to the `ensure_installed` list passed to
  `require('mason-tool-installer').setup`.
- **Git branch:**
  `I-1794988615-nvim-markdownlint/P-1794988632-ef2415b3-antigravity-agent-gemini-3.8-flash-medium/E-1-mason-install-markdownlint/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/nvim-kickstart/.config/nvim/init.lua`.
2. Locate the `vim.list_extend(ensure_installed, { ... })` invocation in Section 6 (LSP & Tooling Setup) around
   line 805.
3. Add `'markdownlint'` as a list element inside the `vim.list_extend` table argument.
4. Ensure formatting preserves Kickstart Lua indentation and syntax conventions.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Project Layout & Multi-Variant Stow Packaging),
  `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** Lua syntax error or invalid table specification causing Neovim
  initialization failure.
- **Guardrails and early‑abort checks:** Inspect file content and ensure clean syntax.

### Success & Discard Criteria

- **Success:** `'markdownlint'` is present in `ensure_installed` in `dotfiles/nvim-kickstart/.config/nvim/init.lua`.
- **Discard:** Syntax error or accidental mutation of adjacent LSP configuration blocks.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 85.0  |
| cost_pred           | 0.15  |
| learning_value_pred | 0.5   |
| ev_pred             | 84.25 |

Calculated via: `EV = 0.99 * 85.0 + 0.5 * 0.5 - 0.3 * 0.01 - 0.15 = 84.15 + 0.25 - 0.003 - 0.15 = 84.247 ~ 84.25`.

---

## Step 2: Guard nvim-lint Against Missing Binary ENOENT Errors in lint.lua

- **Sub‑intent recommendation:** NO
- **Reasoning:** Localized modification within `dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/lint.lua`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Passing `{ ignore_errors = true }` to `lint.try_lint()` silences runtime `ENOENT`
  exceptions when Markdown buffers are opened or edited before Mason finishes background installation of `markdownlint`.
- **Learning target:** Ensure seamless asynchronous installation tolerance without noisy popups or error notifications
  during initial user session setup.
- **Maximum acceptable cost for this learning:** 0.15

### Intent & Git Integration

- **Step Intent:** Update `lint.try_lint()` invocation in
  `dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/lint.lua` to pass `nil` for names and
  `{ ignore_errors = true }` for options.
- **Git branch:**
  `I-1794988615-nvim-markdownlint/P-1794988632-ef2415b3-antigravity-agent-gemini-3.8-flash-medium/E-2-guard-nvim-lint-errors/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/lint.lua`.
2. Locate the autocommand definition for `lint_augroup` registered on `{ 'BufEnter', 'BufWritePost', 'InsertLeave' }`.
3. Inside the `callback` function, change `if vim.bo.modifiable then lint.try_lint() end` to
   `if vim.bo.modifiable then lint.try_lint(nil, { ignore_errors = true }) end`.
4. Ensure comments remain accurate and no unrelated options are modified.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Project Layout & Multi-Variant Stow Packaging),
  `holon-config/world/ruleset.md` §2 (Assertion over hope).
- **Potential failure modes for this step:** Passing invalid argument structures to `try_lint`, breaking lint trigger
  mechanisms.
- **Guardrails and early‑abort checks:** Verify function signature according to `nvim-lint` documentation where the
  first argument is names (`nil` triggers filetype default linters) and second argument is options table.

### Success & Discard Criteria

- **Success:** `lint.try_lint(nil, { ignore_errors = true })` is present in `lint.lua`.
- **Discard:** Lint execution disabled completely or syntax error introduced.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 88.0  |
| cost_pred           | 0.15  |
| learning_value_pred | 0.5   |
| ev_pred             | 87.22 |

Calculated via: `EV = 0.99 * 88.0 + 0.5 * 0.5 - 0.3 * 0.01 - 0.15 = 87.12 + 0.25 - 0.003 - 0.15 = 87.217 ~ 87.22`.

---

## Step 3: Add Unit Tests in test_manifest.py and Execute Quality Gates

- **Sub‑intent recommendation:** NO
- **Reasoning:** Deterministic unit test assertions in `tests/test_manifest.py` and repository verification checks.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicit unit tests in `tests/test_manifest.py` prevent regressions in Kickstart Mason
  tool auto-installation and nvim-lint error handling.
- **Learning target:** Confirm full test and lint suite passes across Python, Ansible, and Markdown linters.
- **Maximum acceptable cost for this learning:** 0.20

### Intent & Git Integration

- **Step Intent:** Add unit tests to `tests/test_manifest.py` verifying `'markdownlint'` in Kickstart `init.lua` and
  `lint.try_lint(nil, { ignore_errors = true })` in `lint.lua`, and run all quality gates.
- **Git branch:**
  `I-1794988615-nvim-markdownlint/P-1794988632-ef2415b3-antigravity-agent-gemini-3.8-flash-medium/E-3-tests-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_manifest.py`.
2. Add a new test function `test_nvim_kickstart_markdownlint_auto_install_and_lint_guard()`:
   - Read `dotfiles/nvim-kickstart/.config/nvim/init.lua`.
   - Assert `'markdownlint'` is declared within the `ensure_installed` block or `vim.list_extend` list passed to
     `require('mason-tool-installer').setup`.
   - Read `dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/lint.lua`.
   - Assert `lint.try_lint(nil, { ignore_errors = true })` is present in the `BufEnter`/`BufWritePost`/`InsertLeave`
     autocmd callback.
3. Run verification commands:
   - `uv run --extra test pytest -m "not network"`
   - `uv run ruff check .`
   - `uv run --extra test ansible-lint ansible/site.yml`
   - `npx prettier --check "**/*.md"`
   - `make check`

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing Constraints: all test modifications explicitly
  declared in plan), `holon-config/world/ruleset.md` §2 (Assertion over hope).
- **Potential failure modes for this step:** Test assertion mismatch due to whitespace or formatting nuances.
- **Guardrails and early‑abort checks:** Use robust string/regex matching that allows standard Lua formatting.

### Success & Discard Criteria

- **Success:** Unit tests added to `tests/test_manifest.py` pass; pytest, ruff, ansible-lint, prettier, and make check
  all succeed cleanly.
- **Discard:** Any test assertion failure, lint violation, or formatting error.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 92.0  |
| cost_pred           | 0.20  |
| learning_value_pred | 1.0   |
| ev_pred             | 91.38 |

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.20 = 91.08 + 0.50 - 0.003 - 0.20 = 91.377 ~ 91.38`.

---

## Strategy Rationale

The overall plan metrics are synthesized from the step-level metrics and system objectives as follows:

- **p_success_pred**: 0.99. Very high probability of success across all three steps: adding `'markdownlint'` to
  `ensure_installed` in Kickstart `init.lua`, adding `{ ignore_errors = true }` to `lint.try_lint()` in Kickstart
  `lint.lua`, and asserting both behaviors via unit tests in `tests/test_manifest.py`.
- **entropy_pred**: 0.03. Calculated as the cumulative sum of step entropies across all three steps
  (`0.01 + 0.01 + 0.01 = 0.03`). This is well within the allocated budget limit of 10.0.
- **impact_pred**: 90.0. Completely resolves unhandled Neovim `ENOENT` crashes when opening or editing Markdown buffers
  prior to Mason downloading linters, while ensuring `markdownlint` is automatically installed on startup without manual
  user intervention.
- **cost_pred**: 0.50. Calculated as the direct sum of individual step costs (`0.15 + 0.15 + 0.20 = 0.50`).
- **learning_value_pred**: 2.0. Codifies best practices for asynchronous plugin installation resilience in Neovim
  Kickstart dotfiles.
- **ev_pred**: 89.59. Computed using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 90.0 + 0.5 * 2.0 - 0.3 * 0.03 - 0.50 = 89.10 + 1.00 - 0.009 - 0.50 = 89.591 ~ 89.59`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Project Layout & Multi-Variant Stow Packaging: packages in `dotfiles/`, no loose
    files outside packages).
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: configuration behaves identically across Linux and macOS).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: single-pass Prettier formatting with backtick
    code spans for arithmetic expressions, assertion over hope).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: zero unauthorized writes outside
    workspace).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Mutating default linters in `nvim-lint` unexpectedly: Guarded by only passing `{ ignore_errors = true }` to
    `lint.try_lint(nil, ...)`, preserving existing `linters_by_ft` table bindings.
  - Lua syntax breakage during `ensure_installed` modification: Mitigated by standard table syntax insertion.
- **Mitigations built into the plan:**
  - Unit test in `tests/test_manifest.py` ensuring configuration directives remain intact.
  - Complete check suite execution (`pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check`).
- **Residual risk accepted (and why):**
  - Minimal residual risk: purely declarative configuration updates and assertions within existing Kickstart plugin
    specifications.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.03
- **Budget Compliance:** The plan entropy of 0.03 is well within the budget limit (`0.03 <= 10.0`).

# Plan for I-1794888493-galaxy-check

- **Plan ID:** P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794888493-galaxy-check
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.5.9)
- **Created At:** 2026-11-17T04:08:34Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent directly improves bootstrap execution speed and idempotence by
  guarding Ansible collection downloads and removing the `--force` flag, while enhancing interactive conflict resolution
  in `devenv_wizard.py` with side-by-side terminal diffs (`delta` -> `diff -y` -> `difflib.unified_diff` fallback) and
  expanding regression test coverage.
- **Exploration stance:** Focused exploit with deterministic verification across Makefile recipes, wizard diff
  formatting, and pytest invariants.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification), §2 (Coding conventions, PEP 8, backtick arithmetic code spans for Prettier), §3 (Testing constraints),
  and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic optimizations, shell recipe safeguards, subprocess integrations with
  robust fallbacks, and regression tests.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.13  |
| impact_pred         | 92.0  |
| cost_pred           | 4.5   |
| learning_value_pred | 4.0   |
| ev_pred             | 88.54 |

---

## Step 1: Makefile Galaxy Collection Guard & Remove `--force`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Modifies the `bootstrap` target in `Makefile` to conditionally skip `ansible-galaxy collection install`
  when `$(COLLECTIONS)/ansible_collections/community/general` is already present, and removes the destructive `--force`
  download flag.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Adding a directory existence check for
  `$(COLLECTIONS)/ansible_collections/community/general` makes repeated runs of `make bootstrap` fully idempotent and
  instantaneous without network roundtrips or overwriting locally cached collections.
- **Learning target:** Verify GNU Make 3.81 recipe execution and POSIX shell branch behavior across clean vs
  pre-existing collection directories.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** In `Makefile` (`bootstrap:` target):
  1. Guard the collection installation by testing if directory `$(COLLECTIONS)/ansible_collections/community/general`
     exists.
  2. If the directory exists, print `"Ansible collections: ok (already installed in $(COLLECTIONS))"` and skip running
     `ansible-galaxy collection install`.
  3. If missing, run
     `ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)" "$(GALAXY)" collection install -r "$(SELF_DIR)/ansible/requirements.yml"`
     without the `--force` flag.
- **Git branch:**
  `I-1794888493-galaxy-check/P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium/E-1-galaxy-guard/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Inspect `Makefile` line 150-151 under target `bootstrap:`.
2. Replace unconditional
   `ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)" "$(GALAXY)" collection install -r "$(SELF_DIR)/ansible/requirements.yml" --force || exit 1`
   with a POSIX shell
   `if [ -d "$(COLLECTIONS)/ansible_collections/community/general" ]; then echo "Ansible collections: ok (already installed in $(COLLECTIONS))"; else ...; fi`
   block.
3. Remove the `--force` argument from the collection install invocation.
4. Ensure recipe indentation uses literal tabs and remains compatible with GNU Make 3.81 (no `.ONESHELL`, no `$(file)`,
   no `!=`).

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification),
  `holon-config/world/constraints.md` §3 (Environment mutation boundaries).
- **Potential failure modes for this step:** Shell quoting errors or broken exit status handling causing bootstrap to
  fail silently or crash on spaces in paths.
- **Guardrails and early‑abort checks:** Ensure `$(COLLECTIONS)` path variable is quoted in test and galaxy arguments,
  and ensure `|| exit 1` propagates non-zero exits on install failure.

### Success & Discard Criteria

- **Success:** When `$(COLLECTIONS)/ansible_collections/community/general` exists, running `make bootstrap` prints
  `Ansible collections: ok (already installed in ...)` and executes zero network calls. When the directory is absent,
  galaxy collection install runs without `--force`.
- **Discard:** Retaining `--force` or failing to skip collection install when the directory exists.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.03  |
| impact_pred         | 90.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 1.0   |
| ev_pred             | 88.59 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.0 - 0.3 * 0.03 - 1.0 = 89.10 + 0.5 - 0.009 - 1.0 = 88.591 ~ 88.59`.

---

## Step 2: Implement Side-by-Side Diff Formatting in devenv_wizard.py

- **Sub‑intent recommendation:** NO
- **Reasoning:** Enhances `format_diff(src_path, dest_path)` in `scripts/devenv_wizard.py` to produce side-by-side diffs
  using `delta` or `diff`, falling back gracefully to Python's built-in `difflib.unified_diff`.
- **Step Type:** FEATURE
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Terminal-width-aware side-by-side diff rendering via `delta` or `diff -y` dramatically
  improves readability during interactive conflict resolution while maintaining 100% zero-dependency fallback via
  `difflib`.
- **Learning target:** Ensure robust subprocess invocation, terminal column discovery, and error isolation so missing
  tools or subprocess errors never crash the wizard.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** In `scripts/devenv_wizard.py`:
  1. Update `format_diff(src_path: Path, dest_path: Path) -> str` to determine available terminal width using
     `shutil.get_terminal_size(fallback=(80, 24)).columns`.
  2. If `delta` is on `PATH` (`shutil.which("delta")`): invoke `delta --side-by-side -w <cols>` (or
     `delta -s -w <cols>`) via `subprocess.run` on `dest_path` and `src_path`, returning the rendered output.
  3. Else if `diff` is on `PATH` (`shutil.which("diff")`): invoke `diff -y -W <cols>` via `subprocess.run`, capturing
     stdout (handling return codes 0 and 1 cleanly).
  4. Fallback: if external tools are unavailable or return an error, generate unified diff using Python's
     `difflib.unified_diff`.
- **Git branch:**
  `I-1794888493-galaxy-check/P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium/E-2-wizard-side-by-side-diff/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. In `scripts/devenv_wizard.py`, examine `format_diff(src_path: Path, dest_path: Path) -> str`.
2. Inspect terminal column width via `shutil.get_terminal_size(fallback=(80, 24)).columns`.
3. Check for `delta` using `shutil.which("delta")`. If present, run
   `subprocess.run(["delta", "--side-by-side", "-w", str(cols), str(dest_path), str(src_path)], capture_output=True, text=True, check=False)`.
   If successful and returns output, return `result.stdout`.
4. If `delta` is not found or fails, check for `diff` via `shutil.which("diff")`. If present, run
   `subprocess.run(["diff", "-y", "-W", str(cols), str(dest_path), str(src_path)], capture_output=True, text=True, check=False)`.
   If returncode is 0 or 1, return `result.stdout`.
5. Fall back to existing `difflib.unified_diff` if neither command succeeded.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Coding conventions, PEP 8, robust error handling).
- **Potential failure modes for this step:** `subprocess.run` raising `OSError`, unexpected return codes from `diff`
  (exit code 1 is expected when differences exist), or broken encoding.
- **Guardrails and early‑abort checks:** Wrap subprocess executions in `try...except OSError`, check
  `returncode in (0, 1)`, and verify output text is non-empty before returning.

### Success & Discard Criteria

- **Success:** `format_diff` produces side-by-side diff with `delta` when available, with `diff -y` when delta is
  absent, and falls back to unified diff when neither is present.
- **Discard:** Any unhandled subprocess exception that causes `format_diff` to crash when external commands fail.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.05  |
| impact_pred         | 91.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 1.5   |
| ev_pred             | 88.42 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 91.0 + 0.5 * 1.5 - 0.3 * 0.05 - 1.5 = 89.18 + 0.75 - 0.015 - 1.5 = 88.415 ~ 88.42`.

---

## Step 3: Add Unit Tests in test_manifest.py and test_wizard.py

- **Sub‑intent recommendation:** NO
- **Reasoning:** Codifies structural invariants in `tests/test_manifest.py` to prevent regression of the Makefile
  collection guard and `--force` flag removal, and adds unit test coverage in `tests/test_wizard.py` for side-by-side
  diffing across `delta`, `diff -y`, and `difflib` fallback paths.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicit structural tests ensure that future modifications to `Makefile` or
  `scripts/devenv_wizard.py` cannot inadvertently re-introduce `--force`, remove the collection idempotency guard, or
  break side-by-side formatting fallbacks.
- **Learning target:** Confirm test coverage of all execution branches in `format_diff` using clean unit test mocks.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:**
  1. In `tests/test_manifest.py`: add `test_makefile_bootstrap_guards_collections_and_omits_force()` verifying that
     `Makefile`'s bootstrap target checks for `ansible_collections/community/general`, prints the ok message, does NOT
     include `--force` in `collection install`, and uses `ANSIBLE_COLLECTIONS_PATH`.
  2. In `tests/test_wizard.py`: expand `test_format_diff` to test `delta --side-by-side`, `diff -y -W`, and `difflib`
     fallback branches using `unittest.mock.patch`.
- **Git branch:**
  `I-1794888493-galaxy-check/P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium/E-3-tests-and-invariants/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. In `tests/test_manifest.py`:
   - Read `Makefile` contents.
   - Extract the `bootstrap:` recipe.
   - Assert `community/general` directory guard is present.
   - Assert `--force` does not appear in `collection install`.
   - Assert `Ansible collections: ok (already installed in` message string is present.
2. In `tests/test_wizard.py`:
   - Test when `delta` is available on PATH and returns formatted output.
   - Test when `delta` is absent but `diff` is available and returns side-by-side output.
   - Test when neither is available, verifying standard unified diff formatting.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing constraints: pytest runner, manifest coverage).
- **Potential failure modes for this step:** Brittle regex matching or mock leakage across tests.
- **Guardrails and early‑abort checks:** Use scoped `patch` context managers or `monkeypatch` fixtures in pytest.

### Success & Discard Criteria

- **Success:** All new tests pass cleanly under `pytest`, asserting both Makefile invariant checks and wizard diff
  formatting behavior.
- **Discard:** Flaky tests or reliance on unmanaged host binaries.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.03  |
| impact_pred         | 92.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 1.0   |
| ev_pred             | 90.57 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 1.0 - 0.3 * 0.03 - 1.0 = 91.08 + 0.5 - 0.009 - 1.0 = 90.571 ~ 90.57`.

---

## Step 4: Full Quality Suite Verification

- **Sub‑intent recommendation:** NO
- **Reasoning:** Executes the complete repository verification suite across pytest, ruff, ansible-lint, prettier, and
  make check to guarantee zero regressions.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** The proposed changes to `Makefile`, `scripts/devenv_wizard.py`, and tests satisfy all
  linter, formatting, syntax, and invariant requirements across the workspace.
- **Learning target:** Confirm full workspace compliance with CI quality gates.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** Run and verify all local quality gates:
  1. `uv run --extra test pytest -m "not network"`
  2. `uv run ruff check .`
  3. `uv run --extra test ansible-lint ansible/site.yml`
  4. `npx prettier --check "**/*.md"`
  5. `make check`
- **Git branch:**
  `I-1794888493-galaxy-check/P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium/E-4-quality-suite/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Execute pytest suite with `-m "not network"`.
2. Execute ruff linter over the entire workspace.
3. Execute ansible-lint on `ansible/site.yml`.
4. Execute prettier markdown check across all markdown files.
5. Execute `make check` prerequisite verification.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Coding conventions, Prettier compliance), §3 (Testing
  constraints).
- **Potential failure modes for this step:** Prettier formatting failure due to unquoted or unescaped math expressions
  in markdown, or Ruff lint violations in Python files.
- **Guardrails and early‑abort checks:** Ensure single-pass Prettier convergence by enclosing all math formulas in
  backtick code spans.

### Success & Discard Criteria

- **Success:** All five quality commands exit with returncode 0.
- **Discard:** Any linting, formatting, or test failure.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 0.5   |
| ev_pred             | 90.32 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 0.5 - 0.3 * 0.02 - 1.0 = 91.08 + 0.25 - 0.006 - 1.0 = 90.324 ~ 90.32`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Composite probability across all four steps. The proposed changes consist of targeted shell
  recipe guards in `Makefile`, straightforward standard library and subprocess enhancements in
  `scripts/devenv_wizard.py`, and standard pytest additions in `tests/test_manifest.py` and `tests/test_wizard.py`.
- **entropy_pred**: 0.13. Calculated as the direct sum of step entropies across all four steps
  (`0.03 + 0.05 + 0.03 + 0.02 = 0.13`). This is well within the system budget limit of 10.0.
- **impact_pred**: 92.0. Eliminates redundant network operations and destructive overwrites in `make bootstrap`,
  significantly speeds up developer loop iteration, provides a high-fidelity visual side-by-side diff in
  `devenv_wizard.py` for terminal users, and codifies invariant test guarantees.
- **cost_pred**: 4.5. Calculated as the direct sum of individual step costs (`1.0 + 1.5 + 1.0 + 1.0 = 4.5`).
- **learning_value_pred**: 4.0. Direct sum of step learning values (`1.0 + 1.5 + 1.0 + 0.5 = 4.0`), reflecting value
  gained in establishing standard subprocess fallback patterns and Makefile idempotent guards.
- **ev_pred**: 88.54. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 92.0 + 0.5 * 4.0 - 0.3 * 0.13 - 4.5 = 91.08 + 2.0 - 0.039 - 4.5 = 88.541 ~ 88.54`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: GNU Make 3.81 compatibility, no
    `.ONESHELL`, no `$(file)`, no `!=`, no `.RECIPEPREFIX`).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8 compliance, single-pass Prettier
    formatting with backtick code spans for arithmetic expressions).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, manifest invariant
    assertions).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: zero unmanaged state modifications).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Non-GNU Make 3.81 syntax: using advanced makefile functions or features. Mitigated by using standard POSIX shell
    conditional test `[ -d "..." ]` within the recipe tab.
  - Subprocess crashes in `format_diff`: `subprocess.run` could fail if `delta` or `diff` exits with non-zero or raises
    `OSError`. Mitigated by catching exceptions and handling diff returncodes `(0, 1)`, falling back cleanly to
    `difflib.unified_diff`.
  - Markdown formatting drift: unformatted markdown or arithmetic formulas failing Prettier checks. Mitigated by
    enclosing all formulas in backtick code spans and verifying with `npx prettier --check "**/*.md"`.
- **Mitigations built into the plan:**
  - Comprehensive unit testing of all fallback paths in `format_diff`.
  - Invariant assertion tests in `tests/test_manifest.py` ensuring `--force` is never reintroduced.
  - Full end-to-end quality suite verification before completion.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.13
- **Budget Compliance:** The plan entropy of 0.13 is strictly below the budget limit (`0.13 <= 10.0`).

# Plan for I-1794922981-unify-sh

- **Plan ID:** P-1794922998-8e517433-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794922981-unify-sh
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T13:43:25Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses three concrete areas of shell and build UX: unifying
  NVM version storage across Fish and Bash/Zsh, preventing Homebrew path usurpation and canonicalizing NVM
  initialization in Bash and Zsh, and cleaning up Makefile bootstrap output so the next-step instruction only appears
  when running `make bootstrap` directly.
- **Exploration stance:** Focused exploit across dotfiles, Makefile, and test manifests adhering strictly to world
  constraints, GNU Make 3.81 compatibility, and single-pass Prettier formatting.
- **Safety priority level:** standard
- **Priority Justification:** Adheres strictly to `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81
  compatibility, no hardcoded paths), §2 (Assertion over hope, single-pass Prettier convergence with code-span
  arithmetic), §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic configuration refinements across shell dotfiles, Makefiles, and test
  invariants.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.06  |
| impact_pred         | 92.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 4.0   |
| ev_pred             | 91.56 |

---

## Step 1: Unify Fish NVM Storage and Provide Migration Fallback

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped modification to `dotfiles/fish/.config/fish/conf.d/00-devenv.fish` to align Fish's `nvm.fish`
  data root with canonical `nvm-sh` version paths and provide backward-compatible symlinks for legacy versions.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Setting `set -g nvm_data $XDG_DATA_HOME/nvm/versions/node` enables `nvm.fish` and
  `nvm-sh` to share the exact same Node binary installations under `$XDG_DATA_HOME/nvm/versions/node/v*` without
  duplicate downloads, while symlink/migration fallback guarantees legacy versions under `$XDG_DATA_HOME/nvm/v*` remain
  accessible.
- **Learning target:** Confirm `nvm_data` points to `$XDG_DATA_HOME/nvm/versions/node`, verify that directory
  initialization handles existing versions gracefully, and verify path resolution.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Configure unified NVM version directory in `00-devenv.fish` and implement fallback/symlink handling.
- **Git branch:**
  `I-1794922981-unify-sh/P-1794922998-8e517433-antigravity-agent-gemini-3.8-flash-medium/E-1-fish-nvm-storage/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
2. Update the `nvm_data` definition to `set -g nvm_data $XDG_DATA_HOME/nvm/versions/node`.
3. Add a lightweight migration or symlink fallback check:
   - Ensure the directory `$XDG_DATA_HOME/nvm/versions/node` exists.
   - For any existing directory or symlink matching `$XDG_DATA_HOME/nvm/v*`, if no corresponding entry exists in
     `$XDG_DATA_HOME/nvm/versions/node/`, create a relative or absolute symlink so that legacy installations remain
     discoverable.
   - Conversely, if versions exist in `$XDG_DATA_HOME/nvm/versions/node/v*` and legacy tools look under
     `$XDG_DATA_HOME/nvm/v*`, ensure symlink parity.
4. Maintain `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"` ensuring highest precedence.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, no hardcoded home paths),
  `holon-config/world/constraints.md` §3 (Environment mutation boundaries).
- **Potential failure modes for this step:** Fish syntax error during conf.d evaluation if path expansion fails or if
  wildcard globbing expands to literal strings when no files match.
- **Guardrails and early‑abort checks:** Use `test -d` and proper Fish path list checking or glob suppression (e.g.
  `path is -d` or checking if matching paths exist before looping) so empty directories don't cause errors.

### Success & Discard Criteria

- **Success:** `00-devenv.fish` sets `nvm_data` to `$XDG_DATA_HOME/nvm/versions/node` and safely preserves legacy
  versions.
- **Discard:** Syntax error in Fish startup or broken NVM version discovery in Fish.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 88.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 1.0   |
| ev_pred             | 87.32 |

Calculated via: `EV = 0.99 * 88.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.3 = 87.12 + 0.5 - 0.003 - 0.3 = 87.317 ~ 87.32`.

---

## Step 2: Prevent Homebrew Path Usurpation and Canonicalize NVM Sourcing in Bash and Zsh

- **Sub‑intent recommendation:** NO
- **Reasoning:** Updates `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc` to guard Homebrew `shellenv` evaluation
  against overwriting prior `PATH` ordering, moves NVM to the front of `PATH` after Homebrew initialization, and
  simplifies NVM to canonical XDG sourcing.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Guarding `brew shellenv` so it only evaluates when Homebrew is not already present on
  `PATH`, and ensuring NVM is prepended to the front of `PATH` after Homebrew initialization, prevents Homebrew's node
  binary from usurping repo-managed NVM Node and eliminates false `-> system` alias display in `nvm ls`.
- **Learning target:** Confirm that `/opt/homebrew/bin` does not override NVM or `~/.local/bin` in both login and
  interactive Bash and Zsh shells, and that canonical sourcing of `nvm.sh` and `bash_completion` functions smoothly.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Update `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc` with Homebrew path guards, NVM precedence
  re-assertion, and canonical XDG sourcing.
- **Git branch:**
  `I-1794922981-unify-sh/P-1794922998-8e517433-antigravity-agent-gemini-3.8-flash-medium/E-2-bash-zsh-homebrew-nvm/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc`.
2. Update the Multi-OS Homebrew initialization:
   - For Darwin: check if `/opt/homebrew/bin` (or `/usr/local/bin` for Intel) is already on `PATH` via pattern matching
     `case ":$PATH:" in *":/opt/homebrew/bin:"*) ... ;; esac`. Only evaluate `brew shellenv` if not already present.
   - For Linux: guard `/home/linuxbrew/.linuxbrew/bin` similarly.
3. Ensure NVM and local binary directory precedence:
   - Move or prepend `~/.local/bin` and `$NVM_DIR/current/bin` to the front of `PATH` after Homebrew initialization
     (matching Fish's `fish_add_path -m` behavior).
4. Simplify NVM initialization to standard canonical XDG sourcing convention:
   - `export NVM_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/nvm"`
   - `[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"`
   - `[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"`
   - Remove redundant or conflicting legacy fallback branches that confuse `nvm ls` and cause false `-> system` display.
5. Ensure interactive checks and local override hooks (`.bashrc.local`, `.zshrc.local`) remain intact.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, no hardcoded `/Users` or `/home` paths),
  `holon-config/world/constraints.md` §3 (Environment mutation boundaries).
- **Potential failure modes for this step:** Shell startup errors or unintentional duplicate entries on `PATH` if
  pattern matching is malformed.
- **Guardrails and early‑abort checks:** Use strict POSIX parameter expansion and case pattern matching, validating
  syntax with `bash -n` and `zsh -n` (where available).

### Success & Discard Criteria

- **Success:** In both Bash and Zsh, NVM node has absolute precedence over Homebrew binaries, Homebrew shellenv is
  guarded against re-evaluating when already on `PATH`, and canonical XDG sourcing is clean.
- **Discard:** Regression in PATH precedence or syntax errors in Bash/Zsh dotfiles.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 91.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 1.5   |
| ev_pred             | 90.43 |

Calculated via: `EV = 0.99 * 91.0 + 0.5 * 1.5 - 0.3 * 0.02 - 0.4 = 90.09 + 0.75 - 0.006 - 0.4 = 90.434 ~ 90.43`.

---

## Step 3: Conditionalize Makefile Bootstrap Next-Step Output

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped edit in `Makefile` to conditionally print the next-step guidance message only when `bootstrap`
  is the explicit target goal.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Wrapping the post-bootstrap guidance echo inside `ifeq ($(MAKECMDGOALS),bootstrap)`
  eliminates misleading output when `make install` or other compound targets invoke `bootstrap` sub-recipes.
- **Learning target:** Confirm that GNU Make 3.81 correctly evaluates `$(MAKECMDGOALS)` and that the next-step message
  is printed only during direct `make bootstrap` invocations.
- **Maximum acceptable cost for this learning:** 0.2

### Intent & Git Integration

- **Step Intent:** Update `Makefile` bootstrap recipe with `ifeq ($(MAKECMDGOALS),bootstrap)` guard.
- **Git branch:**
  `I-1794922981-unify-sh/P-1794922998-8e517433-antigravity-agent-gemini-3.8-flash-medium/E-3-makefile-bootstrap-ux/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `Makefile`.
2. Locate the end of the `bootstrap:` recipe where `Run 'make install' or 'make check-mode' next.` is echoed.
3. Wrap that echo statement in a conditional block:
   - `ifeq ($(MAKECMDGOALS),bootstrap)`
   - `@echo "Run 'make install' or 'make check-mode' next."`
   - `endif`
4. Verify that this syntax strictly respects GNU Make 3.81 rules (no `.ONESHELL`, no `.RECIPEPREFIX`, standard GNU Make
   conditional directive).

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: compatible with GNU Make 3.81, no
  prohibited operators).
- **Potential failure modes for this step:** Syntax error if indentation or conditional directives are malformed.
- **Guardrails and early‑abort checks:** Ensure conditional directives (`ifeq`, `endif`) are not indented with recipe
  tabs. Verify `make -n bootstrap` and `make -n install` parse cleanly.

### Success & Discard Criteria

- **Success:** `make bootstrap` displays the next-step instruction, while `make install` omits it.
- **Discard:** Makefile parsing syntax errors or broken target dependencies.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 85.0  |
| cost_pred           | 0.2   |
| learning_value_pred | 0.5   |
| ev_pred             | 84.20 |

Calculated via: `EV = 0.99 * 85.0 + 0.5 * 0.5 - 0.3 * 0.01 - 0.2 = 84.15 + 0.25 - 0.003 - 0.2 = 84.197 ~ 84.20`.

---

## Step 4: Update Manifest Test Invariants for Unified Storage, Shell Parity, and Makefile UX

- **Sub‑intent recommendation:** NO
- **Reasoning:** Updates `tests/test_manifest.py` to establish regression tests for the unified Fish NVM storage path,
  NVM precedence over Homebrew in Bash/Zsh, and conditional Makefile bootstrap output.
- **Step Type:** TESTING
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating the manifest test suite to assert unified NVM storage in `00-devenv.fish`, NVM
  precedence and canonical XDG sourcing in `.bashrc` and `.zshrc`, and conditional bootstrap output in `Makefile`
  ensures long-term structural invariance against regressions.
- **Learning target:** Validate that all modified invariants pass unit test inspection cleanly and fail if
  configurations regress.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Add test assertions to `tests/test_manifest.py` covering Fish unified storage, Bash/Zsh Homebrew
  guards and NVM precedence, and Makefile conditional output.
- **Git branch:**
  `I-1794922981-unify-sh/P-1794922998-8e517433-antigravity-agent-gemini-3.8-flash-medium/E-4-test-manifest-invariants/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_manifest.py`.
2. Update `test_fish_nvm_path_resolution_in_conf_d`:
   - Assert that `00-devenv.fish` sets `nvm_data` to `$XDG_DATA_HOME/nvm/versions/node`.
   - Assert that migration or symlink fallback handling for legacy versions exists.
3. Update `test_multishell_nvm_and_node_parity` and `test_multishell_conda_and_homebrew_parity`:
   - Assert that Homebrew `brew shellenv` evaluation in Bash and Zsh is guarded when `/opt/homebrew/bin` is already on
     `PATH`.
   - Assert that NVM path precedence is re-asserted after Homebrew evaluation.
   - Assert canonical XDG sourcing: `export NVM_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/nvm"`,
     `[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"`, and `[ -s "$NVM_DIR/bash_completion" ]`.
4. Add a test function asserting Makefile bootstrap UX:
   - Check that `Makefile` contains `ifeq ($(MAKECMDGOALS),bootstrap)` guarding
     `Run 'make install' or 'make check-mode' next.`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing constraints: all test modifications explicitly
  declared in plan), `holon-config/world/ruleset.md` §2 (Assertion over hope).
- **Potential failure modes for this step:** Broken regex or assertion mismatch if exact whitespace varies.
- **Guardrails and early‑abort checks:** Use clear semantic substring or AST/pattern checks, and execute `pytest`
  immediately to verify.

### Success & Discard Criteria

- **Success:** `pytest tests/test_manifest.py` passes cleanly and validates all new and updated invariants.
- **Discard:** Assertion errors or test failures.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 90.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 1.0   |
| ev_pred             | 89.30 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.3 = 89.10 + 0.5 - 0.003 - 0.3 = 89.297 ~ 89.30`.

---

## Step 5: Full Repository Quality Suite Execution and Validation

- **Sub‑intent recommendation:** NO
- **Reasoning:** Executes repository-wide linters, formatters, and automated test suites to ensure zero regressions
  across all files touched.
- **Step Type:** TESTING
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Running all mandated validation commands ensures full compliance with code quality,
  linter standards, documentation formatting, and prerequisite checks.
- **Learning target:** Verify that `pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check` all succeed with zero
  warnings or errors.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Validate repository integrity with full test and linter suite.
- **Git branch:**
  `I-1794922981-unify-sh/P-1794922998-8e517433-antigravity-agent-gemini-3.8-flash-medium/E-5-repository-validation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Run `uv run --extra test pytest -m "not network"`.
2. Run `uv run ruff check .` and resolve any Python linting or formatting issues.
3. Run `uv run --extra test ansible-lint ansible/site.yml` to verify playbooks and roles.
4. Run `npx prettier --check "**/*.md"` to guarantee single-pass Prettier convergence across all markdown documents.
5. Run `make check` to verify prerequisites and syntax.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards, Prettier formatting), §3
  (Testing constraints).
- **Potential failure modes for this step:** Prettier formatting divergence or linter warnings.
- **Guardrails and early‑abort checks:** Ensure all math and metric notations are wrapped in backticks to prevent
  formatting drift.

### Success & Discard Criteria

- **Success:** All test and lint commands exit with status 0.
- **Discard:** Any test or linter failure.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 90.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 1.0   |
| ev_pred             | 89.30 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.3 = 89.10 + 0.5 - 0.003 - 0.3 = 89.297 ~ 89.30`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from composite high confidence across all five steps. Each step addresses a modular,
  well-scoped change with clear boundaries: unifying Fish NVM storage with fallback symlinks, guarding Homebrew path
  evaluation and enforcing NVM precedence in Bash/Zsh, conditionalizing Makefile bootstrap output, adding invariant unit
  tests, and executing repository-wide validation.
- **entropy_pred**: 0.06. Calculated as the cumulative sum of step entropies across all steps
  (`0.01 + 0.02 + 0.01 + 0.01 + 0.01 = 0.06`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 92.0. Unifies NVM storage across Fish, Bash, and Zsh so that all shells share identical version
  directories under `~/.local/share/nvm/versions/node/v*`, prevents Homebrew path usurpation, eliminates false
  `-> system` aliases, cleans up Makefile UX, and enforces these guarantees through automated test invariants.
- **cost_pred**: 1.5. Calculated as the direct sum of individual step costs (`0.3 + 0.4 + 0.2 + 0.3 + 0.3 = 1.5`).
- **learning_value_pred**: 4.0. Reflects the value of standardizing cross-shell NVM version layout, cementing Homebrew
  path guard patterns, and improving Makefile build messaging.
- **ev_pred**: 91.56. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 92.0 + 0.5 * 4.0 - 0.3 * 0.06 - 1.5 = 91.08 + 2.0 - 0.018 - 1.5 = 91.562 ~ 91.56`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: no hardcoded home or system paths; resolve from facts or `$HOME`
    / `$XDG_*`).
  - `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: must stay compatible with GNU Make 3.81, no `.ONESHELL`,
    no `.RECIPEPREFIX`).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: single-pass Prettier formatting with backtick
    code spans for arithmetic expressions, assertion over hope).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, dotfile editing
    boundaries).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Legacy version accessibility: If existing versions exist at `~/.local/share/nvm/v*`, changing `nvm_data` to
    `$XDG_DATA_HOME/nvm/versions/node` could render them invisible if migration or symlink fallback is omitted. The plan
    explicitly addresses this with symlink fallback logic.
  - Homebrew PATH reordering: `brew shellenv` unconditionally prepends brew paths. Guarding it with a PATH containment
    check and re-asserting NVM precedence ensures NVM Node is never shadowed.
  - Makefile conditional syntax: `ifeq ($(MAKECMDGOALS),bootstrap)` is standard GNU Make syntax supported in GNU Make
    3.81.
- **Mitigations built into the plan:**
  - Fallback symlinks between `~/.local/share/nvm/v*` and `~/.local/share/nvm/versions/node/v*`.
  - Case pattern matching in Bash and Zsh to guard against duplicate or usurping PATH prepends.
  - Manifest unit tests to prevent future regressions.
- **Residual risk accepted (and why):**
  - Minimal residual risk: all changes are non-destructive and verified through the full test suite.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.06
- **Budget Compliance:** The plan entropy of 0.06 is well below the budget limit (`0.06 <= 10.0`).

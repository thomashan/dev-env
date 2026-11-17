# Plan for I-1794891050-fish-path-order

- **Plan ID:** P-1794891067-8b9d55f7-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794891050-fish-path-order
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T04:51:12Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses a PATH precedence order bug where Homebrew's
  `brew shellenv` moves Homebrew bin paths (`/opt/homebrew/bin`, `/opt/homebrew/sbin`) to the front of Fish's `$PATH`,
  superseding nvm-managed node binaries.
- **Exploration stance:** Focused exploit with deterministic path ordering in fish config, test assertion updates in
  `tests/test_manifest.py`, and verification across test and lint suites.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification, Multi-OS Darwin/Linux parity), `holon-config/world/ruleset.md` §2 (Assertion over hope, single-pass
  Prettier formatting with code-span arithmetic), `holon-config/world/ruleset.md` §3 (pytest verification under
  `tests/`, all test modifications declared in plan), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic shell configuration adjustments, manifest test assertions, and
  automated test suite verifications.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.06  |
| impact_pred         | 88.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 3.0   |
| ev_pred             | 87.10 |

---

## Step 1: Reorder PATH Setup in `dotfiles/fish/.config/fish/config.fish`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Directly fixes the PATH initialization order in fish shell configuration so that Homebrew and user tool
  paths are evaluated prior to nvm's path addition.
- **Step Type:** BUGFIX
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Invoking `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"` after Homebrew's
  `brew shellenv | source` (and after `$HOME/.local/bin`) moves the nvm node directory to the absolute front of `$PATH`,
  ensuring nvm node wins over Homebrew's `/opt/homebrew/bin/node` on macOS and Linuxbrew on Linux.
- **Learning target:** Confirm that fish path ordering behavior deterministically places the most recently prepended
  directory (`-p -m`) at the front of `$PATH` regardless of earlier modifications by `brew shellenv`.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** In `dotfiles/fish/.config/fish/config.fish`:
  1. Relocate user tool paths (`fish_add_path -gaP "$HOME/.local/bin"`) and Homebrew initialization
     (`switch "$devenv_os" ... case Darwin ... brew shellenv | source ... case Linux ...`) so they execute before nvm
     configuration.
  2. Place `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"` immediately after the Homebrew block, ensuring it runs
     after `brew shellenv` moves Homebrew paths to the front.
  3. Maintain explanatory comments clarifying why nvm must be prepended after `brew shellenv`.
- **Git branch:**
  `I-1794891050-fish-path-order/P-1794891067-8b9d55f7-antigravity-agent-gemini-3.8-flash-medium/E-1-reorder-fish-path-setup/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/fish/.config/fish/config.fish`.
2. Move `fish_add_path -gaP "$HOME/.local/bin"` to appear under `# --- PATH` before the OS switch block.
3. Keep the `switch "$devenv_os"` block (which sources `brew shellenv` on Darwin and adds linuxbrew paths on Linux)
   before nvm.
4. Place `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"` after the `switch "$devenv_os"` block.
5. Update comments to document that `brew shellenv` calls
   `fish_add_path --global --move --path "/opt/homebrew/bin" "/opt/homebrew/sbin"`, so nvm must be added with `-gpPm`
   after `brew shellenv` to guarantee nvm-managed node wins on `$PATH`.
6. Verify file formatting and syntax.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification, Multi-OS Darwin/Linux
  rules, no hardcoded user paths), `holon-config/world/ruleset.md` §2 (Assertion over hope),
  `holon-config/world/constraints.md` §3 (Environment mutation boundaries).
- **Potential failure modes for this step:** Broken syntax in fish config or inverted OS detection block.
- **Guardrails and early‑abort checks:** Maintain exact fish syntax, preserve Darwin/Linux case branches, and ensure
  `$XDG_DATA_HOME` variable fallback remains in place.

### Success & Discard Criteria

- **Success:** `dotfiles/fish/.config/fish/config.fish` contains `brew shellenv` and `$HOME/.local/bin` setup before
  `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"`.
- **Discard:** Retaining nvm path addition prior to `brew shellenv`.

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

## Step 2: Update Manifest Test Assertions in `tests/test_manifest.py` and Run Validation Suite

- **Sub‑intent recommendation:** NO
- **Reasoning:** Updates the unit test assertion in `tests/test_manifest.py` to reflect the new ordering requirement
  (nvm evaluated after `brew shellenv` and user tool paths) and runs the entire automated verification suite.
- **Step Type:** TESTING
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating `test_node_bin_is_first_on_path` to assert that
  `fish_cfg.index("brew shellenv") < fish_cfg.index("nvm/current/bin")` and
  `fish_cfg.index('$HOME/.local/bin') < fish_cfg.index("nvm/current/bin")` permanently validates the invariant that nvm
  path addition occurs after Homebrew and user tools.
- **Learning target:** Confirm pytest test suite, ruff linter, ansible-lint, prettier, and make check all pass cleanly.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `tests/test_manifest.py`, modify `test_node_bin_is_first_on_path()`:
     - Update assertion to verify that `brew shellenv` occurs before `nvm/current/bin` in `config.fish` (`brew < nvm`).
     - Update assertion to verify that `$HOME/.local/bin` occurs before `nvm/current/bin` in `config.fish`
       (`local < nvm`).
     - Ensure `-gpPm` is present.
     - Update docstring to explain that nvm must be prepended after `brew shellenv` and `~/.local/bin` so nvm node wins
       over Homebrew node and user tools.
  2. Execute validation commands:
     - `uv run --extra test pytest -m "not network"`
     - `uv run ruff check .`
     - `uv run --extra test ansible-lint ansible/site.yml`
     - `npx prettier --check "**/*.md"`
     - `make check`
- **Git branch:**
  `I-1794891050-fish-path-order/P-1794891067-8b9d55f7-antigravity-agent-gemini-3.8-flash-medium/E-2-manifest-tests-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_manifest.py`.
2. Locate `test_node_bin_is_first_on_path()`.
3. Read `config.fish` and find indices of `"nvm/current/bin"`, `"brew shellenv"`, and `"$HOME/.local/bin"`.
4. Assert `brew < nvm` with informative failure message: "nvm path addition must occur after brew shellenv so
   nvm-managed node wins on PATH".
5. Assert `local < nvm` with informative failure message: "nvm's node must be prepended after ~/.local/bin".
6. Assert `"-gpPm" in fish_cfg`.
7. Format python files with `uv run ruff format .` and check with `uv run ruff check .`.
8. Format markdown files with `npx prettier --write "**/*.md"` or verify with `npx prettier --check "**/*.md"`.
9. Run `uv run --extra test pytest -m "not network"`.
10. Run `uv run --extra test ansible-lint ansible/site.yml`.
11. Run `make check`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (PEP 8 compliance, single-pass Prettier formatting),
  `holon-config/world/ruleset.md` §3 (pytest runner, all test modifications explicitly declared in plan),
  `holon-config/world/constraints.md` §2 (process sandbox entropy limit `< 10`).
- **Potential failure modes for this step:** Prettier formatting failure on markdown files or index lookups in test if
  search strings do not match.
- **Guardrails and early‑abort checks:** Format files prior to checking and verify all commands succeed with exit
  code 0.

### Success & Discard Criteria

- **Success:** All unit tests pass, `ruff` reports zero errors, `prettier` checks pass, `ansible-lint` succeeds, and
  `make check` succeeds.
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

- **p_success_pred**: 0.99. Derived from composite high confidence across both steps. The root cause is a
  straightforward PATH initialization sequence issue in fish configuration: `brew shellenv` moves `/opt/homebrew/bin` to
  the front of `$PATH`, overriding earlier path prepends. Evaluating
  `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"` after `brew shellenv` deterministically restores nvm node
  priority at the front of `$PATH`.
- **entropy_pred**: 0.06. Calculated as the cumulative sum of step entropies across both steps (`0.02 + 0.04 = 0.06`).
  This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 88.0. Unblocks correct Node.js binary resolution in Fish interactive and non-interactive sessions,
  ensuring the declarative nvm-managed Node.js installation (defined in Ansible and fish dotfiles) takes precedence over
  Homebrew-installed Node.js binaries.
- **cost_pred**: 1.5. Calculated as the direct sum of individual step costs (`0.5 + 1.0 = 1.5`).
- **learning_value_pred**: 3.0. Reflects the value of implementing regression test coverage in `tests/test_manifest.py`
  verifying that nvm path addition occurs strictly after Homebrew initialization in fish dotfiles.
- **ev_pred**: 87.10. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 88.0 + 0.5 * 3.0 - 0.3 * 0.06 - 1.5 = 87.12 + 1.5 - 0.018 - 1.5 = 87.102 ~ 87.10`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: GNU Stow multi-variant dotfile packaging,
    Multi-OS Darwin/Linux rules, no hardcoded user paths).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: Ansible style, assertion over hope, PEP 8,
    single-pass Prettier formatting with backtick code spans for arithmetic expressions).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, all test modifications explicitly declared
    in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, dotfile editing
    boundaries).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Inadvertently hardcoding `/opt/homebrew` outside OS conditional guards: mitigated by preserving the
    `switch "$devenv_os"` architecture in `config.fish`.
  - Inadvertent test suite failure: mitigated by explicitly declaring the update of `test_node_bin_is_first_on_path` in
    Step 2 to verify that `brew shellenv` and `$HOME/.local/bin` appear before `nvm/current/bin`.
  - Markdown formatting drift: arithmetic expressions unquoted causing Prettier formatting failures. Mitigated by
    wrapping all arithmetic derivations in backtick code spans.
- **Mitigations built into the plan:**
  - Step-by-step modification and verification of each affected file.
  - Inclusion of manifest test assertions in `tests/test_manifest.py` verifying relative ordering of `brew shellenv` and
    `nvm/current/bin`.
  - Comprehensive multi-tool verification suite (`pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check`).
- **Residual risk accepted (and why):**
  - Residual risk is negligible because reordering path additions in fish configuration is completely deterministic and
    covered by unit test assertions.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.06
- **Budget Compliance:** The plan entropy of 0.06 is well below the budget limit (`0.06 <= 10.0`).

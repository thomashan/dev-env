# Plan for I-1794801434-curl

- **Plan ID:** P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794801434-curl
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-16T03:57:38Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent specifies a clear, high-value simplification of the
  bootstrapping toolchain: standardizing on `curl` as the sole network fetcher for Miniforge3 (with self-install via
  `brew` or `apt` if missing), eliminating `wget` and Python `urllib.request` fallbacks, requiring Conda-owned Python
  for `make configure`, and eradicating legacy `apt-get` references across the repository in favor of `apt`.
- **Exploration stance:** Focused exploit with targeted validation of Makefile shell recipes, GNU Make 3.81
  compatibility, package removal syntax in Ansible, documentation consistency, and test invariant enforcement.
- **Safety priority level:** standard
- **Priority Justification:** Aligned with `holon-config/world/ruleset.md` §1 (GNU Make 3.81 compatibility, pure
  `make -> conda -> ansible` toolchain, Multi-OS Darwin/Linux parity), `holon-config/world/ruleset.md` §2 (Coding
  conventions, static typing, Prettier markdown formatting with code-span arithmetic), `holon-config/world/ruleset.md`
  §3 (Testing constraints), `holon-config/world/constraints.md` §1 (Branch isolation and commit boundaries), and
  `holon-config/world/constraints.md` §3 (Environment mutation boundaries, two supported backends: `brew` and `apt`).

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps follow deterministic implementation patterns with well-defined contracts and verification
  criteria.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.97  |
| entropy_pred        | 0.35  |
| impact_pred         | 92.0  |
| cost_pred           | 6.0   |
| learning_value_pred | 3.5   |
| ev_pred             | 84.89 |

---

## Step 1: Makefile Minimal `curl`-Only & `apt`-Only Bootstrap and Python Runtime Guard

- **Sub‑intent recommendation:** NO
- **Reasoning:** Foundational core change in `Makefile`. Replaces legacy `apt-get` references with `apt`, strips out
  `wget` and `urllib.request` fallbacks, installs `curl` if absent using platform-native package managers (`brew` on
  Darwin, `apt` on Linux), downloads Miniforge3 using `curl` exclusively, and enforces Conda-managed Python in
  `make configure`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Restricting Miniforge3 fetching to `curl -fsSL` and automatically installing `curl` via
  Homebrew on Darwin or `apt` on Linux guarantees minimal surface area while eliminating unneeded network fetcher
  fallbacks and host Python dependency.
- **Learning target:** Confirm POSIX shell recipe semantics in GNU Make 3.81 for conditionally finding or installing
  `curl` across Darwin and Linux without triggering syntax or quoting failures.
- **Maximum acceptable cost for this learning:** 2.0

### Intent & Git Integration

- **Step Intent:** In `Makefile`:
  1. Replace `apt-get` with `apt` across recipes and error strings:
     - Line 42 error message: replace `apt-get install -y make` with `apt install -y make`.
     - Line 83 cold-start instruction: replace `sudo apt-get install -y make` with `sudo apt install -y make`.
     - Line 96 prerequisite check: probe `command -v apt` instead of `command -v apt-get`.
  2. In the `bootstrap` target:
     - Remove `wget` and `python3 urllib.request` download fallbacks entirely.
     - When `$(CONDA)` is missing and `$$target` does not exist:
       - Probe `command -v curl >/dev/null 2>&1`.
       - If `curl` is missing:
         - On Darwin: locate `brew` (`/opt/homebrew/bin/brew`, `/usr/local/bin/brew`, or `command -v brew`) and run
           `"$$brew_bin" install curl`. If Homebrew is not found, exit with error message indicating Homebrew is
           required to install curl.
         - On Linux: execute `apt update && apt install -y curl`, prefixing with `sudo` if `id -u` is not 0.
       - Download Miniforge3 installer using ONLY `curl`: `curl -fsSL "$$url" -o "$$target" || exit 1`.
  3. In the `configure` target:
     - Require `"$(CONDA_DIR)/bin/python3"`. If absent or not executable, print an error instructing the user to run
       `make bootstrap` first and exit with code 1, completely removing the host `python3` fallback.
  4. Preserve strict GNU Make 3.81 compatibility (standard tabs for recipes, no `.ONESHELL`, no `$(file)`, no `!=`, no
     `.RECIPEPREFIX`).
- **Git branch:**
  `I-1794801434-curl/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium/E-1-makefile-curl-apt/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. `Makefile` Error & Help Text Updates:
   - Update line 42 GNU Make requirement check to recommend `apt install -y make` instead of `apt-get install -y make`.
   - Update line 83 help message to display `sudo apt install -y make`.
2. `Makefile` Prerequisite Probe (`check` target):
   - Update line 96 Linux backend check to test `command -v apt` rather than `command -v apt-get`.
3. `Makefile` Bootstrap Target Simplification:
   - In target `bootstrap`: inside the `if [ ! -f "$$target" ]; then ... fi` block:
     - First check if `curl` is installed using `command -v curl >/dev/null 2>&1`.
     - If `curl` is missing:
       - On `Darwin`: check `/opt/homebrew/bin/brew`, `/usr/local/bin/brew`, or `command -v brew`. Set `brew_bin`. If
         found, execute `"$$brew_bin" install curl || exit 1`. If not found, echo
         `Error: curl is missing and Homebrew was not found to install it. Please install curl or Homebrew.` and exit 1.
       - On `Linux`: determine if `id -u` equals 0; run `sudo apt update && sudo apt install -y curl || exit 1` if
         non-root, or `apt update && apt install -y curl || exit 1` if root.
     - Fetch the installer using `curl -fsSL "$$url" -o "$$target" || exit 1`.
     - Ensure no references to `wget`, `python3 -c "import urllib.request..."`, or `No fetcher found` remain.
4. `Makefile` Configure Target Strictness:
   - Check if `"$(CONDA_DIR)/bin/python3"` is executable.
   - If not executable, echo `Error: Python 3 not found in $(CONDA_DIR)/bin/python3. Run 'make bootstrap' first.` and
     exit 1.
   - If executable, invoke `"$(CONDA_DIR)/bin/python3" "$(SELF_DIR)/scripts/devenv_wizard.py"`.
5. Compatibility Verification:
   - Verify all recipe lines use tab indents and POSIX-compliant shell syntax compatible with GNU Make 3.81.

### Dependencies & Critical Path

- **Depends on:** None (Initial execution step).
- **Is Bottleneck:** YES (Core runtime bootstrap depends on Makefile logic).

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (GNU Make 3.81 compatibility, pure `make -> conda -> ansible`
  toolchain), `holon-config/world/constraints.md` §3 (Two-backends-only: brew and apt).
- **Potential failure modes for this step:** Shell syntax error in Make recipe; tab vs space indentation issues;
  unintended Make variable expansion of `$$` escape sequences.
- **Guardrails and early‑abort checks:** Run `make -n bootstrap` and `make check` immediately after editing to verify
  syntax validity without side effects.

### Success & Discard Criteria

- **Success:** `Makefile` contains zero occurrences of `apt-get`, `wget`, or `urllib.request`. `curl -fsSL`,
  `install curl`, and `apt install -y curl` are correctly present in `bootstrap`. `make check` passes.
- **Discard:** Discard if GNU Make fails parsing or recipe syntax breaks.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.25  |
| impact_pred         | 88.0  |
| cost_pred           | 2.0   |
| learning_value_pred | 3.0   |
| ev_pred             | 85.67 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 88.0 + 0.5 * 3.0 - 0.3 * 0.25 - 2.0 = 86.24 + 1.50 - 0.075 - 2.0 = 85.665 ~ 85.67`. High EV
refactoring step that cleanly modernizes the repo entry point.

---

## Step 2: Replace `apt-get` in Ansible Package Removal Task

- **Sub‑intent recommendation:** NO
- **Reasoning:** Single focused task update maintaining strict uniformity across the repository by using `apt` instead
  of `apt-get` for package removals on Linux.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Replacing `'apt-get remove -y '` with `'apt remove -y '` in
  `ansible/roles/packages/tasks/main.yml` preserves package uninstallation semantics on Debian/Ubuntu while removing the
  last operational `apt-get` call in Ansible playbooks.
- **Learning target:** Confirm Ansible task parsing and linting cleanly accept the updated removal command string.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** In `ansible/roles/packages/tasks/main.yml`, locate the task
  `Remove packages that duplicate a managed runtime` and replace `'apt-get remove -y '` on line 28 with
  `'apt remove -y '`.
- **Git branch:**
  `I-1794801434-curl/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium/E-2-ansible-apt-removal/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Modify `ansible/roles/packages/tasks/main.yml`:
   - Inspect line 28 where the ternary operator selects between Homebrew and APT commands.
   - Replace the string literal `'apt-get remove -y '` with `'apt remove -y '`.
   - Preserve all other Jinja templating filters (`map('extract', devenv_pkg_aliases) | join(' ')`), `become:` settings,
     and task conditional expressions.

### Dependencies & Critical Path

- **Depends on:** Step 1
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, two supported backends: `brew` and `apt`),
  `holon-config/world/ruleset.md` §2 (Ansible style).
- **Potential failure modes for this step:** YAML syntax error or improper Jinja indentation.
- **Guardrails and early‑abort checks:** Run `uv run --extra test ansible-lint ansible/site.yml` to ensure YAML validity
  and style conformity.

### Success & Discard Criteria

- **Success:** `ansible/roles/packages/tasks/main.yml` contains `'apt remove -y '` and zero occurrences of `apt-get`.
- **Discard:** Discard if YAML syntax breaks or `ansible-lint` fails.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.10  |
| impact_pred         | 70.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 1.0   |
| ev_pred             | 69.27 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 70.0 + 0.5 * 1.0 - 0.3 * 0.10 - 0.5 = 69.30 + 0.50 - 0.03 - 0.5 = 69.27`. Low entropy,
highly predictable syntax substitution.

---

## Step 3: Update Documentation and World Constraints

- **Sub‑intent recommendation:** NO
- **Reasoning:** Keeps repository documentation and architectural constraints synchronized with implementation reality,
  eliminating stale mentions of `wget`, `python3 urllib`, and `apt-get`.
- **Step Type:** DOCUMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating ASCII architecture diagrams and constraint guidelines ensures full consistency
  between operational behavior and developer-facing documentation while satisfying strict Prettier formatting rules.
- **Learning target:** Verify Markdown table and ASCII art alignment with Prettier formatting constraints.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `README.md`:
     - Update the Step 1 `make bootstrap` ASCII box in the top-level execution diagram: state that `make bootstrap`
       installs `curl` via `brew` (macOS) or `apt` (Linux) if absent and fetches Miniforge3 using `curl` only.
     - Remove all mentions of `wget` and `python3 urllib` from the diagram and accompanying descriptive text.
     - Check for any residual `apt-get` references across `README.md` and replace with `apt`.
  2. In `holon-config/world/constraints.md`:
     - In §3 ("Environment Mutation Boundaries"), replace `apt-get install` with `apt install` in the sentence
       describing package manifest convergence.
- **Git branch:**
  `I-1794801434-curl/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium/E-3-docs-and-constraints/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Update `README.md`:
   - Locate the ASCII flowchart at lines 23-30. Replace line 25:
     `|  - Fetch Miniforge3 installer using curl, wget, or python3 urllib     |` with updated text detailing curl-only
     fetching and automated curl installation via brew/apt if missing, keeping ASCII borders strictly aligned.
   - Audit `README.md` for any remaining mentions of `wget`, `urllib`, or `apt-get`.
2. Update `holon-config/world/constraints.md`:
   - Locate line 52: `never by running brew install / apt-get install inside an execution step.`
   - Replace `apt-get install` with `apt install`.
3. Prettier Formatting Verification:
   - Run `npx prettier --check "**/*.md"` to verify clean single-pass convergence.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Markdown & Docs: enclose arithmetic in code spans for
  single-pass Prettier convergence).
- **Potential failure modes for this step:** Prettier formatting failure if ASCII art column widths or list indents are
  misaligned.
- **Guardrails and early‑abort checks:** Format with `npx prettier --write "**/*.md"` and verify diff.

### Success & Discard Criteria

- **Success:** Neither `README.md` nor `holon-config/world/constraints.md` contains `apt-get`, `wget`, or
  `python3 urllib`. `npx prettier --check "**/*.md"` exits 0.
- **Discard:** Discard if documentation drifts from code reality or markdown formatting checks fail.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.15  |
| impact_pred         | 75.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 1.5   |
| ev_pred             | 73.96 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 75.0 + 0.5 * 1.5 - 0.3 * 0.15 - 1.0 = 74.25 + 0.75 - 0.045 - 1.0 = 73.955 ~ 73.96`.
Straightforward doc and specification alignment with near-certain execution success.

---

## Step 4: Unit and Manifest Test Assertions

- **Sub‑intent recommendation:** NO
- **Reasoning:** In accordance with `holon-config/world/ruleset.md` §3, test modifications and additions must be
  explicitly declared during planning. Adding automated tests locks in the invariant that `apt-get`, `wget`, and
  `urllib` cannot regress into the codebase.
- **Step Type:** TESTING
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Manifest test assertions will permanently enforce that: (1) `Makefile` bootstrap uses
  only `curl`, (2) `curl` is conditionally installed via Homebrew or APT, (3) `wget` and `urllib.request` are banned
  from `Makefile`, and (4) `apt-get` does not exist anywhere in core repository orchestration and documentation files.
- **Learning target:** Implement pytest assertions parsing Makefile target definitions and scanning targeted manifest
  files without brittle formatting assumptions.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:** In `tests/test_manifest.py`, add two new test functions:
  1. `test_makefile_bootstrap_uses_only_curl_and_installs_curl_via_brew_or_apt()`:
     - Assert that `wget` and `urllib.request` do NOT appear in `Makefile`.
     - Extract the `bootstrap:` recipe block from `Makefile`.
     - Assert that `curl -fsSL`, `install curl`, and `apt install -y curl` are present within the `bootstrap:` target.
  2. `test_no_apt_get_in_repo()`:
     - Check `Makefile`, `ansible/roles/packages/tasks/main.yml`, `README.md`, and `holon-config/world/constraints.md`.
     - Assert that `apt-get` does NOT appear anywhere in those files.
- **Git branch:**
  `I-1794801434-curl/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium/E-4-manifest-test-assertions/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Inspect `tests/test_manifest.py`:
   - Identify existing test patterns utilizing `read(REPO_ROOT / "Makefile")` and pytest fixtures.
2. Add `test_makefile_bootstrap_uses_only_curl_and_installs_curl_via_brew_or_apt`:
   - Read `Makefile` content.
   - Assert `wget` not in makefile.
   - Assert `urllib.request` not in makefile.
   - Split `Makefile` content by `bootstrap:` and isolate the recipe block up to the subsequent target (`configure:`).
   - Assert `"curl -fsSL"` in bootstrap block.
   - Assert `"install curl"` in bootstrap block.
   - Assert `"apt install -y curl"` in bootstrap block.
3. Add `test_no_apt_get_in_repo`:
   - Define the list of target files: `Makefile`, `ansible/roles/packages/tasks/main.yml`, `README.md`, and
     `holon-config/world/constraints.md`.
   - Read each file and assert `"apt-get"` not in content, providing informative error messages if an instance is
     detected.
4. Run Unit Tests:
   - Run `uv run --extra test pytest tests/test_manifest.py -k "curl or apt"` to verify test execution and assertion
     behavior.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2, Step 3
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing constraints: pytest runner, explicit test modification
  declarations in plan).
- **Potential failure modes for this step:** Test failure due to unexpected target slicing or whitespace mismatch in
  `Makefile`.
- **Guardrails and early‑abort checks:** Ensure robust substring searching and verify that slice delimiters cleanly
  isolate the `bootstrap:` recipe.

### Success & Discard Criteria

- **Success:** Both test functions pass cleanly under `uv run pytest`.
- **Discard:** Discard if tests fail or if test declarations were not explicitly planned.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.20  |
| impact_pred         | 85.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 2.5   |
| ev_pred             | 82.99 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 85.0 + 0.5 * 2.5 - 0.3 * 0.20 - 1.5 = 83.30 + 1.25 - 0.06 - 1.5 = 82.99`. High expected
value by securing regress-free architectural invariants through automated tests.

---

## Step 5: Full Suite Verification & Quality Gates

- **Sub‑intent recommendation:** NO
- **Reasoning:** Mandatory comprehensive validation gate ensuring all static analyses, linting suites, unit test
  frameworks, and Makefile targets succeed with zero warnings or errors.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** The complete set of changes adheres strictly to the repo world rules, constraints, coding
  conventions, and test invariants.
- **Learning target:** Confirm full end-to-end integration pass across pytest, ruff, ansible-lint, prettier, and GNU
  make.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:** Execute all mandated project quality gates:
  1. `uv run --extra test pytest -m "not network"`
  2. `uv run ruff check .`
  3. `uv run --extra test ansible-lint ansible/site.yml`
  4. `npx prettier --check "**/*.md"`
  5. `make check`
- **Git branch:**
  `I-1794801434-curl/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium/E-5-verification-and-gates/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Run unit test suite:
   - Execute `uv run --extra test pytest -m "not network"`.
   - Ensure all tests pass, specifically manifest and templating tests.
2. Run Python linter:
   - Execute `uv run ruff check .`.
   - Verify zero lint issues across tests and scripts.
3. Run Ansible linter:
   - Execute `uv run --extra test ansible-lint ansible/site.yml`.
   - Verify tasks, roles, and playbooks pass lint checks.
4. Run Markdown formatter check:
   - Execute `npx prettier --check "**/*.md"`.
   - Ensure zero formatting deviations across all documentation, plans, and config markdown files.
5. Run Make prerequisite check:
   - Execute `make check`.
   - Verify prerequisite probe reports clean status and accurate tool descriptions.

### Dependencies & Critical Path

- **Depends on:** Steps 1 through 4
- **Is Bottleneck:** YES (Final gate for execution release)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1, §2, §3; `holon-config/world/constraints.md` §1, §3.
- **Potential failure modes for this step:** Residual lint discrepancies or Prettier formatting issues on markdown
  files.
- **Guardrails and early‑abort checks:** Format files prior to check using `npx prettier --write "**/*.md"` and
  `uv run ruff check --fix .`.

### Success & Discard Criteria

- **Success:** All verification commands exit with code 0 without any error or warning.
- **Discard:** Discard if any test, lint, or format check fails.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.15  |
| impact_pred         | 90.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 2.0   |
| ev_pred             | 89.06 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 2.0 - 0.3 * 0.15 - 1.0 = 89.10 + 1.00 - 0.045 - 1.0 = 89.055 ~ 89.06`.
Deterministic validation audit ensuring release readiness.

---

## Strategy Rationale

The overall plan metrics were derived from individual step-level metrics as follows:

- **p_success_pred**: 0.97. Rooted in the step probabilities (Step 1: 0.98, Step 2: 0.99, Step 3: 0.99, Step 4: 0.98,
  Step 5: 0.99). The refactoring tasks involve standard Make, Ansible, Markdown, and Python pytest syntax, leading to
  very high execution confidence.
- **entropy_pred**: 0.35. Evaluated as the maximum single-step risk profile (Step 1: 0.25, with buffer for
  cross-platform POSIX make syntax). The sum of predicted step entropies across all five steps is 0.85
  (`0.25 + 0.10 + 0.15 + 0.20 + 0.15 = 0.85`), comfortably below the process sandbox entropy threshold of 10.0.
- **impact_pred**: 92.0. Standardizes bootstrapping onto `curl`-only fetching with automatic self-install via `brew`
  (Darwin) or `apt` (Linux), eliminates obsolete `wget` and `urllib.request` fallbacks, banishes `apt-get` throughout
  the repo in favor of `apt`, restricts Python execution in `configure` strictly to Conda, updates architecture
  documentation, and adds permanent test invariants.
- **cost_pred**: 6.0. Calculated as the direct sum of individual step costs (`2.0 + 0.5 + 1.0 + 1.5 + 1.0 = 6.0`).
- **learning_value_pred**: 3.5. Epistemic value of verifying minimal GNU Make 3.81 bootstrap patterns and cross-platform
  package manager invocation without sub-shells or external `.sh` scripts.
- **ev_pred**: 84.89. Computed strictly via the config-driven Expected Value formula:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system constants `lambda = 0.3`
  and `mu = 0.5` loaded from `holon-config/metrics/ev_config.json`:
  `EV = 0.97 * 92.0 + 0.5 * 3.5 - 0.3 * 0.35 - 6.0 = 89.24 + 1.75 - 0.105 - 6.0 = 84.885 ~ 84.89`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: pure `make -> conda -> ansible` toolchain,
    GNU Make 3.81 compatibility, no shell scripts tracked, Python target `==3.13.*` via Miniforge Conda, Multi-OS
    Darwin/Linux parity).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8, static typing, single-pass Prettier
    formatting with code-span arithmetic).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, tests located in `tests/`, all test
    modifications explicitly declared during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow & Branch Constraints: branch prefix isolation
    `I-{timestamp}-{slug}/P-{timestamp}-{agent}-{model}/E-{timestamp}-{action}/_`, rebase discipline, commit
    boundaries).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment Tiers: process sandbox $< 10$ entropy).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: converge through manifest, two backends
    only: `brew` and `apt`).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero modifications to historical ledger entries).
- **Potential violations or edge cases:**
  - GNU Make 3.81 incompatibility: Using modern Make features like `.ONESHELL`, `$(file ...)`, or `!=`. Mitigated by
    adhering strictly to POSIX shell compound statements and standard Make variables.
  - Sudo requirement on Linux: Running `apt update && apt install -y curl` might require elevated privileges if executed
    by a non-root user. Mitigated by probing `$(id -u)` and conditionally prepending `sudo`.
  - Missing Homebrew on macOS: When `curl` is missing on macOS and Homebrew is also absent. Mitigated by checking
    Homebrew binary locations (`/opt/homebrew/bin/brew`, `/usr/local/bin/brew`, `command -v brew`) and outputting an
    actionable error message if neither is found.
  - Prettier formatting failure: Unformatted math or tables breaking CI checks. Mitigated by enclosing all arithmetic
    and derivations in backtick code spans.
- **Mitigations built into the plan:**
  - Explicit checking of `command -v curl` before attempting package manager installation.
  - Strict conditional branching for root vs non-root on Linux `apt`.
  - Explicit test assertions added to `tests/test_manifest.py` verifying that forbidden tools (`wget`, `urllib.request`,
    `apt-get`) do not reappear.
- **Residual risk accepted (and why):**
  - Host without `curl` and without `brew` on macOS cannot auto-install `curl`; accepted as macOS ships `curl` by
    default, and `brew` is the supported macOS package manager.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.35
- **Budget Compliance:** The strategy fits well within budget (`0.35 <= 10.0`).

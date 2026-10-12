# Plan for I-1791798831-add-cicd-pipeline

- **Plan ID:** P-1791798842-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** NONE
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-10-12T09:54:07Z

## Planner Autonomy Summary

- **Intent handling:** REFRAME
- **Reframed intent (if applicable):** While accepting the root intent to establish GitHub Actions CI/CD workflows and resolve test suite errors, autonomous analysis of the repository's active state uncovered that fixing only the single syntax error in `tests/test_templating.py` (line 228) is insufficient for clean quality gate convergence. The test suite and hygiene checks suffer from three coupled upstream defects: (1) `tests/test_manifest.py` contains an undefined variable `text` (instead of `code`) and an overly restrictive regex that rejects valid GNU Make 3.81 conditionals (`ifeq`, `ifneq`, `else`, `endif`) and directives (`$(error ...)`), (2) `tests/conftest.py` does not merge `group_vars` into Jinja templar context, causing 19 templating unit tests to fail on undefined variables, and (3) `ruff` is omitted from `pyproject.toml` and `uv.lock`, preventing `uv run ruff check .` from running. The intent is reframed to holistically resolve all test collection, execution, dependency currency, and markdown Prettier formatting discrepancies so that both local validation and all newly established GitHub Actions workflows converge with 100% test pass rates.
- **Exploration stance:** balanced with targeted empirical validation of GitHub Actions multi-OS matrix runners (`ubuntu-latest`, `macos-latest`), GNU Make 3.81 tab parsing semantics, and Ansible templar execution boundaries across Linux and Darwin.
- **Safety priority level:** standard
- **Priority Justification:** Triggered by `holon-config/world/ruleset.md` §1 (Multi-OS rule, Python runtime `==3.13.*`, GNU Make 3.81 compatibility, no shell scripts), `holon-config/world/ruleset.md` §2 (Coding conventions, static typing, Prettier markdown formatting with code-span arithmetic), `holon-config/world/ruleset.md` §3 (Testing constraints: pytest runner, tests placed in `tests/`, all test modifications explicitly declared in the planning phase), `holon-config/world/constraints.md` §1 (Prefix-based branch isolation and git flow), `holon-config/world/constraints.md` §2 (Process sandbox containment `< 10` entropy), and `holon-config/world/constraints.md` §3 (Ledger immutability).

## Exploration

- **Proportion of steps that are exploratory:** 0.33
- **Justification:** Steps 1 and 4 incorporate balanced exploratory validation to empirically probe Ansible Templar variable inheritance in pytest fixtures and verify multi-OS workflow runner behavior across Linux and macOS platforms without internet access during unit tests.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.93  |
| entropy_pred        | 0.70  |
| impact_pred         | 93.0  |
| cost_pred           | 10.4  |
| learning_value_pred | 5.0   |
| ev_pred             | 78.38 |

### Strategy Rationale

The overall plan metrics were derived from individual step-level metrics as follows:

- **p_success_pred**: 0.93. Dictated by the bottleneck step (Step 4: 0.93), where multi-stage hygiene workflow steps (combining `uv lock`, Ruff, Prettier, and Ansible-lint) must cleanly harmonize across locked dependencies and linters.
- **entropy_pred**: 0.70. Evaluated as the maximum single-step risk profile (Step 4: 0.70), where hygiene workflow composition and linter rule suites are validated. The sum of predicted step entropies across all six steps is 2.70 (`0.60 + 0.40 + 0.50 + 0.70 + 0.20 + 0.30 = 2.70`), well within the allocated entropy budget of 15.0.
- **impact_pred**: 93.0. Establishes robust CI/CD automation across Darwin and Linux, resolves breaking syntax and test collection errors, and locks in repository hygiene gates.
- **cost_pred**: 10.4. Calculated as the direct sum of individual step costs (`2.0 + 1.5 + 2.2 + 2.5 + 1.0 + 1.2 = 10.4`).
- **learning_value_pred**: 5.0. Epistemic gain from establishing canonical multi-OS GitHub Actions workflow architecture for `dev-env` adapted from `holon-agentic-coder`, hardening Ansible Jinja template test fixtures, and codifying single-pass Prettier formatting standards.
- **ev_pred**: 78.38. Computed strictly via the config-driven Expected Value formula:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system constants `lambda = 0.3` and `mu = 0.5` loaded from `holon-config/metrics/ev_config.json`:
  `EV = 0.93 * 93.0 + 0.5 * 5.0 - 0.3 * 0.70 - 10.4 = 86.49 + 2.50 - 0.21 - 10.4 = 78.38`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: Python target `==3.13.*`, package management via `uv`, no `.sh` scripts tracked, GNU Make 3.81 compatibility, Multi-OS Darwin/Linux parity).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8, static typing, single-pass Prettier formatting with code-span arithmetic).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: `uv run pytest`, tests located in `tests/`, all test modifications explicitly declared during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow & Branch Constraints: branch prefix isolation `I-{timestamp}-{slug}/P-{timestamp}-{agent}-{model}/E-{timestamp}-{action}/_`, rebase discipline, commit boundaries).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment Tiers: process sandbox $< 10$ entropy).
  - `holon-config/world/constraints.md` §3 (Ledger Immutability: zero modifications to historical ledger entries).
- **Potential violations or edge cases:**
  - Introducing `.sh` scripts into `.github/` or repo root (strictly prohibited by `ruleset.md` §1; workflows must call make targets or inline multi-line YAML commands directly).
  - Running network-dependent tests during standard CI unit runs (prohibited by `ruleset.md` §3 and intent requirements; network tests must be marked `@pytest.mark.network` and isolated behind `DEVENV_NETWORK_TESTS=1`).
  - GitHub Actions runners drifting from Python 3.13 pin (mitigated by explicit `astral-sh/setup-uv` and `python-version: "3.13"`).
  - Inadvertent edits to `holon-knowledge/ledger/` historical lines.
- **Mitigations built into the plan:**
  - Workflows use pure native GitHub Actions steps without standalone shell scripts.
  - Test suite error fixes in `tests/test_templating.py`, `tests/test_manifest.py`, and `tests/conftest.py` are explicitly enumerated and declared in the plan prior to execution.
  - Local verification mirrors CI steps precisely to guarantee zero divergence.
- **Residual risk accepted (and why):**
  - Upstream network assets in `test-network.yml` depending on external GitHub release URLs; accepted because network tests run exclusively on scheduled/manual triggers with clear failure isolation.
- **Allocated Entropy Budget:** 15.0
- **Predicted Plan Entropy:** 0.70
- **Budget Compliance:** The strategy fits within budget (`0.70 <= 15.0`).

## Plan Description & Strategy

This plan establishes the automated GitHub Actions CI/CD workflows and repairs the test and hygiene foundations of `dev-env`:

1. **Test Suite Collection & Execution Repairs (`tests/`):**
   - In `tests/test_templating.py`: Remove the unmatched closing parenthesis on line 228 after `@pytest.mark.skipif(...)`.
   - In `tests/test_manifest.py`: Fix `NameError: name 'text' is not defined` on line 157 by referencing `code`; remove unused imports (`pathlib.Path`, `role_files`); update the recipe/directive regex in `test_makefile_recipes_are_tab_indented` to recognize GNU Make conditionals (`ifeq`, `ifneq`, `ifdef`, `ifndef`, `else`, `endif`) and directives (`$(error ...)`).
   - In `tests/conftest.py`: Update the session `templar` fixture to accept `group_vars` and merge them into the rendering variable dictionary, ensuring role template tests resolve group variables without `AnsibleUndefinedVariable` exceptions.

2. **Tooling Hygiene & Lockfile Currency (`pyproject.toml`, `uv.lock`):**
   - Add `ruff>=0.8` to `[project.optional-dependencies]` under `test` in `pyproject.toml` so that `uv sync --locked --extra test` provisions Ruff for `uv run ruff check .`.
   - Regenerate and verify `uv.lock` via `uv lock`, asserting that `uv lock --check` and `git diff --exit-code uv.lock` succeed.
   - Run Prettier write convergence across repository markdown documents to ensure `npx prettier --check "**/*.md"` passes cleanly.

3. **Multi-OS GNU Make Workflow (`.github/workflows/make.yml`):**
   - Implement matrix workflow on `ubuntu-latest` and `macos-latest` triggered on push and pull requests targeting `main`.
   - Validate host architecture via `uname -m`, run `make help`, and run `make check` to ensure prerequisite probe integrity across both operating systems.

4. **Automated Unit Testing Workflow (`.github/workflows/test-unit.yml`):**
   - Implement matrix workflow on `ubuntu-latest` and `macos-latest` using `actions/checkout@v4` and `astral-sh/setup-uv@v5`.
   - Synchronize locked test dependencies and run `uv run --extra test pytest -v -l --tb=short -m "not network"`.

5. **Hygiene & Network Test Workflows (`test-hygiene.yml`, `test-network.yml`):**
   - `test-hygiene.yml`: Run on `ubuntu-latest` to verify lockfile currency (`uv lock --check`, `git diff --exit-code uv.lock`), synchronize test virtualenv (`uv sync --locked --extra test`), run Ruff linter (`uv run ruff check .`), verify Markdown Prettier formatting (`npx prettier --check "**/*.md"`), and run Ansible playbook linting (`uv run --extra test ansible-lint`).
   - `test-network.yml`: Run on `ubuntu-latest` triggered on schedule (`cron: '0 6 * * *'`) and manual `workflow_dispatch` (with optional PR opt-in), running `DEVENV_NETWORK_TESTS=1 uv run --extra test pytest -m network`.

6. **CI/CD Architecture Documentation (`.github/workflows/README.md`):**
   - Document all workflow specifications, runner matrix architectures, triggering strategies, quality gates, and recommended branch protection rules.

7. **Full Verification Quality Gate:**
   - Run local validation matching all CI checks (`pytest`, `ruff`, `prettier`, `make check`), confirming 100% convergence.

---

## Step 1: Repair Test Suite Syntax, Invariant Assertions, and Templar Fixture in tests/

- **Sub‑intent recommendation:** NO
- **Reasoning:** Targeted test suite repair explicitly declared in planning per `holon-config/world/ruleset.md` §3 to resolve collection syntax errors and execution failures.
- **Step Type:** FIX
- **Exploration level:** BALANCED
- **Hypothesis being tested:** Merging `group_vars` into `templar` in `tests/conftest.py` and expanding the Makefile tab indentation regex enables the complete 30-item unit test suite to pass cleanly without network calls.
- **Learning target:** Confirm Ansible Templar variable inheritance across Jinja tests and verify GNU Make 3.81 conditional syntax parsing.
- **Maximum acceptable cost for this learning:** 2.0

### Intent & Git Integration

- **Step Intent:** Fix line 228 syntax error in `tests/test_templating.py`, repair undefined variable and tab indentation regex in `tests/test_manifest.py`, and update `templar` fixture in `tests/conftest.py`.
- **Git branch:** `I-1791798831-add-cicd-pipeline/P-1791798842-antigravity-agent-gemini-3.8-flash-medium/E-1-fix-test-suite-errors/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. In `tests/test_templating.py`:
   - Locate line 227-228: `@pytest.mark.skipif(...)` followed by an orphaned closing parenthesis `)`.
   - Remove the orphaned `)` on line 228 so `test_miniforge_installer_names_exist_upstream` has valid Python decorator syntax.
2. In `tests/test_manifest.py`:
   - In `test_dotfiles_hardcode_no_per_user_paths`: replace `if "/opt/homebrew" in text or "/usr/local/bin/brew" in text:` with `code` instead of `text`, and in the subsequent assertion replace `in text` with `in code`.
   - Remove unused imports `pathlib.Path` and `.conftest.role_files` from the top of the file to maintain clean Ruff lint status.
   - In `test_makefile_recipes_are_tab_indented`: update the regex matching valid top-level Makefile lines to include GNU Make conditionals and directives: `^(?:ifeq|ifneq|ifdef|ifndef|else|endif|\$\(error\b|ifn?e?lse?|include|-?\.|[\w.\-/() $*]+\s*[:?+]?=|[\w./ ,@%()$-]+:)`.
3. In `tests/conftest.py`:
   - Update `templar` fixture signature to take `group_vars: dict`.
   - In `render(expression: str, variables: dict)`: construct merged context `ctx = dict(group_vars)` and update it with `variables`, then pass `variables=ctx` to `Templar(loader=DataLoader(), variables=ctx).template(...)`.
4. Validate locally: execute `uv run --extra test pytest -v -m "not network"` and verify all unit tests pass with zero failures.

### Dependencies & Criticality

- **Depends on:** NONE
- **Is Bottleneck:** YES (Unit tests and CI workflows cannot validate until test collection succeeds)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing constraints; explicit test modification declaration), `holon-config/world/ruleset.md` §2 (PEP 8, docstrings).
- **Potential failure modes for this step:** Breaking existing test assertions by over-generalizing variable inheritance.
- **Guardrails and early‑abort checks:** Run `pytest tests/` after each modification to verify incremental test stability.

### Success & Discard Criteria

- **Success:** Pytest successfully collects all tests in `tests/test_templating.py` and `tests/test_manifest.py`; all non-network unit tests pass.
- **Discard:** Discard if any test failure persists or network access is triggered during non-network test execution.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.95  |
| entropy_pred        | 0.60  |
| impact_pred         | 92.0  |
| cost_pred           | 2.0   |
| learning_value_pred | 4.5   |
| ev_pred             | 87.47 |

### Step Metrics Rationale

Calculated via: `EV = 0.95 * 92.0 + 0.5 * 4.5 - 0.3 * 0.60 - 2.0 = 87.40 + 2.25 - 0.18 - 2.0 = 87.47`. High success probability; resolves test collection blocking issue and restores test suite integrity.

---

## Step 2: Harmonize Tooling Dependencies, uv.lock Currency, and Prettier Formatting

- **Sub‑intent recommendation:** NO
- **Reasoning:** Direct dependency and formatting convergence ensuring local repository passes `uv lock --check`, `uv run ruff check .`, and `npx prettier --check`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT

### Intent & Git Integration

- **Step Intent:** Add `ruff` to `[project.optional-dependencies] test` in `pyproject.toml`, update `uv.lock`, and format repository markdown files to achieve Prettier convergence.
- **Git branch:** `I-1791798831-add-cicd-pipeline/P-1791798842-antigravity-agent-gemini-3.8-flash-medium/E-2-tooling-hygiene-lock-convergence/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. In `pyproject.toml`:
   - Under `[project.optional-dependencies] test`, add `"ruff>=0.8"`.
   - Preserve existing pins: `pytest>=8.3`, `pytest-xdist>=3.6`, `ansible-lint>=25.0`.
2. Update lockfile:
   - Run `uv lock` to update `uv.lock` with the locked `ruff` package and dependencies.
   - Verify lock currency with `uv lock --check` and `git diff --stat uv.lock`.
3. Synchronize test virtual environment:
   - Run `uv sync --locked --extra test` to install Ruff and test dependencies into `.venv`.
4. Run Ruff linting:
   - Run `uv run ruff check .` to verify that Python sources conform to lint standards.
5. Markdown formatting:
   - Run `npx --yes prettier@3 --write "**/*.md"` (or `make docs-fmt`) to format existing markdown files (`README.md`, `holon-config/metrics/README.md`, `holon-config/prompts/*.md`, `holon-config/world/*.md`).
   - Validate with `npx --yes prettier@3 --check "**/*.md"`.

### Dependencies & Criticality

- **Depends on:** Step 1
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (uv package management), `holon-config/world/ruleset.md` §2 (Prettier markdown formatting with code spans).
- **Potential failure modes for this step:** Prettier altering semantic markdown content; `uv lock` introducing unintended dependency bumps.
- **Guardrails and early‑abort checks:** Inspect `git diff` after formatting to ensure no semantic loss in documentation.

### Success & Discard Criteria

- **Success:** `uv lock --check`, `uv run ruff check .`, and `npx prettier --check "**/*.md"` all return exit code 0.
- **Discard:** Discard if `uv.lock` fails lock check or Prettier warnings persist.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.96  |
| entropy_pred        | 0.40  |
| impact_pred         | 88.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 3.5   |
| ev_pred             | 84.61 |

### Step Metrics Rationale

Calculated via: `EV = 0.96 * 88.0 + 0.5 * 3.5 - 0.3 * 0.40 - 1.5 = 84.48 + 1.75 - 0.12 - 1.5 = 84.61`. Deterministic dependency resolution and automated formatting convergence.

---

## Step 3: Implement Multi-OS GNU Make and Unit Test Workflows (make.yml & test-unit.yml)

- **Sub‑intent recommendation:** NO
- **Reasoning:** Core CI workflow implementation under `.github/workflows/` validating Multi-OS build and unit test matrices.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** BALANCED
- **Hypothesis being tested:** Standard GitHub Actions runners (`ubuntu-latest` and `macos-latest`) using `astral-sh/setup-uv` reliably execute `make check` and isolated pytest unit tests without platform drift.
- **Learning target:** Validate macOS GNU Make 3.81 compatibility and uv virtualenv caching on GitHub-hosted runners.
- **Maximum acceptable cost for this learning:** 2.2

### Intent & Git Integration

- **Step Intent:** Create `.github/workflows/make.yml` and `.github/workflows/test-unit.yml` supporting Multi-OS (`ubuntu-latest`, `macos-latest`) matrices.
- **Git branch:** `I-1791798831-add-cicd-pipeline/P-1791798842-antigravity-agent-gemini-3.8-flash-medium/E-3-make-and-unit-workflows/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Create directory `.github/workflows/` if it does not already exist.
2. In `.github/workflows/make.yml`:
   - Name: `Make Check`
   - Trigger on: `push` (branches: `[main]`), `pull_request` (branches: `[main]`), and `workflow_dispatch`.
   - Concurrency: cancel in-progress runs on the same branch or PR using `concurrency: group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true`.
   - Define job `make-matrix`:
     - Runs-on: matrix of `[ubuntu-latest, macos-latest]`.
     - Steps:
       - Checkout code via `actions/checkout@v4`.
       - Print host architecture and OS: `uname -a && uname -m`.
       - Run `make help` to verify default Makefile recipe rendering.
       - Run `make check` to verify prerequisite probe passes on both Linux and Darwin.
3. In `.github/workflows/test-unit.yml`:
   - Name: `Unit Tests`
   - Trigger on: `push` (branches: `[main]`), `pull_request` (branches: `[main]`), and `workflow_dispatch`.
   - Concurrency: `group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true`.
   - Define job `test-unit`:
     - Runs-on: matrix of `[ubuntu-latest, macos-latest]`.
     - Steps:
       - Checkout code via `actions/checkout@v4`.
       - Install uv using `astral-sh/setup-uv@v5` with `enable-cache: true`.
       - Set up Python 3.13 via `actions/setup-python@v5` with `python-version: "3.13"`.
       - Sync locked dependencies: `uv sync --locked --extra test`.
       - Run unit tests: `uv run --extra test pytest -v -l --tb=short -m "not network"`.

### Dependencies & Criticality

- **Depends on:** Step 1, Step 2
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81 compatibility, Python `==3.13.*`), `holon-config/world/ruleset.md` §3 (pytest standard runner).
- **Potential failure modes for this step:** Runner-specific syntax quirks or missing GNU Make on clean GitHub runner images.
- **Guardrails and early‑abort checks:** Use standard GitHub actions (`actions/checkout@v4`, `astral-sh/setup-uv@v5`) and assert `uv.lock` is used with `--locked`.

### Success & Discard Criteria

- **Success:** YAML files conform to valid GitHub Actions workflow schemas; runner matrices cover `ubuntu-latest` and `macos-latest`; steps execute commands specified in intent.
- **Discard:** Discard if workflow uses unapproved shell scripts or hardcodes Linux-only paths.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.94  |
| entropy_pred        | 0.50  |
| impact_pred         | 90.0  |
| cost_pred           | 2.2   |
| learning_value_pred | 4.0   |
| ev_pred             | 84.25 |

### Step Metrics Rationale

Calculated via: `EV = 0.94 * 90.0 + 0.5 * 4.0 - 0.3 * 0.50 - 2.2 = 84.60 + 2.00 - 0.15 - 2.2 = 84.25`. High value establishing automated Multi-OS quality gates.

---

## Step 4: Implement Hygiene and Network Workflows (test-hygiene.yml & test-network.yml)

- **Sub‑intent recommendation:** NO
- **Reasoning:** Workflow expansion covering static hygiene checks (uv lock currency, Ruff, Prettier, Ansible-lint) and isolated network asset validation.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** BALANCED
- **Hypothesis being tested:** Combining lockfile diff checks, Ruff linting, Prettier markdown verification, and Ansible-lint in a single hygiene workflow on `ubuntu-latest` provides fail-fast developer feedback within 60 seconds.
- **Learning target:** Evaluate interaction between `uv sync --locked`, Node/Prettier execution in CI, and ansible-lint collection discovery.
- **Maximum acceptable cost for this learning:** 2.5

### Intent & Git Integration

- **Step Intent:** Create `.github/workflows/test-hygiene.yml` and `.github/workflows/test-network.yml` adhering to repository standards.
- **Git branch:** `I-1791798831-add-cicd-pipeline/P-1791798842-antigravity-agent-gemini-3.8-flash-medium/E-4-hygiene-and-network-workflows/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. In `.github/workflows/test-hygiene.yml`:
   - Name: `Code Hygiene & Lint`
   - Trigger on: `push` (branches: `[main]`), `pull_request` (branches: `[main]`), and `workflow_dispatch`.
   - Concurrency: `group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true`.
   - Define job `hygiene`:
     - Runs-on: `ubuntu-latest`.
     - Steps:
       - Checkout code via `actions/checkout@v4`.
       - Install uv using `astral-sh/setup-uv@v5` with `enable-cache: true`.
       - Set up Python 3.13 via `actions/setup-python@v5` with `python-version: "3.13"`.
       - Set up Node.js via `actions/setup-node@v4` with `node-version: "20"`.
       - Check `uv.lock` currency: `uv lock --check` followed by `git diff --exit-code uv.lock`.
       - Sync dependencies: `uv sync --locked --extra test`.
       - Run Ruff lint: `uv run ruff check .`.
       - Run Prettier markdown check: `npx --yes prettier@3 --check "**/*.md"`.
       - Run Ansible-lint: `uv run --extra test ansible-lint`.
2. In `.github/workflows/test-network.yml`:
   - Name: `Network Upstream Asset Tests`
   - Trigger on:
     - Schedule: daily at 06:00 UTC via `cron: '0 6 * * *'`.
     - Manual trigger via `workflow_dispatch`.
     - Optional PR trigger when labeled `network-tests` or targeting `main`.
   - Define job `test-network`:
     - Runs-on: `ubuntu-latest`.
     - Steps:
       - Checkout code via `actions/checkout@v4`.
       - Install uv using `astral-sh/setup-uv@v5` with `enable-cache: true`.
       - Set up Python 3.13 via `actions/setup-python@v5` with `python-version: "3.13"`.
       - Sync dependencies: `uv sync --locked --extra test`.
       - Run network tests: `DEVENV_NETWORK_TESTS=1 uv run --extra test pytest -v -l --tb=short -m network`.

### Dependencies & Criticality

- **Depends on:** Step 2, Step 3
- **Is Bottleneck:** YES (Hygiene workflow defines all PR status checks required for branch protection)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Python `==3.13.*`, package management via uv), `holon-config/world/ruleset.md` §2 (Ansible linting, Prettier markdown), `holon-config/world/ruleset.md` §3 (Network test isolation).
- **Potential failure modes for this step:** Ansible-lint complaining about collection paths; npx Prettier hanging on interactive prompt.
- **Guardrails and early‑abort checks:** Use `npx --yes` to bypass prompts; verify `ansible.cfg` points to correct collection paths.

### Success & Discard Criteria

- **Success:** Both workflow definitions are syntactically valid YAML and implement the complete sequence of checks specified in the intent.
- **Discard:** Discard if any un-whitelisted command or non-standard trigger is introduced.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.93  |
| entropy_pred        | 0.70  |
| impact_pred         | 91.0  |
| cost_pred           | 2.5   |
| learning_value_pred | 4.5   |
| ev_pred             | 84.17 |

### Step Metrics Rationale

Calculated via: `EV = 0.93 * 91.0 + 0.5 * 4.5 - 0.3 * 0.70 - 2.5 = 84.63 + 2.25 - 0.21 - 2.5 = 84.17`. High impact step establishing comprehensive automated code hygiene and upstream sanity checking.

---

## Step 5: Document CI/CD Architecture and Recommended Branch Protection Rules

- **Sub‑intent recommendation:** NO
- **Reasoning:** Author comprehensive architectural documentation in `.github/workflows/README.md`.
- **Step Type:** DOCUMENTATION
- **Exploration level:** EXPLOIT

### Intent & Git Integration

- **Step Intent:** Create `.github/workflows/README.md` documenting all workflows, runners, triggers, schedules, and recommended branch protection rules.
- **Git branch:** `I-1791798831-add-cicd-pipeline/P-1791798842-antigravity-agent-gemini-3.8-flash-medium/E-5-cicd-documentation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Create `.github/workflows/README.md`.
2. Document the CI/CD Pipeline Architecture:
   - Provide overview of the 4 workflows (`make.yml`, `test-unit.yml`, `test-hygiene.yml`, `test-network.yml`).
   - Detail matrix runner strategy (`ubuntu-latest`, `macos-latest`) and explain GNU Make 3.81 compatibility verification on macOS.
   - Detail hygiene checks: lockfile parity (`uv lock --check`), Ruff linting, Prettier markdown verification, and Ansible playbook linting (`ansible-lint`).
   - Detail network tests: explain opt-in flag `DEVENV_NETWORK_TESTS=1`, upstream GitHub release asset probing, and why network tests are excluded from standard PR builds.
3. Document Recommended Branch Protection Rules:
   - Required status checks on `main`:
     - `make-matrix (ubuntu-latest)`
     - `make-matrix (macos-latest)`
     - `test-unit (ubuntu-latest)`
     - `test-unit (macos-latest)`
     - `hygiene`
   - Require branches to be up to date before merging.
4. Run `npx --yes prettier@3 --write .github/workflows/README.md` to ensure Prettier single-pass compliance.

### Dependencies & Criticality

- **Depends on:** Step 3, Step 4
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Docstrings and documentation integrity, Prettier markdown formatting).
- **Potential failure modes for this step:** Discrepancies between workflow file names and documented job identifiers.
- **Guardrails and early‑abort checks:** Cross-reference all job names and step commands against the active YAML files.

### Success & Discard Criteria

- **Success:** `.github/workflows/README.md` thoroughly documents all workflows and passes Prettier formatting without errors.
- **Discard:** Discard if documentation leaves any workflow or runner unmentioned.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.20  |
| impact_pred         | 82.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 2.5   |
| ev_pred             | 80.55 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 82.0 + 0.5 * 2.5 - 0.3 * 0.20 - 1.0 = 80.36 + 1.25 - 0.06 - 1.0 = 80.55`. Deterministic documentation step with low entropy and high clarity.

---

## Step 6: Full Verification and Quality Gate Convergence

- **Sub‑intent recommendation:** NO
- **Reasoning:** Standard final verification step confirming all checks pass locally prior to merge readiness.
- **Step Type:** TEST
- **Exploration level:** EXPLOIT

### Intent & Git Integration

- **Step Intent:** Execute all required verification checks (`pytest`, `ruff`, `prettier`, `make check`, `ansible-lint`, `uv lock`) and verify zero regression.
- **Git branch:** `I-1791798831-add-cicd-pipeline/P-1791798842-antigravity-agent-gemini-3.8-flash-medium/E-6-local-verification-gate/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Run unit test suite: `uv run --extra test pytest -v -l --tb=short -m "not network"`. Confirm 100% test pass rate with zero errors and zero skipped failures.
2. Run Ruff linter: `uv run ruff check .`. Confirm zero violations.
3. Run Prettier check: `npx --yes prettier@3 --check "**/*.md"`. Confirm all markdown files converge cleanly.
4. Run prerequisite probe: `make check`. Confirm exit code 0.
5. Run Ansible linter: `uv run --extra test ansible-lint`. Confirm playbook passes linting.
6. Verify lockfile status: `uv lock --check` and `git diff --exit-code uv.lock`. Confirm lockfile is fully current.
7. Confirm git working tree is clean with all changes staged and committed within branch prefix boundaries.

### Dependencies & Criticality

- **Depends on:** Step 1, Step 2, Step 3, Step 4, Step 5
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1, §2, §3, `holon-config/world/constraints.md` §1.
- **Potential failure modes for this step:** Any residual unformatted markdown or stray lint warning.
- **Guardrails and early‑abort checks:** Format before check using `make docs-fmt` and `uv run ruff check --fix .`.

### Success & Discard Criteria

- **Success:** All verification commands exit with status 0.
- **Discard:** Discard if any check fails or reports warnings.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.97  |
| entropy_pred        | 0.30  |
| impact_pred         | 85.0  |
| cost_pred           | 1.2   |
| learning_value_pred | 3.0   |
| ev_pred             | 82.66 |

### Step Metrics Rationale

Calculated via: `EV = 0.97 * 85.0 + 0.5 * 3.0 - 0.3 * 0.30 - 1.2 = 82.45 + 1.50 - 0.09 - 1.2 = 82.66`. Deterministic verification confirming complete project readiness and quality gate satisfaction.
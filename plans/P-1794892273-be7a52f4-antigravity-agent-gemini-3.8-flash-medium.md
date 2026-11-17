# Plan for I-1794892256-align-versions

- **Plan ID:** P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794892256-align-versions
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T05:11:45Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses centralizing version configurations into
  `versions.json`, aligning versions across consumers (Makefile, Ansible, dotfiles, devenv_wizard.py, CI workflows,
  pyproject.toml), fixing breaking commands (`make lint`, `check-mode` in node role, and Neovim version assertions in
  Ansible), and establishing automated manifest alignment tests.
- **Exploration stance:** Focused exploit with deterministic configuration alignment, standard Ansible module and filter
  corrections, Makefile portability improvements, and automated regression test coverage.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification, Multi-OS Darwin/Linux parity), `holon-config/world/ruleset.md` §2 (Assertion over hope, single-pass
  Prettier formatting with code-span arithmetic), `holon-config/world/ruleset.md` §3 (pytest verification under
  `tests/`, all test modifications declared in plan), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic configuration centralization, recipe enhancements, Ansible task fixes,
  and manifest verification tests.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.12  |
| impact_pred         | 95.0  |
| cost_pred           | 2.5   |
| learning_value_pred | 5.0   |
| ev_pred             | 94.01 |

---

## Step 1: Create Centralized Version Configuration `versions.json`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Establishes the authoritative repository root source of truth for runtime and tool version pins
  (`python`, `node`, `ansible_core`, `neovim_min`) required by downstream consumers.
- **Step Type:** INFRASTRUCTURE
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Defining authoritative versions in a simple JSON document at repository root allows
  automated tools, shell scripts, Python wizards, and manifest tests to query and enforce consistent version constraints
  without manual synchronization across disparate files.
- **Learning target:** Verify schema simplicity and JSON parse compatibility across python, jq, and shell tooling.
- **Maximum acceptable cost for this learning:** 0.2

### Intent & Git Integration

- **Step Intent:** Create `versions.json` at repo root defining authoritative versions:
  `{"python": "3.13", "node": "26.13.1", "ansible_core": "2.22", "neovim_min": "0.12"}`.
- **Git branch:**
  `I-1794892256-align-versions/P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium/E-1-create-versions-json/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Create `versions.json` at repo root.
2. Structure the JSON object with the required string key-value mappings: `python` set to `"3.13"`, `node` set to
   `"26.13.1"`, `ansible_core` set to `"2.22"`, and `neovim_min` set to `"0.12"`.
3. Format with 2-space indentation and trailing newline for clean git diffs and Prettier compatibility.
4. Verify JSON validity using python `json.load`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification),
  `holon-config/world/ruleset.md` §2 (Assertion over hope), `holon-config/world/constraints.md` §3 (Environment mutation
  boundaries).
- **Potential failure modes for this step:** Malformed JSON syntax or schema key mismatches.
- **Guardrails and early‑abort checks:** Ensure valid JSON syntax parseable by standard library `json` module.

### Success & Discard Criteria

- **Success:** `versions.json` exists at the repo root and parses cleanly into the dictionary with keys `python`,
  `node`, `ansible_core`, and `neovim_min`.
- **Discard:** Missing file or invalid JSON syntax.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 1.00  |
| entropy_pred        | 0.01  |
| impact_pred         | 90.0  |
| cost_pred           | 0.2   |
| learning_value_pred | 1.0   |
| ev_pred             | 90.30 |

Calculated via: `EV = 1.00 * 90.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.2 = 90.0 + 0.5 - 0.003 - 0.2 = 90.297 ~ 90.30`.

---

## Step 2: Align Consumers Across Configurations and Tooling

- **Sub‑intent recommendation:** NO
- **Reasoning:** Directly aligns existing consumers (`ansible/group_vars/all.yml`,
  `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`, `scripts/devenv_wizard.py`, `Makefile`, and
  `.github/workflows/test-hygiene.yml`) with the authoritative pins defined in `versions.json`.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Synchronizing version pins across Ansible variables, Fish shell configuration, setup
  wizards, Makefile rules, and CI workflow configurations eliminates configuration drift and ensures all tools operate
  against identical runtime versions.
- **Learning target:** Verify how `scripts/devenv_wizard.py` gracefully loads `versions.json` while maintaining
  backwards-compatible fallbacks if the file is absent.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** Ensure `Makefile`, `ansible/group_vars/all.yml`, `dotfiles/fish/.../00-devenv.fish`,
  `scripts/devenv_wizard.py`, and GitHub workflows (`test-hygiene.yml`, etc.) read or align with `versions.json`.
- **Git branch:**
  `I-1794892256-align-versions/P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium/E-2-align-version-consumers/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. In `scripts/devenv_wizard.py`, add logic to inspect `versions.json` located at the repository root (relative to the
   script directory) to extract authoritative default versions (`python`, `node`), using them as default fallbacks when
   choices are not yet set in `choices.yml`.
2. In `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`, verify that `set -g devenv_node_default_version 26.13.1`
   matches `versions.json["node"]`.
3. In `ansible/group_vars/all.yml`, verify that `devenv_python_version: "3.13"` and `devenv_conda_env_python: "3.13"`
   match `versions.json["python"]`.
4. In `Makefile`, define `PYTHON_VERSION ?= 3.13` (optionally read from `versions.json`) and verify that conda
   environment creation uses this version pin.
5. In `.github/workflows/test-hygiene.yml`, update step `Set up Node.js` from version `20` to `26` (or `26.13.1`) to
   match `versions.json["node"]`.
6. Verify `pyproject.toml` retains `requires-python = "==3.13.*"` aligning with `versions.json["python"]`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification),
  `holon-config/world/ruleset.md` §2 (Assertion over hope), `holon-config/world/constraints.md` §3 (Environment mutation
  boundaries).
- **Potential failure modes for this step:** Broken wizard startup if `versions.json` path resolution fails when
  executed from arbitrary working directories.
- **Guardrails and early‑abort checks:** Use `Path(__file__).resolve().parent.parent / "versions.json"` with try/except
  fallback to existing defaults in `devenv_wizard.py`.

### Success & Discard Criteria

- **Success:** All consumer files reflect the authoritative versions (`python: 3.13`, `node: 26.13.1`,
  `ansible_core: 2.22`, `neovim_min: 0.12`) and `scripts/devenv_wizard.py` runs without error.
- **Discard:** Discrepancies between `versions.json` and consumer files.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.03  |
| impact_pred         | 92.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 2.0   |
| ev_pred             | 91.57 |

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 2.0 - 0.3 * 0.03 - 0.5 = 91.08 + 1.0 - 0.009 - 0.5 = 91.571 ~ 91.57`.

---

## Step 3: Fix Breaking Command `make lint` in `Makefile`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Resolves broken `make lint` execution by prioritizing `uv run --extra test ansible-lint` when `uv` is
  present (matching the modern behavior of `make test`), and providing a robust fallback for conda installations where
  `PATH="$(dir $(LINT)):$$PATH"` prevents CLI and Python module version mismatches.
- **Step Type:** BUGFIX
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Running `ansible-lint` through `uv run --extra test ansible-lint` ensures hermetic
  dependencies locked in `pyproject.toml` / `uv.lock`, while prepending `$(dir $(LINT))` to `PATH` under the Conda
  fallback prevents invoking a mismatched system `ansible-lint` binary or Python interpreter.
- **Learning target:** Confirm that `make lint` completes cleanly with 0 violations across both uv-managed environments
  and conda-managed environments.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** In `Makefile`, update `lint:` to check `command -v uv >/dev/null 2>&1` and run
  `uv run --extra test ansible-lint` when available (mirroring `make test`), falling back to conda with
  `PATH="$(dir $(LINT)):$$PATH"` so CLI and python module versions match.
- **Git branch:**
  `I-1794892256-align-versions/P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium/E-3-fix-make-lint-recipe/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `Makefile` at the `lint:` target recipe.
2. Replace the static check and invocation with a branch checking `command -v uv >/dev/null 2>&1`.
3. If `uv` is installed, run `$(ANSIBLE_ENV) uv run --extra test ansible-lint ansible/site.yml` (passing
   `ansible/site.yml` and collections environment).
4. In the `else` branch, verify `[ -x "$(LINT)" ]` (or output the error message asking to run `make bootstrap`).
5. Execute the Conda fallback with `PATH="$(dir $(LINT)):$$PATH" $(ANSIBLE_ENV) "$(LINT)" ansible/site.yml` within
   `$(SELF_DIR)`.
6. Ensure GNU Make 3.81 compatibility (no non-standard GNU Make extensions).
7. Test the updated target by executing `make lint`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification),
  `holon-config/world/ruleset.md` §2 (Assertion over hope, no .ONESHELL), `holon-config/world/constraints.md` §3
  (Environment mutation boundaries).
- **Potential failure modes for this step:** Syntax error in Makefile shell script lines or missing environment
  variables (`ANSIBLE_ENV`).
- **Guardrails and early‑abort checks:** Ensure tab indentation for Makefile recipes and test execution in both
  environments where `uv` is and is not on path.

### Success & Discard Criteria

- **Success:** `make lint` runs successfully and executes `uv run --extra test ansible-lint` when `uv` is present, or
  conda fallback when absent.
- **Discard:** `make lint` fails due to binary/module path mismatches or syntax errors.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 94.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 2.0   |
| ev_pred             | 93.55 |

Calculated via: `EV = 0.99 * 94.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.5 = 93.06 + 1.0 - 0.006 - 0.5 = 93.554 ~ 93.55`.

---

## Step 4: Fix Breaking Assertion in `ansible/roles/neovim/tasks/main.yml`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Replaces invalid Jinja string method calls `.regex_replace(...)` (which cause runtime template errors
  in Ansible) with standard Ansible filter `| regex_replace(...)` and the built-in version test
  `is version('0.12', '>=')`.
- **Step Type:** BUGFIX
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Standardizing on Ansible's official `version` test operator eliminates Jinja template
  evaluation failures and correctly verifies whether the installed Neovim version satisfies the minimum requirement for
  `vim.pack()` and `nvim-pack-lock.json`.
- **Learning target:** Confirm that Neovim version assertions pass seamlessly across semver variants (e.g. `0.12.0`,
  `0.12.1`, `0.13.0-dev`).
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** In `TASK [neovim : Assert Neovim is new enough for vim.pack and nvim-pack-lock.json]`, replace
  invalid `.regex_replace(...)` method calls with Ansible's standard `is version('0.12', '>=')`:
  - `- devenv_nvim_version.stdout_lines[0] is match('NVIM v')`
  - `- devenv_nvim_version.stdout_lines[0] | regex_replace('^NVIM v', '') is version('0.12', '>=')`
- **Git branch:**
  `I-1794892256-align-versions/P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium/E-4-fix-neovim-assertion/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/roles/neovim/tasks/main.yml`.
2. Locate the task named `Assert Neovim is new enough for vim.pack and nvim-pack-lock.json`.
3. In the `that:` condition list, preserve `- devenv_nvim_version.stdout_lines[0] is match('NVIM v')`.
4. Remove the two broken conditions invoking `.regex_replace('^NVIM v(\\d+)...')`.
5. Add the standard Ansible version test:
   `- devenv_nvim_version.stdout_lines[0] | regex_replace('^NVIM v', '') is version('0.12', '>=')`.
6. Preserve the `fail_msg`, `quiet: true`, and `when:` conditional.
7. Run jinja templating evaluation or ansible-lint to ensure valid syntax.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification),
  `holon-config/world/ruleset.md` §2 (Assertion over hope, Ansible conventions), `holon-config/world/constraints.md` §3
  (Environment mutation boundaries).
- **Potential failure modes for this step:** Regexp stripping non-matching prefixes or malformed version string syntax.
- **Guardrails and early‑abort checks:** Guard condition `is match('NVIM v')` precedes the version comparison.

### Success & Discard Criteria

- **Success:** The assertion uses `| regex_replace('^NVIM v', '') is version('0.12', '>=')` and evaluates without Jinja
  runtime method errors.
- **Discard:** Retaining `.regex_replace(...)` method call syntax.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 1.00  |
| entropy_pred        | 0.02  |
| impact_pred         | 95.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 2.0   |
| ev_pred             | 95.69 |

Calculated via: `EV = 1.00 * 95.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.3 = 95.0 + 1.0 - 0.006 - 0.3 = 95.694 ~ 95.69`.

---

## Step 5: Fix Breaking Check-Mode in `ansible/roles/node/tasks/main.yml`

- **Sub‑intent recommendation:** NO
- **Reasoning:** In dry-run `--check` mode on fresh machines, directory creation tasks report changes without creating
  directories on disk; downstream tasks requiring the directory immediately fail unless `check_mode: false` is
  explicitly set on directory creation.
- **Step Type:** BUGFIX
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Setting `check_mode: false` on `TASK [node : Ensure the fisher path exists]` guarantees
  the destination directory exists during `make check-mode` and `make doctor`, allowing downstream tasks like `get_url`
  to inspect and check destination state without failing.
- **Learning target:** Confirm that dry-run invocations (`ansible-playbook --check`) execute cleanly on fresh
  environments without unexpected missing directory errors.
- **Maximum acceptable cost for this learning:** 0.2

### Intent & Git Integration

- **Step Intent:** In `ansible/roles/node/tasks/main.yml`, add `check_mode: false` to
  `TASK [node : Ensure the fisher path exists]` so dry-run `--check` mode (`make check-mode`, `make doctor`) does not
  fail downstream `get_url` on fresh machines.
- **Git branch:**
  `I-1794892256-align-versions/P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium/E-5-fix-node-check-mode/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/roles/node/tasks/main.yml`.
2. Locate the task `Ensure the fisher path exists (plugin payloads stay out of the repo)`.
3. Add `check_mode: false` directly to the task specification.
4. Verify YAML formatting and indentation.
5. Run linting to confirm task validity.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification),
  `holon-config/world/ruleset.md` §2 (Assertion over hope, Ansible conventions), `holon-config/world/constraints.md` §3
  (Environment mutation boundaries).
- **Potential failure modes for this step:** Misidentifying task or improper indentation breaking YAML parse.
- **Guardrails and early‑abort checks:** Validate with `ansible-lint` and `yaml.safe_load`.

### Success & Discard Criteria

- **Success:** The fisher directory creation task includes `check_mode: false`.
- **Discard:** Omission of `check_mode: false` on the directory task.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 1.00  |
| entropy_pred        | 0.01  |
| impact_pred         | 94.0  |
| cost_pred           | 0.2   |
| learning_value_pred | 1.0   |
| ev_pred             | 94.30 |

Calculated via: `EV = 1.00 * 94.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.2 = 94.0 + 0.5 - 0.003 - 0.2 = 94.297 ~ 94.30`.

---

## Step 6: Automated Manifest Tests and Comprehensive Verification

- **Sub‑intent recommendation:** NO
- **Reasoning:** Enforces regression prevention by embedding assertions in `tests/test_manifest.py` to continuously
  validate `versions.json` integrity, cross-consumer version synchronization, Neovim assertion syntax, and `make lint`
  recipe compatibility.
- **Step Type:** TESTING
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Automated manifest assertions prevent future version drift across files and verify that
  critical Makefile and Ansible fixes remain intact across PRs and CI workflows.
- **Learning target:** Ensure test coverage comprehensively touches all modified components without introducing false
  positives.
- **Maximum acceptable cost for this learning:** 0.8

### Intent & Git Integration

- **Step Intent:** Add automated tests in `tests/test_manifest.py` verifying version alignment across `versions.json`,
  `00-devenv.fish`, `devenv_wizard.py`, `pyproject.toml`, and `Makefile`; verify Neovim assertion syntax and `make lint`
  recipe structure; run full suite verification (`make test`, `make lint`, `make check`, `ruff check .`).
- **Git branch:**
  `I-1794892256-align-versions/P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium/E-6-tests-and-validation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_manifest.py`.
2. Add a test verifying `versions.json` exists at repository root, is valid JSON, and defines the authoritative keys
   `python`, `node`, `ansible_core`, and `neovim_min`.
3. Add a test asserting that `versions.json["node"]` matches the pin in
   `dotfiles/fish/.config/fish/conf.d/00-devenv.fish` and the fallback in `scripts/devenv_wizard.py`.
4. Add a test asserting that `versions.json["python"]` matches `pyproject.toml`, `ansible/group_vars/all.yml`, and
   `Makefile`.
5. Add a test verifying `ansible/roles/neovim/tasks/main.yml` uses `is version('0.12', '>=')` and does not contain
   `.regex_replace`.
6. Add a test verifying `Makefile`'s `lint:` target checks for `command -v uv` and includes
   `uv run --extra test ansible-lint`.
7. Add a test verifying `ansible/roles/node/tasks/main.yml` includes `check_mode: false` on the fisher directory
   creation task.
8. Execute `uv run pytest tests/test_manifest.py`.
9. Execute full test suite `make test`.
10. Execute `make lint` and `ruff check .`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Runtime & environment specification),
  `holon-config/world/ruleset.md` §2 (Assertion over hope), `holon-config/world/ruleset.md` §3 (Testing constraints),
  `holon-config/world/constraints.md` §3 (Environment mutation boundaries).
- **Potential failure modes for this step:** Broken test assertions or syntax regressions.
- **Guardrails and early‑abort checks:** Run `pytest` directly to verify assertions pass cleanly.

### Success & Discard Criteria

- **Success:** All new tests pass, `make test`, `make lint`, and `ruff check .` exit with 0 errors.
- **Discard:** Test failures or regression in linting.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.03  |
| impact_pred         | 95.0  |
| cost_pred           | 0.8   |
| learning_value_pred | 3.0   |
| ev_pred             | 94.74 |

Calculated via: `EV = 0.99 * 95.0 + 0.5 * 3.0 - 0.3 * 0.03 - 0.8 = 94.05 + 1.5 - 0.009 - 0.8 = 94.741 ~ 94.74`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from composite high confidence across all six steps. Each step addresses a
  well-isolated configuration, syntax, or recipe issue with unambiguous failure mechanisms and standard upstream
  solutions.
- **entropy_pred**: 0.12. Calculated as the cumulative sum of step entropies across all steps
  (`0.01 + 0.03 + 0.02 + 0.02 + 0.01 + 0.03 = 0.12`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 95.0. Establishes a single authoritative version manifest for the dev-env repository, unblocks
  breaking linter commands across uv and conda toolchains, resolves fatal syntax failures in Neovim version assertions,
  and enables clean dry-run `--check` execution on fresh systems.
- **cost_pred**: 2.5. Calculated as the direct sum of individual step costs (`0.2 + 0.5 + 0.5 + 0.3 + 0.2 + 0.8 = 2.5`).
- **learning_value_pred**: 5.0. Reflects the value of introducing unified manifest validation patterns in
  `tests/test_manifest.py` ensuring permanent alignment across multi-language tooling (Python, Make, Ansible, Fish).
- **ev_pred**: 94.01. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 95.0 + 0.5 * 5.0 - 0.3 * 0.12 - 2.5 = 94.05 + 2.5 - 0.036 - 2.5 = 94.014 ~ 94.01`.

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
  - `Makefile` portability regression: Ensure no `.ONESHELL` or non-standard GNU Make 3.81 extensions are introduced.
  - Ansible syntax issues: Replacing `.regex_replace(...)` with filter `| regex_replace(...)` and version test
    `is version('0.12', '>=')` avoids Jinja template evaluation failures.
  - Markdown formatting drift: Arithmetic expressions enclosed in backticks ensure single-pass Prettier formatting
    convergence.
- **Mitigations built into the plan:**
  - Deterministic version centralizations under `versions.json`.
  - Comprehensive unit testing in `tests/test_manifest.py` validating all changes.
  - Multi-tier validation via `make test`, `make lint`, and `ruff check .`.
- **Residual risk accepted (and why):**
  - Residual risk is minimal because all edits are backward-compatible, standardizing existing syntax without altering
    core environment semantics.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.12
- **Budget Compliance:** The plan entropy of 0.12 is well below the budget limit (`0.12 <= 10.0`).

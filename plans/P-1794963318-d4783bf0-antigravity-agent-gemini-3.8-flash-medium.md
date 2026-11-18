# Plan for I-1794963302-inject-ca

- **Plan ID:** P-1794963318-d4783bf0-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794963302-inject-ca
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-18T00:56:00Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses injecting custom CA certificates (such as enterprise
  intercepting proxy or root tenant certificates) from `/usr/local/share/ca-certificates` into Conda's `cacert.pem`
  bundle during `make bootstrap` and Ansible convergence:
  1. Inject custom certificates into `$(CONDA_DIR)/ssl/cacert.pem` before `conda install` and `ansible-galaxy` in
     `Makefile`.
  2. Implement idempotent CA synchronization in Ansible's `conda` role (`ansible/roles/conda/tasks/main.yml`) for
     Debian/Ubuntu hosts.
  3. Enforce invariants with unit tests in `tests/test_toolchain.py` and run quality gates (`pytest`, `ruff`,
     `ansible-lint`, `prettier`, `make check`).
- **Exploration stance:** Focused exploit across `Makefile`, Ansible conda role tasks, and pytest unit assertions.
- **Safety priority level:** standard
- **Priority Justification:** Adheres strictly to `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81
  compatibility, no hardcoded paths), §2 (Assertion over hope, single-pass Prettier formatting with backtick arithmetic
  spans, idempotent certificate operations), §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic configuration refinements, shell logic enhancements within Make,
  idempotent Ansible tasks, and invariant assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.05  |
| impact_pred         | 92.0  |
| cost_pred           | 1.1   |
| learning_value_pred | 4.0   |
| ev_pred             | 91.05 |

---

## Step 1: Pre-Ansible CA Auto-Injection in Makefile

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped, deterministic enhancement within the `Makefile` `bootstrap` recipe to inject custom root/tenant
  certificates into Conda's SSL bundle prior to invoking network-dependent Conda package installs or Ansible Galaxy
  collection downloads.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Scanning `/usr/local/share/ca-certificates` for `.crt` and `.pem` files, extracting the
  first non-header certificate body line as a duplicate check pattern, and appending missing certificates to
  `$(CONDA_DIR)/ssl/cacert.pem` with a `# Custom CA: <filename>` comment header allows cold bootstrap to succeed behind
  enterprise TLS interception proxies without breaking GNU Make 3.81 compatibility.
- **Learning target:** Verify POSIX-compatible certificate extraction and duplicate-check logic in GNU Make 3.81 recipes
  without requiring external Python or Bash dependencies.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Add automated, idempotent CA certificate injection to `Makefile` `bootstrap` target.
- **Git branch:**
  `I-1794963302-inject-ca/P-1794963318-d4783bf0-antigravity-agent-gemini-3.8-flash-medium/E-1-makefile-ca-injection/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `Makefile`.
2. Inspect the `bootstrap:` recipe.
3. Insert pre-network CA injection logic before `$(CONDA) install` and `$(GALAXY) collection install`:
   - Check if the directory `/usr/local/share/ca-certificates` exists and `$(CONDA_DIR)/ssl/cacert.pem` exists.
   - For each candidate file in `/usr/local/share/ca-certificates/*.crt` and `/usr/local/share/ca-certificates/*.pem`:
     - Verify that the candidate is a regular file (`[ -f "$$f" ]`) to guard against unmatched shell glob literals.
     - Extract the first certificate body line as the duplicate check pattern by filtering out lines starting with `-`
       (e.g., `-----BEGIN CERTIFICATE-----`) or empty lines, and selecting the first line (`head -n 1`).
     - If the pattern is non-empty, test whether it already exists in `$(CONDA_DIR)/ssl/cacert.pem` using `grep -F -q`.
     - If the pattern is not found, append a header `# Custom CA: <filename>` followed by the certificate contents to
       `$(CONDA_DIR)/ssl/cacert.pem`.
4. Ensure the CA check runs both after initial Conda creation (e.g., micromamba create / brew install) and before any
   subsequent Conda install or Ansible Galaxy collection install command in the recipe.
5. Maintain strict GNU Make 3.81 compatibility: use tab indentation, POSIX `sh` syntax, escaped dollar signs (`$$`), and
   avoid `.ONESHELL` or GNU Make extensions.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: GNU Make 3.81 compliant, no
  `.ONESHELL`, no `$(file ...)`, no `!=`), `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** Shell glob literals when no `.crt` or `.pem` exists; empty pattern
  extraction causing false positives; or permission errors when modifying `cacert.pem`.
- **Guardrails and early‑abort checks:** Guard with `[ -f "$$f" ]` to skip unmatched globs; ensure pattern is non-empty
  before grep (`[ -n "$$pattern" ]`); and verify writable or existing `$(CONDA_DIR)/ssl/cacert.pem`.

### Success & Discard Criteria

- **Success:** Running `make bootstrap` checks `/usr/local/share/ca-certificates` and idempotently appends unmerged
  certificates to `$(CONDA_DIR)/ssl/cacert.pem` before calling `conda install` or `ansible-galaxy collection install`.
- **Discard:** Syntax error under GNU Make 3.81 or duplicate certificate additions on repeated runs.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 2.0   |
| ev_pred             | 90.75 |

Calculated via: `EV = 0.98 * 92.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.4 = 90.16 + 1.0 - 0.006 - 0.4 = 90.754 ~ 90.75`.

---

## Step 2: Idempotent CA Sync in Ansible Conda Role

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped additions to `ansible/roles/conda/tasks/main.yml` ensuring idempotent discovery of custom
  certificates in `/usr/local/share/ca-certificates/*.crt` on Debian/Ubuntu systems and appending them to
  `{{ devenv_conda_root | default(devenv_conda_dir) }}/ssl/cacert.pem`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Utilizing `ansible.builtin.stat` and `ansible.builtin.find` to discover custom CA
  certificates under `/usr/local/share/ca-certificates`, reading certificate contents, and applying
  `ansible.builtin.blockinfile` or idempotent insertion into Conda's SSL certificate bundle ensures zero changes on
  subsequent runs and conforms strictly to Ansible and `ansible-lint` standards.
- **Learning target:** Verify declarative, idempotent certificate injection across Ansible convergence on Debian/Ubuntu.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Add idempotent custom CA certificate discovery and injection tasks to the Conda Ansible role.
- **Git branch:**
  `I-1794963302-inject-ca/P-1794963318-d4783bf0-antigravity-agent-gemini-3.8-flash-medium/E-2-ansible-ca-sync/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/roles/conda/tasks/main.yml`.
2. Ensure variable alias `devenv_conda_root` is established or defaults to `devenv_conda_dir`
   (`"{{ devenv_conda_root | default(devenv_conda_dir) }}"`).
3. Add a section of tasks dedicated to custom CA certificate synchronization:
   - Check if `/usr/local/share/ca-certificates` exists using `ansible.builtin.stat`.
   - Check if `{{ devenv_conda_root | default(devenv_conda_dir) }}/ssl/cacert.pem` exists using `ansible.builtin.stat`.
   - When both the CA certificates directory and Conda `cacert.pem` exist:
     - Search for `*.crt` files in `/usr/local/share/ca-certificates` using `ansible.builtin.find`.
     - Read the content of each discovered certificate file using `ansible.builtin.slurp`.
     - For each certificate, insert its content into
       `{{ devenv_conda_root | default(devenv_conda_dir) }}/ssl/cacert.pem` using `ansible.builtin.blockinfile` with a
       deterministic marker: `# {mark} ANSIBLE MANAGED BLOCK: Custom CA {{ item.path | basename }}`.
     - Alternatively, check if the certificate body or fingerprint is already in `cacert.pem` and append with
       `# Custom CA: <filename>` comment header.
4. Set appropriate task conditionals: restrict execution or discovery to Linux systems where
   `/usr/local/share/ca-certificates` exists.
5. Verify Ansible best practices:
   - Use FQCN on all modules (`ansible.builtin.stat`, `ansible.builtin.find`, `ansible.builtin.slurp`,
     `ansible.builtin.blockinfile`).
   - Use `ansible_facts["..."]` formatting for facts.
   - Ensure proper `changed_when` or let `blockinfile` manage idempotent state reporting.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Ansible Style: FQCN, Idempotence, Assertion over Hope),
  `holon-config/world/ruleset.md` §1 (Multi-OS rule: do not break macOS where `/usr/local/share/ca-certificates` does
  not exist).
- **Potential failure modes for this step:** Target `cacert.pem` file not existing yet, or directory missing on macOS /
  non-Debian Linux distributions.
- **Guardrails and early‑abort checks:** Use `ansible.builtin.stat` to verify file existence before attempting slurp or
  blockinfile modifications, guarding with `when: ...stat.exists`.

### Success & Discard Criteria

- **Success:** Custom certificates in `/usr/local/share/ca-certificates` are synchronized to `cacert.pem` during Ansible
  convergence, reporting changes only when newly added, and 0 changes on re-run.
- **Discard:** Ansible syntax errors, `ansible-lint` failures, or non-idempotent convergence.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 90.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 1.5   |
| ev_pred             | 88.54 |

Calculated via: `EV = 0.98 * 90.0 + 0.5 * 1.5 - 0.3 * 0.02 - 0.4 = 88.20 + 0.75 - 0.006 - 0.4 = 88.544 ~ 88.54`.

---

## Step 3: Verification & Invariant Tests

- **Sub‑intent recommendation:** NO
- **Reasoning:** Add unit test coverage in `tests/test_toolchain.py` verifying that the `Makefile` bootstrap target
  contains idempotent CA injection logic, and run the mandatory validation suite.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Adding invariant tests for CA injection logic in `tests/test_toolchain.py` ensures
  against regressions, while running `pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check` confirms complete
  codebase integrity.
- **Learning target:** Confirm full automated test suite and linter convergence across all modified files.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Add CA injection unit test in `tests/test_toolchain.py` and run repository quality checks.
- **Git branch:**
  `I-1794963302-inject-ca/P-1794963318-d4783bf0-antigravity-agent-gemini-3.8-flash-medium/E-3-tests-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_toolchain.py`.
2. Add a new unit test function `test_makefile_bootstrap_ca_injection()`:
   - Read `Makefile` via `read(REPO_ROOT / "Makefile")`.
   - Slice out the `bootstrap:` recipe.
   - Assert that `/usr/local/share/ca-certificates` is probed.
   - Assert that `$(CONDA_DIR)/ssl/cacert.pem` existence is checked.
   - Assert that duplicate detection pattern extraction and `# Custom CA:` comment header are present.
3. Run the complete test suite: `uv run --extra test pytest -m "not network"`.
4. Run static linting: `uv run ruff check .`.
5. Run Ansible linting: `uv run --extra test ansible-lint ansible/site.yml`.
6. Run Prettier documentation check: `npx prettier --check "**/*.md"`.
7. Run repository check: `make check`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Markdown & Docs: backtick spans for arithmetic), §3 (Testing
  Constraints).
- **Potential failure modes for this step:** Prettier formatting discrepancies or regex mismatch in tests.
- **Guardrails and early‑abort checks:** Format documents with `npx prettier --write` if needed and verify backtick
  formatting.

### Success & Discard Criteria

- **Success:** Unit tests assert `Makefile` CA injection logic, and all verification commands (`pytest`, `ruff`,
  `ansible-lint`, `prettier`, `make check`) exit cleanly with code 0.
- **Discard:** Test failures or linter violations.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 91.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 1.0   |
| ev_pred             | 90.29 |

Calculated via: `EV = 0.99 * 91.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.3 = 90.09 + 0.5 - 0.003 - 0.3 = 90.287 ~ 90.29`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.98. Derived from composite high confidence across all three steps. Each step addresses a
  modular, well-scoped domain with clear verification contracts: POSIX-compliant shell logic in `Makefile` compatible
  with GNU Make 3.81, declarative Ansible role tasks using built-in FQCN modules, and regression test assertions in
  `tests/test_toolchain.py`.
- **entropy_pred**: 0.05. Calculated as the cumulative sum of step entropies across all three steps
  (`0.02 + 0.02 + 0.01 = 0.05`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 92.0. Resolves network and TLS handshake failures when running `make bootstrap` or `make converge` in
  enterprise or container environments with custom/corporate CA certificates in `/usr/local/share/ca-certificates`,
  ensuring both pre-Ansible and Ansible convergence stages have trusted Conda TLS bundles.
- **cost_pred**: 1.1. Calculated as the direct sum of individual step costs (`0.4 + 0.4 + 0.3 = 1.1`).
- **learning_value_pred**: 4.0. Validates repeatable patterns for handling corporate proxy/tenant certificates across
  both Makefile bootstrap scripts and Ansible playbooks without introducing third-party script dependencies.
- **ev_pred**: 91.05. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.98 * 92.0 + 0.5 * 4.0 - 0.3 * 0.05 - 1.1 = 90.16 + 2.0 - 0.015 - 1.1 = 91.045 ~ 91.05`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: do not assume `/usr/local/share/ca-certificates` exists on
    Darwin; guard with existence checks).
  - `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: must stay compatible with GNU Make 3.81; no `.ONESHELL`,
    no `$(file ...)`, no `!=`, no `.RECIPEPREFIX`).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: single-pass Prettier formatting with backtick
    code spans for arithmetic expressions, assertion over hope, FQCN in Ansible).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, no unauthorized
    writes).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Missing `/usr/local/share/ca-certificates` or `cacert.pem`: Handled safely by conditional directory and file
    existence checks before any processing.
  - Glob literals matching nothing: Handled by checking `[ -f "$$f" ]` inside loops.
  - Duplicate certificate entries: Prevented by inspecting the first non-header body line of each certificate before
    appending.
- **Mitigations built into the plan:**
  - Standard POSIX shell branching in `Makefile` compatible with GNU Make 3.81.
  - Declarative FQCN modules in Ansible tasks with idempotence checks.
  - Unit test invariant assertions in `tests/test_toolchain.py`.
- **Residual risk accepted (and why):**
  - Minimal residual risk: all operations are additive and guarded by file existence and duplication checks.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.05
- **Budget Compliance:** The plan entropy of 0.05 is well within the budget limit (`0.05 <= 10.0`).

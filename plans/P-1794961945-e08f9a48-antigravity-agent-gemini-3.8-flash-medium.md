# Plan for I-1794961928-proxy-ssl

- **Plan ID:** P-1794961945-e08f9a48-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794961928-proxy-ssl
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-18T00:34:00Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses four interrelated areas of corporate proxy SSL
  certificate support and developer experience:
  1. Auto-detecting host system CA certificate bundles across Linux (Debian/Ubuntu and RHEL/Fedora) and macOS in
     `Makefile`, exporting standard environment variables (`SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`).
  2. Configuring `ca_cert` under `[galaxy]` in `ansible.cfg` and implementing robust retry with `--ignore-certs` in
     `Makefile` upon SSL verification failure or when `DEVENV_INSECURE_SSL=true`.
  3. Preserving or injecting `ssl_verify: <system_ca_bundle>` when `scripts/devenv_wizard.py` manages or writes
     `.condarc`.
  4. Adding automated unit tests in `tests/test_toolchain.py` and verifying toolchain invariants across pytest, ruff,
     ansible-lint, and make check.
- **Exploration stance:** Focused exploit across `Makefile`, `ansible.cfg`, `scripts/devenv_wizard.py`, and
  `tests/test_toolchain.py`.
- **Safety priority level:** standard
- **Priority Justification:** Adheres strictly to `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81
  compatibility, no hardcoded paths), §2 (Assertion over hope, single-pass Prettier formatting with backtick arithmetic
  spans), §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic configuration refinements, proxy SSL certificate compatibility
  additions, and invariant assertions across standard repository files.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.08  |
| impact_pred         | 93.0  |
| cost_pred           | 1.8   |
| learning_value_pred | 4.5   |
| ev_pred             | 91.57 |

---

## Step 1: Auto-Detect System CA Bundle in Makefile

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped, deterministic addition to `Makefile` probing host system CA certificate bundles across Linux
  and macOS and exporting standard environment variables (`SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`).
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Probing `/etc/ssl/certs/ca-certificates.crt` (Debian/Ubuntu),
  `/etc/pki/tls/certs/ca-bundle.crt` (RHEL/Fedora), and `/etc/ssl/cert.pem` (macOS) in `Makefile` and conditionally
  exporting `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`, and `CURL_CA_BUNDLE` ensures Python urllib, requests, curl, and
  downstream tools automatically trust corporate proxy certificates.
- **Learning target:** Verify multi-OS CA bundle detection without breaking GNU Make 3.81 compatibility.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Auto-detect host CA bundle in `Makefile` and export SSL environment variables.
- **Git branch:**
  `I-1794961928-proxy-ssl/P-1794961945-e08f9a48-antigravity-agent-gemini-3.8-flash-medium/E-1-autodetect-ca-bundle/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `Makefile`.
2. Define `SYSTEM_CA_BUNDLE ?=` using POSIX shell commands compatible with GNU Make 3.81:
   - Check if `/etc/ssl/certs/ca-certificates.crt` exists (Debian/Ubuntu), and if so return that path.
   - Else check if `/etc/pki/tls/certs/ca-bundle.crt` exists (RHEL/Fedora), and if so return that path.
   - Else check if `/etc/ssl/cert.pem` exists (macOS), and if so return that path.
3. If `SYSTEM_CA_BUNDLE` is non-empty (`ifneq ($(SYSTEM_CA_BUNDLE),)`):
   - Export `SSL_CERT_FILE ?= $(SYSTEM_CA_BUNDLE)`
   - Export `REQUESTS_CA_BUNDLE ?= $(SYSTEM_CA_BUNDLE)`
   - Export `CURL_CA_BUNDLE ?= $(SYSTEM_CA_BUNDLE)`
4. In `Makefile` `check:` target:
   - Add a diagnostic display line printing `system CA bundle: ok (<path>)` or
     `none detected (using default certificate store)`.
5. Ensure GNU Make 3.81 compatibility is maintained: no `.ONESHELL`, no `!=` operator, no `$(file ...)`, standard shell
   execution.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: GNU Make 3.81 compliant; Multi-OS
  rule).
- **Potential failure modes for this step:** Shell syntax errors inside `$(shell ...)` or breaking Make parsing on
  non-Debian distributions.
- **Guardrails and early‑abort checks:** Use `test -f` checks inside a single POSIX-compliant `shell` invocation with
  `elif` ladders.

### Success & Discard Criteria

- **Success:** `SYSTEM_CA_BUNDLE` discovers existing host CA certificates on Debian, Ubuntu, RHEL, Fedora, or macOS;
  exports `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`, and `CURL_CA_BUNDLE` if found; `make check` executes without syntax
  errors.
- **Discard:** Syntax error or crash during `make check`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 1.0   |
| ev_pred             | 91.27 |

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 1.0 - 0.3 * 0.02 - 0.3 = 91.08 + 0.5 - 0.006 - 0.3 = 91.274 ~ 91.27`.

---

## Step 2: Ansible Galaxy CA Configuration & Retry with Insecure Fallback

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped updates to `ansible.cfg` and `Makefile` to configure Galaxy CA certificate trust and implement
  automated insecure retry fallback for corporate SSL proxies.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Declaring `[galaxy]` with `ca_cert` in `ansible.cfg` provides Galaxy with system CA trust
  store paths, and adding fallback logic with `--ignore-certs` in `Makefile` guarantees bootstrap proceeds cleanly even
  behind restrictive corporate intercepting proxies.
- **Learning target:** Ensure `ansible-galaxy collection install` handles corporate proxy environments gracefully
  without manual developer intervention.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Configure Galaxy `ca_cert` in `ansible.cfg` and add insecure fallback retry in `Makefile`.
- **Git branch:**
  `I-1794961928-proxy-ssl/P-1794961945-e08f9a48-antigravity-agent-gemini-3.8-flash-medium/E-2-galaxy-ca-insecure-fallback/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible.cfg`.
2. Add a `[galaxy]` section:
   - Configure `ca_cert = /etc/ssl/certs/ca-certificates.crt` (or system CA bundle reference).
   - Document that galaxy honors `ca_cert` or falls back to system trust store.
3. Open `Makefile`.
4. In the `bootstrap:` recipe under the collection installation check:
   - Check if `DEVENV_INSECURE_SSL` environment variable is set to `"true"`.
   - If `DEVENV_INSECURE_SSL="true"`, execute
     `$(GALAXY) collection install --ignore-certs -p "$(COLLECTIONS)" -r "$(SELF_DIR)/ansible/requirements.yml"`.
   - If not set or `"false"`, execute standard
     `$(GALAXY) collection install -p "$(COLLECTIONS)" -r "$(SELF_DIR)/ansible/requirements.yml"`.
   - If the standard install fails (such as SSL certificate verification failure from an intercepting corporate proxy),
     display a warning:
     `ansible-galaxy collection install failed; retrying with --ignore-certs for proxy SSL fallback...` and retry with
     `--ignore-certs -p "$(COLLECTIONS)" -r "$(SELF_DIR)/ansible/requirements.yml"`.
   - If the retry fails, exit with error code 1.
5. Verify syntax and formatting of both `ansible.cfg` and `Makefile`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: POSIX shell in recipes),
  `holon-config/world/ruleset.md` §2 (Idempotence, Assertion over hope).
- **Potential failure modes for this step:** Shell quoting or compound statement syntax errors in Make recipes;
  collection directory left in partial state on unhandled abort.
- **Guardrails and early‑abort checks:** Ensure compound shell recipe uses proper parentheses/braces and line
  continuations (`\` and `;`).

### Success & Discard Criteria

- **Success:** `ansible.cfg` includes `[galaxy]` `ca_cert`; `Makefile` bootstrap recipe executes standard install and
  automatically falls back to `--ignore-certs` or honors `DEVENV_INSECURE_SSL=true`.
- **Discard:** Inability to run `make bootstrap` or broken Make recipe syntax.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 93.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 1.2   |
| ev_pred             | 91.33 |

Calculated via: `EV = 0.98 * 93.0 + 0.5 * 1.2 - 0.3 * 0.02 - 0.4 = 91.14 + 0.6 - 0.006 - 0.4 = 91.334 ~ 91.33`.

---

## Step 3: Preserve Condarc SSL Verify in Devenv Wizard

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped additions to `scripts/devenv_wizard.py` to detect host CA bundle and preserve or inject
  `ssl_verify: <system_ca_bundle>` into the repo-managed `.condarc`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Adding system CA bundle detection in `scripts/devenv_wizard.py` and checking `.condarc`
  guarantees that Conda inherits corporate CA certificates when the wizard executes, preventing SSL verification errors
  during Conda package operations.
- **Learning target:** Verify robust parsing and preservation of existing `.condarc` configuration while injecting host
  system CA bundle when missing.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Implement CA bundle detection and `ssl_verify` preservation/injection in `scripts/devenv_wizard.py`.
- **Git branch:**
  `I-1794961928-proxy-ssl/P-1794961945-e08f9a48-antigravity-agent-gemini-3.8-flash-medium/E-3-preserve-condarc-ssl-verify/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `scripts/devenv_wizard.py`.
2. Add a function `detect_system_ca_bundle() -> str | None`:
   - Probe known host paths in order: `/etc/ssl/certs/ca-certificates.crt` (Debian/Ubuntu),
     `/etc/pki/tls/certs/ca-bundle.crt` (RHEL/Fedora), `/etc/ssl/cert.pem` (macOS).
   - Return the first existing path as a string, or `None` if none exist.
3. Add a function `configure_condarc_ssl_verify(condarc_path: Path, system_ca_bundle: str | None = None) -> bool`:
   - If `condarc_path` exists, read its contents.
   - Check if `ssl_verify` is already configured in the file.
   - If `ssl_verify` already exists, preserve its existing value without overwriting.
   - If `ssl_verify` does not exist:
     - Determine the CA bundle to use (passed `system_ca_bundle` or `detect_system_ca_bundle()`).
     - If a bundle path is found, append or inject `ssl_verify: <ca_bundle>` to the condarc file.
   - Return `True` if modified or configured, `False` otherwise.
4. Integrate `configure_condarc_ssl_verify` into `run_wizard()`:
   - Call `configure_condarc_ssl_verify(repo_root / "dotfiles" / "conda" / ".condarc")` during wizard execution so the
     repo-managed `.condarc` is updated prior to Ansible stowing.
5. Ensure type annotations conform to PEP 484 and full docstrings are provided.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Python Runtime ==3.13.\*), §2 (PEP 8 Compliance, Typing
  Guidelines, Docstring Requirements).
- **Potential failure modes for this step:** Corrupting `.condarc` formatting or stripping existing comments and
  channels.
- **Guardrails and early‑abort checks:** Use non-destructive appending or line-based injection that preserves header
  comments and `channels: [conda-forge]` structure.

### Success & Discard Criteria

- **Success:** Existing `ssl_verify` values are preserved unchanged; when absent and a system CA bundle exists,
  `ssl_verify: <bundle>` is cleanly injected into `.condarc`.
- **Discard:** Syntax error in `devenv_wizard.py` or mangling of `.condarc`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 1.1   |
| ev_pred             | 90.30 |

Calculated via: `EV = 0.98 * 92.0 + 0.5 * 1.1 - 0.3 * 0.02 - 0.4 = 90.16 + 0.55 - 0.006 - 0.4 = 90.304 ~ 90.30`.

---

## Step 4: Unit Tests for CA Detection, Galaxy SSL, and Condarc SSL Verify

- **Sub‑intent recommendation:** NO
- **Reasoning:** Automated regression tests in `tests/test_toolchain.py` and `tests/test_wizard.py` to assert toolchain
  invariants, CA detection, and configuration persistence.
- **Step Type:** TESTING
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicit structural unit tests prevent regression in CA bundle detection, environment
  variable propagation, Ansible Galaxy retry fallback, and `.condarc` SSL verification preservation.
- **Learning target:** Confirm 100% test coverage and validation of corporate proxy SSL handling across `Makefile`,
  `ansible.cfg`, and `devenv_wizard.py`.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Add comprehensive unit tests in `tests/test_toolchain.py` and `tests/test_wizard.py`.
- **Git branch:**
  `I-1794961928-proxy-ssl/P-1794961945-e08f9a48-antigravity-agent-gemini-3.8-flash-medium/E-4-tests-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_toolchain.py`.
2. Add `test_makefile_system_ca_bundle_detection()`:
   - Read `Makefile`.
   - Assert `SYSTEM_CA_BUNDLE ?=` probes `/etc/ssl/certs/ca-certificates.crt`, `/etc/pki/tls/certs/ca-bundle.crt`, and
     `/etc/ssl/cert.pem`.
   - Assert `export SSL_CERT_FILE`, `export REQUESTS_CA_BUNDLE`, and `export CURL_CA_BUNDLE` are present and reference
     `SYSTEM_CA_BUNDLE`.
3. Add `test_makefile_galaxy_retry_insecure_fallback()`:
   - Read `Makefile`.
   - Assert `DEVENV_INSECURE_SSL` is checked.
   - Assert `--ignore-certs` is used as a fallback on failure and when insecure SSL is forced.
4. Add `test_ansible_cfg_galaxy_ca_cert()`:
   - Read `ansible.cfg`.
   - Assert `[galaxy]` section exists.
   - Assert `ca_cert` is configured under `[galaxy]`.
5. Open `tests/test_wizard.py`.
6. Add `test_detect_system_ca_bundle()`:
   - Test detection when Debian CA bundle exists.
   - Test fallback to RHEL CA bundle.
   - Test fallback to macOS cert.pem.
   - Test `None` returned when no bundle is present.
7. Add `test_configure_condarc_ssl_verify_inject()`:
   - Given a minimal `.condarc` with only `channels: [conda-forge]`, run
     `configure_condarc_ssl_verify(tmp_condarc, system_ca_bundle="/etc/ssl/certs/ca-certificates.crt")`.
   - Assert `ssl_verify: /etc/ssl/certs/ca-certificates.crt` is added.
8. Add `test_configure_condarc_ssl_verify_preserve()`:
   - Given a `.condarc` with existing `ssl_verify: /custom/cert.pem`, run `configure_condarc_ssl_verify`.
   - Assert `ssl_verify: /custom/cert.pem` is preserved and not overwritten.
9. Execute `uv run --extra test pytest -m "not network"` to confirm all tests pass.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing Constraints: uv run pytest as standard test runner;
  sandbox executions must declare test edits in the plan).
- **Potential failure modes for this step:** Flaky tests relying on host filesystem state rather than mock paths.
- **Guardrails and early‑abort checks:** Use `tmp_path` fixtures and `monkeypatch` for filesystem path checks in wizard
  tests.

### Success & Discard Criteria

- **Success:** All new tests pass cleanly without requiring network access; all assertions validate specified
  invariants.
- **Discard:** Failure in unit test execution.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 94.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 0.8   |
| ev_pred             | 93.06 |

Calculated via: `EV = 0.99 * 94.0 + 0.5 * 0.8 - 0.3 * 0.01 - 0.4 = 93.06 + 0.4 - 0.003 - 0.4 = 93.057 ~ 93.06`.

---

## Step 5: Full Repository Verification and Quality Gates

- **Sub‑intent recommendation:** NO
- **Reasoning:** Execute repository linters, quality gates, formatters, and pre-flight check recipes to guarantee
  complete regression-free delivery.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Running the complete suite of linters, formatters, and unit tests ensures full compliance
  with repository standards and prevents syntax or typing regressions.
- **Learning target:** Confirm full repository quality and formatting compliance across Python, Ansible, and
  documentation.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Verify repository quality gates across all touched files.
- **Git branch:**
  `I-1794961928-proxy-ssl/P-1794961945-e08f9a48-antigravity-agent-gemini-3.8-flash-medium/E-5-verification-and-quality-gates/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Run `uv run --extra test pytest -m "not network"` and ensure all unit tests pass.
2. Run `uv run ruff check .` to verify PEP 8 compliance, import discipline, and linting rules across modified Python
   files.
3. Run `make check` to verify prerequisite probing, GNU Make parsing, and CA bundle detection.
4. Run `npx prettier --check "**/*.md"` to verify single-pass Prettier formatting of all markdown documentation and plan
   files.
5. If prettier reports any discrepancies, execute `npx prettier --write "**/*.md"` and re-check.
6. Verify `git status` reports clean working directory for non-plan assets.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (PEP 8 Compliance, Markdown & Docs single-pass Prettier
  convergence with backtick arithmetic spans), §3 (Testing Constraints).
- **Potential failure modes for this step:** Prettier formatting diffs on markdown math expressions; linting errors in
  modified Python scripts.
- **Guardrails and early‑abort checks:** Format all arithmetic expressions in backtick spans before running prettier
  check.

### Success & Discard Criteria

- **Success:** `pytest`, `ruff check`, `make check`, and `prettier` pass with exit code 0.
- **Discard:** Unresolved lint or test failures.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 91.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 0.4   |
| ev_pred             | 89.99 |

Calculated via: `EV = 0.99 * 91.0 + 0.5 * 0.4 - 0.3 * 0.01 - 0.3 = 90.09 + 0.2 - 0.003 - 0.3 = 89.987 ~ 89.99`.

---

## Strategy Rationale

The overall plan metrics are derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.98. Derived from composite high confidence across all five steps. Each step addresses a modular,
  well-scoped domain with clear verification contracts: multi-OS CA bundle auto-detection and standard SSL variable
  exports in `Makefile`, Galaxy CA declaration in `ansible.cfg` and automated `--ignore-certs` retry fallback in
  `Makefile`, `ssl_verify` preservation and injection in `scripts/devenv_wizard.py`, comprehensive invariant unit tests
  in `tests/test_toolchain.py` and `tests/test_wizard.py`, and end-to-end repository quality gates.
- **entropy_pred**: 0.08. Calculated as the cumulative sum of step entropies across all five steps
  (`0.02 + 0.02 + 0.02 + 0.01 + 0.01 = 0.08`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 93.0. Directly resolves enterprise proxy SSL inspection blockages during bootstrap, collection
  downloads, and Conda environment resolution, enabling seamless corporate developer onboarding without requiring manual
  certificate installation hacks or compromised security defaults.
- **cost_pred**: 1.8. Calculated as the direct sum of individual step costs (`0.3 + 0.4 + 0.4 + 0.4 + 0.3 = 1.8`).
- **learning_value_pred**: 4.5. Reflects the cumulative value of standardizing corporate proxy SSL certificate discovery
  and fallback patterns across Make, Ansible, Python, and Conda (`1.0 + 1.2 + 1.1 + 0.8 + 0.4 = 4.5`).
- **ev_pred**: 91.57. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.98 * 93.0 + 0.5 * 4.5 - 0.3 * 0.08 - 1.8 = 91.14 + 2.25 - 0.024 - 1.8 = 91.566 ~ 91.57`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: no hardcoded system paths; probe OS facts and standard paths
    across Linux and Darwin).
  - `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: must stay compatible with GNU Make 3.81, no `.ONESHELL`,
    no `$(file ...)`, no `!=`, no `.RECIPEPREFIX`).
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
  - Insecure SSL fallback overuse: Insecure fallback with `--ignore-certs` is only activated if standard verification
    fails (or if explicitly forced via `DEVENV_INSECURE_SSL=true`), preserving secure default certificate validation
    whenever possible.
  - Custom user CA certificate locations: If a user or corporation has already configured `ssl_verify` in `.condarc`,
    `devenv_wizard.py` will preserve the existing user value without overwriting it.
  - Multi-OS path variations: Probing `/etc/ssl/certs/ca-certificates.crt` first, then
    `/etc/pki/tls/certs/ca-bundle.crt`, then `/etc/ssl/cert.pem` ensures broad coverage across Debian/Ubuntu,
    RHEL/CentOS/Fedora, and macOS.
- **Mitigations built into the plan:**
  - Standard POSIX shell conditionals in `Makefile` compatible with GNU Make 3.81.
  - Non-destructive updates in `devenv_wizard.py` protecting existing user settings.
  - Unit tests verifying both bundle injection and preservation of existing settings.
- **Residual risk accepted (and why):**
  - Minimal residual risk: all changes are non-destructive, strictly scoped to proxy SSL certificate discovery and
    fallback, and verified through unit tests and repo quality checks.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.08
- **Budget Compliance:** The plan entropy of 0.08 is well within the budget limit (`0.08 <= 10.0`).

# Plan for I-1795057633-node-extra-ca

- **Plan ID:** P-1795057650-d739e30f-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1795057633-node-extra-ca
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-19T03:07:34Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent directly addresses custom CA certificate bundling for Node.js
  environments and unified shell export across Fish, Bash, Zsh, and example snippets:
  1. Fold custom CA certificates from `/usr/local/share/ca-certificates` into
     `{{ devenv_home }}/.config/node/node-extra-ca.pem` within the `node` Ansible role
     (`ansible/roles/node/tasks/main.yml`) using `ansible.builtin.stat`, `ansible.builtin.find` (recursive),
     `ansible.builtin.slurp`, and idempotent `ansible.builtin.blockinfile` with
     `# {mark} ANSIBLE MANAGED BLOCK: Custom CA <basename>` markers.
  2. Set `NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"` across all supported shells when the file exists:
     Fish (`dotfiles/fish/.config/fish/conf.d/00-devenv.fish`), Bash (`dotfiles/bash/.bashrc`), Zsh
     (`dotfiles/zsh/.zshrc` before interactive-only early return), and `dotfiles/examples/devenv-shell-snippets.sh`.
  3. Add comprehensive unit tests in `tests/test_toolchain.py` asserting the Ansible role tasks and multi-shell parity,
     and run verification commands (`pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check`).
- **Exploration stance:** Focused exploit across Ansible role tasks, shell configurations, and unit assertions.
- **Safety priority level:** standard
- **Priority Justification:** Adheres strictly to `holon-config/world/ruleset.md` §1 (Multi-OS rule, no hardcoded paths,
  XDG conventions), §2 (Ansible style, FQCN, Idempotence, Assertion over hope, single-pass Prettier formatting with
  backtick arithmetic spans), §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic Ansible role tasks, declarative shell configurations, and test
  assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.04  |
| impact_pred         | 92.0  |
| cost_pred           | 0.90  |
| learning_value_pred | 3.0   |
| ev_pred             | 91.67 |

---

## Step 1: Fold Custom CA Certificates in Node Ansible Role

- **Sub‑intent recommendation:** NO
- **Reasoning:** Direct, well-scoped Ansible task implementation within `ansible/roles/node/tasks/main.yml`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Utilizing `ansible.builtin.stat` and `ansible.builtin.find` (with `recurse: true`) to
  discover custom CA certificates in `/usr/local/share/ca-certificates`, ensuring `{{ devenv_home }}/.config/node`
  exists, slurping each file, and injecting blocks with `ansible.builtin.blockinfile` into
  `{{ devenv_home }}/.config/node/node-extra-ca.pem` produces an idempotent, well-formed PEM bundle without throwing
  errors on macOS or hosts lacking custom certificates.
- **Learning target:** Verify multi-certificate folding pattern using `ansible.builtin.blockinfile` with `create: true`
  and per-certificate marker blocks in the Node Ansible role.
- **Maximum acceptable cost for this learning:** 0.35

### Intent & Git Integration

- **Step Intent:** Add automated CA certificate discovery, slurping, and idempotent blockinfile folding into the `node`
  Ansible role.
- **Git branch:**
  `I-1795057633-node-extra-ca/P-1795057650-d739e30f-antigravity-agent-gemini-3.8-flash-medium/E-1-ansible-node-ca-folding/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/roles/node/tasks/main.yml`.
2. Add a new task section dedicated to Node custom CA certificate folding:
   - Check if `/usr/local/share/ca-certificates` exists and is a directory using `ansible.builtin.stat`. Register
     `devenv_node_ca_certs_dir_stat`.
   - Find all `*.crt` and `*.pem` files under `/usr/local/share/ca-certificates` using `ansible.builtin.find` with
     `paths: /usr/local/share/ca-certificates`, `patterns: ["*.crt", "*.pem"]`, `file_type: file`, and `recurse: true`.
     Register `devenv_node_custom_ca_certs`. Conditionalize on `devenv_node_ca_certs_dir_stat.stat.exists` and
     `devenv_node_ca_certs_dir_stat.stat.isdir`.
   - When matching certificates are found (`devenv_node_custom_ca_certs.matched | default(0) > 0`):
     - Ensure the target directory `{{ devenv_home }}/.config/node` exists using `ansible.builtin.file` with
       `state: directory` and `mode: "0755"`.
     - Slurp each discovered certificate with `ansible.builtin.slurp` using `src: "{{ item.path }}"`, registering
       `devenv_node_custom_ca_contents`, looping over `devenv_node_custom_ca_certs.files | default([])` with
       `loop_control.label: "{{ item.path }}"`.
     - Fold each certificate into `{{ devenv_home }}/.config/node/node-extra-ca.pem` using `ansible.builtin.blockinfile`
       with `create: true`, `mode: "0644"`,
       `marker: "# {mark} ANSIBLE MANAGED BLOCK: Custom CA {{ (item.item.path | default(item.path | default(''))) | basename }}"`,
       and `block: "{{ item.content | b64decode }}"`, looping over
       `(devenv_node_custom_ca_contents.results | default([])) | selectattr('content', 'defined') | list` with
       `loop_control.label: "{{ (item.item.path | default(item.path | default(''))) | basename }}"`.
3. Adhere strictly to Ansible style guidelines:
   - Use FQCN on all modules (`ansible.builtin.stat`, `ansible.builtin.find`, `ansible.builtin.file`,
     `ansible.builtin.slurp`, `ansible.builtin.blockinfile`).
   - Use `ansible_facts` dictionary access when querying facts.
   - Maintain idempotence so repeated runs report zero unexpected mutations.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule: do not fail when
  `/usr/local/share/ca-certificates` is absent on macOS), `holon-config/world/ruleset.md` §2 (Ansible Style: FQCN,
  Idempotence, Assertion over Hope), `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** Target directory missing prior to `blockinfile` invocation; missing source
  directory failing find task; unmatched globs or empty files causing slurp/block errors.
- **Guardrails and early‑abort checks:** Guard all find and folding tasks behind stat checks; explicitly create
  `{{ devenv_home }}/.config/node` before file operations; specify `create: true` on `blockinfile`.

### Success & Discard Criteria

- **Success:** Certificates in `/usr/local/share/ca-certificates` are idempotently combined into
  `{{ devenv_home }}/.config/node/node-extra-ca.pem` with per-certificate marker blocks; task suite runs cleanly on
  hosts with and without `/usr/local/share/ca-certificates`.
- **Discard:** Ansible syntax errors, `ansible-lint` failures, or non-idempotent changes on subsequent runs.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.35  |
| learning_value_pred | 2.0   |
| ev_pred             | 91.72 |

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.35 = 91.08 + 1.00 - 0.006 - 0.35 = 91.724 ~ 91.72`.

---

## Step 2: Configure NODE_EXTRA_CA_CERTS Across Supported Shells

- **Sub‑intent recommendation:** NO
- **Reasoning:** Deterministic configuration updates across four existing shell configuration files.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Placing an existence check for `$HOME/.config/node/node-extra-ca.pem` in Fish conf.d,
  Bash (before interactive-only return), Zsh (before interactive-only return / local overrides), and reusable shell
  snippets ensures both interactive and non-interactive subshells inherit `NODE_EXTRA_CA_CERTS` whenever custom CA
  certificates are folded, without incurring warnings or performance overhead on systems without custom CAs.
- **Learning target:** Enforce multi-shell environment variable parity across POSIX and Fish shells.
- **Maximum acceptable cost for this learning:** 0.30

### Intent & Git Integration

- **Step Intent:** Export `NODE_EXTRA_CA_CERTS` in Fish, Bash, Zsh, and snippet templates when the bundle file exists.
- **Git branch:**
  `I-1795057633-node-extra-ca/P-1795057650-d739e30f-antigravity-agent-gemini-3.8-flash-medium/E-2-shell-node-extra-ca-export/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`:
   - Locate the Node/NVM configuration section.
   - Add a test checking if `$HOME/.config/node/node-extra-ca.pem` exists (`test -f`).
   - If present, set global exported variable `NODE_EXTRA_CA_CERTS` to `"$HOME/.config/node/node-extra-ca.pem"` using
     `set -gx`.
2. Open `dotfiles/bash/.bashrc`:
   - Locate the Node/NVM environment section prior to the interactive-only early return
     (`case $- in *i*) ;; *) return;; esac`).
   - Add a shell conditional checking if `[ -f "$HOME/.config/node/node-extra-ca.pem" ]`.
   - If present, export `NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"`.
3. Open `dotfiles/zsh/.zshrc`:
   - Locate the Node/NVM environment section prior to interactive hooks.
   - Add a shell conditional checking if `[ -f "$HOME/.config/node/node-extra-ca.pem" ]`.
   - If present, export `NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"`.
4. Open `dotfiles/examples/devenv-shell-snippets.sh`:
   - Add a dedicated snippet block (e.g., Block F: Custom Node Extra CA Bundle) documenting and implementing the
     conditional export of `NODE_EXTRA_CA_CERTS="$HOME/.config/node/node-extra-ca.pem"`.
5. Ensure clean indentation, comments, and adherence to repository conventions.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, Multi-Variant Stow Packaging),
  `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: edits restricted to declared dotfile paths).
- **Potential failure modes for this step:** Placing the export after interactive-only early returns in `.bashrc` or
  `.zshrc`, preventing non-interactive tools or scripts from discovering the CA bundle; or syntax incompatibilities
  between Fish and POSIX shells.
- **Guardrails and early‑abort checks:** Explicitly place exports in non-interactive prelude sections of `.bashrc` and
  `.zshrc`; use native Fish syntax (`test -f`, `set -gx`) in `00-devenv.fish`.

### Success & Discard Criteria

- **Success:** Fish, Bash, Zsh, and snippet configurations all conditionally export `NODE_EXTRA_CA_CERTS` when
  `$HOME/.config/node/node-extra-ca.pem` exists.
- **Discard:** Syntax error when sourcing shell configs, or export placed after early-exit guards.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 90.0  |
| cost_pred           | 0.30  |
| learning_value_pred | 1.5   |
| ev_pred             | 89.55 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.5 - 0.3 * 0.01 - 0.30 = 89.10 + 0.75 - 0.003 - 0.30 = 89.547 ~ 89.55`.

---

## Step 3: Implement Unit Tests and Execute Verification Suite

- **Sub‑intent recommendation:** NO
- **Reasoning:** Invariant assertions in `tests/test_toolchain.py` and execution of standard repository verification
  targets.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Unit tests asserting the presence and structure of the CA folding tasks in `node` tasks
  and the presence of `NODE_EXTRA_CA_CERTS` logic across all shell dotfiles ensure invariants are maintained and prevent
  regressions, while the full check suite (`pytest`, `ruff`, `ansible-lint`, `prettier`, `make check`) confirms overall
  repository health.
- **Learning target:** Codify regression tests for Node custom CA handling and multi-shell configuration parity.
- **Maximum acceptable cost for this learning:** 0.25

### Intent & Git Integration

- **Step Intent:** Add test functions to `tests/test_toolchain.py` and run quality verification gates.
- **Git branch:**
  `I-1795057633-node-extra-ca/P-1795057650-d739e30f-antigravity-agent-gemini-3.8-flash-medium/E-3-tests-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_toolchain.py`.
2. Add a new test function `test_node_ansible_role_ca_folding()`:
   - Read `ansible/roles/node/tasks/main.yml`.
   - Assert presence of `/usr/local/share/ca-certificates`.
   - Assert presence of `node-extra-ca.pem`.
   - Assert presence of `ansible.builtin.blockinfile`.
   - Assert presence of `recurse: true` (or `recurse: yes` / `recurse: True`).
   - Assert presence of `# {mark} ANSIBLE MANAGED BLOCK: Custom CA` marker format.
3. Add a new test function `test_multishell_node_extra_ca_certs_parity()`:
   - Read `dotfiles/bash/.bashrc`.
   - Read `dotfiles/zsh/.zshrc`.
   - Read `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
   - Read `dotfiles/examples/devenv-shell-snippets.sh`.
   - Assert `NODE_EXTRA_CA_CERTS` and `.config/node/node-extra-ca.pem` are present in all four files.
   - Assert `export NODE_EXTRA_CA_CERTS=` is in `.bashrc`, `.zshrc`, and `devenv-shell-snippets.sh`.
   - Assert `set -gx NODE_EXTRA_CA_CERTS` is in `00-devenv.fish`.
4. Run comprehensive repository verification commands:
   - `uv run --extra test pytest -m "not network"`
   - `uv run ruff check .`
   - `uv run --extra test ansible-lint ansible/site.yml`
   - `npx prettier --check "**/*.md"`
   - `make check`

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing Constraints: all test modifications explicitly
  declared in plan), `holon-config/world/ruleset.md` §2 (Assertion over hope).
- **Potential failure modes for this step:** Test assertion mismatch due to formatting differences or regex strictness;
  linter warnings on YAML or Python formatting.
- **Guardrails and early‑abort checks:** Use clear, resilient assertions matching canonical tokens; run linters locally
  to verify compliance before finishing.

### Success & Discard Criteria

- **Success:** Both test functions pass cleanly under pytest; ruff, ansible-lint, prettier, and make check exit with
  code 0.
- **Discard:** Any test assertion failure, lint error, or unformatted markdown.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 92.0  |
| cost_pred           | 0.25  |
| learning_value_pred | 1.5   |
| ev_pred             | 91.58 |

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 1.5 - 0.3 * 0.01 - 0.25 = 91.08 + 0.75 - 0.003 - 0.25 = 91.577 ~ 91.58`.

---

## Strategy Rationale

The overall plan metrics are synthesized from the step-level metrics and system objectives as follows:

- **p_success_pred**: 0.99. Very high probability of success across all three steps: implementing standard declarative
  Ansible tasks (`stat`, `find`, `slurp`, `blockinfile`) in the `node` role, configuring environment variable exports in
  Fish, Bash, Zsh, and snippet templates, and adding unit tests in `tests/test_toolchain.py`.
- **entropy_pred**: 0.04. Calculated as the cumulative sum of step entropies across all three steps
  (`0.02 + 0.01 + 0.01 = 0.04`). This is well within the allocated budget limit of 10.0.
- **impact_pred**: 92.0. Eliminates TLS/SSL certificate verification failures in Node.js applications and tools (such as
  npm, npx, yarn, pnpm) when running in corporate or enterprise environments with custom root/intercepting CA
  certificates.
- **cost_pred**: 0.90. Calculated as the direct sum of individual step costs (`0.35 + 0.30 + 0.25 = 0.90`).
- **learning_value_pred**: 3.0. Establishes a standardized, reproducible pattern for application-specific CA certificate
  bundling and multi-shell environment variable orchestration across the repository.
- **ev_pred**: 91.67. Computed using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 92.0 + 0.5 * 3.0 - 0.3 * 0.04 - 0.90 = 91.08 + 1.50 - 0.012 - 0.90 = 91.668 ~ 91.67`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Project Layout & Multi-Variant Stow Packaging: packages in `dotfiles/`, no loose
    files outside packages).
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: configuration behaves cleanly across Linux and macOS).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: single-pass Prettier formatting with backtick
    code spans for arithmetic expressions, assertion over hope).
  - `holon-config/world/ruleset.md` §2 (Ansible Style: FQCN modules, fact referencing conventions, idempotent
    operations).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: zero unauthorized writes outside
    workspace).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Missing `/usr/local/share/ca-certificates` on macOS or non-Debian distributions: Guarded by `ansible.builtin.stat`
    checking `stat.exists` and `stat.isdir` before searching or reading files.
  - Non-interactive shells not discovering `NODE_EXTRA_CA_CERTS`: Mitigated by placing the export before early return
    guards in `.bashrc` and `.zshrc`.
  - Block duplication upon successive converges: Mitigated by `ansible.builtin.blockinfile` using deterministic markers
    `# {mark} ANSIBLE MANAGED BLOCK: Custom CA <basename>`.
- **Mitigations built into the plan:**
  - Directory existence checks before file read/write operations.
  - Automated test assertions in `tests/test_toolchain.py` verifying both Ansible task structures and shell script
    exports.
  - Execution of full verification suite (`pytest`, `ruff`, `ansible-lint`, `prettier`, `make check`).
- **Residual risk accepted (and why):**
  - Minimal residual risk: all tasks are declarative and conditionally guarded against missing files or paths.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.04
- **Budget Compliance:** The plan entropy of 0.04 is well within the budget limit (`0.04 <= 10.0`).

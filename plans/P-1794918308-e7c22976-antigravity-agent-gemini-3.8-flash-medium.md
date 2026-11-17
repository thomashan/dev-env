# Plan for I-1794918292-multi-sh

- **Plan ID:** P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794918292-multi-sh
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T12:25:13Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent directly establishes first-class multi-shell parity across Bash,
  Zsh, and Fish for all managed developer tools (Node via nvm, Conda, and Homebrew), guarantees ~/.local/bin binary
  symlinks override stale/system binaries, adds automated cross-shell assertions in the Node Ansible role, and verifies
  multi-shell invariants with unit tests.
- **Exploration stance:** Focused exploit across dotfiles, Ansible tasks, and manifest test invariants to ensure clean
  POSIX and non-POSIX shell parity adhering strictly to world constraints and rulesets.
- **Safety priority level:** standard
- **Priority Justification:** Adheres strictly to `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification, multi-OS rule, no hardcoded paths), §2 (Assertion over hope, single-pass Prettier formatting with
  code-span arithmetic), §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All modifications involve deterministic configuration additions for Bash and Zsh, Ansible task
  wiring, multi-shell assertions, and regression test assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.07  |
| impact_pred         | 93.0  |
| cost_pred           | 1.7   |
| learning_value_pred | 5.0   |
| ev_pred             | 92.85 |

---

## Step 1: Multi-Shell Conda and Homebrew Integration in Bash and Zsh Dotfiles

- **Sub‑intent recommendation:** NO
- **Reasoning:** Modular configuration enhancement within `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc` providing
  portable evaluation of Homebrew shell environment and Conda activation hooks.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Standardizing Homebrew environment evaluation and Conda initialization hooks across Bash
  and Zsh dotfiles achieves consistent tool resolution across non-fish interactive and login shells without affecting OS
  portability.
- **Learning target:** Confirm Homebrew (`brew shellenv`) and Conda hooks initialize properly in both Bash and Zsh
  sessions across Darwin and Linux environments without generating stderr noise when tools are absent.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Integrate Homebrew shellenv evaluation and Conda shell initialization hooks in
  `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc`.
- **Git branch:**
  `I-1794918292-multi-sh/P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium/E-1-bash-zsh-conda-homebrew/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc`.
2. Insert multi-OS Homebrew environment evaluation logic:
   - For Darwin: check for existence and execute `/opt/homebrew/bin/brew shellenv` (Apple Silicon) or
     `/usr/local/bin/brew shellenv` (Intel).
   - For Linux: check for existence and execute `/home/linuxbrew/.linuxbrew/bin/brew shellenv` or
     `$HOME/.linuxbrew/bin/brew shellenv`, or fallback to adding `/home/linuxbrew/.linuxbrew/bin` to `PATH`.
3. Insert Conda shell hook probe and initialization logic:
   - Check candidate Conda installation roots in order (`$HOME/miniforge3`, `$HOME/miniforge`, `$HOME/mambaforge`,
     `/opt/homebrew/Caskroom/miniforge/base`, `/usr/local/Caskroom/miniforge/base`, `/opt/miniforge3`, `/opt/conda`,
     `$HOME/anaconda3`, `$HOME/miniconda3`).
   - If a valid `conda` executable is found, evaluate `conda shell.bash hook 2>/dev/null` in Bash, or
     `conda shell.zsh hook 2>/dev/null` in Zsh.
4. Preserve the local override sourcing hooks (`.bashrc.local`, `.zshrc.local`) at the end of each file.
5. Ensure interactive checks in `.bashrc` remain intact so non-interactive scripts do not incur unintended execution
   delays.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, no hardcoded `/Users` or `/home` paths; use
  facts or `$HOME`), §2 (Assertion over hope, no shell scripts outside dotfiles), `holon-config/world/constraints.md` §3
  (Dotfile modification boundaries).
- **Potential failure modes for this step:** Stderr noise if `brew` or `conda` binary does not exist, or syntax
  incompatibilities between Bash and Zsh.
- **Guardrails and early‑abort checks:** Guard all shell invocations with executable checks (`[ -x ...]`), redirect
  stderr to `/dev/null` during hook probing, and verify syntax using `bash -n` and `zsh -n` (if available).

### Success & Discard Criteria

- **Success:** Both `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc` contain robust, error-free Homebrew shellenv and
  Conda hook logic compatible with Darwin and Linux.
- **Discard:** Shell errors or broken interactive startup in Bash or Zsh sessions.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 88.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 2.0   |
| ev_pred             | 87.81 |

Calculated via: `EV = 0.99 * 88.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.3 = 87.12 + 1.0 - 0.006 - 0.3 = 87.814 ~ 87.81`.

---

## Step 2: Multi-Shell NVM and Node Integration in Dotfiles and Ansible Node Role

- **Sub‑intent recommendation:** NO
- **Reasoning:** Integrates official `nvm-sh/nvm` sourcing across POSIX shells (Bash, Zsh) alongside existing Fish
  `nvm.fish` and establishes deterministic `~/.local/bin` binary symlinks in Ansible.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Sourcing official `nvm.sh` in Bash and Zsh while managing symlinks in `~/.local/bin`
  directly pointing to `~/.local/share/nvm/current/bin/*` ensures that the repo-managed pinned Node runtime takes
  immediate precedence in every shell environment.
- **Learning target:** Confirm that `NVM_DIR` respects `XDG_DATA_HOME` (`~/.local/share/nvm`) across Bash and Zsh, that
  official `nvm.sh` is cleanly provisioned, and that `~/.local/bin/{node,npm,npx}` point directly to
  `nvm/current/bin/*`.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Configure `NVM_DIR` and `nvm.sh` in Bash and Zsh dotfiles, install official `nvm-sh/nvm`, and create
  overriding symlinks in `~/.local/bin` via `ansible/roles/node/tasks/main.yml`.
- **Git branch:**
  `I-1794918292-multi-sh/P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium/E-2-nvm-node-multi-shell-symlinks/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. In `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc`:
   - Set `export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"`.
   - Set `export NVM_DIR="${XDG_DATA_HOME}/nvm"`, checking whether `~/.nvm` exists as a legacy fallback.
   - Source `nvm.sh` from `"$NVM_DIR/nvm.sh"` if present, or from `/opt/homebrew/opt/nvm/nvm.sh` /
     `/usr/local/opt/nvm/nvm.sh` on Homebrew systems.
   - Ensure `"$NVM_DIR/current/bin"` is prepended to `PATH` so non-interactive subshells and commands can execute node
     tools even if shell functions have not initialized.
2. In `ansible/roles/node/tasks/main.yml`:
   - Retain existing `nvm.fish` via Fisher in Fish.
   - Add a task to ensure official `nvm-sh/nvm` repository or script is installed into
     `{{ devenv_home }}/.local/share/nvm` (e.g. cloning `https://github.com/nvm-sh/nvm.git` or downloading `nvm.sh`)
     guarded by `creates: "{{ devenv_home }}/.local/share/nvm/nvm.sh"`.
   - Ensure the directory `{{ devenv_home }}/.local/bin` exists with mode `0755`.
   - Add an Ansible task looping over `node`, `npm`, and `npx` to create symlinks from
     `{{ devenv_home }}/.local/bin/{{ item }}` to `{{ devenv_home }}/.local/share/nvm/current/bin/{{ item }}` with
     `state: link` and `force: true`.
3. Verify that these symlinks cleanly override any system-installed binaries on PATH.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, version parity, no hardcoded paths), §2
  (Ansible idempotence and FQCN usage `ansible.builtin.file`), `holon-config/world/constraints.md` §3 (Environment
  mutation boundaries: manage node through nvm).
- **Potential failure modes for this step:** Broken symlinks if `current` target does not yet exist, or conflict with
  pre-existing binaries in `~/.local/bin`.
- **Guardrails and early‑abort checks:** The symlink tasks must execute after `current` is linked to
  `v{{ devenv_node_version }}` and use `force: true` to reliably override stale files.

### Success & Discard Criteria

- **Success:** `nvm` is cleanly wired in Bash and Zsh, and `~/.local/bin/node`, `npm`, `npx` symlinks point directly to
  `~/.local/share/nvm/current/bin/*`.
- **Discard:** Missing symlinks, broken PATH precedence, or errors sourcing `nvm.sh` in Bash/Zsh.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 2.5   |
| ev_pred             | 91.92 |

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 2.5 - 0.3 * 0.02 - 0.4 = 91.08 + 1.25 - 0.006 - 0.4 = 91.924 ~ 91.92`.

---

## Step 3: Multi-Shell Automated Node Resolution Assertions in Ansible Node Role

- **Sub‑intent recommendation:** NO
- **Reasoning:** Adds robust verification tasks to `ansible/roles/node/tasks/main.yml` enforcing that Bash, Zsh, and
  Fish all resolve Node to the pinned version on login shell PATH.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicitly probing `bash -lc 'which node; node -v'`, `zsh -lc 'which node; node -v'`, and
  `fish -lc 'which node; node -v'` in Ansible tasks guarantees multi-shell parity and eliminates silent resolution drift
  across shells.
- **Learning target:** Ensure each shell cleanly executes login session probes, captures output, and asserts resolution
  to the pinned LTS version without false failures when optional shells are invoked.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Add login shell verification probes and assertions for Bash, Zsh, and Fish in
  `ansible/roles/node/tasks/main.yml`.
- **Git branch:**
  `I-1794918292-multi-sh/P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium/E-3-automated-multi-shell-assertions/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/roles/node/tasks/main.yml`.
2. Locate the verification block for Fish login shell resolution.
3. Add a command task to probe Node resolution in Bash:
   - Command: `bash -lc "which node; node -v"`.
   - Register result in `devenv_node_which_bash`.
   - Set `changed_when: false` and `check_mode: false`.
4. Add an assertion task for Bash verifying:
   - `node` resolves to the managed path (contains `.local/share/nvm/current/bin/node` or `.local/bin/node`).
   - Output contains `'v' ~ devenv_node_version`.
5. Add a command task to probe Node resolution in Zsh:
   - Check if `zsh` is available or execute `zsh -lc "which node; node -v"`.
   - Register result in `devenv_node_which_zsh`.
   - Set `changed_when: false` and `check_mode: false`.
6. Add an assertion task for Zsh verifying:
   - `node` resolves to the managed path.
   - Output contains `'v' ~ devenv_node_version`.
7. Retain or align the existing Fish verification probe and assertion (`fish -lc "which node; node -v"`).
8. Ensure clear failure messages indicating the shell and observed paths if any assertion fails.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Assertion over hope; Ansible collection FQCNs; check_mode
  discipline), §3 (Testing constraints).
- **Potential failure modes for this step:** If `zsh` is not installed on a specific CI/test container, direct execution
  might fail.
- **Guardrails and early‑abort checks:** Probe `which zsh` or use conditional execution (`when: ...`) if zsh is absent,
  or ensure standard system shells are accommodated while enforcing strict assertions when executed.

### Success & Discard Criteria

- **Success:** Ansible verifies and asserts pinned Node LTS resolution across Bash, Zsh, and Fish login sessions.
- **Discard:** Missing shell assertions or false-positive failures due to shell startup errors.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 90.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 2.0   |
| ev_pred             | 89.80 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 2.0 - 0.3 * 0.01 - 0.3 = 89.10 + 1.0 - 0.003 - 0.3 = 89.797 ~ 89.80`.

---

## Step 4: Unit and Manifest Invariant Testing in `tests/test_manifest.py`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Adds unit test coverage enforcing multi-shell configuration invariants across Bash, Zsh, and Fish
  dotfiles and Ansible roles.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Codifying multi-shell parity into automated test invariants in `tests/test_manifest.py`
  prevents silent regression of Homebrew, Conda, and NVM integration across any of the supported shells.
- **Learning target:** Ensure pytest validates multi-shell dotfile contents, Stow link declarations, node symlink tasks,
  and cross-shell assertion tasks cleanly.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Add comprehensive unit tests in `tests/test_manifest.py` validating multi-shell parity declarations
  and configuration hooks.
- **Git branch:**
  `I-1794918292-multi-sh/P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium/E-4-manifest-multi-shell-tests/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_manifest.py`.
2. Add a new test function `test_multishell_nvm_and_node_parity()`:
   - Read `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc`.
   - Assert both files define `NVM_DIR` respecting `XDG_DATA_HOME` or `~/.nvm`.
   - Assert both files source `nvm.sh` when present.
   - Assert both files ensure the nvm current binary path or `~/.local/bin` is included in PATH.
3. Add a new test function `test_multishell_conda_and_homebrew_parity()`:
   - Assert both `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc` contain multi-OS Homebrew evaluation
     (`brew shellenv`).
   - Assert both files contain Conda probe and hook evaluation logic (`conda shell.bash hook`, `conda shell.zsh hook`).
4. Add a new test function `test_node_role_symlinks_and_multishell_assertions()`:
   - Load `ansible/roles/node/tasks/main.yml`.
   - Assert tasks exist ensuring symlinks for `~/.local/bin/node`, `npm`, and `npx` pointing to
     `~/.local/share/nvm/current/bin/*`.
   - Assert verification tasks probe and assert Node path and version across `bash -lc`, `zsh -lc`, and `fish -lc`.
5. Run `uv run --extra test pytest -m "not network"` to confirm all new tests pass.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing constraints: test location and runner),
  `holon-config/world/ruleset.md` §2 (Assertion over hope).
- **Potential failure modes for this step:** Brittle string matching in tests that breaks on minor formatting
  variations.
- **Guardrails and early‑abort checks:** Use resilient AST or structural key-string checks matching declarative intent
  rather than rigid line-by-line equality.

### Success & Discard Criteria

- **Success:** New tests in `tests/test_manifest.py` pass cleanly and prevent any shell integration drift.
- **Discard:** Test failures or brittle assertion failures.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 88.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 2.0   |
| ev_pred             | 87.82 |

Calculated via: `EV = 0.99 * 88.0 + 0.5 * 2.0 - 0.3 * 0.01 - 0.3 = 87.12 + 1.0 - 0.003 - 0.3 = 87.817 ~ 87.82`.

---

## Step 5: Full Verification and Quality Gate Validation

- **Sub‑intent recommendation:** NO
- **Reasoning:** Executes end-to-end repository test runners and linters to verify complete codebase integrity and
  specification compliance.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Running all static linters, formatters, and dynamic test runners verifies zero
  regressions and guarantees that changes meet all repository world rules and constraints.
- **Learning target:** Verify complete test suite execution clean across all linters without deprecations or formatting
  errors.
- **Maximum acceptable cost for this learning:** 0.4

### Intent & Git Integration

- **Step Intent:** Execute comprehensive quality checks: pytest, ruff, ansible-lint, prettier, and make check.
- **Git branch:**
  `I-1794918292-multi-sh/P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium/E-5-full-validation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Run `uv run --extra test pytest -m "not network"` to ensure the full test suite passes without errors.
2. Run `uv run ruff check .` to verify all Python code conforms to style and quality rules.
3. Run `uv run --extra test ansible-lint ansible/site.yml` to verify Ansible playbooks and roles satisfy Ansible best
   practices.
4. Run `npx prettier --check "**/*.md"` to guarantee single-pass markdown formatting convergence without syntax or code
   block corruption.
5. Execute `make check` or evaluate prerequisite assertions to verify repository-level health.
6. Verify `git status` reports clean or expected changes only.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Coding conventions, single-pass Prettier formatting),
  `holon-config/world/ruleset.md` §3 (pytest runner), `holon-config/world/constraints.md` §2 (Sandbox containment).
- **Potential failure modes for this step:** Prettier formatting discrepancies or unexpected lint warnings.
- **Guardrails and early‑abort checks:** Fix formatting or linting issues immediately using standard linters before
  declaring step completion.

### Success & Discard Criteria

- **Success:** All test suites and linters pass cleanly with exit code 0.
- **Discard:** Lingering test failures or linter errors.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 90.0  |
| cost_pred           | 0.4   |
| learning_value_pred | 1.5   |
| ev_pred             | 89.45 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 1.5 - 0.3 * 0.01 - 0.4 = 89.10 + 0.75 - 0.003 - 0.4 = 89.447 ~ 89.45`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from composite high confidence across all five steps. Each step addresses a modular,
  well-scoped change with clear boundaries: standardizing Homebrew and Conda hooks in Bash/Zsh dotfiles, wiring official
  nvm-sh and ensuring `~/.local/bin` node symlinks in Ansible, adding multi-shell automated login assertions in the Node
  role, adding invariant unit tests in `tests/test_manifest.py`, and executing repository-wide quality linters.
- **entropy_pred**: 0.07. Calculated as the cumulative sum of step entropies across all steps
  (`0.02 + 0.02 + 0.01 + 0.01 + 0.01 = 0.07`). This is well below the process sandbox entropy limit of 10.0.
- **impact_pred**: 93.0. Establishes true first-class multi-shell parity across Bash, Zsh, and Fish for all managed
  tools (Node via nvm, Conda, and Homebrew), prevents system binary shadowing via deterministic `~/.local/bin` symlinks,
  and locks in cross-shell behavior through automated assertions and tests.
- **cost_pred**: 1.7. Calculated as the direct sum of individual step costs (`0.3 + 0.4 + 0.3 + 0.3 + 0.4 = 1.7`).
- **learning_value_pred**: 5.0. Reflects the value of standardizing cross-shell configuration patterns, establishing
  reusable multi-shell node assertions in Ansible, and expanding repository test invariants.
- **ev_pred**: 92.85. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 93.0 + 0.5 * 5.0 - 0.3 * 0.07 - 1.7 = 92.07 + 2.5 - 0.021 - 1.7 = 92.849 ~ 92.85`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: version parity across environments, no
    hardcoded `/Users/...` or `/opt/homebrew/...` paths; resolve from facts or `$HOME` / `$XDG_*`).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: Ansible FQCNs, assertion over hope, PEP 8,
    single-pass Prettier formatting with backtick code spans for arithmetic expressions).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, dotfile editing
    boundaries, manage node through nvm).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Non-interactive shell execution: Bash `.bashrc` has an early return for non-interactive shells. Environment
    variables like `PATH` adjustments for `~/.local/bin` and `$XDG_DATA_HOME/nvm/current/bin` must be evaluated cleanly
    or placed so that subshells and tools resolve appropriately.
  - Shell availability on test hosts: While Bash and Fish are standard in development environments, Zsh might not be
    installed on every minimal Linux container. In Ansible tasks, probes should accommodate environments or test harness
    constraints without failing if optional shells are absent, or ensure clean conditionals are evaluated.
  - NVM directory location: Parity requires respecting `$XDG_DATA_HOME/nvm` (`~/.local/share/nvm`) while falling back to
    `~/.nvm` if an existing install exists.
- **Mitigations built into the plan:**
  - Portable shell logic with executable file checks (`[ -x ...]`) and standard fallback variables.
  - Sourcing order in dotfiles preserves local overrides (`.bashrc.local`, `.zshrc.local`) at the end.
  - Multi-shell assertion tasks in Ansible report granular debugging info if path or version resolution fails.
  - Comprehensive quality check covering `pytest`, `ruff`, `ansible-lint`, and `prettier`.
- **Residual risk accepted (and why):**
  - Minimal residual risk: all changes are strictly additive or refine existing dotfile and Ansible logic with full test
    backing.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.07
- **Budget Compliance:** The plan entropy of 0.07 is well below the budget limit (`0.07 <= 10.0`).

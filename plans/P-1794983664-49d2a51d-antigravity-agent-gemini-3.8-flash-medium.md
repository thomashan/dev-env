# Plan for I-1794983648-tmux-home-conf

- **Plan ID:** P-1794983664-49d2a51d-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794983648-tmux-home-conf
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-18T06:36:15Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent addresses a critical dotfiles shadowing and backup detection
  flaw by relocating the tmux Stow package configuration from the XDG path (`~/.config/tmux/tmux.conf`) to the standard
  home path (`~/.tmux.conf`):
  1. Relocate Stow package file from `dotfiles/tmux/.config/tmux/tmux.conf` to `dotfiles/tmux/.tmux.conf` and prune the
     empty `dotfiles/tmux/.config/` directory tree.
  2. Update the header comment in `dotfiles/tmux/.tmux.conf` to document `~/.tmux.conf` rather than the XDG path.
  3. Update `devenv_links` in `ansible/group_vars/all.yml` to target `{{ devenv_home }}/.tmux.conf`.
  4. Ensure existing legacy symlinks at `{{ devenv_home }}/.config/tmux/tmux.conf` pointing into the repo or targeting
     legacy paths are safely removed during dotfiles convergence (`ansible/roles/dotfiles/tasks/main.yml`) and dotfiles
     unlinking (`ansible/playbooks/unlink.yml`).
  5. Update documentation in `README.md`.
  6. Update tests in `tests/test_manifest.py` and verify all quality gates pass cleanly (`pytest`, `ruff`,
     `ansible-lint`, `prettier`, `make check`).
- **Exploration stance:** Focused exploit across Stow package organization, Ansible manifest declarations, cleanup
  tasks, documentation, and test assertions.
- **Safety priority level:** standard
- **Priority Justification:** Follows `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81 compatibility),
  §2 (Assertion over hope, single-pass Prettier formatting with backtick arithmetic spans, idempotent package
  installations), §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic filesystem relocations, manifest updates, legacy symlink cleanups,
  documentation adjustments, and test suite synchronizations.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.06  |
| impact_pred         | 92.0  |
| cost_pred           | 0.9   |
| learning_value_pred | 3.0   |
| ev_pred             | 91.66 |

---

## Step 1: Relocate Tmux Stow Package File and Update Header Comment

- **Sub‑intent recommendation:** NO
- **Reasoning:** Deterministic filesystem relocation and comment modification within `dotfiles/tmux/`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Relocating `tmux.conf` to root level `dotfiles/tmux/.tmux.conf` enables GNU Stow to map
  directly to `~/.tmux.conf`, ensuring interactive conflict detection works reliably and avoiding stale `~/.tmux.conf`
  shadowing.
- **Learning target:** Confirm Stow package layout matches standard top-level dotfile convention and clean removal of
  empty nested directories.
- **Maximum acceptable cost for this learning:** 0.15

### Intent & Git Integration

- **Step Intent:** Move `dotfiles/tmux/.config/tmux/tmux.conf` to `dotfiles/tmux/.tmux.conf`, remove empty
  `.config/tmux/` and `.config/` directories, and update header comments in `.tmux.conf`.
- **Git branch:**
  `I-1794983648-tmux-home-conf/P-1794983664-49d2a51d-antigravity-agent-gemini-3.8-flash-medium/E-1-relocate-tmux-stow-file/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Move the file `dotfiles/tmux/.config/tmux/tmux.conf` to `dotfiles/tmux/.tmux.conf`.
2. Remove the now-empty directories `dotfiles/tmux/.config/tmux` and `dotfiles/tmux/.config`.
3. In `dotfiles/tmux/.tmux.conf`, update the opening header comment to reflect that the configuration lives at
   `~/.tmux.conf` rather than the XDG path (`~/.config/tmux/tmux.conf`), explaining that linking to `~/.tmux.conf`
   prevents unmanaged legacy configuration files from shadowing repository settings and allows conflict detection during
   setup.
4. Preserve the existing smart pane switching bindings (`is_vim` detection and C-h/j/k/l keys) intact.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Project Layout & Multi-Variant Stow Packaging),
  `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, no loose files under
  `dotfiles/`).
- **Potential failure modes for this step:** Forgetting to remove empty `.config` directories under `dotfiles/tmux/` or
  accidentally modifying active vim-tmux-navigator bindings.
- **Guardrails and early‑abort checks:** Verify that `dotfiles/tmux/.tmux.conf` exists, contains expected bindings, and
  no leftover files or folders remain under `dotfiles/tmux/.config`.

### Success & Discard Criteria

- **Success:** File exists at `dotfiles/tmux/.tmux.conf` with updated header comment and intact pane-switching
  directives; `dotfiles/tmux/.config` is completely removed.
- **Discard:** File missing at destination or vim-tmux-navigator directives altered.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 91.0  |
| cost_pred           | 0.15  |
| learning_value_pred | 0.5   |
| ev_pred             | 90.19 |

Calculated via: `EV = 0.99 * 91.0 + 0.5 * 0.5 - 0.3 * 0.01 - 0.15 = 90.09 + 0.25 - 0.003 - 0.15 = 90.187 ~ 90.19`.

---

## Step 2: Update Link Manifest in Ansible Group Vars

- **Sub‑intent recommendation:** NO
- **Reasoning:** Straightforward YAML manifest update in `ansible/group_vars/all.yml`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating `devenv_links` ensures Ansible's dotfiles role and link assertions track
  `~/.tmux.conf` pointing to `dotfiles/tmux/.tmux.conf`.
- **Learning target:** Confirm YAML syntax and link manifest schema consistency across all declared links.
- **Maximum acceptable cost for this learning:** 0.15

### Intent & Git Integration

- **Step Intent:** Update `devenv_links` entry for tmux from `dotfiles/tmux/.config/tmux/tmux.conf` to
  `dotfiles/tmux/.tmux.conf` and destination from `{{ devenv_home }}/.config/tmux/tmux.conf` to
  `{{ devenv_home }}/.tmux.conf`.
- **Git branch:**
  `I-1794983648-tmux-home-conf/P-1794983664-49d2a51d-antigravity-agent-gemini-3.8-flash-medium/E-2-update-manifest-vars/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/group_vars/all.yml`.
2. Locate the `devenv_links` list.
3. Find the item targeting tmux:
   - Change `src: dotfiles/tmux/.config/tmux/tmux.conf` to `src: dotfiles/tmux/.tmux.conf`.
   - Change `dest: "{{ devenv_home }}/.config/tmux/tmux.conf"` to `dest: "{{ devenv_home }}/.tmux.conf"`.
4. Ensure indentation and YAML formatting align with existing entries.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Ansible Style: valid YAML syntax, explicit list of individual
  files in `devenv_links`), `holon-config/world/constraints.md` §3 (Converge Through the Manifest).
- **Potential failure modes for this step:** YAML syntax error or indentation mismatch causing Ansible parse failure.
- **Guardrails and early‑abort checks:** Validate YAML syntax using Python `yaml.safe_load`.

### Success & Discard Criteria

- **Success:** `devenv_links` defines `src: dotfiles/tmux/.tmux.conf` and `dest: "{{ devenv_home }}/.tmux.conf"`; YAML
  parses cleanly.
- **Discard:** Invalid YAML syntax or incorrect destination path.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 92.0  |
| cost_pred           | 0.15  |
| learning_value_pred | 0.5   |
| ev_pred             | 91.18 |

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 0.5 - 0.3 * 0.01 - 0.15 = 91.08 + 0.25 - 0.003 - 0.15 = 91.177 ~ 91.18`.

---

## Step 3: Clean Up Legacy XDG Symlink in Dotfiles Role and Unlink Playbook

- **Sub‑intent recommendation:** NO
- **Reasoning:** Ansible task updates in `ansible/roles/dotfiles/tasks/main.yml` and `ansible/playbooks/unlink.yml` to
  remove legacy symlinks during convergence and unlinking.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicitly checking and unlinking legacy `{{ devenv_home }}/.config/tmux/tmux.conf`
  symlinks if they point into the repository prevents orphaned or broken symlinks on machines that previously converged
  with the XDG path.
- **Learning target:** Ensure clean migration across existing converged hosts without leaving broken symlinks or
  removing user-created independent files.
- **Maximum acceptable cost for this learning:** 0.25

### Intent & Git Integration

- **Step Intent:** Add legacy symlink cleanup tasks for `{{ devenv_home }}/.config/tmux/tmux.conf` in
  `ansible/roles/dotfiles/tasks/main.yml` and `ansible/playbooks/unlink.yml`.
- **Git branch:**
  `I-1794983648-tmux-home-conf/P-1794983664-49d2a51d-antigravity-agent-gemini-3.8-flash-medium/E-3-cleanup-legacy-xdg-symlink/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/roles/dotfiles/tasks/main.yml`.
2. Add a task to check and remove legacy `{{ devenv_home }}/.config/tmux/tmux.conf` symlink:
   - Stat the path `{{ devenv_home }}/.config/tmux/tmux.conf`.
   - If it exists and is a symlink, and either its link target points inside `devenv_repo_root` or its raw target
     contains `dotfiles/tmux/.config/tmux/tmux.conf` (handling broken symlinks where target no longer exists), remove
     the file with `ansible.builtin.file` (`state: absent`).
   - Place this task before Stow linking so legacy links are purged cleanly.
3. Open `ansible/playbooks/unlink.yml`.
4. Add corresponding cleanup in `unlink.yml` to also check and remove `{{ devenv_home }}/.config/tmux/tmux.conf` if it
   exists as a symlink pointing into the repository or legacy target.
5. Ensure all Ansible modules use Fully-Qualified Collection Names (`ansible.builtin.*`) and include appropriate
   `changed_when` specifications.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Ansible Style: FQCN, idempotence, assertion over hope),
  `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: never delete unmanaged real user files).
- **Potential failure modes for this step:** Accidentally deleting a real, non-symlink user config at
  `~/.config/tmux/tmux.conf`.
- **Guardrails and early‑abort checks:** Guard task with strict condition checking that `stat.islnk` is true and the
  target resolves to or references `devenv_repo_root`. Real files must never be removed.

### Success & Discard Criteria

- **Success:** Both `main.yml` and `unlink.yml` safely remove repository-pointing legacy tmux XDG symlinks without
  disturbing real files.
- **Discard:** Attempting to delete non-symlink files or failure of `ansible-lint`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 93.0  |
| cost_pred           | 0.25  |
| learning_value_pred | 1.0   |
| ev_pred             | 92.31 |

Calculated via: `EV = 0.99 * 93.0 + 0.5 * 1.0 - 0.3 * 0.02 - 0.25 = 92.07 + 0.50 - 0.006 - 0.25 = 92.314 ~ 92.31`.

---

## Step 4: Update Documentation in README.md

- **Sub‑intent recommendation:** NO
- **Reasoning:** Documentation updates in `README.md` reflecting the new destination path for tmux configuration.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Keeping documentation perfectly aligned with the repository's concrete dotfile links
  avoids developer confusion and passes documentation checks.
- **Learning target:** Verify clear and consistent explanation of dotfiles directory layout and target symlinks in
  `README.md`.
- **Maximum acceptable cost for this learning:** 0.15

### Intent & Git Integration

- **Step Intent:** Replace references to `~/.config/tmux/tmux.conf` with `~/.tmux.conf` in `README.md`.
- **Git branch:**
  `I-1794983648-tmux-home-conf/P-1794983664-49d2a51d-antigravity-agent-gemini-3.8-flash-medium/E-4-update-documentation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `README.md`.
2. In Section 1 (Core Packages table), update the row for `tmux`:
   - Change description from `Terminal multiplexer (XDG path ~/.config/tmux/tmux.conf)` to
     `Terminal multiplexer (~/.tmux.conf)`.
3. In Section 1 (Dotfiles Inventory list), update the bullet for `dotfiles/tmux/`:
   - Change `dotfiles/tmux/ (**Terminal / Multiplexer (tmux)**): ~/.config/tmux/tmux.conf` to
     `dotfiles/tmux/ (**Terminal / Multiplexer (tmux)**): ~/.tmux.conf`.
4. Scan `README.md` for any remaining references to `.config/tmux/tmux.conf` and update them accordingly.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Markdown & Docs: enclose arithmetic and metrics in code spans
  for single-pass Prettier convergence).
- **Potential failure modes for this step:** Markdown formatting drift or Prettier check failure.
- **Guardrails and early‑abort checks:** Run `npx prettier --check README.md` to guarantee clean single-pass formatting.

### Success & Discard Criteria

- **Success:** `README.md` reflects `~/.tmux.conf` across package tables and lists; Prettier check passes.
- **Discard:** Prettier check failure or outdated references remaining.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 90.0  |
| cost_pred           | 0.15  |
| learning_value_pred | 0.5   |
| ev_pred             | 89.20 |

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 0.5 - 0.3 * 0.01 - 0.15 = 89.10 + 0.25 - 0.003 - 0.15 = 89.197 ~ 89.20`.

---

## Step 5: Update Tests and Verify Quality Gates

- **Sub‑intent recommendation:** NO
- **Reasoning:** Updating test assertions to match relocated files and validating all CI quality gates.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating `test_manifest.py` to assert `~/.tmux.conf` validates the entire relocated
  configuration and ensures no regressions across linting, syntax, and formatting.
- **Learning target:** Confirm full test suite passes cleanly with updated Stow links and verify repository integrity.
- **Maximum acceptable cost for this learning:** 0.20

### Intent & Git Integration

- **Step Intent:** Replace `test_tmux_config_uses_the_xdg_path` with `test_tmux_config_uses_home_tmux_conf` in
  `tests/test_manifest.py`, update path in `test_tmux_conf_smart_pane_switching`, and execute the full test and lint
  suite.
- **Git branch:**
  `I-1794983648-tmux-home-conf/P-1794983664-49d2a51d-antigravity-agent-gemini-3.8-flash-medium/E-5-update-tests-and-verify/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_manifest.py`.
2. Locate `test_tmux_config_uses_the_xdg_path`.
3. Replace `test_tmux_config_uses_the_xdg_path` with `test_tmux_config_uses_home_tmux_conf`:
   - Assert `any(d.endswith("/.tmux.conf") or d.endswith(".tmux.conf") for d in dests)`.
   - Assert `not any(d.endswith(".config/tmux/tmux.conf") for d in dests)`.
4. Locate `test_tmux_conf_smart_pane_switching`:
   - Change the path read from `REPO_ROOT / "dotfiles" / "tmux" / ".config" / "tmux" / "tmux.conf"` to
     `REPO_ROOT / "dotfiles" / "tmux" / ".tmux.conf"`.
5. Execute verification commands:
   - Run `uv run --extra test pytest -m "not network"`.
   - Run `uv run ruff check .`.
   - Run `uv run --extra test ansible-lint ansible/site.yml`.
   - Run `npx prettier --check "**/*.md"`.
   - Run `make check`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (Testing Constraints: all test modifications explicitly
  declared in plan), `holon-config/world/ruleset.md` §2 (Assertion over hope).
- **Potential failure modes for this step:** Test failure due to path mismatch or forgotten references in other test
  fixtures.
- **Guardrails and early‑abort checks:** Run pytest locally and verify 100% test pass rate.

### Success & Discard Criteria

- **Success:** `tests/test_manifest.py` tests pass cleanly; `pytest`, `ruff`, `ansible-lint`, `prettier`, and
  `make check` all succeed without errors.
- **Discard:** Any test assertion failure, lint error, or format violation.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 94.0  |
| cost_pred           | 0.20  |
| learning_value_pred | 0.5   |
| ev_pred             | 93.11 |

Calculated via: `EV = 0.99 * 94.0 + 0.5 * 0.5 - 0.3 * 0.01 - 0.20 = 93.06 + 0.25 - 0.003 - 0.20 = 93.107 ~ 93.11`.

---

## Strategy Rationale

The overall plan metrics are derived from the step-level metrics and system objectives as follows:

- **p_success_pred**: 0.99. Very high confidence across all five steps: moving a file and removing empty folders,
  updating an explicit manifest list in `ansible/group_vars/all.yml`, adding idempotent symlink cleanup tasks in
  Ansible, updating documentation in `README.md`, and synchronizing test assertions in `tests/test_manifest.py`.
- **entropy_pred**: 0.06. Calculated as the cumulative sum of step entropies across all five steps
  (`0.01 + 0.01 + 0.02 + 0.01 + 0.01 = 0.06`). This is well below the process sandbox entropy budget of 10.0.
- **impact_pred**: 92.0. Eliminates dotfiles shadowing and configuration drift between legacy `~/.tmux.conf` files and
  repository-managed tmux configuration, enables automatic conflict detection in the interactive wizard
  (`devenv_wizard.py`) and dotfiles role, and cleans up legacy symlinks gracefully.
- **cost_pred**: 0.9. Calculated as the direct sum of individual step costs (`0.15 + 0.15 + 0.25 + 0.15 + 0.20 = 0.90`).
- **learning_value_pred**: 3.0. Validates safe dotfile migration patterns, handling of legacy symlink cleanup across
  Ansible playbooks, and maintaining strict Stow package invariants.
- **ev_pred**: 91.66. Computed using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 92.0 + 0.5 * 3.0 - 0.3 * 0.06 - 0.9 = 91.08 + 1.5 - 0.018 - 0.9 = 91.662 ~ 91.66`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Project Layout & Multi-Variant Stow Packaging: packages in `dotfiles/`, no loose
    files outside packages).
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: support macOS and Linux consistently).
  - `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: ensure recipes remain compatible with GNU Make 3.81).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: single-pass Prettier formatting with backtick
    code spans for arithmetic expressions, assertion over hope, FQCN in Ansible).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner under `tests/`, all test modifications
    explicitly declared in plan).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions and prefix isolation).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, no unauthorized
    writes, preserve unmanaged user files).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Deleting user config at `~/.config/tmux/tmux.conf` if it is a real file rather than a symlink: Mitigated by strictly
    verifying `stat.islnk` is true and that the link points into the repository or target path before unlinking.
  - Broken symlink handling: If the symlink was pointing to the old repo location
    (`dotfiles/tmux/.config/tmux/tmux.conf`), `stat` might fail or report nonexistent target; mitigated by checking
    `stat.lnk_source` or raw symlink target before removing.
  - Stow pruning issues: Removing the empty `dotfiles/tmux/.config/tmux` and `dotfiles/tmux/.config` directories avoids
    GNU Stow creating unintended directory structure or stow collisions.
- **Mitigations built into the plan:**
  - Clean directory cleanup under `dotfiles/tmux/`.
  - Guarded Ansible cleanup tasks checking symlink status before deletion.
  - Comprehensive quality checks across `pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check`.
- **Residual risk accepted (and why):**
  - Minimal residual risk: standard file move within a version-controlled repository with full test coverage and
    automated verification.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.06
- **Budget Compliance:** The plan entropy of 0.06 is well within the budget limit (`0.06 <= 10.0`).

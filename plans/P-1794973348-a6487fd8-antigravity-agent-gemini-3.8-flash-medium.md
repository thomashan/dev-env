# Plan for I-1794973331-dev-enhancements

- **Plan ID:** P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794973331-dev-enhancements
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-18T03:42:35Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent delivers essential developer workflow enhancements across
  Neovim, tmux, and the Go toolchain:
  1. Enable kickstart Neovim plugins (`indent_line`, `lint`, `autopairs`, `neo-tree`) in `init.lua`.
  2. Implement seamless tmux-neovim navigation via `christoomey/vim-tmux-navigator` in Neovim (`tmux_navigator.lua`) and
     smart pane switching with `is_vim` process detection in `tmux.conf`.
  3. Configure Homebrew Go toolchain across Linux and macOS in Ansible (`all.yml`, `pkg_brew.yml`, `pkg_apt.yml`,
     `os_Linux.yml`, `packages/tasks/main.yml`) and export `$HOME/go/bin` across shell configs.
  4. Synchronize and lock plugin revisions in `nvim-pack-lock.json`.
  5. Update unit tests in `test_templating.py` and `test_manifest.py` and verify all quality gates pass cleanly.
- **Exploration stance:** Focused exploit across Lua configuration, tmux bindings, Ansible package vars/tasks, shell
  snippets, and pytest assertions.
- **Safety priority level:** standard
- **Priority Justification:** Follows `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81 compatibility),
  §2 (Assertion over hope, single-pass Prettier formatting with backtick arithmetic spans, idempotent package
  installations), §3 (Testing constraints), and `holon-config/world/constraints.md` §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic dotfile, package manifest, and test suite updates with strict invariant
  checks.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.08  |
| impact_pred         | 94.0  |
| cost_pred           | 1.2   |
| learning_value_pred | 4.0   |
| ev_pred             | 92.90 |

---

## Step 1: Enable Kickstart Neovim Plugins

- **Sub‑intent recommendation:** NO
- **Reasoning:** Scoped, deterministic configuration changes in `dotfiles/nvim-kickstart/.config/nvim/init.lua` to
  enable core Kickstart plugins.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Activating `indent_line`, `lint`, `autopairs`, and `neo-tree` in `init.lua` enhances
  editor ergonomics while remaining fully compatible with the `vim.pack` declarative package lifecycle.
- **Learning target:** Confirm clean loading of enabled plugins without startup degradation or runtime collisions.
- **Maximum acceptable cost for this learning:** 0.2

### Intent & Git Integration

- **Step Intent:** Uncomment and enable kickstart plugins in `init.lua`.
- **Git branch:**
  `I-1794973331-dev-enhancements/P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium/E-1-enable-kickstart-plugins/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/nvim-kickstart/.config/nvim/init.lua`.
2. Locate Section 10 (`kickstart.plugins.* examples`).
3. Uncomment the following plugin requirement statements:
   - `require 'kickstart.plugins.indent_line'`
   - `require 'kickstart.plugins.lint'`
   - `require 'kickstart.plugins.autopairs'`
   - `require 'kickstart.plugins.neo-tree'`
4. Maintain `require 'kickstart.plugins.debug'` commented out as specified by intent scope.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Assertion over hope, single-pass Prettier formatting with
  backtick arithmetic spans), `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** Syntax error in Lua comments or accidental disruption of neighboring plugin
  loaders.
- **Guardrails and early‑abort checks:** Inspect diff with `git diff` and ensure clean Lua syntax.

### Success & Discard Criteria

- **Success:** Lines enabling `indent_line`, `lint`, `autopairs`, and `neo-tree` are active in `init.lua`.
- **Discard:** Syntax error in `init.lua` or unauthorized edits outside Section 10.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 93.0  |
| cost_pred           | 0.2   |
| learning_value_pred | 1.0   |
| ev_pred             | 92.37 |

Calculated via: `EV = 0.99 * 93.0 + 0.5 * 1.0 - 0.3 * 0.01 - 0.2 = 92.07 + 0.5 - 0.003 - 0.2 = 92.367 ~ 92.37`.

---

## Step 2: Seamless Tmux-Neovim Navigation

- **Sub‑intent recommendation:** NO
- **Reasoning:** Modular integration of `vim-tmux-navigator` in Neovim alongside smart pane switching bindings in
  `tmux.conf`.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Declaring `christoomey/vim-tmux-navigator` in a dedicated plugin loader file with
  `<C-h>`, `<C-j>`, `<C-k>`, `<C-l>` mappings and pairing it with `is_vim` process detection in `tmux.conf` delivers
  seamless cross-window navigation between tmux panes and Neovim splits.
- **Learning target:** Validate seamless dual-directional navigation and process-detection ergonomics between tmux and
  Neovim.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Implement `tmux_navigator.lua` plugin config, require it in `init.lua`, and add `is_vim` smart pane
  switching bindings in `tmux.conf`.
- **Git branch:**
  `I-1794973331-dev-enhancements/P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium/E-2-tmux-neovim-navigation/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Create `dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/tmux_navigator.lua`.
   - Add module description and reference URL for `christoomey/vim-tmux-navigator`.
   - Invoke `vim.pack.add` with `'https://github.com/christoomey/vim-tmux-navigator'`.
   - Configure directional navigation keymaps in normal mode:
     - Map `<C-h>` to `<Cmd>TmuxNavigateLeft<CR>` with description `Navigate left (tmux/vim)`.
     - Map `<C-j>` to `<Cmd>TmuxNavigateDown<CR>` with description `Navigate down (tmux/vim)`.
     - Map `<C-k>` to `<Cmd>TmuxNavigateUp<CR>` with description `Navigate up (tmux/vim)`.
     - Map `<C-l>` to `<Cmd>TmuxNavigateRight<CR>` with description `Navigate right (tmux/vim)`.
2. Open `dotfiles/nvim-kickstart/.config/nvim/init.lua`.
   - Under Section 10, add `require 'kickstart.plugins.tmux_navigator'`.
3. Open `dotfiles/tmux/.config/tmux/tmux.conf`.
   - Define `is_vim` shell probe string inspecting `#{pane_tty}` process states matching `view`, `vim`, `nvim`, or
     `diff`.
   - Bind `-n C-h` with `if-shell "$is_vim"` to send `C-h` or select pane `-L`.
   - Bind `-n C-j` with `if-shell "$is_vim"` to send `C-j` or select pane `-D`.
   - Bind `-n C-k` with `if-shell "$is_vim"` to send `C-k` or select pane `-U`.
   - Bind `-n C-l` with `if-shell "$is_vim"` to send `C-l` or select pane `-R`.
   - Add copy-mode vi key table bindings for `C-h`, `C-j`, `C-k`, `C-l` for smooth navigation when navigating in
     scrollback.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule), §2 (Assertion over hope, backtick spans for
  formulas), `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** Broken regex syntax in `is_vim` causing tmux parse errors; incorrect keymap
  strings causing Neovim startup failure.
- **Guardrails and early‑abort checks:** Validate tmux configuration syntax and test Lua parsing in Neovim headless
  mode.

### Success & Discard Criteria

- **Success:** `tmux_navigator.lua` declared and required; `tmux.conf` contains working `is_vim` bindings.
- **Discard:** Syntax error in `tmux.conf` or failure in Neovim plugin loading.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 94.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 3.0   |
| ev_pred             | 93.31 |

Calculated via: `EV = 0.98 * 94.0 + 0.5 * 3.0 - 0.3 * 0.02 - 0.3 = 92.12 + 1.5 - 0.006 - 0.3 = 93.314 ~ 93.31`.

---

## Step 3: Homebrew Go Toolchain on macOS and Linux

- **Sub‑intent recommendation:** NO
- **Reasoning:** Standardized, multi-platform toolchain provisioning integrating Go via Homebrew across Linux and macOS
  with cross-shell PATH export parity.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Declaring `go` in core packages, aliasing `go: go` for brew and `go: golang-go` for apt,
  skipping apt installation on Linux in favor of Homebrew (`devenv_brew_bin`), and exporting `$HOME/go/bin` in Bash,
  Zsh, and Fish guarantees a unified, modern Go runtime across all developer environments.
- **Learning target:** Confirm Homebrew binary resolution and declarative task execution for Go package management on
  Linux.
- **Maximum acceptable cost for this learning:** 0.3

### Intent & Git Integration

- **Step Intent:** Configure Go toolchain package declarations, skip lists, Linux Homebrew installation task, and
  multishell PATH exports.
- **Git branch:**
  `I-1794973331-dev-enhancements/P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium/E-3-homebrew-go-toolchain/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `ansible/group_vars/all.yml`.
   - Add `go` to `devenv_packages_core` list.
2. Open `ansible/vars/pkg_brew.yml`.
   - Add alias mapping `go: go`.
3. Open `ansible/vars/pkg_apt.yml`.
   - Add alias mapping `go: golang-go`.
4. Open `ansible/vars/os_Linux.yml`.
   - Update `devenv_pkg_skip` list to include both `neovim` and `go` (`devenv_pkg_skip: [neovim, go]`).
5. Open `ansible/roles/packages/tasks/main.yml`.
   - Add tasks to locate Homebrew binary on Linux using `ansible.builtin.stat` across standard paths
     (`/home/linuxbrew/.linuxbrew/bin/brew`, `{{ devenv_home }}/.linuxbrew/bin/brew`, `/usr/local/bin/brew`,
     `/opt/homebrew/bin/brew`) if `devenv_brew_bin` is not yet defined.
   - Record `devenv_brew_bin` using `ansible.builtin.set_fact` on Linux.
   - Add task to install `go` via `community.general.homebrew` with `name: go`, `state: present`, and
     `path: "{{ devenv_brew_bin | default(omit) }}"`, conditioned on `devenv_system == 'Linux'` and `devenv_brew_bin`
     being defined and non-empty.
6. Open `dotfiles/examples/devenv-shell-snippets.sh`.
   - Add Block E exporting `$HOME/go/bin` to `PATH` if `$HOME/go/bin` exists.
7. Open `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
   - Add Go toolchain PATH export section using `fish_add_path` for `$HOME/go/bin`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule), §2 (Ansible Style: FQCN, Idempotence,
  Assertion over Hope), `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** Unset `devenv_brew_bin` causing task failure if Linuxbrew is not present;
  missing directory causing shell PATH pollution.
- **Guardrails and early‑abort checks:** Guard Homebrew Go installation on Linux with conditional checks verifying
  `devenv_brew_bin` exists and is non-empty; guard shell PATH additions with directory existence tests.

### Success & Discard Criteria

- **Success:** Go package alias present across all tables, skip list configured on Linux, declarative Homebrew Go task
  defined, and multishell PATH exported.
- **Discard:** Unhandled package manager error or failure in Ansible syntax checks.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.02  |
| impact_pred         | 95.0  |
| cost_pred           | 0.3   |
| learning_value_pred | 4.0   |
| ev_pred             | 94.79 |

Calculated via: `EV = 0.98 * 95.0 + 0.5 * 4.0 - 0.3 * 0.02 - 0.3 = 93.10 + 2.0 - 0.006 - 0.3 = 94.794 ~ 94.79`.

---

## Step 4: Lockfile & Plugin Synchronization

- **Sub‑intent recommendation:** NO
- **Reasoning:** Enforce reproducible package management by pinning all newly activated and created Neovim plugins to
  deterministic 40-character commit hashes in `nvim-pack-lock.json` and updating documentation coverage.
- **Step Type:** IMPLEMENTATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicitly locking `neo-tree.nvim`, `nui.nvim`, `windwp/nvim-autopairs`,
  `lukas-reineke/indent-blankline.nvim`, `mfussenegger/nvim-lint`, and `christoomey/vim-tmux-navigator` in
  `nvim-pack-lock.json` satisfies `test_nvim_lockfile_covers_every_declared_plugin()` and guarantees deterministic
  installation across all hosts.
- **Learning target:** Verify lockfile schema adherence, 40-character SHA validation, and documentation synchronization.
- **Maximum acceptable cost for this learning:** 0.2

### Intent & Git Integration

- **Step Intent:** Lock newly enabled plugins in `nvim-pack-lock.json` and document them in `README.md`.
- **Git branch:**
  `I-1794973331-dev-enhancements/P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium/E-4-lockfile-synchronization/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `dotfiles/nvim-kickstart/.config/nvim/nvim-pack-lock.json`.
2. Add entries under `plugins` dictionary with pinned 40-character hex commit hashes:
   - `neo-tree.nvim`: src `https://github.com/nvim-neo-tree/neo-tree.nvim`, rev
     `760d9701953ad2b0277fe9776ba99bb011ecac2b`.
   - `nui.nvim`: src `https://github.com/MunifTanjim/nui.nvim`, rev `10fc361835c856ba4233ef5ea135b919bf3dce97`.
   - `nvim-autopairs`: src `https://github.com/windwp/nvim-autopairs`, rev `3172f40c16563db871a58f20d205c710ad782311`.
   - `indent-blankline.nvim`: src `https://github.com/lukas-reineke/indent-blankline.nvim`, rev
     `f1e186e44d3b7f9ae918008e2c28ce37c6023d2d`.
   - `nvim-lint`: src `https://github.com/mfussenegger/nvim-lint`, rev `52107ce2076a27a285af781248e2c59bad817cd0`.
   - `vim-tmux-navigator`: src `https://github.com/christoomey/vim-tmux-navigator`, rev
     `fb217852efb294a50a10507fc8d53709696b6e23`.
3. Open `README.md`.
   - Under Section 5 (`Neovim Plugins (nvim-pack-lock.json)`), document each newly added plugin with its logical name,
     description, and source URL to maintain compliance with `test_readme_manifest_coverage`.
   - Update total plugin count description to match the new locked count.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Assertion over hope, single-pass Prettier formatting with
  backtick arithmetic spans), `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries).
- **Potential failure modes for this step:** Malformed JSON in lockfile; non-40-character commit hashes causing
  assertion failure; omitted plugin descriptions in README triggering manifest coverage failure.
- **Guardrails and early‑abort checks:** Validate JSON syntax with Python `json.loads` or `jq`; verify 40-character hex
  pattern match for every `rev`.

### Success & Discard Criteria

- **Success:** All declared plugins are locked with valid 40-hex commit hashes and documented in `README.md`.
- **Discard:** Missing plugin from lockfile or malformed JSON structure.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.01  |
| impact_pred         | 93.0  |
| cost_pred           | 0.2   |
| learning_value_pred | 2.0   |
| ev_pred             | 92.87 |

Calculated via: `EV = 0.99 * 93.0 + 0.5 * 2.0 - 0.3 * 0.01 - 0.2 = 92.07 + 1.0 - 0.003 - 0.2 = 92.867 ~ 92.87`.

---

## Step 5: Tests and Verification

- **Sub‑intent recommendation:** NO
- **Reasoning:** Update existing regression tests to cover the newly introduced Go package alias, smart tmux bindings,
  and plugins, then execute the full validation suite.
- **Step Type:** TESTING
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Updating `tests/test_templating.py` and `tests/test_manifest.py` verifies invariant
  guarantees for the Go package alias, shell PATH exports, and Neovim/tmux navigation bindings while ensuring zero
  regressions across existing test suites.
- **Learning target:** Validate test harness execution across modified Jinja templating, manifest invariants, and
  formatters.
- **Maximum acceptable cost for this learning:** 0.2

### Intent & Git Integration

- **Step Intent:** Update tests in `test_templating.py` and `test_manifest.py` and run all project quality gates.
- **Git branch:**
  `I-1794973331-dev-enhancements/P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium/E-5-tests-and-verification/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Open `tests/test_templating.py`.
   - Verify that `test_wanted_list_drops_os_provided_packages` and `test_logical_names_resolve_on_every_backend` cleanly
     process `go` across both `brew` and `apt` alias tables.
   - If needed, add targeted templating test for `devenv_pkg_skip` containing `go` alongside `neovim`.
2. Open `tests/test_manifest.py`.
   - Update `test_tmux_conf_is_comment_only_factory_default` to recognize the smart pane switching configuration with
     `is_vim` process detection instead of requiring comment-only lines.
   - Add invariant assertion ensuring `go` is declared in `devenv_packages_core`.
   - Add invariant assertion ensuring `devenv_pkg_skip` in `os_Linux.yml` includes `go`.
   - Update `test_devenv_shell_snippets_exists_and_valid` to assert the presence of the Go toolchain PATH export block
     (`$HOME/go/bin`).
   - Add assertion verifying `$HOME/go/bin` path addition in `00-devenv.fish`.
3. Run verification gates in sequence:
   - Run unit test suite: `uv run --extra test pytest -m "not network"`.
   - Run Python linter: `uv run ruff check .`.
   - Run Ansible linter: `uv run --extra test ansible-lint ansible/site.yml`.
   - Run Markdown linter: `npx prettier --check "**/*.md"`.
   - Run repository prerequisite check: `make check`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Assertion over hope, single-pass Prettier formatting with
  backtick arithmetic spans), §3 (Testing Constraints).
- **Potential failure modes for this step:** Broken tests due to outdated assumptions; Prettier formatting differences
  in modified Markdown files.
- **Guardrails and early‑abort checks:** Format all modified Markdown files with Prettier before running checks; verify
  tests run cleanly under `uv run --extra test pytest`.

### Success & Discard Criteria

- **Success:** All unit tests pass, and all quality checks (`pytest`, `ruff`, `ansible-lint`, `prettier`) succeed.
- **Discard:** Test assertion failure, lint error, or unformatted markdown.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 95.0  |
| cost_pred           | 0.2   |
| learning_value_pred | 2.0   |
| ev_pred             | 94.84 |

Calculated via: `EV = 0.99 * 95.0 + 0.5 * 2.0 - 0.3 * 0.02 - 0.2 = 94.05 + 1.0 - 0.006 - 0.2 = 94.844 ~ 94.84`.

---

## Strategy Rationale

The overall plan metrics are derived from the step-level metrics and system objectives as follows:

- **p_success_pred**: 0.98. High confidence across all five steps: activating established plugins in Neovim Kickstart,
  adding standardized tmux-neovim navigation bindings, declarative Homebrew Go package installation and PATH exports,
  strict commit-pinned lockfile updates, and deterministic unit test invariant updates.
- **entropy_pred**: 0.08. Calculated as the cumulative sum of step entropies across all five steps
  (`0.01 + 0.02 + 0.02 + 0.01 + 0.02 = 0.08`). This is well below the sandbox entropy budget of 10.0.
- **impact_pred**: 94.0. Implements essential developer productivity enhancements across the editor, multiplexer, and Go
  toolchain, eliminates platform drift by using Homebrew for Go across macOS and Linux, and ensures full lockfile
  reproducibility.
- **cost_pred**: 1.2. Calculated as the direct sum of individual step costs (`0.2 + 0.3 + 0.3 + 0.2 + 0.2 = 1.2`).
- **learning_value_pred**: 4.0. Validates dual Neovim-tmux navigation integration patterns, multi-shell Go environment
  configuration, and declarative Linuxbrew toolchain management.
- **ev_pred**: 92.90. Computed using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.98 * 94.0 + 0.5 * 4.0 - 0.3 * 0.08 - 1.2 = 92.12 + 2.0 - 0.024 - 1.2 = 92.896 ~ 92.90`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Multi-OS rule: support macOS and Linux consistently; resolve `devenv_brew_bin`
    across Apple Silicon, Intel, and Linuxbrew paths).
  - `holon-config/world/ruleset.md` §1 (GNU Make Compatibility: ensure recipes remain compatible with GNU Make 3.81).
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
  - `devenv_brew_bin` not found on Linux hosts without Linuxbrew: Mitigated by providing fallback path resolution and
    guarding the Homebrew Go installation task with conditional checks.
  - Neovim lockfile test failures if newly required plugins are not pinned or missing from documentation: Mitigated by
    locking all 6 plugins to valid 40-character commit hashes in `nvim-pack-lock.json` and adding corresponding entries
    to `README.md`.
  - Tmux comment-only test failure: Mitigated by explicitly updating the test in `tests/test_manifest.py` to assert the
    smart pane switching configuration.
- **Mitigations built into the plan:**
  - Explicit 40-character SHA pinning in `nvim-pack-lock.json`.
  - Declarative FQCN modules in Ansible (`community.general.homebrew`, `ansible.builtin.stat`,
    `ansible.builtin.set_fact`).
  - Guarded shell PATH modifications checking directory existence before mutating `PATH`.
  - Verification across all quality gates (`pytest`, `ruff`, `ansible-lint`, `prettier`).
- **Residual risk accepted (and why):**
  - Minimal residual risk: all changes use proven configuration patterns established elsewhere in the repository.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.08
- **Budget Compliance:** The plan entropy of 0.08 is well within the budget limit (`0.08 <= 10.0`).

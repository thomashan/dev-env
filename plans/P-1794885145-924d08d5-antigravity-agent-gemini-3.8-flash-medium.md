# Plan for I-1794885128-factory-defaults

- **Plan ID:** P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794885128-factory-defaults
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-17T03:12:33Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent cleanly decouples tracked developer configs from personal
  workstation state and non-standard plugin overrides, resetting TMUX, Neovim (kickstart, lazyvim, minimal), Conda, and
  shells (fish, bash, zsh) to upstream factory defaults while maintaining required Stow/runtime symlink wiring and test
  manifest coverage.
- **Exploration stance:** Focused exploit with deterministic verification across all configuration domains and test
  manifests.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Runtime & environment
  specification, GNU Stow packaging, multi-variant Neovim architecture, zero loose dotfiles, local override hooks),
  `holon-config/world/ruleset.md` §2 (Coding conventions, PEP 8, backtick arithmetic code spans for Prettier),
  `holon-config/world/ruleset.md` §3 (pytest verification under `tests/`), and `holon-config/world/constraints.md`
  §1-§5.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** All steps are deterministic configuration resets, file cleanups, manifest registrations, and test
  invariants.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.25  |
| impact_pred         | 92.0  |
| cost_pred           | 7.0   |
| learning_value_pred | 4.0   |
| ev_pred             | 86.01 |

---

## Step 1: Reset TMUX Configuration to Upstream Factory Defaults

- **Sub‑intent recommendation:** NO
- **Reasoning:** Replaces all custom tmux options and keybindings with a clean comment-only stub at the standard XDG
  location (`dotfiles/tmux/.config/tmux/tmux.conf`), preserving Stow symlink wiring while running purely vanilla tmux
  behavior.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Removing all overrides from `tmux.conf` restores vanilla tmux keybindings (standard
  prefix `C-b`, default `%` and `"` splits, default status bar position and indexing) without breaking GNU Stow or
  Ansible link verification.
- **Learning target:** Confirm that a comment-only tmux configuration satisfies both runtime syntax parsing and manifest
  invariants.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:** In `dotfiles/tmux/.config/tmux/tmux.conf`:
  1. Remove all custom settings:
     - `default-terminal "tmux-256color"` and `terminal-overrides`
     - `history-limit 50000`, `escape-time 10`, `focus-events on`, `mouse on`
     - `base-index 1`, `pane-base-index 1`, `renumber-windows on`, `set-titles on`, `automatic-rename on`
     - Split bindings (`bind | split-window ...`, `bind - split-window ...`)
     - Pane navigation bindings (`bind -r h ...`, `j`, `k`, `l`)
     - Status position override (`set -g status-position top`)
  2. Write a clean, informative comment-only factory default `tmux.conf` noting that upstream defaults are in effect and
     machine-local customizations should be placed in unversioned user configs.
- **Git branch:**
  `I-1794885128-factory-defaults/P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium/E-1-tmux-factory-defaults/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Modify `dotfiles/tmux/.config/tmux/tmux.conf`:
   - Strip all active `set`, `setw`, and `bind` commands.
   - Maintain introductory comments noting that tmux reads the XDG config path `~/.config/tmux/tmux.conf` (tmux >= 3.1)
     and adheres to vanilla factory defaults.
2. Verification:
   - Run `tmux -f dotfiles/tmux/.config/tmux/tmux.conf -C new-session -d` or inspect the file to ensure no syntax errors
     or active keybindings exist.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (project layout and Stow packaging),
  `holon-config/world/constraints.md` §3 (manifest links).
- **Potential failure modes for this step:** Accidental deletion of the `tmux.conf` file instead of content replacement,
  which would break Stow symlink mappings.
- **Guardrails and early‑abort checks:** Ensure the file continues to exist at `dotfiles/tmux/.config/tmux/tmux.conf`.

### Success & Discard Criteria

- **Success:** `dotfiles/tmux/.config/tmux/tmux.conf` contains only descriptive comments and zero active
  options/bindings.
- **Discard:** Retaining any custom split binding or status position override.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 0.5   |
| ev_pred             | 90.82 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 0.5 - 0.3 * 0.02 - 0.5 = 91.08 + 0.25 - 0.006 - 0.5 = 90.824 ~ 90.82`.

---

## Step 2: Reset Neovim Kickstart to Upstream Factory Defaults & Align Lockfile

- **Sub‑intent recommendation:** NO
- **Reasoning:** Removes non-upstream plugin configurations and entries from Kickstart, unlinks deleted custom plugin
  files from Ansible's manifest, comments out optional plugin requires in `init.lua`, purges 7 non-default plugins from
  `nvim-pack-lock.json`, and updates `README.md` to reflect the 19 factory-default plugins.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Pruning custom plugins to the pure 19 upstream `kickstart.nvim` plugins guarantees
  reproducible vanilla Neovim Kickstart installations and satisfies `test_nvim_lockfile_covers_every_declared_plugin`
  and `test_readme_manifest_coverage`.
- **Learning target:** Ensure `nvim-pack-lock.json` exact set alignment with `README.md` and active plugin declarations.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:**
  1. Delete files:
     - `dotfiles/nvim-kickstart/.config/nvim/lua/custom/plugins/diffview.lua`
     - `dotfiles/nvim-kickstart/.config/nvim/lua/custom/plugins/render-markdown.lua`
  2. In `ansible/group_vars/all.yml`:
     - Remove `dotfiles/nvim-kickstart/.config/nvim/lua/custom/plugins/diffview.lua` and
       `dotfiles/nvim-kickstart/.config/nvim/lua/custom/plugins/render-markdown.lua` from `devenv_links`.
  3. In `dotfiles/nvim-kickstart/.config/nvim/init.lua`:
     - Comment out `require 'kickstart.plugins.neo-tree'` to `-- require 'kickstart.plugins.neo-tree'`
     - Comment out `require 'custom.plugins'` to `-- require 'custom.plugins'`
  4. In `dotfiles/nvim-kickstart/.config/nvim/nvim-pack-lock.json`:
     - Remove the 7 non-default plugins: `diffview.nvim`, `render-markdown.nvim`, `neo-tree.nvim`, `nui.nvim`,
       `fzf-lua`, `mini.completion`, and `quicker.nvim`.
     - Retain exactly the 19 upstream `kickstart.nvim` factory-default plugins: `LuaSnip`, `blink.cmp`, `conform.nvim`,
       `fidget.nvim`, `gitsigns.nvim`, `guess-indent.nvim`, `mason-lspconfig.nvim`, `mason-tool-installer.nvim`,
       `mason.nvim`, `mini.nvim`, `nvim-lspconfig`, `nvim-treesitter`, `plenary.nvim`, `telescope-fzf-native.nvim`,
       `telescope-ui-select.nvim`, `telescope.nvim`, `todo-comments.nvim`, `tokyonight.nvim`, `which-key.nvim`.
  5. In `README.md` (`### 5. Neovim Plugins`):
     - Update heading description to specify 19 plugins (down from 26).
     - Remove the 7 purged plugins and renumber the list 1 to 19.
- **Git branch:**
  `I-1794885128-factory-defaults/P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium/E-2-kickstart-factory-defaults/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Delete `diffview.lua` and `render-markdown.lua` via filesystem remove.
2. Edit `ansible/group_vars/all.yml` to remove the corresponding dictionary entries under `devenv_links`.
3. In `dotfiles/nvim-kickstart/.config/nvim/init.lua`, comment out the calls to `require 'kickstart.plugins.neo-tree'`
   and `require 'custom.plugins'`.
4. Edit `dotfiles/nvim-kickstart/.config/nvim/nvim-pack-lock.json` and remove keys `diffview.nvim`, `fzf-lua`,
   `mini.completion`, `neo-tree.nvim`, `nui.nvim`, `quicker.nvim`, and `render-markdown.nvim`.
5. Update `README.md` section 5 with the 19 remaining plugins and their metadata.
6. Verify JSON formatting and validate lockfile integrity with
   `uv run --extra test pytest tests/test_manifest.py -k test_nvim_lockfile`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (manifest consistency), §2 (Prettier markdown formatting),
  `holon-config/world/constraints.md` §3 (no unmanaged state).
- **Potential failure modes for this step:** Discrepancy between declared plugins in Lua files and locked plugins in
  `nvim-pack-lock.json`, or orphaned entries in `devenv_links`.
- **Guardrails and early‑abort checks:** Run `pytest tests/test_manifest.py` to confirm all dotfiles are linked and all
  active plugins are locked.

### Success & Discard Criteria

- **Success:** Exactly 19 plugins in `nvim-pack-lock.json`, matching `README.md`, zero custom plugin files remaining
  beyond `init.lua`, and test pass.
- **Discard:** Retaining any of the 7 non-default plugins in the lockfile or leaving unlinked files in
  `custom/plugins/`.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.06  |
| impact_pred         | 92.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 1.0   |
| ev_pred             | 90.06 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 1.0 - 0.3 * 0.06 - 1.5 = 91.08 + 0.50 - 0.018 - 1.5 = 90.062 ~ 90.06`.

---

## Step 3: Align Neovim LazyVim with Upstream Starter & Register Manifest Links

- **Sub‑intent recommendation:** NO
- **Reasoning:** Disables active plugin overrides in `dotfiles/nvim-lazyvim/.config/nvim/lua/plugins/example.lua` to
  match canonical `LazyVim/starter` defaults, adds the standard `autocmds.lua` stub, and registers it in the Ansible
  dynamic variant link manifest.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Conforming `nvim-lazyvim` to upstream `LazyVim/starter` ensures out-of-the-box LazyVim
  behavior without unexpected local overrides, and registering `autocmds.lua` ensures Ansible correctly links the full
  starter configuration.
- **Learning target:** Verify multi-variant dynamic link generation in `ansible/roles/bootstrap/tasks/main.yml`.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:**
  1. In `dotfiles/nvim-lazyvim/.config/nvim/lua/plugins/example.lua`:
     - Update to match upstream `LazyVim/starter` specification, beginning with `if true then return {} end` so that no
       custom plugin overrides or extra packages are loaded by default.
  2. Create `dotfiles/nvim-lazyvim/.config/nvim/lua/config/autocmds.lua`:
     - Provide the upstream `LazyVim/starter` comment stub for user autocmd customization:
       `-- Autocmds are automatically loaded on the VeryLazy event`
       `-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua`
       `-- Add any additional autocmds here`
  3. In `ansible/roles/bootstrap/tasks/main.yml`:
     - Under task `Update link manifest for lazyvim nvim variant`, add the link item for `autocmds.lua`:
       `{'src': 'dotfiles/nvim-lazyvim/.config/nvim/lua/config/autocmds.lua', 'dest': devenv_home ~ '/.config/nvim/lua/config/autocmds.lua'}`.
- **Git branch:**
  `I-1794885128-factory-defaults/P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium/E-3-lazyvim-factory-defaults/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Modify `dotfiles/nvim-lazyvim/.config/nvim/lua/plugins/example.lua` to start with `if true then return {} end`
   followed by upstream explanatory comments.
2. Create `dotfiles/nvim-lazyvim/.config/nvim/lua/config/autocmds.lua` with the upstream comment stub.
3. Update `ansible/roles/bootstrap/tasks/main.yml` to include `autocmds.lua` in the `devenv_links` list when
   `devenv_active_nvim_variant == 'lazyvim'`.
4. Validate that `uv run --extra test ansible-lint ansible/site.yml` passes and YAML indentation is clean.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-variant Stow packaging and link manifests), §2 (Ansible
  standards).
- **Potential failure modes for this step:** Misalignment between `dotfiles/` files and the variant link manifest in
  Ansible bootstrap tasks.
- **Guardrails and early‑abort checks:** Confirm all files in `dotfiles/nvim-lazyvim/` are represented in the Ansible
  variant linking task.

### Success & Discard Criteria

- **Success:** `example.lua` starts with early return; `autocmds.lua` exists; `autocmds.lua` is registered in
  `ansible/roles/bootstrap/tasks/main.yml`.
- **Discard:** Leaving active custom plugins loaded in `example.lua` or omitting `autocmds.lua` from Ansible links.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.04  |
| impact_pred         | 92.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 0.5   |
| ev_pred             | 90.32 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 0.5 - 0.3 * 0.04 - 1.0 = 91.08 + 0.25 - 0.012 - 1.0 = 90.318 ~ 90.32`.

---

## Step 4: Reset Neovim Minimal to Vanilla Upstream Factory Defaults

- **Sub‑intent recommendation:** NO
- **Reasoning:** Converts `dotfiles/nvim-minimal/.config/nvim/init.lua` to a clean comment-only configuration file,
  stripping all custom options, keybindings, and autocmds so that selecting the `minimal` variant provides pure,
  unmodified Neovim default behavior.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** A comment-only `init.lua` preserves variant linkability and file presence while allowing
  vanilla Neovim core defaults to govern the editing session.
- **Learning target:** Verify that minimal variant invariants pass when `init.lua` contains no custom Lua statements.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:**
  1. In `dotfiles/nvim-minimal/.config/nvim/init.lua`:
     - Remove all custom `vim.opt` settings (`number`, `relativenumber`, `mouse`, `showmode`, `clipboard`,
       `breakindent`, `undofile`, `ignorecase`, `smartcase`, `signcolumn`, `updatetime`, `timeoutlen`, `splitright`,
       `splitbelow`, `list`, `listchars`, `inccommand`, `cursorline`, `scrolloff`, `expandtab`, `shiftwidth`,
       `tabstop`).
     - Remove leader key assignments (`vim.g.mapleader`, `vim.g.maplocalleader`).
     - Remove custom keymaps (`<Esc>`, `<leader>q`, `<Esc><Esc>`, window navigations `<C-h>/<C-j>/<C-k>/<C-l>`).
     - Remove custom autocmds (`minimal-highlight-yank`).
     - Replace with a clean, comment-only factory-default header explaining that this variant runs pure vanilla Neovim
       without custom options or mappings.
- **Git branch:**
  `I-1794885128-factory-defaults/P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium/E-4-minimal-factory-defaults/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Rewrite `dotfiles/nvim-minimal/.config/nvim/init.lua` to contain solely descriptive comments.
2. Confirm that the file exists and is readable by Neovim without syntax errors or warnings.
3. Validate against test invariants requiring `init.lua` presence for variants.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (variant packaging requires `init.lua` in each variant).
- **Potential failure modes for this step:** Deleting `init.lua` rather than replacing its contents, which would violate
  `test_package_variants_structure_and_invariants`.
- **Guardrails and early‑abort checks:** Ensure `init.lua` remains an existing regular file.

### Success & Discard Criteria

- **Success:** `dotfiles/nvim-minimal/.config/nvim/init.lua` contains zero active code statements and 100% comments.
- **Discard:** Retaining any active `vim.opt`, `vim.keymap`, or `vim.api` call in the minimal config.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 0.5   |
| ev_pred             | 90.82 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 0.5 - 0.3 * 0.02 - 0.5 = 91.08 + 0.25 - 0.006 - 0.5 = 90.824 ~ 90.82`.

---

## Step 5: Reset Conda Configuration to Miniforge Upstream Factory Defaults

- **Sub‑intent recommendation:** NO
- **Reasoning:** Resets `dotfiles/conda/.condarc` to upstream Miniforge factory defaults
  (`channels:\n  - conda-forge\n`), stripping custom agent overrides (`channel_priority: strict`,
  `auto_activate_base: false`, `changeps1: false`, `always_yes: false`, `notify_outdated_conda: false`).
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Miniforge defaults with only `channels: [conda-forge]` satisfy Conda standard behavior
  and Ansible/Stow link integrity while removing non-standard local configurations.
- **Learning target:** Verify that stripping `.condarc` overrides leaves Conda CLI operations completely intact.
- **Maximum acceptable cost for this learning:** 0.5

### Intent & Git Integration

- **Step Intent:**
  1. In `dotfiles/conda/.condarc`:
     - Replace existing file contents with upstream Miniforge defaults: `channels:` `  - conda-forge`
     - Remove `channel_priority: strict`.
     - Remove `auto_activate_base: false`.
     - Remove `changeps1: false`.
     - Remove `always_yes: false`.
     - Remove `notify_outdated_conda: false`.
- **Git branch:**
  `I-1794885128-factory-defaults/P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium/E-5-conda-factory-defaults/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Rewrite `dotfiles/conda/.condarc` to specify only `channels: [conda-forge]` with clear explanatory comments on
   Miniforge upstream defaults.
2. Verify YAML validity using Python or YAML parser.
3. Check that `dotfiles/conda/.condarc` remains in `devenv_links` in `ansible/group_vars/all.yml`.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Conda configuration must be repo-managed).
- **Potential failure modes for this step:** Indentation error in YAML syntax or missing channel configuration.
- **Guardrails and early‑abort checks:** Parse `.condarc` with `yaml.safe_load`.

### Success & Discard Criteria

- **Success:** `.condarc` contains only `channels: [conda-forge]` and descriptive comments; no custom overrides remain.
- **Discard:** Retaining any removed flag (`channel_priority`, `auto_activate_base`, etc.).

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.02  |
| impact_pred         | 92.0  |
| cost_pred           | 0.5   |
| learning_value_pred | 0.5   |
| ev_pred             | 90.82 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 0.5 - 0.3 * 0.02 - 0.5 = 91.08 + 0.25 - 0.006 - 0.5 = 90.824 ~ 90.82`.

---

## Step 6: Purge Host-Specific Paths, Pager Overrides, and SDKMAN Stubs from Shell Configurations

- **Sub‑intent recommendation:** NO
- **Reasoning:** Cleanses shell configurations (`config.fish`, `00-devenv.fish`, `.bashrc`, `.zshrc`) by removing
  personal workstation paths (`.docker`, `.lmstudio`, `.antigravity-ide`), stripping editor/pager environment variable
  overrides from fish defaults, and removing SDKMAN initialization blocks from bash and zsh while preserving critical
  runtime wiring (`XDG_*`, `nvm`, `~/.local/bin`, `brew`, `conda`, and local hooks).
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Shell configurations stripped of personal host paths and SDKMAN initialization remain
  fully functional across Darwin and Linux, adhere strictly to multi-OS rules, and allow users to configure personal
  tools in unmanaged `.local` hooks.
- **Learning target:** Validate that removing SDKMAN and tool path loops does not disrupt existing nvm/Conda/Brew PATH
  ordering across bash, zsh, and fish.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:**
  1. In `dotfiles/fish/.config/fish/config.fish`:
     - Remove the tool loop adding `$HOME/.docker/bin`, `$HOME/.lmstudio/bin`, and
       `$HOME/.antigravity-ide/antigravity-ide/bin`.
  2. In `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`:
     - Remove `fish_greeting`, `EDITOR`, `VISUAL`, `PAGER`, and `GIT_PAGER` overrides.
     - Retain strictly:
       - `set -g devenv_node_default_version 22.23.2`
       - OS and architecture detection (`devenv_os`, `devenv_arch`)
       - nvm configuration (`nvm_data`, `nvm_mirror`, `nvm_default_version`)
  3. In `dotfiles/bash/.bashrc`:
     - Remove personal tool loop adding `$HOME/.docker/bin`, `$HOME/.lmstudio/bin`, and
       `$HOME/.antigravity-ide/antigravity-ide/bin`.
     - Remove custom SDKMAN initialization block (`SDKMAN_DIR`, `sdkman-init.sh`).
     - Retain standard `XDG_*`, nvm PATH precedence (`$XDG_DATA_HOME/nvm/current/bin` and `$HOME/.local/bin`), Homebrew
       / Linuxbrew `shellenv`, Conda shell hook probe, and local override hook (`~/.bashrc.local`).
  4. In `dotfiles/zsh/.zshrc`:
     - Remove personal tool loop adding `$HOME/.docker/bin`, `$HOME/.lmstudio/bin`, and
       `$HOME/.antigravity-ide/antigravity-ide/bin`.
     - Remove custom SDKMAN initialization block (`SDKMAN_DIR`, `sdkman-init.sh`).
     - Retain standard `XDG_*`, nvm PATH precedence, Homebrew / Linuxbrew `shellenv`, Conda shell hook probe, and local
       override hook (`~/.zshrc.local`).
- **Git branch:**
  `I-1794885128-factory-defaults/P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium/E-6-shell-defaults-cleanup/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Remove personal binary directory loops from `config.fish`, `.bashrc`, and `.zshrc`.
2. Delete the `# --- editor / pager defaults ---` section from `00-devenv.fish`.
3. Delete the `# --- SDKMAN ---` case statements from `.bashrc` and `.zshrc`.
4. Ensure line endings and comment headers remain clean, readable, and properly formatted.
5. Verify syntax with shell linters or shell dry-runs (`bash -n dotfiles/bash/.bashrc`, `zsh -n dotfiles/zsh/.zshrc`).

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rules, local override hooks),
  `holon-config/world/constraints.md` §3 (no touching unmanaged state).
- **Potential failure modes for this step:** Breaking `devenv_node_default_version` pin parsing by altering its syntax
  in `00-devenv.fish`.
- **Guardrails and early‑abort checks:** Keep `set -g devenv_node_default_version 22.23.2` untouched and run
  `pytest tests/test_manifest.py -k test_node_pin` immediately.

### Success & Discard Criteria

- **Success:** No occurrences of `.docker`, `.lmstudio`, `.antigravity-ide`, `SDKMAN`, `GIT_PAGER`, or `VISUAL` in
  tracked shell dotfiles; node version pin remains intact.
- **Discard:** Any residual personal workstation paths in shell configs or broken nvm PATH wiring.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.05  |
| impact_pred         | 92.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 0.5   |
| ev_pred             | 89.82 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 0.5 - 0.3 * 0.05 - 1.5 = 91.08 + 0.25 - 0.015 - 1.5 = 89.815 ~ 89.82`.

---

## Step 7: Update Verification Suite with Factory Default Invariants and Execute Test Pipeline

- **Sub‑intent recommendation:** NO
- **Reasoning:** Adapts existing tests in `tests/test_manifest.py` to match the cleaned configurations, adds dedicated
  manifest tests codifying factory default invariants (zero personal paths, comment-only tmux and nvim-minimal configs,
  clean kickstart plugins directory, disabled lazyvim example plugin), and executes full CI verification suite.
- **Step Type:** TEST
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Codifying factory default invariants in `tests/test_manifest.py` prevents future
  regressions from reintroducing host-specific paths or personal dotfile overrides into version-controlled files.
- **Learning target:** Ensure all linter, schema, documentation, and manifest tests pass cleanly with 100% convergence.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:**
  1. In `tests/test_manifest.py`:
     - Update any existing tests checking removed lines in `.condarc` or `00-devenv.fish`.
     - Add new test functions asserting factory-default invariants across dotfiles:
       - Verify no file under `dotfiles/` contains personal path fragments (`.lmstudio`, `.antigravity-ide`).
       - Verify `dotfiles/tmux/.config/tmux/tmux.conf` contains no active configuration directives (only comments or
         empty lines).
       - Verify `dotfiles/nvim-minimal/.config/nvim/init.lua` contains no active Lua statements (only comments or empty
         lines).
       - Verify `dotfiles/nvim-kickstart/.config/nvim/lua/custom/plugins/` contains only `init.lua` (no active custom
         plugin files).
       - Verify `dotfiles/nvim-lazyvim/.config/nvim/lua/plugins/example.lua` begins with `if true then return {} end`
         (ignoring comments/whitespace/stylua pragmas).
  2. Execute the full verification suite:
     - `uv run --extra test pytest -m "not network"`
     - `uv run ruff check .`
     - `uv run --extra test ansible-lint ansible/site.yml`
     - `npx prettier --check "**/*.md"`
     - `make check`
- **Git branch:**
  `I-1794885128-factory-defaults/P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium/E-7-verification-suite-updates/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Add invariant tests in `tests/test_manifest.py`:
   - `test_dotfiles_contain_no_personal_paths()`: scans all text files in `dotfiles/` and asserts neither `.lmstudio`
     nor `.antigravity-ide` appears anywhere.
   - `test_tmux_conf_is_comment_only_factory_default()`: asserts every non-empty line starts with `#`.
   - `test_nvim_minimal_init_lua_is_comment_only()`: asserts every non-empty line starts with `--`.
   - `test_nvim_kickstart_custom_plugins_contains_only_init_lua()`: asserts list of files in `custom/plugins/` equals
     `{"init.lua"}`.
   - `test_nvim_lazyvim_example_starts_with_early_return()`: strips comments and asserts first executable line is
     `if true then return {} end`.
2. Format all modified python files with `uv run ruff format .` and lint with `uv run ruff check .`.
3. Format markdown files with `npx prettier --write "**/*.md"`.
4. Run test suites and verify exit code 0.

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (PEP 8, docstrings, typing), §3 (all test modifications
  declared in plan), `holon-config/world/constraints.md` §2 (process sandbox).
- **Potential failure modes for this step:** Test failure due to uncommitted formatting or unexpected lint warnings.
- **Guardrails and early‑abort checks:** Run `ruff` and `prettier` before final test assertion.

### Success & Discard Criteria

- **Success:** All 5 verification tools report 0 errors; all new invariant tests pass.
- **Discard:** Any test assertion failure or lint error.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.04  |
| impact_pred         | 92.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 0.5   |
| ev_pred             | 89.82 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 0.5 - 0.3 * 0.04 - 1.5 = 91.08 + 0.25 - 0.012 - 1.5 = 89.818 ~ 89.82`.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from the composite success probability across all seven steps (each step evaluated
  at 0.99). The modifications involve standardizing configuration files to upstream factory defaults, removing unneeded
  overrides, aligning the Ansible manifest, and augmenting pytest assertions with clear, deterministic checks.
- **entropy_pred**: 0.25. Calculated as the cumulative sum of step entropies across all seven steps
  (`0.02 + 0.06 + 0.04 + 0.02 + 0.02 + 0.05 + 0.04 = 0.25`). This is orders of magnitude below the process sandbox
  entropy limit of 10.0.
- **impact_pred**: 92.0. Eliminates personal workstation state, ensures clean upstream factory defaults across tmux,
  Neovim (kickstart, lazyvim, minimal), Conda, and shells, and codifies factory default invariants into automated pytest
  checks, making the environment completely reproducible and portable across new machines and user accounts.
- **cost_pred**: 7.0. Calculated as the direct sum of individual step costs
  (`0.5 + 1.5 + 1.0 + 0.5 + 0.5 + 1.5 + 1.5 = 7.0`).
- **learning_value_pred**: 4.0. Reflects the value of codifying factory default invariants in `test_manifest.py` and
  establishing clean multi-variant configuration boundaries for Neovim and shells.
- **ev_pred**: 86.01. Computed strictly using the system Expected Value formulation:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system weights `lambda = 0.3`
  and `mu = 0.5` from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 92.0 + 0.5 * 4.0 - 0.3 * 0.25 - 7.0 = 91.08 + 2.0 - 0.075 - 7.0 = 86.005 ~ 86.01`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: GNU Stow packaging, zero loose dotfiles,
    multi-variant Neovim architecture, local override hooks).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8 compliance, single-pass Prettier
    formatting with backtick code spans for arithmetic expressions).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, all test modifications explicitly declared
    during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow: branch naming conventions).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment: process sandbox entropy limit `< 10`).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: stow manifest links, no touching unmanaged
    state).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero edits to existing ledger entries).
- **Potential violations or edge cases:**
  - Accidental removal of essential runtime wiring: removing necessary PATH exports or nvm/Conda shell hook evaluation
    would break shell initialization. Mitigated by explicitly preserving `XDG_*`, `nvm`, `brew shellenv`, `conda hook`,
    and local `.local` hooks in Step 6.
  - Stow/Ansible link drift: deleting custom plugin files in Kickstart without removing them from `devenv_links` in
    `ansible/group_vars/all.yml` or adding `autocmds.lua` to `dotfiles/nvim-lazyvim/` without updating Ansible tasks
    would cause manifest check failures. Mitigated by coupling file changes with manifest updates in Steps 2 and 3.
  - Markdown formatting drift: unformatted tables or arithmetic formulas failing Prettier checks. Mitigated by wrapping
    all arithmetic calculations in backtick code spans and validating with `npx prettier --check "**/*.md"`.
- **Mitigations built into the plan:**
  - Step-by-step validation of each tool's configuration and manifest entries.
  - Addition of regression invariant tests in `tests/test_manifest.py` verifying no personal paths or custom overrides
    pollute the repo.
  - Final end-to-end verification via `pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check`.
- **Residual risk accepted (and why):**
  - Users who relied on personal overrides previously baked into the repo (e.g. `.docker/bin` or custom pane
    keybindings) will need to declare them in their unversioned `~/.bashrc.local`, `~/.zshrc.local`, or fish `local/`
    hooks; this is the intended design of the repository.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.25
- **Budget Compliance:** The plan entropy of 0.25 is well below the budget limit (`0.25 <= 10.0`).

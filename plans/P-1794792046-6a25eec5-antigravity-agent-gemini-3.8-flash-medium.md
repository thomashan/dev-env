# Plan for I-1794792028-stow

- **Plan ID:** P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794792028-stow
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-16T01:20:46Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent specifies a coherent, high-value migration to GNU Stow per-tool
  package architecture, explicit prerequisite validation, complete Neovim and shell config integration, and
  comprehensive documentation/tests.
- **Exploration stance:** balanced with targeted empirical verification of `stow --no-folding` behavior, relative
  symlink resolution, and multi-OS shell initialization.
- **Safety priority level:** standard
- **Priority Justification:** Triggered by `holon-config/world/ruleset.md` §1 (Multi-OS Darwin/Linux parity, GNU Make
  3.81 compatibility, no shell scripts outside package managers), `holon-config/world/ruleset.md` §2 (Coding
  conventions, static typing, Prettier markdown formatting with code-span arithmetic), `holon-config/world/ruleset.md`
  §3 (Testing constraints: pytest runner, explicit test modification declarations), `holon-config/world/constraints.md`
  §1 (Branch isolation and git flow), `holon-config/world/constraints.md` §3 (Environment mutation boundaries: converge
  through manifest, never write outside repo except through Ansible).

## Exploration

- **Proportion of steps that are exploratory:** 0.33
- **Justification:** Steps 2 and 3 incorporate exploratory validation of `stow --no-folding` symlink generation,
  ensuring non-folding directory behavior across nested `.config/` structures and relative path traversal.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.94  |
| entropy_pred        | 0.60  |
| impact_pred         | 95.0  |
| cost_pred           | 13.0  |
| learning_value_pred | 5.5   |
| ev_pred             | 78.87 |

---

## Step 1: Declare Stow as Core Package, Map Aliases, Probe in Makefile, and Enforce in Entrypoints

- **Sub‑intent recommendation:** NO
- **Reasoning:** Fundamental configuration step establishing GNU Stow as an explicit prerequisite across the Ansible
  manifest, package manager maps, Makefile targets, and playbook entry assertions.
- **Step Type:** CONFIG
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Declaring `stow` in `devenv_packages_core` and mapping `stow: stow` across both
  `pkg_brew.yml` and `pkg_apt.yml` guarantees availability prior to dotfile operations, while non-fatal probing in
  `make check` preserves CI runner compatibility.
- **Learning target:** Confirm prerequisite checking mechanics in GNU Make 3.81 and PATH resolution in Ansible tasks
  before playbook execution.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:** Add `stow` to `ansible/group_vars/all.yml` under `devenv_packages_core`; map `stow: stow` in
  `ansible/vars/pkg_brew.yml` and `ansible/vars/pkg_apt.yml`; update Makefile `check` target to probe `stow` with
  non-fatal warning; enforce `command -v stow` in `make dotfiles` and `make unlink`; add pre-flight `stow` assertions in
  `ansible/roles/dotfiles/tasks/main.yml` and `ansible/playbooks/unlink.yml`.
- **Git branch:**
  `I-1794792028-stow/P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium/E-1-stow-prerequisite-manifest/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Manifest and Package Aliases:
   - In `ansible/group_vars/all.yml`: append `stow` to the `devenv_packages_core` list.
   - In `ansible/vars/pkg_brew.yml`: map logical `stow` to Homebrew formula `stow`.
   - In `ansible/vars/pkg_apt.yml`: map logical `stow` to APT package `stow`.
2. Makefile Entrypoints and Probes:
   - In `Makefile` under the `check` target: add a probe for `stow` using `command -v stow`. If present, output
     `ok (<path>)`. If absent, increment `warn` count and output `will be installed by bootstrap (packages role)` so
     that cold-start `make check` on fresh CI runners remains non-fatal (exit code 0).
   - In `Makefile` under the `dotfiles` recipe: prepend a hard check
     `command -v stow >/dev/null 2>&1 || { echo "GNU Stow is required for dotfiles management. Run 'make converge' or install stow."; exit 1; }`.
   - In `Makefile` under the `unlink` recipe: prepend a hard check
     `command -v stow >/dev/null 2>&1 || { echo "GNU Stow is required for unlink. Please install stow first."; exit 1; }`.
3. Ansible Playbook and Role Assertions:
   - At the beginning of `ansible/roles/dotfiles/tasks/main.yml`: add an `ansible.builtin.command` task locating `stow`
     via `command -v stow` (with `changed_when: false` and `failed_when: false`), followed by an
     `ansible.builtin.assert` task confirming `stow` is executable on the controller PATH.
   - At the beginning of `ansible/playbooks/unlink.yml`: add matching `ansible.builtin.command` and
     `ansible.builtin.assert` tasks asserting `stow` presence on PATH with a clear failure message directing the user to
     install stow before attempting to remove dotfiles.

### Dependencies & Criticality

- **Depends on:** NONE
- **Is Bottleneck:** YES (Downstream dotfiles linking and unlinking steps strictly rely on Stow being declared and
  available)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, GNU Make 3.81 compatibility),
  `holon-config/world/constraints.md` §3 (Converge through the manifest: never install packages outside the manifest).
- **Potential failure modes for this step:** Broken Makefile tab formatting or unhandled exit codes causing CI runner
  failure.
- **Guardrails and early‑abort checks:** Ensure `make check` returns exit code 0 even when `stow` is missing, only
  raising warnings for uninstalled bootstrap items.

### Success & Discard Criteria

- **Success:** `stow` is declared in `devenv_packages_core` and mapped in both alias tables; `make check` probes stow
  cleanly; `make dotfiles` and `make unlink` refuse execution if stow is missing; pre-flight assertions are active in
  `dotfiles` role and `unlink.yml`.
- **Discard:** Discard if `make check` fails fatally on a runner lacking stow, or if package mapping diverges between
  Darwin and Linux.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.30  |
| impact_pred         | 85.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 3.0   |
| ev_pred             | 83.21 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 85.0 + 0.5 * 3.0 - 0.3 * 0.30 - 1.5 = 83.30 + 1.50 - 0.09 - 1.5 = 83.21`. High confidence
configuration step with low entropy and deterministic verification.

---

## Step 2: Restructure Dotfiles into Per-Tool Stow Packages and Integrate Host Neovim Config

- **Sub‑intent recommendation:** NO
- **Reasoning:** Core migration of the dotfiles repository layout into modular GNU Stow package trees (`bash`, `conda`,
  `fish`, `nvim`, `tmux`, `zsh`), integrating the host Neovim configuration and updating the declarative manifest.
- **Step Type:** REFACTOR
- **Exploration level:** BALANCED
- **Hypothesis being tested:** Structuring `dotfiles/` into discrete per-tool Stow package directories with zero loose
  files eliminates path coupling, allows granular tool stowage, and preserves non-folding symlink paths into `$HOME`.
- **Learning target:** Verify multi-OS POSIX shell initialization patterns (`Darwin)` vs `Linux)` Homebrew/Linuxbrew
  resolution) and Neovim module tree layout.
- **Maximum acceptable cost for this learning:** 2.5

### Intent & Git Integration

- **Step Intent:** Create directories `dotfiles/{bash,conda,fish,nvim,tmux,zsh}`; author multi-OS
  `dotfiles/bash/.bashrc` and `.bash_profile`; author multi-OS `dotfiles/zsh/.zshrc`; migrate `.condarc` to
  `dotfiles/conda/.condarc`; move Fish configs into `dotfiles/fish/.config/fish/`; copy staged host Neovim configs from
  `.cache/host-nvim/` to `dotfiles/nvim/.config/nvim/` (excluding `.git`/`.github`); move tmux config to
  `dotfiles/tmux/.config/tmux/tmux.conf`; remove legacy `dotfiles/.config` and `dotfiles/.condarc`; update
  `ansible/group_vars/all.yml` with `devenv_stow_packages` and updated `devenv_links`.
- **Git branch:**
  `I-1794792028-stow/P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium/E-2-stow-packages-layout/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Create Per-Tool Stow Directory Trees:
   - Establish directory structure: `dotfiles/bash/`, `dotfiles/conda/`, `dotfiles/fish/.config/fish/conf.d/`,
     `dotfiles/nvim/.config/nvim/`, `dotfiles/tmux/.config/tmux/`, and `dotfiles/zsh/`.
2. Bash Stow Package (`dotfiles/bash/`):
   - Create `dotfiles/bash/.bashrc`:
     - Detect OS via `case "$(uname -s)" in Darwin)` and `Linux)`.
     - On Darwin, initialize Homebrew environment by probing `/opt/homebrew/bin/brew` or `/usr/local/bin/brew` and
       running `eval "$(/path/to/brew shellenv)"`.
     - On Linux, evaluate Linuxbrew environment from `/home/linuxbrew/.linuxbrew/bin/brew` if present.
     - Prepend `$XDG_DATA_HOME/nvm/current/bin` (or `~/.local/share/nvm/current/bin`) and `$HOME/.local/bin` to `PATH`.
     - Append `$HOME/.docker/bin`, `$HOME/.lmstudio/bin`, and `$HOME/.antigravity-ide/antigravity-ide/bin` to `PATH` if
       the respective directories exist.
     - Probe Conda candidates (`$HOME/miniforge3`, `/opt/homebrew/Caskroom/miniforge/base`,
       `/usr/local/Caskroom/miniforge/base`) and execute `eval "$(/path/to/conda shell.bash hook)"`.
     - Initialize SDKMAN via `[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ] && . "$HOME/.sdkman/bin/sdkman-init.sh"`, or via
       Homebrew installed `brew --prefix sdkman-cli` under Darwin guard.
     - Source optional local override: `[ -f "$HOME/.bashrc.local" ] && . "$HOME/.bashrc.local"`.
     - Ensure zero hardcoded per-user `/Users/...` or literal `/home/...` (other than `/home/linuxbrew`) paths.
   - Create `dotfiles/bash/.bash_profile`:
     - Source `[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"`.
     - Source `[ -f "$HOME/.bash_profile.local" ] && . "$HOME/.bash_profile.local"`.
3. Zsh Stow Package (`dotfiles/zsh/`):
   - Create `dotfiles/zsh/.zshrc`:
     - Implement OS detection with `case "$(uname -s)" in Darwin)` and `Linux)` for Homebrew / Linuxbrew shellenv
       evaluation.
     - Prepend `$XDG_DATA_HOME/nvm/current/bin` and `$HOME/.local/bin` to `PATH`.
     - Append `$HOME/.docker/bin`, `$HOME/.lmstudio/bin`, and `$HOME/.antigravity-ide/antigravity-ide/bin` when present.
     - Probe Conda installation paths and execute `eval "$(/path/to/conda shell.zsh hook)"`.
     - Initialize SDKMAN with Darwin Homebrew guard or `$HOME/.sdkman`.
     - Source optional local override: `[ -f "$HOME/.zshrc.local" ] && . "$HOME/.zshrc.local"`.
4. Conda Stow Package (`dotfiles/conda/`):
   - Move `dotfiles/.condarc` to `dotfiles/conda/.condarc`.
5. Fish Stow Package (`dotfiles/fish/`):
   - Move `dotfiles/.config/fish/config.fish` to `dotfiles/fish/.config/fish/config.fish`.
   - Move `dotfiles/.config/fish/fish_plugins` to `dotfiles/fish/.config/fish/fish_plugins`.
   - Move `dotfiles/.config/fish/conf.d/00-devenv.fish` to `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
6. Neovim Stow Package (`dotfiles/nvim/`):
   - Copy tracked Neovim files from `.cache/host-nvim/` into `dotfiles/nvim/.config/nvim/`:
     - `init.lua`, `nvim-pack-lock.json`, `.stylua.toml`.
     - `lua/kickstart/health.lua`,
       `lua/kickstart/plugins/{autopairs.lua,debug.lua,indent_line.lua,lint.lua,neo-tree.lua}`.
     - `lua/custom/plugins/{init.lua,diffview.lua,render-markdown.lua}`.
   - Do NOT copy `.git` or `.github` from `.cache/host-nvim/`.
7. Tmux Stow Package (`dotfiles/tmux/`):
   - Move `dotfiles/.config/tmux/tmux.conf` to `dotfiles/tmux/.config/tmux/tmux.conf`.
8. Clean Legacy Directory State:
   - Remove legacy `dotfiles/.config` and `dotfiles/.condarc` so that zero files reside in `dotfiles/` outside declared
     Stow package folders.
9. Manifest Updates (`ansible/group_vars/all.yml`):
   - Define `devenv_stow_packages: [bash, conda, fish, nvim, tmux, zsh]`.
   - Update `devenv_links` to reflect the new package sources for every managed dotfile:
     - `dotfiles/bash/.bashrc` -> `{{ devenv_home }}/.bashrc`
     - `dotfiles/bash/.bash_profile` -> `{{ devenv_home }}/.bash_profile`
     - `dotfiles/zsh/.zshrc` -> `{{ devenv_home }}/.zshrc`
     - `dotfiles/conda/.condarc` -> `{{ devenv_home }}/.condarc`
     - `dotfiles/fish/.config/fish/config.fish` -> `{{ devenv_home }}/.config/fish/config.fish`
     - `dotfiles/fish/.config/fish/fish_plugins` -> `{{ devenv_home }}/.config/fish/fish_plugins`
     - `dotfiles/fish/.config/fish/conf.d/00-devenv.fish` -> `{{ devenv_home }}/.config/fish/conf.d/00-devenv.fish`
     - `dotfiles/nvim/.config/nvim/init.lua` -> `{{ devenv_home }}/.config/nvim/init.lua`
     - `dotfiles/nvim/.config/nvim/nvim-pack-lock.json` -> `{{ devenv_home }}/.config/nvim/nvim-pack-lock.json`
     - `dotfiles/nvim/.config/nvim/.stylua.toml` -> `{{ devenv_home }}/.config/nvim/.stylua.toml`
     - All 8 kickstart and custom lua plugin files under `dotfiles/nvim/.config/nvim/lua/...` mapped to
       `{{ devenv_home }}/.config/nvim/lua/...`
     - `dotfiles/tmux/.config/tmux/tmux.conf` -> `{{ devenv_home }}/.config/tmux/tmux.conf`

### Dependencies & Criticality

- **Depends on:** Step 1
- **Is Bottleneck:** YES (Stow symlink execution and testing depend on the package directory layout)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Multi-OS rule, no per-user hardcoded paths),
  `holon-config/world/constraints.md` §3 (Environment mutation boundaries).
- **Potential failure modes for this step:** Accidental copying of `.git` metadata from `.cache/host-nvim/` or missing
  links in `devenv_links`.
- **Guardrails and early‑abort checks:** Assert zero `.git` directory under `dotfiles/nvim/` and ensure every file in
  `dotfiles/` is tracked in `devenv_links`.

### Success & Discard Criteria

- **Success:** All files in `dotfiles/` belong to one of the 6 Stow packages; legacy root dotfiles files are removed;
  Neovim config from `.cache/host-nvim/` is migrated; all files are mapped in `devenv_links`.
- **Discard:** Discard if any untracked or legacy file remains directly under `dotfiles/`, or if hardcoded username
  paths leak into shell configs.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.96  |
| entropy_pred        | 0.50  |
| impact_pred         | 92.0  |
| cost_pred           | 2.5   |
| learning_value_pred | 4.5   |
| ev_pred             | 87.92 |

### Step Metrics Rationale

Calculated via: `EV = 0.96 * 92.0 + 0.5 * 4.5 - 0.3 * 0.50 - 2.5 = 88.32 + 2.25 - 0.15 - 2.5 = 87.92`. Significant
architectural improvement unifying package boundaries across tools and modernizing Neovim.

---

## Step 3: Refactor Ansible Dotfiles Role and Unlink Playbook to Execute stow --no-folding

- **Sub‑intent recommendation:** NO
- **Reasoning:** Core engine refactoring of dotfile deployment and teardown logic from manual file symlinks to GNU Stow
  invocation with `--no-folding`.
- **Step Type:** FEATURE
- **Exploration level:** BALANCED
- **Hypothesis being tested:** Invoking `stow --no-folding --restow` ensures idempotent relative symlinking for nested
  paths without directory folding, while parsing stderr `LINK:`/`UNLINK:` strings accurately reports task change status
  in normal and dry-run check modes.
- **Learning target:** Master GNU Stow `--no-folding` flag semantics, relative symlink resolution via Ansible
  stat/realpath filters, and check-mode `-n` dry-run behavior.
- **Maximum acceptable cost for this learning:** 3.0

### Intent & Git Integration

- **Step Intent:** Replace direct `ansible.builtin.file` loop in `ansible/roles/dotfiles/tasks/main.yml` with
  `stow --no-folding --restow`; handle stale symlink removal and real-file backups; support check mode with `-n`; update
  post-condition assertions to resolve relative symlinks against `devenv_repo_root`; refactor
  `ansible/playbooks/unlink.yml` to call `stow --delete`.
- **Git branch:**
  `I-1794792028-stow/P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium/E-3-dotfiles-stow-engine/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Dotfiles Role (`ansible/roles/dotfiles/tasks/main.yml`):
   - Assert `stow` binary is executable on PATH (from Step 1).
   - Retain source verification: check that all `item.src` files exist and are not directories.
   - Inspect existing destination paths via `ansible.builtin.stat`.
   - Backup unmanaged real files: if `item.stat.exists` and `not item.stat.islnk`, move to `{{ devenv_backup_dir }}`.
   - Stale symlink removal: if `item.stat.islnk` and the resolved link path (`(item.stat.lnk_source | default(''))` or
     realpath) does not match `{{ devenv_repo_root }}/{{ item.item.src }}`, remove the stale symlink with
     `ansible.builtin.file: state=absent` so Stow encounters no collision.
   - Execute Stow: invoke `ansible.builtin.command` running:
     `stow --no-folding --restow -v {{ '-n' if ansible_check_mode else '' }} -d "{{ devenv_repo_root }}/dotfiles" -t "{{ devenv_home }}" {{ devenv_stow_packages | join(' ') }}`
   - Detect changes: configure
     `changed_when: "'LINK:' in devenv_stow_result.stderr or 'UNLINK:' in devenv_stow_result.stderr"`.
   - Verify managed symlinks: inspect destination paths via `ansible.builtin.stat`. Assert that `item.stat.islnk` is
     true and
     `(item.stat.lnk_source if item.stat.lnk_source.startswith('/') else (item.dest | dirname ~ '/' ~ item.stat.lnk_source) | realpath)`
     starts with `devenv_repo_root` (allowing Stow's relative symlink format).
2. Unlink Playbook (`ansible/playbooks/unlink.yml`):
   - Locate and assert `stow` binary on PATH.
   - Check managed link status: inspect destination paths in `devenv_links`. Assert that any existing file is indeed a
     symlink pointing into `devenv_repo_root`.
   - Invoke `stow --delete`: run
     `stow --delete -v -d "{{ devenv_repo_root }}/dotfiles" -t "{{ devenv_home }}" {{ devenv_stow_packages | join(' ') }}`.
   - Report unlinked results cleanly.

### Dependencies & Criticality

- **Depends on:** Step 1, Step 2
- **Is Bottleneck:** YES (The dotfiles converge and unlink workflows depend entirely on this engine)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/constraints.md` §3 (Destructive operations, make unlink requires confirmation,
  never write outside repo except through Ansible).
- **Potential failure modes for this step:** Stow failing due to directory folding collisions or relative symlink
  assertion mismatches in Ansible.
- **Guardrails and early‑abort checks:** The `--no-folding` flag prevents Stow from collapsing directories into
  symlinks, and stale symlink pre-cleaning prevents conflict aborts.

### Success & Discard Criteria

- **Success:** Running `make dotfiles` links all package dotfiles via relative symlinks into `$HOME`; check mode reports
  changes cleanly; `ansible/playbooks/unlink.yml` removes symlinks reversibly.
- **Discard:** Discard if Stow folds any parent directories (e.g. symlinking `~/.config/fish` instead of individual
  files) or if dry run modifies filesystem state.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.95  |
| entropy_pred        | 0.60  |
| impact_pred         | 95.0  |
| cost_pred           | 3.0   |
| learning_value_pred | 5.0   |
| ev_pred             | 89.57 |

### Step Metrics Rationale

Calculated via: `EV = 0.95 * 95.0 + 0.5 * 5.0 - 0.3 * 0.60 - 3.0 = 90.25 + 2.50 - 0.18 - 3.0 = 89.57`. Highest impact
technical step establishing safe, idempotent Stow execution with rigorous pre- and post-condition checks.

---

## Step 4: Update Role References, Fish Shell Config, .gitignore, and Test Invariants

- **Sub‑intent recommendation:** NO
- **Reasoning:** Necessary refactoring of repository path references across roles, shell files, `.gitignore`, and the
  test suite to match the new Stow package hierarchy and enforce new structural invariants.
- **Step Type:** FIX
- **Exploration level:** BALANCED
- **Hypothesis being tested:** Updating all file-path references and extending test assertions guarantees that the new
  Stow package layout is enforced across all roles and that any future unmanaged or hardcoded path will be caught
  immediately.
- **Learning target:** Master Lua Neovim plugin declaration parsing (`gh 'owner/repo'` helper syntax alongside HTTPS
  URLs) and multi-shell OS detection verification.
- **Maximum acceptable cost for this learning:** 2.5

### Intent & Git Integration

- **Step Intent:** Update role path references in `node`, `neovim`, and `conda` tasks; update
  `dotfiles/fish/.config/fish/config.fish` header; update `.gitignore` paths for fish local state; update test paths in
  `tests/test_manifest.py` and `tests/test_templating.py`; adapt `test_dotfiles_hardcode_no_per_user_paths` for
  `Darwin)`; adapt `test_nvim_lockfile_covers_every_declared_plugin` for `gh` helper and URLs; add tests for Stow
  package alignment, Makefile probe, and README manifest coverage.
- **Git branch:**
  `I-1794792028-stow/P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium/E-4-test-and-reference-updates/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Role References Updates:
   - In `ansible/roles/node/tasks/main.yml`: update file path from `dotfiles/.config/fish/conf.d/00-devenv.fish` to
     `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`. Also update error messages and fisher plugin sync paths to
     `dotfiles/fish/.config/fish/fish_plugins`.
   - In `ansible/roles/neovim/tasks/main.yml`: update message references from `dotfiles/.config/nvim/init.lua` to
     `dotfiles/nvim/.config/nvim/init.lua`.
   - In `ansible/roles/conda/tasks/main.yml`: update comment references from `dotfiles/.config/fish/config.fish` to
     `dotfiles/fish/.config/fish/config.fish`.
   - In `dotfiles/fish/.config/fish/config.fish`: update header comments and candidate paths if necessary.
2. Gitignore Updates:
   - Update `.gitignore` to prefix fish state paths with `dotfiles/fish/`:
     - `dotfiles/fish/.config/fish/local/`
     - `dotfiles/fish/.config/fish/fish_variables`
     - `dotfiles/fish/.config/fish/completions/`
     - `dotfiles/fish/.config/fish/functions/`
     - `dotfiles/fish/.config/fish/conf.d/sdk.fish`
     - `dotfiles/fish/.config/fish/conf.d/nvm.fish`
3. Test Suite Path Updates:
   - In `tests/test_templating.py`: update path in `test_node_pin_is_parsed_from_the_real_fish_config` to
     `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
   - In `tests/test_manifest.py`:
     - Update `MACHINE_LOCAL_FISH` and `FISHER_PAYLOADS` directory root in
       `test_dotfiles_contain_no_machine_local_fish_state` to `dotfiles/fish/.config/fish`.
     - In `test_conda_path_parity_between_ansible_and_fish`: update path to `dotfiles/fish/.config/fish/config.fish`.
     - In `test_node_pin_is_declared_exactly_once_and_well_formed`: update path to
       `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
     - In `test_node_bin_is_first_on_path`: update path to `dotfiles/fish/.config/fish/config.fish`.
4. Multi-OS Guard Test Enhancement:
   - In `test_dotfiles_hardcode_no_per_user_paths`: update check for macOS brew paths (`/opt/homebrew`,
     `/usr/local/bin/brew`) to accept either POSIX shell syntax (`Darwin)`) or Fish syntax (`case Darwin`).
5. Neovim Plugin Lockfile Test Enhancement:
   - In `test_nvim_lockfile_covers_every_declared_plugin`: update to search across `dotfiles/nvim/.config/nvim/init.lua`
     and all `dotfiles/nvim/.config/nvim/lua/**/*.lua` files. Filter out comment lines (`--`). Parse both
     `gh\s*['"]([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)['"]` (mapping to `https://github.com/{match}`) and standard URL
     declarations `'https://github.com/...'. Verify all declared plugins are present in `nvim-pack-lock.json` with
     40-character commit revisions.
6. New Manifest and Structural Invariant Tests:
   - Test (a): Assert `stow` is present in `devenv_packages_core`.
   - Test (b): Assert `Makefile` `check` target contains a probe for `stow`.
   - Test (c): Assert `devenv_stow_packages` in `group_vars/all.yml` matches the set of directory names under
     `dotfiles/` (`bash`, `conda`, `fish`, `nvim`, `tmux`, `zsh`).
   - Test (d): Assert every tracked file under `dotfiles/` resides within one of the declared Stow packages and is
     mapped in `devenv_links`.
   - Test (e): Assert `README.md` explicitly lists every logical package in `devenv_packages_core`, every tool in
     `devenv_uv_tools`, every plugin in `fish_plugins`, and every plugin in `nvim-pack-lock.json`.

### Dependencies & Criticality

- **Depends on:** Step 2, Step 3
- **Is Bottleneck:** YES (Quality gates in pytest cannot pass until test expectations reflect the new layout)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §3 (All test modifications explicitly declared during planning),
  `holon-config/world/ruleset.md` §2 (PEP 8, docstrings).
- **Potential failure modes for this step:** Incomplete plugin regex matching or broken path parsing.
- **Guardrails and early‑abort checks:** Run `pytest tests/` continuously to ensure test updates align precisely with
  the codebase.

### Success & Discard Criteria

- **Success:** Pytest passes with 100% success on all manifest and templating tests; all new structural invariant tests
  pass; Neovim plugin lockfile parser correctly maps both `gh` helpers and URLs.
- **Discard:** Discard if any test failure remains or if any file in `dotfiles/` is unvalidated.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.94  |
| entropy_pred        | 0.50  |
| impact_pred         | 90.0  |
| cost_pred           | 2.5   |
| learning_value_pred | 4.0   |
| ev_pred             | 83.95 |

### Step Metrics Rationale

Calculated via: `EV = 0.94 * 90.0 + 0.5 * 4.0 - 0.3 * 0.50 - 2.5 = 84.60 + 2.00 - 0.15 - 2.5 = 83.95`. Restores test
suite green status while expanding invariant enforcement to prevent regressions.

---

## Step 5: Synchronize World Model Rules, Constraints, and Author Comprehensive Reference Documentation in README.md

- **Sub‑intent recommendation:** NO
- **Reasoning:** Essential alignment of project world documentation and public-facing reference guides with the
  implemented Stow package architecture and tool manifests.
- **Step Type:** DOCS
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicitly documenting all prerequisites, bare git worktree patterns, and per-tool tables
  in `README.md`, `ruleset.md`, and `constraints.md` satisfies all manifest coverage tests and guarantees human/agent
  onboarding transparency.
- **Learning target:** Codify bare `.git` + worktree developer workflow patterns and structured markdown manifest tables
  adhering to single-pass Prettier formatting.
- **Maximum acceptable cost for this learning:** 2.0

### Intent & Git Integration

- **Step Intent:** Update `README.md`, `holon-config/world/constraints.md`, and `holon-config/world/ruleset.md` to
  document bare `.git` + worktree layout, `stow` as explicit prerequisite, `stow --no-folding` per-tool architecture,
  and `.local` override hooks; add comprehensive reference tables in `README.md` covering all 22 core CLI packages,
  bootstrap tooling, runtimes, uv tools, fish plugins, Neovim plugins, and removed packages.
- **Git branch:**
  `I-1794792028-stow/P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium/E-5-documentation-manifest-sync/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. World Constraints & Ruleset Updates:
   - In `holon-config/world/constraints.md`: Document bare `.git` + worktree repository structure (`dev-env/.git`,
     `dev-env/main`, `dev-env/<worktree>`); document Stow as prerequisite for dotfile management; record per-tool Stow
     package boundaries (`bash`, `conda`, `fish`, `nvim`, `tmux`, `zsh`) with `stow --no-folding`.
   - In `holon-config/world/ruleset.md`: Document Stow packaging convention under `dotfiles/<pkg>/`; specify `.local`
     override hooks (`.bashrc.local`, `.bash_profile.local`, `.zshrc.local`, `conf.d/*.fish`) for machine-local
     configurations.
2. README.md Documentation Overhaul:
   - Architecture & Layout:
     - Document bare `.git` + worktree repository layout and clone instructions.
     - Document GNU Stow prerequisite and explanation of `stow --no-folding --restow`.
     - Document `.local` override hooks in bash, zsh, and fish.
   - Reference Table 1: Prerequisites & Bootstrap Tooling:
     - Cold-start host prerequisites checked by `make check`: `GNU Make >= 3.81`, `git`, `curl`, `apt-get` (Linux).
     - Bootstrap tools installed by `make bootstrap`: `uv`, `ansible-core` (Python 3.13), `ansible-lint` (Python 3.13),
       `community.general >= 9.0.0`.
     - Dotfiles prerequisite: `stow` (GNU Stow).
     - Package managers & optional GUI casks: `Homebrew` (`brew`), `docker-desktop` (optional cask).
   - Reference Table 2: Core CLI Packages (`devenv_packages_core`):
     - Exhaustive table listing all 22 logical packages: `aria2`, `autossh`, `curl`, `delta`, `fd`, `fish`, `fzf`, `gh`,
       `git`, `htop`, `iperf3`, `jq`, `ncdu`, `neovim`, `openssh`, `ripgrep`, `rsync`, `stow`, `tmux`, `tree`, `unzip`,
       `watch`.
     - Columns: Logical Name, macOS (`brew`) Formula, Debian/Ubuntu (`apt`) Package, Description & Notes.
   - Reference Table 3: Runtimes, Tools, & Plugins:
     - Python & uv tools: `CPython 3.13`, `ruff`, `pre-commit`.
     - Conda: `Miniforge3` installed at `~/miniforge3` with `dev` environment on `python=3.13`.
     - Node.js: `22.23.2` managed via `nvm.fish`.
     - Fish Plugins: `jorgebucaran/fisher`, `reitzig/sdkman-for-fish@v2.1.0`, `jorgebucaran/nvm.fish`.
     - Neovim Plugins: all 26 locked plugins from `dotfiles/nvim/.config/nvim/nvim-pack-lock.json` explicitly
       enumerated.
     - Packages purged on opt-in cleanup: `devenv_packages_remove` (`nvm`, `node`).
3. Markdown Prettier Formatting:
   - Format all modified documentation files using `npx --yes prettier@3 --write` to ensure clean single-pass
     convergence.

### Dependencies & Criticality

- **Depends on:** Step 1, Step 2, Step 4
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (Docstrings and documentation integrity, code-span arithmetic
  in markdown, Prettier compliance).
- **Potential failure modes for this step:** Discrepancy between names in `README.md` and names in
  `ansible/group_vars/all.yml` or plugin lockfiles triggering test failure.
- **Guardrails and early‑abort checks:** Run `test_readme_manifest_coverage` to programmatically verify that every
  required item is named in `README.md`.

### Success & Discard Criteria

- **Success:** `README.md`, `constraints.md`, and `ruleset.md` accurately document the Stow architecture; all reference
  tables match code manifests; Prettier check passes.
- **Discard:** Discard if any documented package or plugin name is missing from the reference tables.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.20  |
| impact_pred         | 88.0  |
| cost_pred           | 2.0   |
| learning_value_pred | 3.5   |
| ev_pred             | 85.93 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 88.0 + 0.5 * 3.5 - 0.3 * 0.20 - 2.0 = 86.24 + 1.75 - 0.06 - 2.0 = 85.93`. High-assurance
documentation alignment providing comprehensive transparency across the entire developer environment.

---

## Step 6: Full Verification and Quality Gate Convergence

- **Sub‑intent recommendation:** NO
- **Reasoning:** Final convergence verification executing all static, dynamic, linting, formatting, and prerequisite
  checks across the repository.
- **Step Type:** TEST
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Executing the complete suite of local verification commands confirms 100% convergence
  across pytest, ruff, ansible-lint, prettier, and make check without regressions.
- **Learning target:** Validate holistic quality gate pass across multi-tool toolchains.
- **Maximum acceptable cost for this learning:** 1.5

### Intent & Git Integration

- **Step Intent:** Execute unit test suite, code linter, playbook linter, markdown formatter checks, and make check
  target to confirm all quality criteria are met.
- **Git branch:**
  `I-1794792028-stow/P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium/E-6-final-verification-gate/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Execute Unit Tests:
   - Run `uv run --extra test pytest -v -l --tb=short -m "not network"`. Confirm 100% test pass rate with zero errors
     and zero skipped failures.
2. Execute Code Linter:
   - Run `uv run ruff check .`. Confirm zero violations across Python files.
3. Execute Playbook Linter:
   - Run `uv run --extra test ansible-lint ansible/site.yml`. Confirm zero errors across playbooks and roles.
4. Execute Markdown Prettier Check:
   - Run `npx --yes prettier@3 --check "**/*.md"`. Confirm zero formatting discrepancies.
5. Execute Prerequisite Probe:
   - Run `make check`. Confirm exit status 0 and clean prerequisite reporting.
6. Verify Working Tree Cleanliness:
   - Check `git status --porcelain`. Confirm only tracked, intended changes exist.

### Dependencies & Criticality

- **Depends on:** Step 1, Step 2, Step 3, Step 4, Step 5
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1, §2, §3, `holon-config/world/constraints.md` §1, §3.
- **Potential failure modes for this step:** Residual markdown unformatted lines or stray lint warnings.
- **Guardrails and early‑abort checks:** Format before check using `make docs-fmt` and `uv run ruff check --fix .`.

### Success & Discard Criteria

- **Success:** All verification commands exit with code 0; test suite passes completely; working tree is clean.
- **Discard:** Discard if any test, linter, or syntax check fails.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.98  |
| entropy_pred        | 0.20  |
| impact_pred         | 90.0  |
| cost_pred           | 1.5   |
| learning_value_pred | 2.5   |
| ev_pred             | 87.89 |

### Step Metrics Rationale

Calculated via: `EV = 0.98 * 90.0 + 0.5 * 2.5 - 0.3 * 0.20 - 1.5 = 88.20 + 1.25 - 0.06 - 1.5 = 87.89`. Deterministic
verification step ensuring complete delivery readiness and compliance.

---

## Strategy Rationale

The overall plan metrics were derived from individual step-level metrics as follows:

- **p_success_pred**: 0.94. Dictated by the bottleneck step (Step 4: 0.94), where cross-role path updates, regex parsing
  of both `gh` helper syntax and direct URLs in Neovim Lua configurations, and five comprehensive structural test
  invariants must converge cleanly.
- **entropy_pred**: 0.60. Evaluated as the maximum single-step risk profile (Step 3: 0.60), where core Ansible dotfiles
  linking and unlinking tasks are transitioned from `ansible.builtin.file` loops to `stow --no-folding`. The sum of
  predicted step entropies across all six steps is 2.30 (`0.30 + 0.50 + 0.60 + 0.50 + 0.20 + 0.20 = 2.30`), well within
  the allocated entropy budget of 15.0.
- **impact_pred**: 95.0. Establishes GNU Stow as the foundational package manager for all dotfiles, migrates modern
  Neovim configuration, adds cross-platform bash/zsh shell environments with `.local` override hooks, enforces zero
  unmanaged dotfile clutter, and publishes exhaustive reference tables in repository documentation.
- **cost_pred**: 13.0. Calculated as the direct sum of individual step costs
  (`1.5 + 2.5 + 3.0 + 2.5 + 2.0 + 1.5 = 13.0`).
- **learning_value_pred**: 5.5. Epistemic gain from mastering GNU Stow `--no-folding` symlink tree semantics, relative
  path resolution via Ansible stat/realpath filters, multi-OS POSIX shell initialization patterns, and automated
  documentation manifest verification.
- **ev_pred**: 78.87. Computed strictly via the config-driven Expected Value formula:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system constants `lambda = 0.3`
  and `mu = 0.5` loaded from `holon-config/metrics/ev_config.json`:
  `EV = 0.94 * 95.0 + 0.5 * 5.5 - 0.3 * 0.60 - 13.0 = 89.30 + 2.75 - 0.18 - 13.0 = 78.87`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: Python target `==3.13.*`, package
    management via `uv`, no `.sh` scripts tracked, GNU Make 3.81 compatibility, Multi-OS Darwin/Linux parity).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8, static typing, single-pass Prettier
    formatting with code-span arithmetic).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, tests located in `tests/`, all test
    modifications explicitly declared during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow & Branch Constraints: branch prefix isolation
    `I-{timestamp}-{slug}/P-{timestamp}-{agent}-{model}/E-{timestamp}-{action}/_`, rebase discipline, commit
    boundaries).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment Tiers: process sandbox $< 10$ entropy).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: converge through manifest, never write
    outside repo except through Ansible, do not touch unmanaged state, two backends only, destructive operations require
    explicit human confirmation).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero modifications to historical ledger entries).
- **Potential violations or edge cases:**
  - Directory folding by GNU Stow: If Stow creates a directory symlink instead of individual file links (e.g. symlinking
    `~/.config/fish` to repo folder), subsequent writes to machine-local state (`fish_variables`, fisher payloads) would
    pollute the git repository. Mitigated by strictly passing `--no-folding` to all `stow` invocations.
  - Stale symlinks blocking Stow: Pre-existing symlinks pointing to previous paths might cause Stow to abort with
    collision errors. Mitigated by pre-cleaning stale symlinks whose resolved targets do not point to the expected Stow
    package file.
  - POSIX shell path hardcoding: Introducing literal `/Users/...` or `/home/...` paths in `.bashrc` or `.zshrc`.
    Mitigated by using standard environment variables (`$HOME`, `$XDG_DATA_HOME`) and OS switches
    (`case "$(uname -s)" in Darwin)` / `Linux)`).
  - Premature unlink destruction: `make unlink` removing files outside our repo. Mitigated by requiring `CONFIRM=yes`
    and asserting destination paths resolve into `devenv_repo_root`.
- **Mitigations built into the plan:**
  - All Stow commands include `--no-folding --restow` and target directory `-t "{{ devenv_home }}"`.
  - Non-symlink real files are safely backed up to `{{ devenv_backup_dir }}` before linking.
  - All shell configs are verified by automated tests asserting no hardcoded per-user paths.
  - All test modifications and additions are fully enumerated and declared in the plan.
- **Residual risk accepted (and why):**
  - Dependency on host package manager to provision GNU Stow (`stow`); accepted because `stow` is widely available
    across both Homebrew and APT, and `make check` explicitly detects and reports its status.
- **Allocated Entropy Budget:** 15.0
- **Predicted Plan Entropy:** 0.60
- **Budget Compliance:** The strategy fits within budget (`0.60 <= 15.0`).

# dev-env

Your development environment, owned by this repository.

`fish`, `neovim`, `conda`, `nvm`/node, and the CLI tooling around them are declared here and converged onto the machine.
The machine is not the source of truth — this repo is.

Two rules shape everything below:

1. **`make` bootstraps Ansible, Ansible owns the rest.** No `.sh` files in this repository.
2. **Multi-OS by construction.** macOS and Linux are handled by the same declarative lists; package names are translated
   per package manager, and configs never hardcode `/Users/...` or `/opt/homebrew/...`.

---

## Architecture & Layout

### Bare Repository and Worktree Structure

This repository is designed to be cloned using a bare repository structure with Git worktrees, allowing multiple task
branches to be checked out simultaneously without conflicting with the canonical workspace:

```bash
git clone --bare <repo-url> dev-env/.git
cd dev-env
git config core.bare false
git worktree add main
cd main
```

Worktree layout:

- `dev-env/.git` (central Git database)
- `dev-env/main` (default checkout worktree)
- `dev-env/<worktree>` (isolated intent or feature worktrees)

### Directory Layout

```
Makefile                    entry point: prerequisite probe, Ansible bootstrap, scoped runs
ansible.cfg                 paths, interpreter, YAML output
ansible/
  site.yml                  converge order (tagged roles -> scoped runs)
  inventory/localhost.ini   always converges the machine it runs on
  group_vars/all.yml        THE manifest: packages, pins, links, feature flags
  vars/os_Darwin.yml        macOS overrides (neovim from brew, no sudo for installs)
  vars/os_Linux.yml         Linux overrides (neovim from GitHub release, sudo installs)
  vars/pkg_brew.yml         logical name -> Homebrew formula
  vars/pkg_apt.yml          logical name -> Debian/Ubuntu package
  roles/                    bootstrap, homebrew, packages, dotfiles, uv, conda, node, neovim, fish
  playbooks/unlink.yml      reversible teardown of managed symlinks
dotfiles/
  bash/                     .bashrc, .bash_profile (multi-OS + .local hooks)
  conda/                    .condarc (strict conda-forge, no auto base activation)
  fish/                     .config/fish/{config.fish, fish_plugins, conf.d/00-devenv.fish}
  nvim/                     .config/nvim/{init.lua, nvim-pack-lock.json, .stylua.toml, lua/}
  tmux/                     .config/tmux/tmux.conf (XDG path, needs tmux >= 3.1)
  zsh/                      .zshrc (multi-OS + .local hooks)
.github/workflows/          CI/CD workflows (make, hygiene, unit, network)
tests/                      pytest test suite (manifest invariants, templating, network)
```

### GNU Stow Per-Tool Packages (`stow --no-folding`)

Dotfiles are managed via GNU Stow (`stow`). Each tool configuration is isolated within its own dedicated package
directory under `dotfiles/`:

- `dotfiles/bash/`
- `dotfiles/conda/`
- `dotfiles/fish/`
- `dotfiles/nvim/`
- `dotfiles/tmux/`
- `dotfiles/zsh/`

Zero loose files reside directly under `dotfiles/` outside these package boundaries.

Symlinks are applied using `stow --no-folding --restow -d dotfiles -t $HOME <packages...>`. The critical `--no-folding`
flag prevents GNU Stow from creating directory-level symlinks when an entire directory tree belongs to a package.
Instead, parent directories are created directly in `$HOME`, and only leaf configuration files are symlinked. This
guarantees that machine-local state or unmanaged runtime files (such as fisher payloads, completions, and history)
written into `$HOME/.config/` never fold into or contaminate the repository.

### Machine-Local Configuration Overrides (`.local`)

Each shell configuration provides explicit, gitignored hooks for machine-local customizations:

- **Bash:** Sources `$HOME/.bashrc.local` at the end of `.bashrc`, and `$HOME/.bash_profile.local` in `.bash_profile`.
- **Zsh:** Sources `$HOME/.zshrc.local` at the end of `.zshrc`.
- **Fish:** Automatically loads machine-local configurations placed in `$__fish_config_dir/conf.d/*.fish` and functions
  in `$fisher_path` (`~/.config/fish/local`).

---

## Reference Tables

### 1. Prerequisites & Bootstrap Tooling

All tooling required to bootstrap or manage the environment:

| Tool                | Phase        | Checked By   | Installed By     | Notes                                                              |
| ------------------- | ------------ | ------------ | ---------------- | ------------------------------------------------------------------ |
| `GNU Make >= 3.81`  | Host Cold    | `make check` | Host OS          | Apple `/usr/bin/make` (3.81) or Linux `apt-get install -y make`    |
| `git`               | Host Cold    | `make check` | Host OS          | Host VCS client                                                    |
| `curl`              | Host Cold    | `make check` | Host OS          | Host HTTP client                                                   |
| `apt-get`           | Host Cold    | `make check` | Host OS (Linux)  | Linux package manager backend                                      |
| `Homebrew` (`brew`) | Package Mgr  | `make check` | Host OS (macOS)  | macOS package backend (`/opt/homebrew` or `/usr/local`)            |
| `uv`                | Bootstrap    | `make check` | `make bootstrap` | Fast Python package runner & tool manager                          |
| `ansible-core`      | Bootstrap    | `make check` | `make bootstrap` | Converge orchestrator pinned to Python `3.13`                      |
| `ansible-lint`      | Bootstrap    | `make check` | `make bootstrap` | Playbook linter pinned to Python `3.13`                            |
| `community.general` | Bootstrap    | `make check` | `make bootstrap` | Ansible collection (requires `>=9.0.0`)                            |
| `stow` (GNU Stow)   | Dotfiles Pre | `make check` | `packages` role  | Hard prerequisite for dotfiles management (`make dotfiles/unlink`) |
| `docker-desktop`    | Optional GUI | Playbook     | Opt-in Cask      | Installed on macOS when `devenv_install_gui_casks: true`           |

### 2. Core CLI Packages (`devenv_packages_core`)

All 22 core packages defined in the declarative manifest `ansible/group_vars/all.yml`:

| Logical Package | macOS (`brew`) Formula | Debian/Ubuntu (`apt`) Package | Description & Notes                                            |
| --------------- | ---------------------- | ----------------------------- | -------------------------------------------------------------- |
| `aria2`         | `aria2`                | `aria2`                       | High-speed multi-protocol download utility                     |
| `autossh`       | `autossh`              | `autossh`                     | Automatically restart SSH sessions and tunnels                 |
| `curl`          | `curl`                 | `curl`                        | Command-line tool for transferring data with URLs              |
| `delta`         | `delta`                | `git-delta`                   | Syntax-highlighting pager for git diffs                        |
| `fd`            | `fd`                   | `fd-find`                     | Simple, fast, user-friendly alternative to `find`              |
| `fish`          | `fish`                 | `fish`                        | Modern interactive command line shell                          |
| `fzf`           | `fzf`                  | `fzf`                         | General-purpose command-line fuzzy finder                      |
| `gh`            | `gh`                   | `gh`                          | GitHub official command-line interface                         |
| `git`           | `git`                  | `git`                         | Distributed version control system                             |
| `htop`          | `htop`                 | `htop`                        | Interactive process viewer                                     |
| `iperf3`        | `iperf3`               | `iperf3`                      | Network bandwidth measurement tool                             |
| `jq`            | `jq`                   | `jq`                          | Command-line JSON processor                                    |
| `ncdu`          | `ncdu`                 | `ncdu`                        | NCurses disk usage analyzer                                    |
| `neovim`        | `neovim`               | `neovim`                      | Hyperextensible Vim-based text editor                          |
| `openssh`       | `openssh`              | `openssh-client`              | OpenSSH client suite for secure shell connectivity             |
| `ripgrep`       | `ripgrep`              | `ripgrep`                     | Line-oriented search tool adhering to gitignore                |
| `rsync`         | `rsync`                | `rsync`                       | Fast and versatile remote file copying tool                    |
| `stow`          | `stow`                 | `stow`                        | Symlink farm manager for dotfiles packages                     |
| `tmux`          | `tmux`                 | `tmux`                        | Terminal multiplexer (XDG path `~/.config/tmux/tmux.conf`)     |
| `tree`          | `tree`                 | `tree`                        | Recursive directory listing program                            |
| `unzip`         | `(OS-provided)`        | `unzip`                       | Extraction utility for zip archives (skipped in brew)          |
| `watch`         | `watch`                | `procps`                      | Periodic command execution viewer (`procps` package on Debian) |

### 3. Runtimes, Tools, & Plugins

#### Runtimes & Python Tools

- **Python Runtime:** `CPython 3.13` (via `uv` and Conda).
- **Python Tools (`devenv_uv_tools`):**
  - `ruff`: Fast Python linter and code formatter.
  - `pre-commit`: Multi-language pre-commit hooks runner.
- **Conda:** `Miniforge3` installed to `~/miniforge3` with a default `dev` environment on `python=3.13`.
- **Node.js:** Node version `22.23.2` managed via `nvm.fish` (single source of truth in
  `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`).

#### Fish Plugins (`fish_plugins`)

Managed by `fisher`:

- `jorgebucaran/fisher`: Fish plugin manager.
- `reitzig/sdkman-for-fish@v2.1.0`: Fish shell integration for SDKMAN.
- `jorgebucaran/nvm.fish`: Node.js version manager wrapper for Fish.

#### Neovim Plugins (`nvim-pack-lock.json`)

All 26 plugins managed via `vim.pack` and locked to specific commit revisions:

1. `LuaSnip` (`https://github.com/L3MON4D3/LuaSnip`)
2. `blink.cmp` (`https://github.com/saghen/blink.cmp`)
3. `conform.nvim` (`https://github.com/stevearc/conform.nvim`)
4. `diffview.nvim` (`https://github.com/sindrets/diffview.nvim`)
5. `fidget.nvim` (`https://github.com/j-hui/fidget.nvim`)
6. `fzf-lua` (`https://github.com/ibhagwan/fzf-lua`)
7. `gitsigns.nvim` (`https://github.com/lewis6991/gitsigns.nvim`)
8. `guess-indent.nvim` (`https://github.com/NMAC427/guess-indent.nvim`)
9. `mason-lspconfig.nvim` (`https://github.com/mason-org/mason-lspconfig.nvim`)
10. `mason-tool-installer.nvim` (`https://github.com/WhoIsSethDaniel/mason-tool-installer.nvim`)
11. `mason.nvim` (`https://github.com/mason-org/mason.nvim`)
12. `mini.completion` (`https://github.com/nvim-mini/mini.completion`)
13. `mini.nvim` (`https://github.com/nvim-mini/mini.nvim`)
14. `neo-tree.nvim` (`https://github.com/nvim-neo-tree/neo-tree.nvim`)
15. `nui.nvim` (`https://github.com/MunifTanjim/nui.nvim`)
16. `nvim-lspconfig` (`https://github.com/neovim/nvim-lspconfig`)
17. `nvim-treesitter` (`https://github.com/nvim-treesitter/nvim-treesitter`)
18. `plenary.nvim` (`https://github.com/nvim-lua/plenary.nvim`)
19. `quicker.nvim` (`https://github.com/stevearc/quicker.nvim`)
20. `render-markdown.nvim` (`https://github.com/MeanderingProgrammer/render-markdown.nvim`)
21. `telescope-fzf-native.nvim` (`https://github.com/nvim-telescope/telescope-fzf-native.nvim`)
22. `telescope-ui-select.nvim` (`https://github.com/nvim-telescope/telescope-ui-select.nvim`)
23. `telescope.nvim` (`https://github.com/nvim-telescope/telescope.nvim`)
24. `todo-comments.nvim` (`https://github.com/folke/todo-comments.nvim`)
25. `tokyonight.nvim` (`https://github.com/folke/tokyonight.nvim`)
26. `which-key.nvim` (`https://github.com/folke/which-key.nvim`)

#### Purged / Unmanaged Packages (`devenv_packages_remove`)

When `devenv_remove_unmanaged: true` is opted in, these conflicting duplicate packages are purged:

- `nvm`: Homebrew formula conflicts with `nvm.fish` and attempts to manage `~/.nvm`.
- `node`: System / Homebrew node package shadowing nvm-managed Node.js binaries.

---

## Getting Started

There is deliberately **no `curl | sh`** bootstrap. The only prerequisite is GNU Make:

| Platform        | Cold start                                                         |
| --------------- | ------------------------------------------------------------------ |
| macOS           | `xcode-select --install` (provides `/usr/bin/make`, GNU Make 3.81) |
| Debian / Ubuntu | `sudo apt-get install -y make git curl`                            |

Then:

```bash
make check        # read-only prerequisite probe; installs nothing
make bootstrap    # installs uv -> ansible-core + ansible-lint -> community.general
make install      # check + bootstrap + converge with --diff
```

Day-to-day:

```bash
make check-mode     # ansible --check --diff : what would change
make doctor         # dry run + repo-write check + tracked dotfiles
make dotfiles       # re-link dotfiles via stow --no-folding
make nvim-sync      # install Neovim plugins at locked revisions
make fisher         # sync fish plugins from dotfiles/fish/.config/fish/fish_plugins
make probe-packages # package installs in --check mode for this OS
make facts          # resolved platform facts + concrete package list
make lint           # ansible-lint
make unlink CONFIRM=yes   # remove the managed symlinks via stow --delete
```

---

## How the Multi-OS Abstraction Works

You never write `brew install ...`. You add a **logical** name once:

```yaml
# ansible/group_vars/all.yml
devenv_packages_core:
  - fzf
```

...and give it a name in each backend table (`ansible/vars/pkg_brew.yml`, `ansible/vars/pkg_apt.yml`). The `bootstrap`
role asserts that every logical name has an alias for the detected backend and aborts with the missing names listed,
rather than passing a guessed package name to `apt`. Names the OS already ships are dropped via `devenv_pkg_skip` (macOS
ships `unzip`, Homebrew has no formula for it).

Backends that have no alias table are refused outright — `devenv_supported_backends` is `brew` and `apt`, so an Arch or
Fedora host fails loudly instead of half-installing.

Runtimes that are not OS packages are installed identically everywhere:

| Runtime                             | Mechanism                                                         |
| ----------------------------------- | ----------------------------------------------------------------- |
| Python for Ansible tooling          | `uv tool install --python 3.13 ansible-core`                      |
| Python tools (`ruff`, `pre-commit`) | `uv tool install`                                                 |
| Conda                               | Miniforge upstream installer into `~/miniforge3` on **both** OSes |
| Node                                | `nvm.fish` + `$XDG_DATA_HOME/nvm/current` symlink                 |
| Neovim plugins                      | `vim.pack` + committed `nvim-pack-lock.json`                      |

Miniforge deliberately does **not** use the Homebrew cask: the cask pins conda to
`/opt/homebrew/Caskroom/miniforge/base`, which would force an OS branch into every config file. Installing to
`~/miniforge3` on macOS and Linux keeps one path, so `dotfiles/fish/.config/fish/config.fish`, `dotfiles/bash/.bashrc`,
and `dotfiles/zsh/.zshrc` probe a candidate list with no `uname` switch for conda.

---

## Decisions This Repo Makes

- **nvm owns node.** Nothing installs node directly. Shell configs prepend `$XDG_DATA_HOME/nvm/current/bin` before
  `~/.local/bin`, and the `node` role asserts that a login shell resolves node through nvm — a failed converge, not a
  silent wrong `node`.
- **The node pin lives in the fish config**, not in Ansible vars. The `node` role parses `devenv_node_default_version`
  out of `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`, so the shell and the playbook cannot disagree.
- **GNU Stow with `--no-folding` manages dotfiles.** Packages live in `dotfiles/<pkg>/`. The `--no-folding` flag ensures
  directories in `$HOME` are real folders and only individual configuration files are symlinked.
- **fisher payloads stay out of the repo.** `fisher_path` is `$__fish_config_dir/local`, so plugin code lands in a
  gitignored directory and `git status` stays clean.
- **`fish_variables` is not version controlled.** It is machine-local universal-variable state. Anything that must be
  equal on every machine is declared in `config.fish` / `conf.d/00-devenv.fish` instead.
- **Existing configs are backed up, never deleted.** Real files sitting where a link belongs are moved to
  `~/.local/share/dev-env/backup/<timestamp>/` first.

---

## Status and Known Gaps

Read this before trusting it.

- **Converged on macOS: not yet run.** Validated so far: `make check`, `make bootstrap`, `make facts`,
  `make probe-packages`, and a `--check --diff` dry run of the `dotfiles` role.
- **Linux is unvalidated.** The apt alias table follows Debian/Ubuntu naming conventions (`fd-find`, `procps`,
  `git-delta`, `openssh-client`) but has not been run on a live host. Start there with `make probe-packages`.
- `community.general` has **no** conda/miniforge/nvm modules (checked upstream), so those roles shell out to the
  upstream installers under `creates:` guards. That is the intended design, not an oversight.
- `--check` mode cannot simulate `command`-based installs, so a full `make check-mode` on a fresh host will fail on the
  runtime assertions; use per-role dry runs (`probe-packages`, `dotfiles`).
- GUI casks (`docker-desktop`, browsers) are declared but off by default (`devenv_install_gui_casks`).
- No `Brewfile` on purpose: `ansible/group_vars/all.yml` is the single package manifest.

---

## CI/CD Pipeline

Continuous integration is orchestrated via GitHub Actions workflows in `.github/workflows/`:

- **Make Check (`make.yml`)**: Multi-OS matrix (`ubuntu-latest`, `macos-latest`) testing `make help` and `make check`.
- **Code Hygiene & Lint (`test-hygiene.yml`)**: Verifies lockfile currency (`uv lock --check`), Ruff linting
  (`uv run ruff check .`), Prettier markdown formatting, and Ansible playbook linting (`ansible-lint`).
- **Unit Tests (`test-unit.yml`)**: Multi-OS unit test execution running `uv run --extra test pytest -m "not network"`.
- **Network Upstream Asset Tests (`test-network.yml`)**: Scheduled and manual validation confirming upstream download
  URLs and installer filenames remain reachable (`DEVENV_NETWORK_TESTS=1`).

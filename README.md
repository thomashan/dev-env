# dev-env

Your development environment, owned by this repository.

`fish`, `neovim`, `conda`, `nvm`/node and the CLI tooling around them are declared here and
converged onto the machine. The machine is not the source of truth — this repo is.

Two rules shape everything below:

1. **`make` bootstraps Ansible, Ansible owns the rest.** No `.sh` files in this repository.
2. **Multi-OS by construction.** macOS and Linux are handled by the same declarative lists;
   package names are translated per package manager, and configs never hardcode
   `/Users/...` or `/opt/homebrew/...`.

---

## Layout

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
  .config/fish/             config.fish, fish_plugins, conf.d/00-devenv.fish (OS detect + pins)
  .config/nvim/             init.lua, nvim-pack-lock.json (vim.pack lockfile -- keep committed)
  .config/tmux/tmux.conf    XDG path, needs tmux >= 3.1
  .condarc                  conda behaviour (strict conda-forge, no auto base activation)
holon-config/               Holon world ruleset, constraints, prompts, metrics
holon-knowledge/ledger/     append-only intents / plans / executions ledger
intents/                    draft intents for the Holon flow (gitignored)
```

## Getting started

There is deliberately **no `curl | sh`** bootstrap. The only prerequisite is GNU Make, which is
the one thing this repo cannot install for you:

| Platform | Cold start |
| --- | --- |
| macOS | `xcode-select --install` (provides `/usr/bin/make`, GNU Make 3.81) |
| Debian / Ubuntu | `sudo apt-get install -y make git curl` |

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
make dotfiles       # re-link dotfiles after editing this repo
make nvim-sync      # install Neovim plugins at their locked revisions
make fisher         # sync fish plugins from dotfiles/.config/fish/fish_plugins
make probe-packages # package installs in --check mode for this OS
make facts          # resolved platform facts + concrete package list
make lint           # ansible-lint
make unlink CONFIRM=yes   # remove the managed symlinks (never deletes real files)
```

## How the multi-OS abstraction works

You never write `brew install ...`. You add a **logical** name once:

```yaml
# ansible/group_vars/all.yml
devenv_packages_core:
  - fzf
```

...and give it a name in each backend table (`ansible/vars/pkg_brew.yml`, `ansible/vars/pkg_apt.yml`).
The `bootstrap` role asserts that every logical name has an alias for the detected backend and
aborts with the missing names listed, rather than passing a guessed package name to `apt`.
Names the OS already ships are dropped via `devenv_pkg_skip` (macOS ships `unzip`, Homebrew has no
formula for it).

Backends that have no alias table are refused outright — `devenv_supported_backends` is
`brew` and `apt`, so an Arch or Fedora host fails loudly instead of half-installing.

Runtimes that are not OS packages are installed identically everywhere:

| Runtime | Mechanism |
| --- | --- |
| Python for Ansible tooling | `uv tool install --python 3.13 ansible-core` |
| python tools (`ruff`, `pre-commit`) | `uv tool install` |
| conda | Miniforge upstream installer into `~/miniforge3` on **both** OSes |
| node | `nvm.fish` + `$XDG_DATA_HOME/nvm/current` symlink |
| neovim plugins | `vim.pack` + committed `nvim-pack-lock.json` |

Miniforge deliberately does **not** use the Homebrew cask: the cask pins conda to
`/opt/homebrew/Caskroom/miniforge/base`, which would force an OS branch into every config file.
Installing to `~/miniforge3` on macOS and Linux keeps one path, so
`dotfiles/.config/fish/config.fish` probes a candidate list with no `uname` switch for conda.

## Decisions this repo makes

- **nvm owns node.** Nothing installs node directly. `dotfiles/.config/fish/config.fish`
  prepends `$XDG_DATA_HOME/nvm/current/bin` before `~/.local/bin`, and the `node` role asserts
  that a login shell resolves node through nvm — a failed converge, not a silent wrong `node`.
- **The node pin lives in the fish config**, not in Ansible vars. The `node` role parses
  `devenv_node_default_version` out of `conf.d/00-devenv.fish`, so the shell and the playbook
  cannot disagree.
- **Dotfiles are linked at file granularity**, never per directory. `~/.config/fish/conf.d` also
  holds fisher's plugin payloads; linking the directory would hide them, and Ansible refuses to
  symlink over a non-empty directory anyway. `devenv_links` entries must be files — the role
  enforces it.
- **fisher payloads stay out of the repo.** `fisher_path` is `$__fish_config_dir/local`, so
  plugin code lands in a gitignored directory and `git status` stays clean.
- **`fish_variables` is not version controlled.** It is machine-local universal-variable state
  (it currently carries absolute macOS paths in `fish_user_paths`). Anything that must be equal
  on every machine is declared in `config.fish` / `conf.d/00-devenv.fish` instead.
- **Existing configs are backed up, never deleted.** Real files sitting where a link belongs are
  moved to `~/.local/share/dev-env/backup/<timestamp>/` first.

## Drift found on the first host (macOS, 2026-10-10)

These are the reasons the assertions above exist:

- **Three node binaries.** `brew node` 26.11.1, `~/.local/bin/node -> ~/.hermes/node` 22.23.2
  (first on `PATH`, so it was the effective `node`), and `nvm.fish` with 24.21.0.
  Pin set to `22.23.2` to match the effective runtime; change one line in `conf.d/00-devenv.fish`
  to move. Set `devenv_remove_unmanaged: true` to purge `brew nvm`/`brew node`.
- **Two nvm installs.** The `nvm` Homebrew formula (bash-oriented, `~/.nvm`, no node installed)
  and `nvm.fish` (`~/.local/share/nvm`). `nvm.fish` wins because fish is the login shell.
- `~/.condarc` did not exist; conda base was auto-activating.
- `~/.config/fish/config.fish` hardcoded `/Users/thomashan/...`, `/opt/homebrew/Caskroom/...` and
  `/opt/homebrew/...` — unusable on Linux, rewritten around `$HOME`/`$XDG_*` plus OS detection.
- `~/.zshrc` carries the old bash-nvm and conda blocks. fish is the login shell
  (`dscl` confirms `/opt/homebrew/bin/fish`), so zsh is not managed in v1.

## Status and known gaps

Read this before trusting it.

- **Converged on macOS: not yet run.** Validated so far: `make check`, `make bootstrap`
  (installed ansible-core 2.21.5, ansible-lint, `community.general` 13.5.0), `make facts`,
  `make probe-packages`, and a `--check --diff` dry run of the `dotfiles` role. Package installs,
  Miniforge, nvm/node, plugin sync and the linking itself have not been executed yet.
- **Linux is unvalidated.** The apt alias table follows Debian/Ubuntu naming conventions
  (`fd-find`, `procps`, `git-delta`, `openssh-client`) but has not been run on a live host.
  Start there with `make probe-packages`.
- `community.general` has **no** conda/miniforge/nvm modules (checked upstream), so those roles
  shell out to the upstream installers under `creates:` guards. That is the intended design, not
  an oversight.
- `--check` mode cannot simulate `command`-based installs, so a full `make check-mode` on a fresh
  host will fail on the runtime assertions; use per-role dry runs (`probe-packages`, `dotfiles`).
- GUI casks (`docker-desktop`, browsers) are declared but off by default (`devenv_install_gui_casks`).
- No `Brewfile` on purpose: `ansible/group_vars/all.yml` is the single package manifest.

## Holon

`holon-config/` and `holon-knowledge/` predate this work; `ruleset.md` and `constraints.md` now
also cover the make-plus-Ansible contract, the no-shell-script rule and the multi-OS rule so the
planner and executor agents work inside these conventions. Draft intents go in `intents/`
(gitignored); the permanent record is `holon-knowledge/ledger/`.

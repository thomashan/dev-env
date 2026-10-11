# Local Dev Environment Setup Plan

## Goal

Provide a single, idempotent, cross-platform setup that bootstraps a
complete local development environment with:

- Prerequisite checks (`make`, `git`, `curl`, etc.)
- **conda** (Miniforge/Miniconda) for Python, providing `python`, `uv`,
  and arbitrary Python toolchains/versions
- **Neovim** as the primary IDE, with a batteries-included config
- **Nix** (or a Nix-managed package set) for reproducible CLI
  toolchains: `openssl`, `fzf`, and friends

Supported matrix:

| OS    | amd64 | arm64 |
|-------|-------|-------|
| Linux | ✅    | ✅    |
| macOS | ✅    | ✅    |

Windows is out of scope for v1 (WSL2 counts as Linux).

## Guiding Principles

1. **Idempotent** – running setup repeatedly is safe and a no-op if
   already installed.
2. **Declarative over imperative** – prefer pinned package manifests
   (Nix flakes, conda lockfiles) over ad-hoc shell installs.
3. **Single entrypoint** – `make bootstrap` (or `./bin/setup.sh`) is the
   only command a new contributor needs to run.
4. **Detect, don't assume** – scripts detect OS/arch and branch
   accordingly; no hardcoded paths.
5. **Fail loud, fail fast** – every check reports a clear pass/fail with
   remediation instructions.
6. **Layered** – prerequisite checks → package manager installs →
   toolchain installs → IDE config, each independently re-runnable.

## Proposed Repository Layout

```
dev-env/
├── Makefile                  # top-level entrypoints (bootstrap, doctor, clean)
├── bin/
│   ├── setup.sh               # orchestrator, detects OS/arch, calls modules
│   └── doctor.sh               # prerequisite / health checks
├── scripts/
│   ├── os/
│   │   ├── linux.sh
│   │   └── macos.sh
│   ├── install-nix.sh
│   ├── install-conda.sh
│   └── install-neovim.sh
├── nix/
│   ├── flake.nix              # devShell with openssl, fzf, ripgrep, etc.
│   └── flake.lock
├── conda/
│   └── environment.yml        # base Python env (python, uv, pip)
├── nvim/
│   └── ...                    # Neovim config (lazy.nvim-based), symlinked
│                                 into $XDG_CONFIG_HOME/nvim
├── docs/
│   ├── plan.md                 # this document
│   └── troubleshooting.md
└── README.md
```

## Phase Breakdown

### Phase 0 — Scaffolding & CI

- Add `Makefile` with targets: `bootstrap`, `doctor`, `lint`, `clean`.
- Add CI (GitHub Actions) matrix over `{ubuntu-latest, macos-latest} x
  {amd64, arm64}` running `make doctor` on every PR (macOS arm64 and
  Linux arm64 via native runners or `docker run --platform`).
- Add `shellcheck` + `shfmt` lint step for all shell scripts.

### Phase 1 — Prerequisite Checks (`bin/doctor.sh`)

- Detect OS (`uname -s`) and arch (`uname -m`, normalize
  `x86_64`→`amd64`, `aarch64`/`arm64`→`arm64`).
- Verify presence/version of: `make`, `git`, `curl`/`wget`, `bash>=4`,
  a C compiler (`cc`/`clang`/`gcc` — needed by Nix/conda native
  builds).
- Print a summary table (✅/❌) and exit non-zero if any required tool
  is missing, with per-OS install hints.
- `make doctor` runs this standalone, without installing anything.

### Phase 2 — Package Manager Bootstrap

- **Nix**: install via the [Determinate Systems
  installer](https://github.com/DeterminateSystems/nix-installer)
  (handles macOS + Linux, amd64 + arm64, idempotent, supports
  uninstall). Enable flakes + nix-command by default.
- **Conda**: install Miniforge (conda-forge default channel, supports
  linux-64/aarch64 and osx-64/arm64) into `~/.local/miniforge3` if not
  already present. Avoid Anaconda's non-free default channel.
- Both installers are idempotent: check for existing install dir /
  `command -v` before downloading.

### Phase 3 — Nix-Managed Toolchains

- `nix/flake.nix` defines a `devShell` (or `nix profile install`) list
  including: `openssl`, `fzf`, `ripgrep`, `fd`, `jq`, `gnupg`, and
  other CLI utilities as needed.
- Use `flake.lock` for reproducibility across machines; CI verifies the
  lock is up to date.
- Provide both:
  - `nix develop` (opt-in shell) for contributors who want isolation.
  - `nix profile install` path for those who want tools on `PATH`
    globally (what `make bootstrap` uses by default).

### Phase 4 — Conda / Python Toolchain

- `conda/environment.yml` pins a base environment: `python=3.12`,
  `pip`, and `uv` (installed via pip or conda-forge).
- `uv` becomes the preferred tool for per-project virtualenvs /
  dependency installs; conda is reserved for managing Python
  interpreter versions themselves.
- Document how to create additional Python versions:
  `conda create -n py311 python=3.11`.

### Phase 5 — Neovim IDE Setup

- Install Neovim via Nix (preferred, pinned version) rather than OS
  package managers, so version is identical across machines.
- `nvim/` holds a lazy.nvim-based config (LSP, treesitter, telescope +
  fzf integration, completion, formatting).
- `make bootstrap` symlinks `nvim/` into
  `${XDG_CONFIG_HOME:-$HOME/.config}/nvim`, backing up any existing
  config first.
- LSP servers for Python (`pyright`/`ruff`) and shell (`bashls`)
  installed via `mason.nvim` or pinned Nix packages — decide in Phase 5
  implementation to avoid duplicate installs.

### Phase 6 — Verification & Docs

- Extend `make doctor` to also verify Phase 2–5 outputs (nix, conda,
  nvim, fzf, openssl all on `PATH` with expected versions).
- Write `docs/troubleshooting.md` for common failure modes (corporate
  proxies, SIP on macOS, missing Rosetta on Apple Silicon for any
  amd64-only fallback binaries).
- Update root `README.md` with quickstart: `git clone ... && cd dev-env
  && make bootstrap`.

## Cross-Platform / Cross-Arch Notes

- All installer scripts branch on `$(uname -s)`/`$(uname -m)` early and
  export normalized `OS`/`ARCH` vars used throughout.
- Prefer tools with first-class multi-arch support (Nix, Miniforge,
  Neovim releases) over anything requiring Rosetta/emulation.
- CI must include at least one native arm64 runner per OS to catch
  arch-specific regressions (GitHub-hosted `macos-latest` is arm64;
  use `ubuntu-24.04-arm` or QEMU for Linux arm64).

## Open Questions

- Shell config management (zsh/bash dotfiles) — in scope for this repo
  or separate?
- Should `make bootstrap` be fully non-interactive (CI-friendly) or
  prompt for confirmation before installing system-wide tools?
- Pin exact tool versions in docs/plan, or always track latest stable?

## Milestones / Sequencing

1. Phase 0 scaffolding + CI skeleton
2. Phase 1 doctor script (immediate value, no installs)
3. Phase 2 Nix + conda bootstrap
4. Phase 3 Nix toolchain flake
5. Phase 4 conda/uv environment
6. Phase 5 Neovim config + symlinking
7. Phase 6 docs + full `make doctor` verification

Each milestone should land as its own PR for easier review.

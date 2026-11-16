# Holon World Constraints

This document defines the strict security, operational, and lifecycle constraints for the Holon Agentic Coder
environment. Violating these constraints triggers automated alerts, sandbox terminations, or trust degradation.

---

## 1. Git Flow & Branch Constraints

- **Repository Layout & Worktrees:** The recommended repository architecture is a bare `.git` directory (`dev-env/.git`)
  with checkouts located in worktrees (`dev-env/main`, `dev-env/<worktree>`), allowing concurrent branch work without
  interfering with active checkouts.
- **Prefix-Based Isolation:** Every active task must run inside its own isolated branch prefix:
  - **Root Intents:** `I-{timestamp}-{slug}/_`. Only human operators can approve merges to canonical branches.
  - **Plan Variants:** `I-{timestamp}-{slug}/P-{timestamp}-{agent}-{model}/_`. Created off of the intent branch.
  - **Execution Runs:** `I-{timestamp}-{slug}/P-{timestamp}-{agent}-{model}/E-{timestamp}-{action}/_`. Created off of
    the plan branch.
- **Rebase Discipline:** Before any execution run or branch merge, the working branch must be rebased from its parent
  branch to prevent divergence.
- **Commit Boundaries:** Code changes must be scoped strictly to the current active step and git branch. Agents are
  prohibited from checking out or committing directly to `main` or other intents' branches.

---

## 2. Sandbox Containment Tiers

All execution and validation activities must run inside an isolated sandbox determined by predicted entropy and trust:

1. **Process Sandbox:** (Low entropy `< 10`, high trust). Local Python sub-process with filesystem containment and
   disabled network access.
2. **Container Sandbox (Docker):** (Medium entropy `10 - 30`, standard trust). Docker container with resource
   constraints and network isolation.
3. **VM Sandbox:** (High entropy `> 30`, low/baseline trust). Highly secure VM with kernel-level isolation and rollback
   support.

---

## 3. Environment Mutation Boundaries

Because this repository owns the developer environment, execution runs must respect these limits:

- **GNU Stow Multi-Variant Dotfile Management:** GNU Stow (`stow`) is an explicit prerequisite for managing dotfiles.
  Dotfiles are structured into per-tool and multi-variant Stow packages (`bash`, `conda`, `fish`, `nvim-kickstart`,
  `nvim-minimal`, `nvim-lazyvim`, `tmux`, `zsh`) under `dotfiles/<pkg>/` and symlinked via `stow --no-folding --restow`.
  Directory folding is strictly prohibited. Inactive variants are unlinked via `stow --delete` prior to restowing.
- **Pure Make -> Conda -> Ansible Bootstrap:** Toolchain bootstrapping flows strictly from the host system package
  manager (`brew` on macOS or `apt` on Linux) to GNU Make (`>= 3.81`), which bootstraps Miniforge Conda into
  `~/miniforge3` (installing `curl` via `brew` or `apt` if absent). Conda provisions Ansible and Python bootstrap
  tooling. `uv` is installed alongside `ruff` and `pre-commit` as part of `devenv_conda_tools`.
- **Host Wizard Configuration:** User choices and conflict resolution decisions are gathered via `make configure`
  (`scripts/devenv_wizard.py`) and persisted to `~/.config/dev-env/choices.yml`. Ansible reads this file cleanly.
- **Converge Through the Manifest:** Add a package by editing `ansible/group_vars/all.yml` plus the alias tables --
  never by running `brew install` / `apt install` inside an execution step. Undeclared installs are invisible to every
  other machine.
- **Never Write Outside the Repo Except Through Ansible:** Direct writes to `$HOME` (for example editing
  `~/.config/nvim/init.lua`) are prohibited; edit `dotfiles/` and let the `dotfiles` role link it. `make dotfiles` is
  the only sanctioned path to `$HOME`.
- **Do Not Touch Unmanaged State:** `$HOME/.config/fish/fish_variables`, fisher payloads under
  `$HOME/.config/fish/local/`, other agents' runtimes (`~/.hermes`, `~/.sdkman`), and the existing Miniforge cask
  install are out of scope unless an intent names them explicitly.
- **Two-Backends-Only:** `devenv_supported_backends` is `brew` and `apt`. Do not introduce `dnf`/`pacman`/`port`
  branches without adding a validated alias table and widening that list.
- **Destructive Operations:** Package removal (`devenv_remove_unmanaged`), `make unlink` and any `become:` privilege
  escalation require an explicit human-approved intent. `make unlink` additionally requires `CONFIRM=yes`.

---

## 4. Ledger Immutability

- **Append-Only Ledger:** The ledgers located at `holon-knowledge/ledger/` (`intents.jsonl`, `plans.jsonl`,
  `executions.jsonl`) are immutable.
- **Zero Modification Policy:** Removing, rewriting, amending, or editing historical lines in `.jsonl` files is strictly
  prohibited. Only append operations are allowed.

---

## 5. Model Routing Constraints

- **Exploration vs. Safety:** Routing is dictated by predicted plan entropy and novelty:
  - **Flash Models:** Recommended for routine tasks, boilerplate implementations, and simple tests.
  - **Deep Models:** Mandated for refactoring core modules, security-sensitive plans, or intents exceeding high entropy.

# Holon World Ruleset

This document defines the static coding conventions, runtime constraints, package specifications,
and architectural rules for this repository. All planning and execution agents must consult and obey these rules.

---

## 1. Runtime & Environment Specification

This repository **is** the development environment. The machine is a build artifact of the repo,
never the other way round.

- **Installation Contract:** `make` bootstraps Ansible and nothing else; Ansible converges every
  package, runtime and dotfile. See `README.md`.
- **No Shell Scripts:** No `.sh` files may be added to this repository. Orchestration belongs in
  `Makefile` recipes (short, reviewable) and Ansible tasks. Upstream installers fetched by
  `ansible.builtin.get_url` into `~/.cache/dev-env/` and run under a `creates:` guard are the only
  permitted exception.
- **GNU Make Compatibility:** The `Makefile` must stay compatible with GNU Make 3.81, which is what
  `/usr/bin/make` is on macOS. No `.ONESHELL`, `$(file ...)`, `!=` or `.RECIPEPREFIX`.
- **Python Runtime:** Strict target version `==3.13.*` for Ansible tooling and uv-managed tools,
  installed via `uv tool install --python 3.13 <tool>`.
- **Package Management:** System tooling is declared in `ansible/group_vars/all.yml` by logical
  name only, with per-backend alias tables (`ansible/vars/pkg_brew.yml`, `ansible/vars/pkg_apt.yml`).
  Python tools are declared in the same manifest under `devenv_uv_tools`. Never hardcode a
  distribution package name into a role.
- **Multi-OS Rule:** Every config and task must work on macOS (Darwin) and Linux. Never hardcode
  `/Users/...`, `/home/...` or `/opt/homebrew/...`; resolve paths from facts, `$HOME`, or `$XDG_*`.
  OS-specific differences go in `ansible/vars/os_<System>.yml`, not inline in role tasks.
- **Project Layout:** `ansible/` (control plane), `dotfiles/` (config source of truth),
  `holon-config/` (world model), `holon-knowledge/` (ledger), `intents/` (drafts, gitignored).

---

## 2. Coding Conventions & Standards

- **PEP 8 Compliance:** All Python source files must conform to standard style rules (spacing, naming, imports layout).
- **Typing Guidelines:** Use strict static type annotations (`typing` module) for all public functions, classes,
  and method signatures.
- **Docstring Requirements:** Every module, class, and public function must have an explanatory docstring outlining
  inputs, outputs, exceptions, and side-effects.
- **Imports Discipline:**
  - Avoid wildcard imports (`from module import *`).
  - Keep core domain models independent of framework-specific classes.
- **Ansible Style:** Fully-qualified collection names on every module (`ansible.builtin.`,
  `community.general.`). Access facts via `ansible_facts["..."]` -- the `ansible_<fact>` shorthand is
  deprecated in ansible-core 2.21. Every task that can change state declares `changed_when` when it
  is not obviously mutating.
- **Idempotence:** Re-runs of `make converge` must report zero changes on an already-converged host.
  Guards (`creates:`), `stat` checks and assertions are preferred over "always run and hope".
- **Assertion over Hope:** Where a wrong outcome is silent (which `node` resolves on `PATH`, whether
  `~/.condarc` is repo-managed, whether Neovim supports `vim.pack`), add an `assert` that fails the
  converge with the observed value.
- **Dotfiles:** `devenv_links` lists files, never directories, so files owned by other tools in the
  same directory are never displaced. Anything generated or machine-local (`fish_variables`,
  fisher payloads) stays out of `dotfiles/`.
- **Markdown & Docs:** Enclose arithmetic and metric notation in code spans (backticks) for
  single-pass Prettier convergence (see `.prettierrc.json`, `make docs-fmt`).

---

## 3. Testing Constraints

- **Testing Tool:** `uv run pytest` as standard test runner.
- **Test Location:** Unit tests must be placed in a corresponding `tests/` directory matching
  the source file being tested.
- **Execution Boundary:** Sandbox executions are not allowed to modify tests or test assertions unless explicitly
  declared in the plan.

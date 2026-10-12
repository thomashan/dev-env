# CI/CD Workflows Architecture

This directory defines the automated GitHub Actions CI/CD workflows for the `dev-env` repository. The pipeline provides
multi-OS test coverage, static hygiene enforcement, and isolated upstream network checks.

---

## Workflows Overview

| Workflow                   | File                                   | Triggers                                                               | Runner Matrix                   | Purpose                                                                                                     |
| -------------------------- | -------------------------------------- | ---------------------------------------------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Make Check**             | [`make.yml`](make.yml)                 | `push` (`main`), `pull_request` (`main`), `workflow_dispatch`          | `ubuntu-latest`, `macos-latest` | Host architecture inspection, Makefile rendering (`make help`), and prerequisite validation (`make check`). |
| **Unit Tests**             | [`test-unit.yml`](test-unit.yml)       | `push` (`main`), `pull_request` (`main`), `workflow_dispatch`          | `ubuntu-latest`, `macos-latest` | Multi-OS test suite execution using `uv` and Python `3.13` (`pytest -m "not network"`).                     |
| **Code Hygiene & Lint**    | [`test-hygiene.yml`](test-hygiene.yml) | `push` (`main`), `pull_request` (`main`), `workflow_dispatch`          | `ubuntu-latest`                 | Lockfile currency (`uv.lock`), Ruff linting, Prettier markdown validation, and `ansible-lint`.              |
| **Network Upstream Tests** | [`test-network.yml`](test-network.yml) | Daily cron (`0 6 * * *`), `pull_request` (`main`), `workflow_dispatch` | `ubuntu-latest`                 | Verifies computed external release assets exist upstream via HEAD HTTP probes (`pytest -m network`).        |

---

## Detailed Workflow Specifications

### 1. Make Check (`make.yml`)

- **Matrix Strategy:** Executes across both `ubuntu-latest` and `macos-latest`.
- **Concurrency:** Cancels superseded runs on the same branch or PR using `${{ github.workflow }}-${{ github.ref }}`.
- **GNU Make 3.81 Compatibility:** Apple macOS ships GNU Make 3.81. This workflow verifies that the `Makefile` runs
  under Darwin without relying on features introduced in GNU Make 3.82+ (such as `.ONESHELL`, `!=`, or `.RECIPEPREFIX`).
- **Steps:**
  1. Check out repository via `actions/checkout@v4`.
  2. Inspect host architecture via `uname -a && uname -m`.
  3. Verify recipe printing via `make help`.
  4. Run prerequisite probe via `make check`.

### 2. Unit Tests (`test-unit.yml`)

- **Matrix Strategy:** Executes in parallel on Linux (`ubuntu-latest`) and macOS (`macos-latest`).
- **Tooling:** Uses `astral-sh/setup-uv@v5` with caching enabled and `actions/setup-python@v5` with Python `3.13`.
- **Environment Isolation:** Synchronizes locked dependencies from `uv.lock` via `uv sync --locked --extra test`.
- **Test Target:** Executes `uv run --extra test pytest -v -l --tb=short -m "not network"`. Network tests are excluded
  from fast PR runs.

### 3. Code Hygiene & Lint (`test-hygiene.yml`)

- **Runner:** `ubuntu-latest`.
- **Hygiene Quality Gates:**
  1. **Lockfile Currency:** Asserts that `uv.lock` is up-to-date and unstaged changes are absent:
     ```bash
     uv lock --check
     git diff --exit-code uv.lock
     ```
  2. **Python Linting:** Evaluates PEP 8, syntax rules, and standard conventions via `uv run ruff check .`.
  3. **Markdown Prettier Formatting:** Enforces single-pass formatting across all documentation:
     ```bash
     npx --yes prettier@3 --check "**/*.md"
     ```
  4. **Ansible Collection Provisioning:** Installs required Galaxy collections (`community.general`):
     ```bash
     uv run ansible-galaxy collection install -r ansible/requirements.yml
     ```
  5. **Ansible Playbook Linting:** Runs `uv run --extra test ansible-lint` against `ansible/site.yml` and role
     definitions.

### 4. Network Upstream Asset Tests (`test-network.yml`)

- **Runner:** `ubuntu-latest`.
- **Triggers:** Daily scheduled cron at 06:00 UTC (`0 6 * * *`), manual dispatch (`workflow_dispatch`), and pull
  requests.
- **Opt-in Guard:** Sets `DEVENV_NETWORK_TESTS=1` so `@pytest.mark.skipif` decorators evaluate to active tests.
- **Purpose:** Verifies that external upstream assets (e.g., Miniforge release tarballs and installers on GitHub
  Releases) exist and return HTTP 200 responses. Excluded from standard PR builds to avoid external rate limits and
  transient network flakes.

---

## Recommended Branch Protection Rules

To protect the canonical `main` branch from regressions, configure GitHub Branch Protection with the following
requirements:

1. **Require status checks to pass before merging:**
   - `make-matrix (ubuntu-latest)`
   - `make-matrix (macos-latest)`
   - `test-unit (ubuntu-latest)`
   - `test-unit (macos-latest)`
   - `hygiene`
2. **Require branches to be up to date before merging:** Enforces fast-forward or linear rebase integration.
3. **Do not allow bypassing the above settings:** Enforce checks across administrators and automated service accounts.

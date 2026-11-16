# Plan for I-1794816280-getting-started

- **Plan ID:** P-1794816297-ea007beb-antigravity-agent-gemini-3.8-flash-medium
- **Parent Intent ID:** I-1794816280-getting-started
- **Agent:** antigravity-agent/gemini-3.8-flash-medium (version: 1.1.22)
- **Created At:** 2026-11-16T08:05:04Z

## Planner Autonomy Summary

- **Intent handling:** ACCEPT
- **Reframed intent (if applicable):** None. The intent directly addresses developer onboarding and structural clarity
  by introducing a prominent `## Getting Started` section anchored on `make install`, fixing broken inline code
  formatting (` `nvm`/node `) in the intro paragraph, establishing comprehensive category and programming language
  attribution across all tools in the inventory, and encoding these documentation invariants into
  `tests/test_manifest.py`.
- **Exploration stance:** Focused exploit with deterministic documentation restructuring and test invariant validation.
- **Safety priority level:** standard
- **Priority Justification:** Fully complies with `holon-config/world/ruleset.md` §1 (Multi-OS Darwin/Linux parity, pure
  `make -> conda -> ansible` toolchain), `holon-config/world/ruleset.md` §2 (PEP 8, single-pass Prettier formatting with
  code-span arithmetic), `holon-config/world/ruleset.md` §3 (pytest suite invariants), and
  `holon-config/world/constraints.md` §1-§4.

## Exploration

- **Proportion of steps that are exploratory:** 0.00
- **Justification:** Every step addresses deterministic documentation enhancements, markdown table formatting,
  cross-reference streamlining, and unit test assertions.

## Overall Plan Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.20  |
| impact_pred         | 92.0  |
| cost_pred           | 4.0   |
| learning_value_pred | 2.5   |
| ev_pred             | 88.27 |

---

## Step 1: Fix Intro Formatting and Add `## Getting Started` Section to `README.md`

- **Sub‑intent recommendation:** NO
- **Reasoning:** Foundational documentation entry-point refactoring. Fixes the broken inline code formatting in the
  intro paragraph, introduces a canonical three-step `## Getting Started` guide highlighting `make install`, and
  streamlines existing worktree and workflow sections to avoid redundant duplication.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Placing an explicit, linear three-step `## Getting Started` onboarding guide before the
  architecture diagram drastically reduces cognitive overhead for new developers and unambiguously clarifies
  `make install` as the single entry point.
- **Learning target:** Ensure clean markdown flow, accurate clone commands for bare git worktree setups, and proper
  cross-linking without duplicate text blocks.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:** In `README.md`:
  1. Fix line 5: replace broken `` `nvm`/node `` inline-code formatting and explicitly state category/language for each
     primary tool: "`fish` (Terminal / Shell), `neovim` (Editor / IDE), `conda` (Python runtime & package manager),
     `nvm` (Node.js version manager), and the CLI tooling around them are declared here and converged onto the machine."
  2. Add `## Getting Started` section immediately after the intro and before `## Tool Chain & Execution Order`
     containing:
     - **1. Prerequisite (`brew` on macOS, `apt` on Linux)**: Verify `brew` (macOS) or `apt` (Debian/Ubuntu Linux) is
       installed, and install `make` and `git` if absent (`brew install make git` on macOS;
       `sudo apt update && sudo apt install -y make git` on Linux).
     - **2. Clone the Repository**: Present bare-repository + `main` worktree clone sequence:
       - `git clone --bare <repo-url> dev-env/.git`
       - `git --git-dir=dev-env/.git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"`
       - `git --git-dir=dev-env/.git fetch origin`
       - `git --git-dir=dev-env/.git worktree add dev-env/main main`
       - `cd dev-env/main`
     - **3. Kick Off the Environment (`make install`)**: Explicitly designate `make install` as the single entry-point
       command that kicks off and converges the entire development environment end-to-end (`make check` ->
       `make bootstrap` -> `make configure` -> `make converge`), while noting individual stage commands (`make check`,
       `make bootstrap`, `make configure`, `make converge`) for granular execution.
  3. Streamline `## Repository Setup & Worktree Architecture` and `## Commands & Workflow` so they complement
     `## Getting Started` cleanly without verbatim repetition.
- **Git branch:**
  `I-1794816280-getting-started/P-1794816297-ea007beb-antigravity-agent-gemini-3.8-flash-medium/E-1-getting-started-section/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Intro Line Refinement:
   - Locate broken inline backticks around `nvm`/node in `README.md`.
   - Update text to explicitly declare each tool's functional category: `fish` (Terminal / Shell), `neovim` (Editor /
     IDE), `conda` (Python runtime & package manager), `nvm` (Node.js version manager).
2. Getting Started Section Placement:
   - Insert `## Getting Started` between the intro paragraph / horizontal rule and `## Tool Chain & Execution Order`.
   - Structure Step 1 with host OS prerequisites (`brew` or `apt`), explaining that `make` and `git` are needed to
     bootstrap the repository. Provide exact command invocations.
   - Structure Step 2 with the 5-command bare repository worktree checkout workflow into `dev-env/.git` and
     `dev-env/main`.
   - Structure Step 3 highlighting `make install` as the universal cold-start pipeline running all 4 phases, followed by
     the individual granular stage commands.
3. Architecture & Command Streamlining:
   - In `## Repository Setup & Worktree Architecture`, frame the section as architectural rationale and ongoing worktree
     branch management (e.g. adding feature worktrees) rather than repeating the initial clone instructions.
   - In `## Commands & Workflow`, align the Quick Start subsection to reference `make install` as documented in
     `## Getting Started`.

### Dependencies & Critical Path

- **Depends on:** Initial repo checkout
- **Is Bottleneck:** YES (establishes new section headers and terminology for subsequent steps)

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Darwin/Linux parity), `holon-config/world/ruleset.md` §2
  (Prettier markdown formatting).
- **Potential failure modes for this step:** Broken markdown lists, backtick syntax errors, or Prettier reformatting
  collisions.
- **Guardrails and early‑abort checks:** Format using `npx prettier --check README.md` immediately after editing.

### Success & Discard Criteria

- **Success:** `README.md` contains `## Getting Started` with the 3 numbered steps, `make install` is highlighted, the
  intro cleanly attributes categories and has no broken backticks, and Prettier checks pass.
- **Discard:** Discard if formatting fails or required steps are omitted.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.10  |
| impact_pred         | 90.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 2.0   |
| ev_pred             | 89.07 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 90.0 + 0.5 * 2.0 - 0.3 * 0.10 - 1.0 = 89.10 + 1.00 - 0.03 - 1.0 = 89.07`. High confidence
documentation alignment.

---

## Step 2: Update `## Package & Tool Inventory` in `README.md` with Category and Programming Language Attribution

- **Sub‑intent recommendation:** NO
- **Reasoning:** Core documentation enhancement across all inventory subsections. Establishes exhaustive category and
  programming language classification across all 22 core packages, language runtimes, stow packages, shell plugins,
  Neovim plugins, and GUI casks/purged packages.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Adding explicit Category / Programming Language columns and annotations across every tool
  in the inventory guarantees full transparency of package taxonomy, runtime origins, and domain boundaries.
- **Learning target:** Ensure clean table syntax conforming to Prettier width and cell alignments across all 6
  subsections.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:** In `README.md` under `## Package & Tool Inventory`:
  1. **### 1. Core CLI Packages (`devenv_packages_core`)**:
     - Expand table to 6 columns: `| Logical Package | Category | macOS (\`brew\`) Formula | Linux (\`apt\`) Package |
       Stow Status | Description |`.
     - Assign exact categories to all 22 core packages:
       - `fish`: `Terminal / Shell`
       - `neovim`: `Editor / IDE`
       - `tmux`: `Terminal / Multiplexer`
       - `git`: `Version Control`
       - `gh`: `Git / GitHub`
       - `delta`: `Git / Diff`
       - `stow`: `Dotfiles / Symlinks`
       - `curl`: `Networking / HTTP`
       - `aria2`: `Networking / Download`
       - `autossh`: `Networking / SSH`
       - `openssh`: `Networking / SSH`
       - `iperf3`: `Networking / Benchmark`
       - `fd`: `Filesystem / Search`
       - `ripgrep`: `Filesystem / Search`
       - `fzf`: `Terminal / Search`
       - `ncdu`: `Filesystem / Disk`
       - `rsync`: `Filesystem / Sync`
       - `tree`: `Filesystem / Navigation`
       - `jq`: `Data / JSON`
       - `htop`: `System Monitoring`
       - `watch`: `System Monitoring`
       - `unzip`: `Archive / Compression`
  2. **### 2. Language Runtimes & Conda Tools**:
     - Replace list with Markdown table `| Tool / Runtime | Category / Language | Provisioned Via | Description |`.
     - Explicitly attribute:
       - `CPython 3.13` / `Miniforge3` (`conda`): `Python (Runtime & Environment Manager)`
       - `uv`: `Python (Package & Project Manager)`
       - `ruff`: `Python (Linter & Formatter)`
       - `pre-commit`: `Multi-Language (Git Hooks)`
       - `nvm.fish` + `Node.js 22.23.2`: `JavaScript / TypeScript (Node.js Runtime & Version Manager)`
  3. **### 3. GNU Stow Packages & Config Variants (`devenv_package_variants`)**:
     - Add explicit category/language labels to each stow package:
       - `bash`: `Terminal / Shell`
       - `conda`: `Python Package Manager`
       - `fish`: `Terminal / Shell`
       - `tmux`: `Terminal / Multiplexer`
       - `zsh`: `Terminal / Shell`
       - `nvim-kickstart` / `nvim-minimal` / `nvim-lazyvim`: `Editor / IDE`
  4. **### 4. Fish Shell Plugins (`fish_plugins`)**:
     - Explicitly label category/language for each plugin:
       - `jorgebucaran/fisher`: `Terminal / Shell`
       - `reitzig/sdkman-for-fish@v2.1.0`: `Java / JVM`
       - `jorgebucaran/nvm.fish`: `JavaScript / Node.js`
  5. **### 5. Neovim Plugins (`nvim-pack-lock.json`)**:
     - Explicitly state that all 26 plugins are `Editor / IDE (Neovim / Lua)` plugins, and provide functional categories
       for each (e.g. Snippets, Completion, Formatting, Diff / Git, Status / Progress, Fuzzy Search, Git Signs,
       Indentation, LSP Management, Treesitter Syntax, Lua Utilities, Markdown Rendering, Theme / Colorscheme,
       Keybinding Discovery).
  6. **### 6. macOS GUI Casks & Purged Unmanaged Packages**:
     - Explicitly label `docker-desktop` (`Containers / Virtualization`) and `nvm`, `node` (`JavaScript / Node.js`).
- **Git branch:**
  `I-1794816280-getting-started/P-1794816297-ea007beb-antigravity-agent-gemini-3.8-flash-medium/E-2-inventory-category-attribution/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Subsection 1 Table Expansion:
   - Edit the Markdown table in `### 1. Core CLI Packages` to insert the `Category` header at index 2.
   - Populate all 22 package rows with the exact required categories.
   - Alphabetize or preserve current order consistently while ensuring every package has its corresponding category tag.
2. Subsection 2 Structured Table:
   - Construct a standard 4-column Markdown table with columns `Tool / Runtime`, `Category / Language`,
     `Provisioned Via`, and `Description`.
   - Populate rows for CPython 3.13 / Miniforge3, uv, ruff, pre-commit, and nvm.fish + Node.js 22.23.2.
3. Subsection 3 GNU Stow Package Attribution:
   - Annotate bash, conda, fish, tmux, and zsh bullet items with their respective categories.
   - Annotate nvim-kickstart, nvim-minimal, and nvim-lazyvim with `Editor / IDE`.
4. Subsection 4 Fish Plugin Attribution:
   - Append `**Terminal / Shell**`, `**Java / JVM**`, and `**JavaScript / Node.js**` to the respective fisher plugin
     entries.
5. Subsection 5 Neovim Plugin Classification:
   - Add a header statement confirming all 26 plugins are `Editor / IDE (Neovim / Lua)`.
   - Add functional tags for each plugin in the list (e.g. `LuaSnip` - Snippet Engine, `blink.cmp` - Autocompletion
     Engine, etc.).
6. Subsection 6 Casks & Purged Attribution:
   - Tag `docker-desktop` with `Containers / Virtualization` and `nvm`/`node` with `JavaScript / Node.js`.

### Dependencies & Critical Path

- **Depends on:** Step 1
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1 (Parity and consistency with group_vars/all.yml),
  `holon-config/world/ruleset.md` §2 (Prettier markdown formatting).
- **Potential failure modes for this step:** Misalignment of markdown table columns or omitting any of the 22 core
  packages.
- **Guardrails and early‑abort checks:** Validate with `npx prettier --check README.md` and check row counts.

### Success & Discard Criteria

- **Success:** All 6 subsections have explicit Category / Programming Language attributions, the core table includes the
  `Category` column for all 22 packages, and Prettier checks cleanly.
- **Discard:** Discard if any tool lacks category attribution or markdown table formatting breaks.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.10  |
| impact_pred         | 92.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 2.0   |
| ev_pred             | 91.05 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 2.0 - 0.3 * 0.10 - 1.0 = 91.08 + 1.00 - 0.03 - 1.0 = 91.05`. High
deterministic documentation fidelity.

---

## Step 3: Update `tests/test_manifest.py` with Structural and Content Invariant Assertions

- **Sub‑intent recommendation:** NO
- **Reasoning:** Invariant testing phase. Embeds automated assertions in `tests/test_manifest.py` ensuring the
  documentation additions cannot be inadvertently regressed or degraded in future changes.
- **Step Type:** REFACTOR
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Explicitly asserting the existence of `## Getting Started`, the `make install` entry
  point, the absence of the broken `` `nvm`/node `` string, and category attributions guarantees permanent compliance
  with documentation architecture.
- **Learning target:** Construct robust string and regex assertions in `tests/test_manifest.py` without brittle
  line-number coupling.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:** In `tests/test_manifest.py`:
  1. Add tests (e.g. `test_readme_getting_started_and_entrypoint` and `test_readme_category_and_language_attributions`):
     - Assert `README.md` contains `## Getting Started`.
     - Assert `README.md` clearly documents `make install` as the single entry-point command.
     - Assert `README.md` does not contain the broken `` `nvm`/node `` inline-code string.
     - Assert `README.md` table header contains
       `| Logical Package | Category | macOS (`brew`) Formula | Linux (`apt`) Package | Stow Status | Description |`.
     - Assert key categories and language attributions are present for primary stacks:
       - `Terminal / Shell`
       - `Editor / IDE`
       - `Python (Runtime & Environment Manager)`
       - `Python (Package & Project Manager)`
       - `Python (Linter & Formatter)`
       - `Multi-Language (Git Hooks)`
       - `JavaScript / TypeScript (Node.js Runtime & Version Manager)`
       - `Java / JVM`
       - `Containers / Virtualization`
     - Assert every core package in `group_vars["devenv_packages_core"]` has an associated category in the table.
- **Git branch:**
  `I-1794816280-getting-started/P-1794816297-ea007beb-antigravity-agent-gemini-3.8-flash-medium/E-3-test-manifest-invariants/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Test Design in `tests/test_manifest.py`:
   - Import necessary fixtures and conftest utilities.
   - Define test `test_readme_getting_started_and_entrypoint`:
     - Load `README.md` via `read(REPO_ROOT / "README.md")`.
     - Assert presence of `## Getting Started` header.
     - Assert `make install` is documented alongside the sequential workflow (`make check`, `make bootstrap`,
       `make configure`, `make converge`).
     - Assert broken string with adjacent backticks and slash is absent.
   - Define test `test_readme_tool_category_attributions`:
     - Assert markdown table header in `### 1. Core CLI Packages` includes the `Category` column.
     - Assert presence of category definitions for core packages, language runtimes, stow packages, fish plugins, Neovim
       plugins, and macOS casks / purged tools.
2. Maintain PEP 8 and Pytest Conventions:
   - Ensure docstrings, typing hints, and formatting align with `ruff` rules.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §2 (PEP 8 standards), §3 (pytest runner, tests in `tests/`).
- **Potential failure modes for this step:** Assertions too brittle (e.g. strict whitespace dependencies) causing
  false-positive failures.
- **Guardrails and early‑abort checks:** Use semantic string searches and table row parsing.

### Success & Discard Criteria

- **Success:** New tests pass when run via `uv run --extra test pytest -m "not network" -k "readme"`.
- **Discard:** Discard if tests fail or if test syntax violates ruff linting.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.10  |
| impact_pred         | 92.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 2.0   |
| ev_pred             | 91.05 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 92.0 + 0.5 * 2.0 - 0.3 * 0.10 - 1.0 = 91.08 + 1.00 - 0.03 - 1.0 = 91.05`. High confidence
test hardening.

---

## Step 4: Execute Full Validation Pipeline across Pytest, Ruff, Ansible-Lint, Prettier, and Make

- **Sub‑intent recommendation:** NO
- **Reasoning:** Complete verification gate ensuring zero regressions across all codebase invariants, style guides,
  playbooks, and documentation.
- **Step Type:** VERIFICATION
- **Exploration level:** EXPLOIT
- **Hypothesis being tested:** Running all five verification suites confirms that the README enhancements and test
  additions satisfy all linting, formatting, schema, and runtime rules without regression.
- **Learning target:** Complete verification pass with zero warnings across all linters.
- **Maximum acceptable cost for this learning:** 1.0

### Intent & Git Integration

- **Step Intent:** Run verification toolchain:
  1. `uv run --extra test pytest -m "not network"`
  2. `uv run ruff check .`
  3. `uv run --extra test ansible-lint ansible/site.yml`
  4. `npx prettier --check "**/*.md"`
  5. `make check`
- **Git branch:**
  `I-1794816280-getting-started/P-1794816297-ea007beb-antigravity-agent-gemini-3.8-flash-medium/E-4-verification-pipeline/_`
- **Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Pytest Execution:
   - Run `uv run --extra test pytest -m "not network"` to test manifest invariants, wizard unit tests, and templating
     checks.
2. Code Formatting & Python Linting:
   - Run `uv run ruff check .` verifying PEP 8 compliance in `tests/test_manifest.py`.
3. Ansible Playbook Linting:
   - Run `uv run --extra test ansible-lint ansible/site.yml` verifying playbook integrity.
4. Markdown Prettier Check:
   - Run `npx prettier --check "**/*.md"` ensuring single-pass Prettier compliance across all Markdown documents
     including tables and plans.
5. Makefile Read-Only Check:
   - Run `make check` to verify prerequisite probe functionality.

### Dependencies & Critical Path

- **Depends on:** Step 1, Step 2, Step 3
- **Is Bottleneck:** NO

### Safety & Constraint Considerations

- **Relevant rules:** `holon-config/world/ruleset.md` §1, §2, §3; `holon-config/world/constraints.md` §1-§4.
- **Potential failure modes for this step:** Prettier formatting diffs on edited markdown; unexpected syntax warnings.
- **Guardrails and early‑abort checks:** Fix any formatting or lint issues immediately before finalizing.

### Success & Discard Criteria

- **Success:** All 5 commands exit with status 0; no lint or formatting errors; `make check` runs cleanly.
- **Discard:** Discard and fix any failure in the verification pipeline.

### Metrics

| metric              | value |
| ------------------- | ----- |
| p_success_pred      | 0.99  |
| entropy_pred        | 0.05  |
| impact_pred         | 94.0  |
| cost_pred           | 1.0   |
| learning_value_pred | 1.0   |
| ev_pred             | 92.55 |

### Step Metrics Rationale

Calculated via: `EV = 0.99 * 94.0 + 0.5 * 1.0 - 0.3 * 0.05 - 1.0 = 93.06 + 0.50 - 0.015 - 1.0 = 92.545 ~ 92.55`. Final
validation audit confirming readiness.

---

## Strategy Rationale

The overall plan metrics were derived from the individual step-level metrics as follows:

- **p_success_pred**: 0.99. Derived from step probabilities (Step 1: 0.99, Step 2: 0.99, Step 3: 0.99, Step 4: 0.99).
  The tasks involve deterministic markdown editing, standard pytest assertions, and established CI verification tooling.
- **entropy_pred**: 0.20. Maximum single-step risk is 0.10. The sum of step entropies across the four steps is 0.35
  (`0.10 + 0.10 + 0.10 + 0.05 = 0.35`), well within the process sandbox threshold of 10.0.
- **impact_pred**: 92.0. Fixes broken inline code formatting, introduces an intuitive, linear `## Getting Started`
  section highlighting `make install`, streamlines redundant workflow text, documents complete Category / Programming
  Language taxonomies for all 22 core packages and associated tools, and establishes permanent regression tests.
- **cost_pred**: 4.0. Computed as the direct sum of predicted step costs (`1.0 + 1.0 + 1.0 + 1.0 = 4.0`).
- **learning_value_pred**: 2.5. Validating clean Prettier table alignment, documentation layout cohesion, and invariant
  testing techniques.
- **ev_pred**: 88.27. Computed strictly via the config-driven Expected Value formula:
  `EV = P(success) * Impact + mu * LearningValue - lambda * Delta_S_intent - Cost`. With system constants `lambda = 0.3`
  and `mu = 0.5` loaded from `holon-config/metrics/ev_config.json`:
  `EV = 0.99 * 92.0 + 0.5 * 2.5 - 0.3 * 0.20 - 4.0 = 91.08 + 1.25 - 0.06 - 4.0 = 88.27`.

## Safety & Constraint Alignment

- **Key world ruleset constraints that affect this plan:**
  - `holon-config/world/ruleset.md` §1 (Runtime & Environment Specification: pure `make -> conda -> ansible` toolchain,
    Darwin/Linux parity, single manifest declarations).
  - `holon-config/world/ruleset.md` §2 (Coding Conventions & Standards: PEP 8 compliance, static typing, single-pass
    Prettier formatting with code-span arithmetic).
  - `holon-config/world/ruleset.md` §3 (Testing Constraints: pytest runner, tests located in `tests/`, all test
    modifications explicitly declared during planning).
  - `holon-config/world/constraints.md` §1 (Git Flow & Branch Constraints: branch prefix isolation
    `I-{timestamp}-{slug}/P-{timestamp}-{agent}-{model}/E-{timestamp}-{action}/_`).
  - `holon-config/world/constraints.md` §2 (Sandbox Containment Tiers: process sandbox $< 10$ entropy).
  - `holon-config/world/constraints.md` §3 (Environment Mutation Boundaries: converge through manifest, two backends
    only: `brew` and `apt`).
  - `holon-config/world/constraints.md` §4 (Ledger Immutability: zero modifications to historical ledger entries).
- **Potential violations or edge cases:**
  - Prettier table reformatting: Markdown tables must have consistent column delimiters so Prettier does not rewrap them
    awkwardly.
  - Test fragility: String assertions in `test_manifest.py` should check semantic tokens rather than exact line breaks
    to avoid unnecessary fragility.
- **Mitigations built into the plan:**
  - Automated format check with `npx prettier --check "**/*.md"` in Step 4.
  - Verification of test suite via `uv run --extra test pytest -m "not network"`.
- **Residual risk accepted (and why):**
  - None. Documentation refactoring and pytest assertion additions carry negligible risk of environmental side effects.
- **Allocated Entropy Budget:** 10.0
- **Predicted Plan Entropy:** 0.20
- **Budget Compliance:** The strategy fits comfortably within budget (`0.20 <= 10.0`).

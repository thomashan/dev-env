# ============================================================================
# dev-env entry point.
#
# Division of labour: make bootstraps Ansible and nothing else; Ansible owns
# every package, runtime and dotfile. There are deliberately no .sh files in
# this repository -- make recipes stay short enough to review in a PR diff.
#
# Compatible with GNU Make 3.81, which is what /usr/bin/make is on macOS.
# No .ONESHELL, no $(file), no != operator, no .RECIPEPREFIX.
# ============================================================================

.DEFAULT_GOAL := help

SELF_DIR := $(patsubst %/,%,$(dir $(realpath $(firstword $(MAKEFILE_LIST)))))

CONDA_DIR   ?= $(shell if command -v conda >/dev/null 2>&1; then conda info --base 2>/dev/null; elif [ -d /opt/homebrew/Caskroom/miniforge/base ]; then echo /opt/homebrew/Caskroom/miniforge/base; elif [ -d /usr/local/Caskroom/miniforge/base ]; then echo /usr/local/Caskroom/miniforge/base; elif [ -d $(HOME)/miniforge3 ]; then echo $(HOME)/miniforge3; elif [ -d /opt/homebrew ]; then echo /opt/homebrew/Caskroom/miniforge/base; elif [ "$$(uname -s)" = "Darwin" ]; then echo /usr/local/Caskroom/miniforge/base; else echo $(HOME)/miniforge3; fi)
CONDA       ?= $(shell command -v conda 2>/dev/null || echo $(CONDA_DIR)/bin/conda)
DEVENV_HOME := $(HOME)/.local/share/dev-env
COLLECTIONS := $(DEVENV_HOME)/collections
PB          := $(CONDA_DIR)/bin/ansible-playbook
GALAXY      := $(CONDA_DIR)/bin/ansible-galaxy
LINT        := $(CONDA_DIR)/bin/ansible-lint
SITE        := $(SELF_DIR)/ansible/site.yml

# The target interpreter comes from ansible_playbook_python (see group_vars),
# so nothing here has to name an interpreter path -- and the space in
# ~/Library/Application Support never reaches Ansible.
ANSIBLE_ENV = ANSIBLE_CONFIG=$(SELF_DIR)/ansible.cfg \
              ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS)

ifeq ($(CI),true)
ANSIBLE_EXTRA ?=
else
ANSIBLE_EXTRA ?=
endif

# --- refuse to run under a non-GNU make, before any target executes ---------
ifeq ($(origin MAKE_VERSION),undefined)
$(error dev-env requires Homebrew (macOS) or apt (Debian/Ubuntu). If make is not installed yet, install it via 'brew install make' (or xcode-select --install) on macOS or 'sudo apt install -y make' on Linux before running make install)
endif
MAKE_OK := $(shell expr $(firstword $(subst ., ,$(MAKE_VERSION))) \>= 3 2>/dev/null)
ifeq ($(MAKE_OK),0)
$(error GNU Make >= 3.81 required, found $(MAKE_VERSION))
endif

.PHONY: help check configure bootstrap install converge check-mode dotfiles nvim-sync fisher \
        lint test test-all docs-fmt probe-packages facts login-shell unlink clean-cache doctor

help:
	@echo "dev-env -- repository-owned development environment (make bootstraps, ansible converges)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Bootstrap and converge:"
	@printf "  %-16s %s\n" "check"          "Read-only prerequisite probe (never installs)"
	@printf "  %-16s %s\n" "configure"      "Interactive host wizard (writes choices.yml)"
	@printf "  %-16s %s\n" "bootstrap"      "Install Conda, ansible-core, ansible-lint and collections"
	@printf "  %-16s %s\n" "install"        "check + configure (interactive) + bootstrap + converge"
	@printf "  %-16s %s\n" "converge"       "ansible-playbook site.yml --diff"
	@printf "  %-16s %s\n" "check-mode"     "ansible --check --diff (dry run; needs prior install)"
	@printf "  %-16s %s\n" "doctor"         "Idempotence probe: dry-run diff plus repo-write check"
	@echo ""
	@echo "Scoped runs:"
	@printf "  %-16s %s\n" "dotfiles"       "Re-link dotfiles only"
	@printf "  %-16s %s\n" "nvim-sync"      "Install Neovim plugins at locked revisions"
	@printf "  %-16s %s\n" "fisher"         "Sync fish plugins"
	@printf "  %-16s %s\n" "probe-packages" "Package installs in --check mode for this OS"
	@printf "  %-16s %s\n" "facts"          "Show resolved platform facts and package list"
	@printf "  %-16s %s\n" "login-shell"    "Make fish the login shell (prompts for password)"
	@printf "  %-16s %s\n" "unlink"         "Remove managed symlinks (needs CONFIRM=yes)"
	@echo ""
	@echo "Quality:"
	@printf "  %-16s %s\n" "lint"           "ansible-lint over the playbook"
	@printf "  %-16s %s\n" "test"           "Pytest unit tests for the manifest and role Jinja"
	@printf "  %-16s %s\n" "test-all"       "unit tests plus the opt-in network asset checks"
	@printf "  %-16s %s\n" "docs-fmt"       "Prettier for markdown (skipped without npx)"
	@printf "  %-16s %s\n" "clean-cache"    "Delete downloaded installers in ~/.cache/dev-env"
	@echo ""
	@echo "Cold start on a machine without make: Homebrew (macOS) or apt (Debian/Ubuntu)"
	@echo "is required. If make is not installed yet, install it via 'brew install make'"
	@echo "(or xcode-select --install) on macOS or 'sudo apt install -y make' on Linux,"
	@echo "then run 'make install'. There is no curl | sh bootstrap by design."
	@echo ""

check:
	@echo "Checking prerequisites for dev-env ($$(uname -s)/$$(uname -m))"; \
	err=0; warn=0; \
	printf "%-26s " "GNU Make"; \
	printf "ok (%s)\n" "$(MAKE_VERSION)"; \
	printf "%-26s " "OS"; \
	case "$$(uname -s)" in Darwin|Linux) echo "supported ($$(uname -s))";; *) echo "UNSUPPORTED: $$(uname -s)"; err=$$((err+1));; esac; \
	printf "%-26s " "brew"; \
	if [ -x /opt/homebrew/bin/brew ] || [ -x /usr/local/bin/brew ] || [ -x /home/linuxbrew/.linuxbrew/bin/brew ] || [ -x "$$HOME/.linuxbrew/bin/brew" ] || command -v brew >/dev/null 2>&1; then \
		echo "ok"; \
	else \
		echo "MISSING: Homebrew (brew) is required"; err=$$((err+1)); \
	fi; \
	printf "%-26s " "apt (Linux backend)"; \
	case "$$(uname -s)" in Linux) \
		if command -v apt >/dev/null 2>&1; then echo "ok"; else echo "MISSING: apt is required"; err=$$((err+1)); fi;; \
		*) echo "n/a";; esac; \
	printf "%-26s " "conda"; \
	if command -v conda >/dev/null 2>&1 || [ -x "$(CONDA)" ]; then conda_ver=$$("$(CONDA)" --version 2>/dev/null | head -1); echo "ok ($$conda_ver)"; else echo "will be installed by make bootstrap"; warn=$$((warn+1)); fi; \
	printf "%-26s " "ansible-core"; \
	if [ -x "$(PB)" ]; then echo "ok"; else echo "will be installed by make bootstrap"; warn=$$((warn+1)); fi; \
	printf "%-26s " "community.general"; \
	if ls "$(COLLECTIONS)/ansible_collections/community/general" >/dev/null 2>&1; then echo "ok"; else echo "will be installed by make bootstrap"; warn=$$((warn+1)); fi; \
	echo ""; \
	if [ $$err -gt 0 ]; then echo "FAILED: $$err critical prerequisite(s) missing."; exit 1; fi; \
	if [ $$warn -gt 0 ]; then echo "ok: core prerequisites present, $$warn item(s) will be installed by 'make bootstrap'."; \
	else echo "ok: every prerequisite is satisfied."; fi

bootstrap:
	@echo "Bootstrapping Ansible via Conda (GNU Make -> Conda -> Ansible)..."
	@brew_bin=""; \
	if [ -x /opt/homebrew/bin/brew ]; then brew_bin="/opt/homebrew/bin/brew"; \
	elif [ -x /usr/local/bin/brew ]; then brew_bin="/usr/local/bin/brew"; \
	elif [ -x /home/linuxbrew/.linuxbrew/bin/brew ]; then brew_bin="/home/linuxbrew/.linuxbrew/bin/brew"; \
	elif [ -x "$$HOME/.linuxbrew/bin/brew" ]; then brew_bin="$$HOME/.linuxbrew/bin/brew"; \
	elif command -v brew >/dev/null 2>&1; then brew_bin="$$(command -v brew)"; fi; \
	if [ -z "$$brew_bin" ]; then echo "Error: Homebrew (brew) is required." >&2; exit 1; fi; \
	os="$$(uname -s)"; \
	case "$$os" in \
		Linux) \
			command -v apt >/dev/null 2>&1 || { echo "Error: apt is required on Linux." >&2; exit 1; } ;; \
		Darwin) ;; \
		*) echo "Unsupported OS: $$os" >&2; exit 1 ;; \
	esac; \
	if ! command -v conda >/dev/null 2>&1 && [ ! -x "$(CONDA)" ]; then \
		echo "Installing Conda via Homebrew..."; \
		case "$$os" in \
			Darwin) \
				"$$brew_bin" install --cask miniforge || exit 1 ;; \
			Linux) \
				"$$brew_bin" install micromamba || exit 1; \
				mamba_bin=""; \
				if [ -x "$$(dirname "$$brew_bin")/micromamba" ]; then \
					mamba_bin="$$(dirname "$$brew_bin")/micromamba"; \
				elif command -v micromamba >/dev/null 2>&1; then \
					mamba_bin="$$(command -v micromamba)"; \
				else \
					echo "Error: micromamba not found after brew install micromamba" >&2; exit 1; \
				fi; \
				"$$mamba_bin" create -y -p "$(CONDA_DIR)" -c conda-forge --override-channels conda python=3.13 ansible-core ansible-lint pyyaml || exit 1 ;; \
		esac; \
	fi
	@"$(CONDA)" install -y -c conda-forge --override-channels python=3.13 ansible-core ansible-lint pyyaml || exit 1
	@mkdir -p "$(DEVENV_HOME)" "$(COLLECTIONS)"
	@test -x "$(PB)" || { echo "bootstrap: $(PB) is missing or not executable"; exit 1; }
	@ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)" "$(GALAXY)" collection install \
		-r "$(SELF_DIR)/ansible/requirements.yml" --force || exit 1
	@echo "Ansible: $$( "$(PB)" --version 2>/dev/null | head -1 )"
	@echo "Run 'make install' or 'make check-mode' next."

configure:
	@if [ -x "$(CONDA_DIR)/bin/python3" ]; then \
		"$(CONDA_DIR)/bin/python3" "$(SELF_DIR)/scripts/devenv_wizard.py"; \
	else \
		echo "Error: Python 3 not found in $(CONDA_DIR)/bin/python3. Run 'make bootstrap' first." >&2; \
		exit 1; \
	fi

install: check
	@$(MAKE) bootstrap
	@if [ -t 0 ] && [ ! "$$CI" = "true" ] && [ ! -f "$$HOME/.config/dev-env/choices.yml" ]; then \
		$(MAKE) configure || exit 1; \
	fi
	@$(MAKE) converge

converge:
	@$(ANSIBLE_ENV) "$(PB)" "$(SITE)" --diff $(ANSIBLE_EXTRA)

check-mode:
	@$(ANSIBLE_ENV) "$(PB)" "$(SITE)" --check --diff $(ANSIBLE_EXTRA)

dotfiles:
	@command -v stow >/dev/null 2>&1 || { echo "GNU Stow is required for dotfiles management. Run 'make converge' or install stow."; exit 1; }
	@$(ANSIBLE_ENV) "$(PB)" "$(SITE)" --tags dotfiles --diff $(ANSIBLE_EXTRA)

nvim-sync:
	@$(ANSIBLE_ENV) "$(PB)" "$(SITE)" --tags nvim-sync --diff $(ANSIBLE_EXTRA)

fisher:
	@$(ANSIBLE_ENV) "$(PB)" "$(SITE)" --tags fisher $(ANSIBLE_EXTRA)

probe-packages:
	@$(ANSIBLE_ENV) "$(PB)" "$(SITE)" --tags packages --check --diff $(ANSIBLE_EXTRA)

facts:
	@$(ANSIBLE_ENV) "$(PB)" "$(SITE)" --tags bootstrap $(ANSIBLE_EXTRA)

login-shell:
	@$(ANSIBLE_ENV) "$(PB)" "$(SITE)" -e devenv_set_login_shell=true $(ANSIBLE_EXTRA)

unlink:
	@command -v stow >/dev/null 2>&1 || { echo "GNU Stow is required for unlink. Please install stow first."; exit 1; }
	@test "$(CONFIRM)" = "yes" || { echo "refusing to touch ~/.config without CONFIRM=yes"; exit 1; }
	@$(ANSIBLE_ENV) "$(PB)" "$(SELF_DIR)/ansible/playbooks/unlink.yml" --diff $(ANSIBLE_EXTRA)

doctor:
	@echo "== dry-run diff (empty output below means the environment is converged) =="
	@$(ANSIBLE_ENV) "$(PB)" "$(SITE)" --check $(ANSIBLE_EXTRA) || { echo "dry run reported changes or failures (see above)"; }
	@echo "== repo integrity (ansible must never write into the working tree) =="
	@git -C "$(SELF_DIR)" status --porcelain -- dotfiles ansible | sed -n '1,20p'
	@echo "== managed links =="
	@git -C "$(SELF_DIR)" ls-files dotfiles | sed -e 's#^#tracked: #'

lint:
	@test -x "$(LINT)" || { echo "ansible-lint not bootstrapped; run 'make bootstrap'"; exit 1; }
	@cd "$(SELF_DIR)" && $(ANSIBLE_ENV) "$(LINT)" ansible/site.yml

docs-fmt:
	@command -v npx >/dev/null 2>&1 || { echo "npx not found (install node via nvm) -- skipping prettier"; exit 0; }
	@npx --yes prettier@3 --write "**/*.md"

clean-cache:
	@rm -rf "$$HOME/.cache/dev-env"
	@echo "cleared ~/.cache/dev-env"

# Unit tests run in a uv-locked virtualenv (pyproject.toml) if uv is installed,
# or under Conda Python / system pytest.
test:
	@if command -v uv >/dev/null 2>&1; then \
		uv run --extra test pytest -m "not network" $(PYTEST_EXTRA); \
	elif [ -x "$(CONDA_DIR)/bin/pytest" ]; then \
		"$(CONDA_DIR)/bin/pytest" -m "not network" $(PYTEST_EXTRA); \
	else \
		pytest -m "not network" $(PYTEST_EXTRA); \
	fi

test-all:
	@if command -v uv >/dev/null 2>&1; then \
		uv run --extra test pytest $(PYTEST_EXTRA); \
	elif [ -x "$(CONDA_DIR)/bin/pytest" ]; then \
		"$(CONDA_DIR)/bin/pytest" $(PYTEST_EXTRA); \
	else \
		pytest $(PYTEST_EXTRA); \
	fi

"""Shared fixtures: repo data plus a real Ansible templar.

The point of the templar fixture is that tests evaluate the *same* Jinja the
roles evaluate, using ansible-core's own filter plugins -- not a Python
re-implementation that could pass while the playbook is broken.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_yaml(path: Path) -> dict:
    with path.open() as handle:
        return yaml.safe_load(handle) or {}


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def group_vars() -> dict:
    return _load_yaml(REPO_ROOT / "ansible" / "group_vars" / "all.yml")


@pytest.fixture(scope="session")
def alias_tables() -> dict[str, dict]:
    """backend name -> alias mapping, for every table on disk."""
    out: dict[str, dict] = {}
    for path in sorted((REPO_ROOT / "ansible" / "vars").glob("pkg_*.yml")):
        backend = path.stem.removeprefix("pkg_")
        out[backend] = _load_yaml(path).get("devenv_pkg_aliases", {})
    return out


@pytest.fixture(scope="session")
def os_vars() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted((REPO_ROOT / "ansible" / "vars").glob("os_*.yml")):
        out[path.stem.removeprefix("os_")] = _load_yaml(path)
    return out


@pytest.fixture(scope="session")
def link_manifest(group_vars) -> list[dict]:
    return group_vars["devenv_links"]


@pytest.fixture(scope="session")
def templar():
    """Ansible's own templating engine, with its real filter plugin set."""
    from ansible.parsing.dataloader import DataLoader
    from ansible.template import Templar, trust_as_template

    def render(expression: str, variables: dict):
        # ansible-core >= 2.19 refuses to render a string it does not consider a
        # trusted template (template-injection hardening). These expressions come
        # from this repository's own YAML, so marking them trusted is correct --
        # and it is what a playbook does implicitly when it reads its own tasks.
        # convert_bare=True is required: `when:` clauses and assert items are
        # written bare (devenv_x not in y) rather than as {{ ... }} templates.
        return Templar(loader=DataLoader(), variables=variables).template(
            trust_as_template(expression),
            convert_bare=True,
        )

    return render


def role_task_files() -> list[Path]:
    return sorted((REPO_ROOT / "ansible" / "roles").glob("*/tasks/*.yml"))


def role_files() -> list[Path]:
    return sorted(p for p in (REPO_ROOT / "ansible").rglob("*.yml"))


def read(path: Path) -> str:
    return path.read_text()


VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

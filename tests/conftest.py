"""Shared test fixtures: import the bundled scripts and fake the registries.

The tests never touch the network. Registry responses are injected through
``rx_common.Net(transport=...)`` so verdict logic is tested deterministically.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict

import pytest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "researchx"
SCRIPTS = SKILL / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SKILL))

import rx_common  # noqa: E402
import verify_citations  # noqa: E402
import prisma_screen  # noqa: E402
import search_literature  # noqa: E402


def load_fixture(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class FakeRegistry:
    """Maps a URL fragment to a recorded registry response."""

    def __init__(self, routes: Dict[str, Any], default_error: str = "not found (404)") -> None:
        self.routes = routes
        self.default_error = default_error
        self.calls = []

    def __call__(self, url: str) -> Any:
        self.calls.append(url)
        for fragment, payload in self.routes.items():
            if fragment in url:
                if isinstance(payload, Exception):
                    raise payload
                if callable(payload):
                    return payload(url)
                return payload
        raise RuntimeError(self.default_error)


@pytest.fixture
def fake_net(monkeypatch):
    """Patch rx.Net so every script under test uses the injected transport."""

    def make(routes: Dict[str, Any], offline: bool = False, default_error: str = "not found (404)"):
        registry = FakeRegistry(routes, default_error=default_error)

        class _Net(rx_common.Net):
            def __init__(self, *args, **kwargs):
                kwargs.update(transport=registry, offline=offline, cache_dir=None)
                super().__init__(*args, **kwargs)

        for module in (verify_citations, prisma_screen, search_literature):
            monkeypatch.setattr(module.rx, "Net", _Net)
        monkeypatch.setattr(sys.modules["rx_common"], "Net", _Net)
        return registry

    return make


@pytest.fixture
def crossref_doi_body():
    return load_fixture("crossref_doi.json")


@pytest.fixture
def crossref_search_body():
    return load_fixture("crossref_search.json")


@pytest.fixture
def openalex_search_body():
    return load_fixture("openalex_search.json")


@pytest.fixture
def arxiv_atom():
    return (FIXTURES / "arxiv_query.xml").read_text(encoding="utf-8")


@pytest.fixture
def hits():
    return load_fixture("hits.json")

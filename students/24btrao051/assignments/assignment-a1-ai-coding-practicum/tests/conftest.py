"""Shared pytest configuration and fixtures for the TabSplit test suite."""

import sys
from itertools import count
from pathlib import Path

# Make the ``tabsplit`` package importable when pytest is run from the
# project root without the project being installed (src-layout).
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from tabsplit import main  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_store(monkeypatch):
    """Give every test a pristine, isolated in-memory store.

    Replaces ``tabsplit.main.groups`` with an empty dict and rewinds the
    id counter, so tests never observe state leaked from other tests.
    ``monkeypatch`` restores the originals afterwards.
    """
    monkeypatch.setattr(main, "groups", {})
    monkeypatch.setattr(main, "_next_group_id", count(start=1))


@pytest.fixture()
def client() -> TestClient:
    """HTTP client wired directly to the FastAPI app (no live server).

    Returns:
        TestClient bound to tabsplit.main.app.
    """
    return TestClient(main.app)

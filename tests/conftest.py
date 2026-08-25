from __future__ import annotations

import pytest

from agents.orchestrator import state as orchestrator_state
from mock_systems.supplier_api.db import DB_PATH
from mock_systems.supplier_api.seed import seed_events
from mock_systems.erp_api.seed import seed_data


@pytest.fixture(autouse=True)
def _fresh_db():
    orchestrator_state.reset()
    if DB_PATH.exists():
        DB_PATH.unlink()
    seed_events()
    seed_data()
    yield
    orchestrator_state.reset()
    if DB_PATH.exists():
        DB_PATH.unlink()

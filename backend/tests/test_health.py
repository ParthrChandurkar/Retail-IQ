"""Tests for the Phase 1 health endpoint."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_ok_when_database_is_reachable() -> None:
    """The endpoint reports a healthy application and database."""
    application = create_app(enable_database_bootstrap=False)

    with (
        patch(
            "app.routers.health.check_database_connection",
            new=AsyncMock(return_value=None),
        ),
        TestClient(application) as client,
    ):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "reachable"}

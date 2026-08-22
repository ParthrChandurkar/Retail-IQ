"""Phase 8 regression, authorization, validation, and service-stage tests."""

from datetime import date
from typing import Any

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import admin_user, current_user
from app.main import create_app
from app.ml.preprocessing import build_preprocessor
from app.routers import analytics
from app.schemas.filters import SharedFilters
from app.services.api_database import pagination_sql, where_clause


def _app_with_identity() -> TestClient:
    app = create_app(enable_database_bootstrap=False)

    async def identity() -> dict[str, Any]:
        return {"id": 1, "email": "qa@example.com", "role": "admin", "is_active": True}

    app.dependency_overrides[current_user] = identity
    app.dependency_overrides[admin_user] = identity
    return TestClient(app)


@pytest.mark.asyncio
async def test_seasonality_regression_interpolates_filter_clause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prevent the Phase 7 literal `{where}` SQL regression from returning."""
    captured: dict[str, Any] = {}

    async def fake_fetch(query: str, *values: object) -> list[dict[str, Any]]:
        captured.update(query=query, values=values)
        return []

    monkeypatch.setattr(analytics, "fetch_all", fake_fetch)
    result = await analytics.seasonality(
        SharedFilters(date_from=date(2018, 1, 1)), {"id": 1}
    )
    assert result.data == []
    assert "{where}" not in captured["query"]
    assert "WHERE date >= $1" in captured["query"]
    assert captured["values"] == (date(2018, 1, 1),)


def test_every_protected_operation_rejects_anonymous_access() -> None:
    client = TestClient(create_app(enable_database_bootstrap=False))
    schema = client.get("/api/v1/openapi.json").json()
    public = {
        ("/health", "get"),
        ("/api/v1/auth/login", "post"),
        ("/api/v1/auth/refresh", "post"),
    }
    replacements = {
        "{customer_id}": "customer-phase8",
    }
    checked: list[str] = []
    for path, operations in schema["paths"].items():
        request_path = path
        for marker, value in replacements.items():
            request_path = request_path.replace(marker, value)
        for method in operations:
            if method not in {"get", "post", "put"} or (path, method) in public:
                continue
            body: dict[str, Any] | None = None
            if path == "/api/v1/classification/predict":
                body = {
                    "entity_id": "audit",
                    "sales": 46837.74,
                    "discount_pct": 14.0,
                    "category": "Sessional Fruits & Vegetables",
                    "sub_category": "Carrots",
                    "segment": "Corporate",
                    "city_type": "Tier 2",
                    "state": "Tamil Nadu",
                    "region": "South",
                    "order_month": 7,
                    "order_dow": 7,
                }
            elif path == "/api/v1/admin/settings":
                body = {"settings": {}}
            response = client.request(method.upper(), request_path, json=body)
            assert response.status_code == 401, (
                f"{method.upper()} {path}: {response.text}"
            )
            assert response.json()["code"] == "not_authenticated"
            checked.append(f"{method.upper()} {path}")
    assert len(checked) == 27


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("post", "/api/v1/auth/login", {"email": "bad", "password": "x"}),
        ("post", "/api/v1/classification/predict", {"entity_id": "x"}),
        ("put", "/api/v1/admin/settings", []),
        ("get", "/api/v1/customers/profiles?page=0", None),
        (
            "get",
            "/api/v1/dashboard/revenue-trend?date_from=2023-01-02&date_to=2023-01-01",
            None,
        ),
    ],
)
def test_post_put_and_query_validation_errors(
    method: str, path: str, body: object
) -> None:
    client = _app_with_identity()
    response = client.request(method.upper(), path, json=body)
    assert response.status_code == 422


def test_parameterized_filter_and_pagination_sql() -> None:
    where, values = where_clause(
        SharedFilters(date_from=date(2019, 1, 1), state="Maharashtra"),
        ("date_from", "state"),
        aliases={"date_from": "date"},
    )
    assert where == " WHERE date >= $1 AND state = $2"
    assert values == [date(2019, 1, 1), "Maharashtra"]
    assert pagination_sql(3, 20, values) == " LIMIT $3 OFFSET $4"
    assert values[-2:] == [20, 40]


def test_preprocessor_encodes_scales_and_handles_missing_values() -> None:
    frame = pd.DataFrame(
        {
            "sales": [10.0, None],
            "discount_pct": [5.0, 20.0],
            "order_month": [1, 2],
            "order_dow": [1, 2],
            "category": ["Electronics", float("nan")],
            "sub_category": ["Phones", "Storage"],
            "segment": ["Consumer", "Corporate"],
            "city_type": ["Tier 1", "Tier 2"],
            "state": ["Maharashtra", "Delhi"],
            "region": ["West", "North"],
        }
    )
    transformed = build_preprocessor().fit_transform(frame)
    assert transformed.shape[0] == 2
    assert not pd.isna(transformed).any()

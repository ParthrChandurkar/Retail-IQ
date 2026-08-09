"""Phase 5 contract tests that do not require a live database."""

import pytest
from fastapi.testclient import TestClient

from app.core.errors import APIError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.main import create_app
from app.schemas.filters import SharedFilters
from app.services.mart_routing import revenue_trend_mart


def test_security_primitives_and_required_claims(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-only-secret")
    from app.core.config import get_settings

    get_settings.cache_clear()
    password_hash = hash_password("valid-password")
    assert verify_password("valid-password", password_hash)
    assert not verify_password("wrong-password", password_hash)
    token = create_access_token(user_id=7, email="admin@example.com", role="admin")
    claims = decode_access_token(token)
    assert {"sub", "email", "role", "iat", "exp"} <= claims.keys()
    refresh = create_refresh_token()
    assert refresh != create_refresh_token()
    assert hash_refresh_token(refresh) != refresh
    get_settings.cache_clear()


@pytest.mark.parametrize(
    ("filters", "table"),
    [
        (SharedFilters(), "marts.revenue_daily"),
        (SharedFilters(category="health_beauty"), "marts.revenue_by_category"),
        (SharedFilters(state="SP"), "marts.revenue_by_region"),
        (SharedFilters(seller_id="seller"), "marts.seller_performance"),
    ],
)
def test_revenue_trend_routing(filters: SharedFilters, table: str) -> None:
    assert revenue_trend_mart(filters)[0] == table


def test_revenue_trend_rejects_cross_family_and_payment() -> None:
    with pytest.raises(APIError):
        revenue_trend_mart(SharedFilters(state="SP", category="health_beauty"))
    with pytest.raises(APIError):
        revenue_trend_mart(SharedFilters(payment_type="credit_card"))


def test_openapi_contains_complete_phase5_contract() -> None:
    client = TestClient(create_app(enable_database_bootstrap=False))
    schema = client.get("/api/v1/openapi.json").json()
    required = {
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/me",
        "/api/v1/dashboard/summary",
        "/api/v1/dashboard/revenue-trend",
        "/api/v1/dashboard/top-products",
        "/api/v1/dashboard/top-categories",
        "/api/v1/dashboard/top-sellers",
        "/api/v1/customers/segments",
        "/api/v1/customers/rfm",
        "/api/v1/customers/{customer_unique_id}",
        "/api/v1/customers/clv-distribution",
        "/api/v1/customers/repeat-purchase-rate",
        "/api/v1/products/performance",
        "/api/v1/products/categories",
        "/api/v1/products/{product_id}",
        "/api/v1/sellers/performance",
        "/api/v1/sellers/{seller_id}",
        "/api/v1/regions/sales",
        "/api/v1/regions/geo",
        "/api/v1/regions/delivery-performance",
        "/api/v1/payments/method-mix",
        "/api/v1/payments/installments-distribution",
        "/api/v1/reviews/score-distribution",
        "/api/v1/reviews/trends",
        "/api/v1/analytics/correlation-matrix",
        "/api/v1/analytics/hypothesis-tests",
        "/api/v1/analytics/descriptive-stats",
        "/api/v1/analytics/seasonality",
        "/api/v1/classification/model-info",
        "/api/v1/classification/metrics",
        "/api/v1/classification/feature-importance",
        "/api/v1/classification/predict",
        "/api/v1/recommendations",
        "/api/v1/admin/settings",
        "/api/v1/admin/data-refresh-status",
    }
    assert required <= schema["paths"].keys()
    assert "HTTPBearer" in schema["components"]["securitySchemes"]


def test_protected_endpoint_requires_bearer_token() -> None:
    client = TestClient(create_app(enable_database_bootstrap=False))
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 401
    assert response.json()["code"] == "not_authenticated"
    assert "generated_at" in response.json()

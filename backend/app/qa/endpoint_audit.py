"""Exercise the complete migrated M7 API contract against a running API."""

import asyncio
import os
import time
from typing import Any

import httpx

from app.etl.database import connect


async def sample_customer_id() -> str:
    connection = await connect()
    try:
        value = await connection.fetchval(
            "SELECT customer_id FROM marts.customer_profile LIMIT 1"
        )
        if value is None:
            raise RuntimeError("The live audit requires populated migrated marts.")
        return str(value)
    finally:
        await connection.close()


def prediction_payload() -> dict[str, Any]:
    """The exact high-profit example fixed in the M6 report."""
    return {
        "entity_id": "m6-high-example",
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


async def run() -> None:
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    if not email or not password:
        raise RuntimeError("ADMIN_EMAIL and ADMIN_PASSWORD are required for the audit.")
    customer_id = await sample_customer_id()
    base_url = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
    results: list[tuple[str, int, float]] = []

    async with httpx.AsyncClient(base_url=base_url, timeout=180) as client:

        async def call(
            name: str,
            method: str,
            path: str,
            *,
            expected: int = 200,
            **kwargs: Any,
        ) -> httpx.Response:
            started = time.perf_counter()
            response = await client.request(method, path, **kwargs)
            elapsed_ms = (time.perf_counter() - started) * 1000
            results.append((name, response.status_code, elapsed_ms))
            if response.status_code != expected:
                raise RuntimeError(
                    f"{name} returned {response.status_code}, expected {expected}: "
                    f"{response.text[:500]}"
                )
            return response

        await call("health", "GET", "/health")
        login = await call(
            "auth.login",
            "POST",
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        client.headers["Authorization"] = (
            f"Bearer {login.json()['data']['access_token']}"
        )
        await call("auth.me", "GET", "/api/v1/auth/me")

        endpoints = [
            ("dashboard.summary", "/api/v1/dashboard/summary"),
            ("dashboard.revenue-trend", "/api/v1/dashboard/revenue-trend"),
            (
                "dashboard.revenue-trend.category",
                "/api/v1/dashboard/revenue-trend?category=Electronics",
            ),
            (
                "dashboard.revenue-trend.city-type",
                "/api/v1/dashboard/revenue-trend?city_type=Tier%201",
            ),
            ("dashboard.top-categories", "/api/v1/dashboard/top-categories?limit=5"),
            ("customers.segments", "/api/v1/customers/segments"),
            ("customers.profiles", "/api/v1/customers/profiles?page=1&page_size=5"),
            (
                "customers.order-value-distribution",
                "/api/v1/customers/order-value-distribution",
            ),
            ("customers.detail", f"/api/v1/customers/{customer_id}"),
            ("products.performance", "/api/v1/products/performance"),
            ("products.categories", "/api/v1/products/categories"),
            ("products.discount-profit", "/api/v1/products/discount-profit"),
            ("regions.sales", "/api/v1/regions/sales?city_type=Tier%201"),
            ("regions.choropleth", "/api/v1/regions/choropleth"),
            (
                "regions.shipping-performance",
                "/api/v1/regions/shipping-performance?date_from=2023-01-01",
            ),
            ("analytics.correlation-matrix", "/api/v1/analytics/correlation-matrix"),
            ("analytics.hypothesis-tests", "/api/v1/analytics/hypothesis-tests"),
            ("analytics.broad-screen", "/api/v1/analytics/broad-screen"),
            ("analytics.descriptive-stats", "/api/v1/analytics/descriptive-stats"),
            ("analytics.seasonality", "/api/v1/analytics/seasonality"),
            ("classification.model-info", "/api/v1/classification/model-info"),
            ("classification.metrics", "/api/v1/classification/metrics"),
            (
                "classification.feature-importance",
                "/api/v1/classification/feature-importance",
            ),
            ("recommendations", "/api/v1/recommendations"),
            ("admin.settings.get", "/api/v1/admin/settings"),
            ("admin.data-refresh-status", "/api/v1/admin/data-refresh-status"),
        ]
        for name, path in endpoints:
            await call(name, "GET", path)

        prediction = await call(
            "classification.predict.m6-example",
            "POST",
            "/api/v1/classification/predict",
            json=prediction_payload(),
        )
        predicted = prediction.json()["data"]
        if predicted["model_id"] != 4:
            raise RuntimeError(
                f"Expected active model_id=4, got {predicted['model_id']}"
            )
        if predicted["predicted_label"] != "high_profit_order":
            raise RuntimeError(f"M6 example label drifted: {predicted}")
        expected_probability = 0.8327976187991819
        if abs(predicted["predicted_probability"] - expected_probability) > 1e-12:
            raise RuntimeError(f"M6 example probability drifted: {predicted}")

        settings = (await client.get("/api/v1/admin/settings")).json()["data"]
        await call(
            "admin.settings.put",
            "PUT",
            "/api/v1/admin/settings",
            json=settings,
        )

        retired_paths = {
            "sellers": "/api/v1/sellers/performance",
            "payments": "/api/v1/payments/method-mix",
            "reviews": "/api/v1/reviews/score-distribution",
        }
        for retired, path in retired_paths.items():
            await call(
                f"retired.{retired}.404",
                "GET",
                path,
                expected=404,
            )

    print(f"ENDPOINTS_VERIFIED={len(results)}")
    for name, status, elapsed_ms in results:
        print(f"ENDPOINT {name} status={status} elapsed_ms={elapsed_ms:.2f}")
    print(
        "M6_PREDICTION model_id=4 label=high_profit_order confidence=0.8327976187991819"
    )


if __name__ == "__main__":
    asyncio.run(run())

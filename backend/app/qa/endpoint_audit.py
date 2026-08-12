"""Exercise every SRS Section 9 operation against a running API."""

import asyncio
import os
import statistics
import time
from typing import Any

import httpx

from app.etl.database import connect


async def sample_identifiers() -> dict[str, str]:
    connection = await connect()
    try:
        row = await connection.fetchrow(
            """SELECT
                 (SELECT customer_unique_id FROM marts.customer_profile
                    LIMIT 1) customer_id,
                 (SELECT product_id FROM curated.products LIMIT 1) product_id,
                 (SELECT seller_id FROM curated.sellers LIMIT 1) seller_id"""
        )
        if row is None or any(value is None for value in row.values()):
            raise RuntimeError(
                "The live audit requires populated curated data and marts."
            )
        return {key: str(value) for key, value in dict(row).items()}
    finally:
        await connection.close()


def prediction_payload() -> dict[str, Any]:
    return {
        "entity_id": "phase8-audit-order",
        "total_price": 100,
        "total_freight": 10,
        "item_count": 1,
        "product_count": 1,
        "seller_count": 1,
        "average_item_price": 100,
        "maximum_item_price": 100,
        "customer_state": "SP",
        "seller_state": "SP",
        "dominant_category": "health_beauty",
        "primary_payment_type": "credit_card",
        "purchase_month": 8,
        "purchase_weekday": 3,
        "purchase_hour": 14,
    }


async def run() -> None:
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    if not email or not password:
        raise RuntimeError("ADMIN_EMAIL and ADMIN_PASSWORD are required for the audit.")
    identifiers = await sample_identifiers()
    base_url = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
    timings: dict[str, list[float]] = {}
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
        login_data = login.json()["data"]
        client.headers["Authorization"] = f"Bearer {login_data['access_token']}"
        refresh_token = login.cookies.get("refresh_token")
        refresh = await call(
            "auth.refresh",
            "POST",
            "/api/v1/auth/refresh",
            headers={"Cookie": f"refresh_token={refresh_token}"},
        )
        client.headers["Authorization"] = (
            f"Bearer {refresh.json()['data']['access_token']}"
        )
        await call("auth.me", "GET", "/api/v1/auth/me")

        endpoints = [
            ("dashboard.summary", "GET", "/api/v1/dashboard/summary"),
            ("dashboard.revenue-trend", "GET", "/api/v1/dashboard/revenue-trend"),
            (
                "dashboard.top-categories",
                "GET",
                "/api/v1/dashboard/top-categories?limit=5",
            ),
            ("dashboard.top-sellers", "GET", "/api/v1/dashboard/top-sellers?limit=5"),
            ("dashboard.top-products", "GET", "/api/v1/dashboard/top-products?limit=5"),
            ("customers.segments", "GET", "/api/v1/customers/segments"),
            ("customers.rfm", "GET", "/api/v1/customers/rfm?page=1&page_size=5"),
            ("customers.clv-distribution", "GET", "/api/v1/customers/clv-distribution"),
            (
                "customers.repeat-purchase-rate",
                "GET",
                "/api/v1/customers/repeat-purchase-rate",
            ),
            (
                "customers.detail",
                "GET",
                f"/api/v1/customers/{identifiers['customer_id']}",
            ),
            ("products.performance", "GET", "/api/v1/products/performance"),
            ("products.categories", "GET", "/api/v1/products/categories"),
            ("products.detail", "GET", f"/api/v1/products/{identifiers['product_id']}"),
            ("sellers.performance", "GET", "/api/v1/sellers/performance"),
            ("sellers.detail", "GET", f"/api/v1/sellers/{identifiers['seller_id']}"),
            ("regions.sales", "GET", "/api/v1/regions/sales"),
            ("regions.geo", "GET", "/api/v1/regions/geo"),
            (
                "regions.delivery-performance",
                "GET",
                "/api/v1/regions/delivery-performance",
            ),
            ("payments.method-mix", "GET", "/api/v1/payments/method-mix"),
            (
                "payments.installments-distribution",
                "GET",
                "/api/v1/payments/installments-distribution",
            ),
            ("reviews.score-distribution", "GET", "/api/v1/reviews/score-distribution"),
            ("reviews.trends", "GET", "/api/v1/reviews/trends"),
            ("reviews.nlp-summary", "GET", "/api/v1/reviews/nlp-summary"),
            (
                "analytics.correlation-matrix",
                "GET",
                "/api/v1/analytics/correlation-matrix",
            ),
            ("analytics.hypothesis-tests", "GET", "/api/v1/analytics/hypothesis-tests"),
            (
                "analytics.descriptive-stats",
                "GET",
                "/api/v1/analytics/descriptive-stats",
            ),
            ("analytics.seasonality", "GET", "/api/v1/analytics/seasonality"),
            ("classification.model-info", "GET", "/api/v1/classification/model-info"),
            ("classification.metrics", "GET", "/api/v1/classification/metrics"),
            (
                "classification.feature-importance",
                "GET",
                "/api/v1/classification/feature-importance",
            ),
            ("recommendations", "GET", "/api/v1/recommendations"),
            ("admin.settings.get", "GET", "/api/v1/admin/settings"),
            ("admin.data-refresh-status", "GET", "/api/v1/admin/data-refresh-status"),
        ]
        for name, method, path in endpoints:
            await call(name, method, path)
        await call(
            "classification.predict",
            "POST",
            "/api/v1/classification/predict",
            json=prediction_payload(),
        )
        settings = (await client.get("/api/v1/admin/settings")).json()["data"]
        await call(
            "admin.settings.put",
            "PUT",
            "/api/v1/admin/settings",
            json=settings,
        )

        performance_paths = {
            "dashboard.summary": "/api/v1/dashboard/summary",
            "dashboard.revenue-trend": "/api/v1/dashboard/revenue-trend",
            "dashboard.top-categories": "/api/v1/dashboard/top-categories?limit=10",
            "dashboard.top-sellers": "/api/v1/dashboard/top-sellers?limit=10",
            "customers.segments": "/api/v1/customers/segments",
            "customers.rfm": "/api/v1/customers/rfm?page=1&page_size=50",
            "customers.clv-distribution": "/api/v1/customers/clv-distribution",
            "customers.repeat-purchase-rate": "/api/v1/customers/repeat-purchase-rate",
            "products.performance": "/api/v1/products/performance",
            "sellers.performance": "/api/v1/sellers/performance",
            "regions.sales": "/api/v1/regions/sales",
            "regions.geo": "/api/v1/regions/geo",
            "regions.delivery-performance": "/api/v1/regions/delivery-performance",
            "payments.method-mix": "/api/v1/payments/method-mix",
            "reviews.score-distribution": "/api/v1/reviews/score-distribution",
            "reviews.trends": "/api/v1/reviews/trends",
            "analytics.seasonality": "/api/v1/analytics/seasonality",
        }
        for name, path in performance_paths.items():
            await client.get(path)
            samples: list[float] = []
            for _ in range(20):
                started = time.perf_counter()
                response = await client.get(path)
                response.raise_for_status()
                samples.append((time.perf_counter() - started) * 1000)
            timings[name] = samples

    print(f"ENDPOINTS_VERIFIED={len(results)}")
    for name, status, elapsed_ms in results:
        print(f"ENDPOINT {name} status={status} elapsed_ms={elapsed_ms:.2f}")
    for name, samples in timings.items():
        p95 = statistics.quantiles(samples, n=20, method="inclusive")[18]
        print(f"PERFORMANCE {name} p95_ms={p95:.2f} max_ms={max(samples):.2f}")


if __name__ == "__main__":
    asyncio.run(run())

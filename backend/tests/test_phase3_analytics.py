"""Statistical correctness and mart-contract tests for Phase 3."""

import inspect

import numpy as np
import pandas as pd
import pytest

from app.etl.clean import _load_orders
from app.models.base import Base
from app.models.marts import (
    PaymentMethodMix,
    RevenueByCategory,
    RevenueByRegion,
    RevenueDaily,
    SellerPerformance,
)
from app.services.eda_service import summarize_series
from app.services.metrics import ELIGIBLE_ORDER_TOTALS_CTE
from app.services.stats_service import (
    compute_anova,
    compute_chi_square,
    compute_welch_ttest,
    t_test_review_late,
)


def test_summary_statistics_are_computed_from_values() -> None:
    result = summarize_series(pd.Series([1, 2, 2, 3, 4], dtype=float))

    assert result["count"] == 5
    assert result["mean"] == pytest.approx(2.4)
    assert result["median"] == pytest.approx(2.0)
    assert result["mode"] == pytest.approx(2.0)
    assert result["variance"] == pytest.approx(1.3)


def test_statistical_helpers_match_known_examples() -> None:
    chi_stat, chi_p, chi_dof = compute_chi_square(
        pd.DataFrame([[10, 20, 30], [20, 20, 20]])
    )
    assert chi_stat == pytest.approx(5.3333333333)
    assert chi_p == pytest.approx(0.0694834512)
    assert chi_dof == 2

    f_stat, anova_p = compute_anova(
        [
            np.array([1.0, 2.0, 3.0]),
            np.array([4.0, 5.0, 6.0]),
            np.array([7.0, 8.0, 9.0]),
        ]
    )
    assert f_stat == pytest.approx(27.0)
    assert anova_p == pytest.approx(0.001)

    t_stat, t_p = compute_welch_ttest(
        pd.Series([1.0, 2.0, 3.0]), pd.Series([4.0, 5.0, 6.0])
    )
    assert t_stat == pytest.approx(-3.674234614)
    assert t_p == pytest.approx(0.0213116411)


def test_mart_contract_has_profile_not_customer_rfm() -> None:
    mart_tables = {
        table.name for table in Base.metadata.tables.values() if table.schema == "marts"
    }

    assert "customer_profile" in mart_tables
    assert "customer_segments" in mart_tables
    assert "customer_rfm" not in mart_tables
    assert len(mart_tables) == 10


def test_shared_metric_contract_is_delivered_only() -> None:
    assert "o.order_status = 'delivered'" in ELIGIBLE_ORDER_TOTALS_CTE
    assert "SUM(oi.price + oi.freight_value)" in ELIGIBLE_ORDER_TOTALS_CTE


def test_refactored_marts_have_endpoint_specific_columns_and_grains() -> None:
    expected_columns = {
        RevenueDaily: {
            "date",
            "revenue",
            "order_count",
            "customer_count",
            "item_count",
        },
        RevenueByCategory: {
            "date",
            "category",
            "revenue",
            "order_count",
            "customer_count",
            "units",
        },
        RevenueByRegion: {
            "date",
            "state",
            "city",
            "revenue",
            "order_count",
            "customer_count",
            "latitude",
            "longitude",
        },
        SellerPerformance: {
            "date",
            "seller_id",
            "revenue",
            "order_count",
            "units",
            "avg_review_score",
        },
        PaymentMethodMix: {
            "date",
            "payment_type",
            "payment_count",
            "order_count",
            "payment_value",
            "avg_installments",
        },
    }
    expected_grains = {
        RevenueDaily: {"date"},
        RevenueByCategory: {"date", "category"},
        RevenueByRegion: {"date", "state", "city"},
        SellerPerformance: {"date", "seller_id"},
        PaymentMethodMix: {"date", "payment_type"},
    }

    for model, columns in expected_columns.items():
        assert set(model.__table__.columns.keys()) == columns
        assert {column.name for column in model.__table__.primary_key} == (
            expected_grains[model]
        )


def test_late_delivery_and_ttest_use_exact_timestamp_label() -> None:
    cleaning_source = inspect.getsource(_load_orders)
    ttest_source = inspect.getsource(t_test_review_late)

    assert "source.order_delivered_customer_date" in cleaning_source
    assert "> source.order_estimated_delivery_date" in cleaning_source
    assert "SELECT o.is_late, r.review_score" in ttest_source
    assert "delivery_delay_days > 0" not in ttest_source

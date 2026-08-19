"""Statistical correctness and mart-contract tests for Phase 3."""

import inspect

import numpy as np
import pandas as pd
import pytest

from app.etl.clean import _load_orders
from app.models.base import Base
from app.models.marts import (
    CategoryDiscountProfit,
    CustomerProfile,
    CustomerSegment,
    RevenueByCategory,
    RevenueByRegion,
    RevenueDaily,
    ShippingPerformance,
)
from app.services.eda_service import (
    CATEGORICAL_FIELDS,
    NUMERIC_OUTCOMES,
    categorical_numeric_screen,
    summarize_series,
)
from app.services.metrics import ELIGIBLE_ORDER_TOTALS_CTE
from app.services.stats_service import (
    compute_anova,
    compute_chi_square,
    compute_welch_ttest,
)


def test_summary_statistics_are_computed_from_values() -> None:
    result = summarize_series(pd.Series([1, 2, 2, 3, 4], dtype=float))

    assert result["count"] == 5
    assert result["mean"] == pytest.approx(2.4)
    assert result["median"] == pytest.approx(2.0)
    assert result["mode"] == pytest.approx(2.0)
    assert result["variance"] == pytest.approx(1.3)


def test_broad_screen_covers_every_categorical_numeric_pair() -> None:
    size = 120
    frame = pd.DataFrame(
        {field: (["a", "b", "c"] * (size // 3)) for field in CATEGORICAL_FIELDS}
    )
    frame["country"] = "India"
    for offset, field in enumerate(NUMERIC_OUTCOMES):
        frame[field] = np.arange(size, dtype=float) + offset

    result = categorical_numeric_screen(frame)
    observed = {
        (row["categorical_field"], row["numeric_outcome"]) for row in result["rows"]
    }

    assert len(result["rows"]) == len(CATEGORICAL_FIELDS) * len(NUMERIC_OUTCOMES)
    assert observed == {
        (categorical, numeric)
        for categorical in CATEGORICAL_FIELDS
        for numeric in NUMERIC_OUTCOMES
    }
    country = next(
        row for row in result["field_summary"] if row["categorical_field"] == "country"
    )
    assert country["classification"] == "constant_metadata"


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
    assert len(mart_tables) == 8
    assert "seller_performance" not in mart_tables
    assert "payment_method_mix" not in mart_tables
    assert "review_summary" not in mart_tables


def test_shared_metric_contract_uses_all_indian_store_orders() -> None:
    assert "order_status" not in ELIGIBLE_ORDER_TOTALS_CTE
    assert "o.sales::numeric AS revenue" in ELIGIBLE_ORDER_TOTALS_CTE
    assert "o.profit::numeric AS profit" in ELIGIBLE_ORDER_TOTALS_CTE
    assert "state_region_reference" in ELIGIBLE_ORDER_TOTALS_CTE


def test_refactored_marts_have_endpoint_specific_columns_and_grains() -> None:
    expected_columns = {
        RevenueDaily: {
            "date",
            "revenue",
            "total_profit",
            "total_discount_value",
            "order_count",
            "customer_count",
            "units",
            "avg_discount_pct",
            "profit_margin_pct",
        },
        RevenueByCategory: {
            "date",
            "category",
            "sub_category",
            "revenue",
            "total_profit",
            "total_discount_value",
            "order_count",
            "customer_count",
            "units",
            "avg_discount_pct",
            "profit_margin_pct",
        },
        RevenueByRegion: {
            "date",
            "state",
            "region",
            "city_type",
            "revenue",
            "total_profit",
            "total_discount_value",
            "order_count",
            "customer_count",
            "units",
            "avg_discount_pct",
            "profit_margin_pct",
            "latitude",
            "longitude",
        },
        ShippingPerformance: {
            "date",
            "ship_mode",
            "region",
            "order_count",
            "avg_shipping_days",
            "median_shipping_days",
            "min_shipping_days",
            "max_shipping_days",
        },
        CustomerProfile: {
            "customer_id",
            "order_date",
            "recency_days",
            "order_value",
            "profit",
            "discount_pct",
            "segment",
            "city_type",
            "region",
            "state",
            "order_value_tier",
        },
        CustomerSegment: {
            "segment",
            "order_value_tier",
            "city_type",
            "customer_count",
            "avg_order_value",
            "avg_profit",
            "avg_discount_pct",
        },
        CategoryDiscountProfit: {
            "category",
            "sub_category",
            "discount_band",
            "order_count",
            "revenue",
            "total_profit",
            "avg_discount_pct",
            "avg_profit_margin_pct",
        },
    }
    expected_grains = {
        RevenueDaily: {"date"},
        RevenueByCategory: {"date", "category", "sub_category"},
        RevenueByRegion: {"date", "state", "region", "city_type"},
        ShippingPerformance: {"date", "ship_mode", "region"},
        CustomerProfile: {"customer_id"},
        CustomerSegment: {"segment", "order_value_tier", "city_type"},
        CategoryDiscountProfit: {"category", "sub_category", "discount_band"},
    }

    for model, columns in expected_columns.items():
        assert set(model.__table__.columns.keys()) == columns
        assert {column.name for column in model.__table__.primary_key} == (
            expected_grains[model]
        )


def test_m4_shipping_duration_does_not_invent_a_delay_label() -> None:
    cleaning_source = inspect.getsource(_load_orders)

    assert "source.ship_date - source.order_date" in cleaning_source
    assert "is_delayed_shipment" not in cleaning_source
    assert "is_high_profit_order" in cleaning_source
    assert "EXTRACT(ISODOW" in cleaning_source

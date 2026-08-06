"""Statistical correctness and mart-contract tests for Phase 3."""

import numpy as np
import pandas as pd
import pytest

from app.models.base import Base
from app.services.eda_service import summarize_series
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

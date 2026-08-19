"""Unit tests for the M1 Indian Store Data contracts."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from app.etl.constants import DATASETS, SOURCE_HEADERS
from app.etl.download_data import missing_files
from app.etl.feature_contract import DISCOUNT_BANDS, discount_band_case
from app.etl.ingest import convert_value
from app.models.curated import Order, StateGeocode, StateRegionReference


def test_dataset_contract_contains_the_verified_single_file() -> None:
    assert len(DATASETS) == 1
    assert DATASETS[0].filename == "store_sales_data (2).csv"
    assert DATASETS[0].table_name == "store_transactions"
    assert len(SOURCE_HEADERS) == 25
    assert SOURCE_HEADERS[20] == "Sub-Category"


def test_manual_dataset_placement_is_detected(tmp_path: Path) -> None:
    data_dir = tmp_path
    for spec in DATASETS:
        (data_dir / spec.filename).touch()

    assert missing_files(data_dir) == []


def test_raw_value_conversion_preserves_typed_values() -> None:
    assert convert_value("", "string") is None
    assert convert_value("abc", "string") == "abc"
    assert convert_value("3", "integer") == 3
    assert convert_value("13.42", "numeric") == Decimal("13.42")
    assert convert_value("2023-12-31", "date") == date(2023, 12, 31)


def test_single_line_order_contract_has_no_order_item_model() -> None:
    assert "quantity" in Order.__table__.c
    assert "sales" in Order.__table__.c
    assert "profit" in Order.__table__.c


def test_outlier_flag_contract_is_reflected_in_models() -> None:
    assert Order.__table__.c.is_sales_outlier.nullable is False
    assert Order.__table__.c.is_profit_outlier.nullable is False


def test_m4_feature_contract_is_first_class_and_excludes_retired_features() -> None:
    columns = Order.__table__.c
    for feature in (
        "profit_margin_pct",
        "discount_band",
        "is_high_profit_order",
        "order_month",
        "order_year",
        "order_dow",
    ):
        assert feature in columns
        assert columns[feature].nullable is False
    assert "is_delayed_shipment" not in columns
    assert "is_repeat_customer" not in columns
    assert DISCOUNT_BANDS == ("low", "medium_low", "medium_high", "high")


def test_discount_band_boundaries_match_the_m3_outer_quartiles() -> None:
    expression = discount_band_case("discount", "q1", "median", "q3")

    assert "discount <= q1" in expression
    assert "discount < median" in expression
    assert "discount < q3" in expression
    assert "ELSE 'high'" in expression


def test_geographic_reference_separates_coordinates_and_regions() -> None:
    assert "region" not in StateGeocode.__table__.c
    assert "region" in StateRegionReference.__table__.c

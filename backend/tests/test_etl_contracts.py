"""Unit tests for Phase 2 dataset and schema contracts."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.etl.constants import DATASETS
from app.etl.download_data import missing_files
from app.etl.ingest import convert_value
from app.models.curated import Order, OrderItem, PaymentDetail, Review


def test_dataset_contract_contains_exactly_nine_files() -> None:
    assert len(DATASETS) == 9
    assert len({spec.filename for spec in DATASETS}) == 9
    assert len({spec.table_name for spec in DATASETS}) == 9


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
    assert convert_value("2018-01-02 03:04:05", "timestamp") == datetime(
        2018, 1, 2, 3, 4, 5
    )


def test_review_uses_approved_composite_primary_key() -> None:
    primary_key_columns = {column.name for column in Review.__table__.primary_key}
    assert primary_key_columns == {"review_id", "order_id"}


def test_outlier_flag_contract_is_reflected_in_models() -> None:
    assert Order.__table__.c.is_delivery_days_outlier.nullable is True
    assert OrderItem.__table__.c.is_price_outlier.nullable is False
    assert OrderItem.__table__.c.is_freight_value_outlier.nullable is False
    assert PaymentDetail.__table__.c.is_payment_value_outlier.nullable is False

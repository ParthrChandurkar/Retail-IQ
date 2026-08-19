"""Canonical Migration M4 feature definitions shared by all runtime layers."""

DISCOUNT_BAND_LOW = "low"
DISCOUNT_BAND_MEDIUM_LOW = "medium_low"
DISCOUNT_BAND_MEDIUM_HIGH = "medium_high"
DISCOUNT_BAND_HIGH = "high"

DISCOUNT_BANDS = (
    DISCOUNT_BAND_LOW,
    DISCOUNT_BAND_MEDIUM_LOW,
    DISCOUNT_BAND_MEDIUM_HIGH,
    DISCOUNT_BAND_HIGH,
)


def discount_band_case(
    value: str,
    first_quartile: str,
    median: str,
    third_quartile: str,
) -> str:
    """Return the single canonical quartile-based discount-band SQL expression.

    Boundary ownership intentionally matches the M3 outer-quartile comparison:
    low includes Q1 and high includes Q3.
    """
    return f"""CASE
        WHEN {value} <= {first_quartile} THEN '{DISCOUNT_BAND_LOW}'
        WHEN {value} < {median} THEN '{DISCOUNT_BAND_MEDIUM_LOW}'
        WHEN {value} < {third_quartile} THEN '{DISCOUNT_BAND_MEDIUM_HIGH}'
        ELSE '{DISCOUNT_BAND_HIGH}'
    END"""

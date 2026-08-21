"""Acquire or validate the single Indian Store Data source CSV."""

import os
from pathlib import Path

from app.core.config import get_settings
from app.etl.constants import DATASETS

KAGGLE_DATASET = "abuhumzakhan/store-data"
KAGGLE_SOURCE_FILENAME = "store_sales_data (2).csv"


def normalize_downloaded_filename(data_dir: Path) -> None:
    """Rename Kaggle's artifact-style filename to the canonical ETL name."""
    canonical = data_dir / DATASETS[0].filename
    upstream = data_dir / KAGGLE_SOURCE_FILENAME
    if not canonical.exists() and upstream.is_file():
        upstream.replace(canonical)


def missing_files(data_dir: Path) -> list[str]:
    """Return required source filenames that are not present."""
    return [
        spec.filename for spec in DATASETS if not (data_dir / spec.filename).is_file()
    ]


def download_or_validate() -> None:
    """Validate manual placement or download the public dataset via Kaggle API."""
    data_dir = get_settings().data_raw_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    missing = missing_files(data_dir)
    if not missing:
        print(f"The Indian Store Data CSV is present in {data_dir}.")
        return

    if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
        missing_list = ", ".join(missing)
        raise RuntimeError(
            "KAGGLE_USERNAME/KAGGLE_KEY are not set and manual placement is "
            f"incomplete. Missing: {missing_list}"
        )

    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(KAGGLE_DATASET, path=data_dir, unzip=True, quiet=False)
    normalize_downloaded_filename(data_dir)

    missing = missing_files(data_dir)
    if missing:
        raise RuntimeError(
            f"Kaggle download completed but files are missing: {missing}"
        )

    print(f"Downloaded and validated Indian Store Data in {data_dir}.")


if __name__ == "__main__":
    download_or_validate()

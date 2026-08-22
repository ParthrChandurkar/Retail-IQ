"""Typed serving contracts for the migrated high-profit classifier."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class GlobalFeature(BaseModel):
    feature: str
    importance: float = Field(ge=0)


class PredictionRequest(BaseModel):
    entity_id: str = Field(min_length=1, description="External order audit identifier")
    sales: float = Field(gt=0, description="Checkout sales value in INR")
    discount_pct: float = Field(ge=0, le=50)
    category: str = Field(min_length=1)
    sub_category: str = Field(min_length=1)
    segment: Literal["Consumer", "Corporate"]
    city_type: Literal["Tier 1", "Tier 2", "Village"]
    state: str = Field(min_length=1)
    region: Literal["North", "South", "East", "West"] = Field(
        description="Trusted state_region_reference-derived region"
    )
    order_month: int = Field(ge=1, le=12)
    order_dow: int = Field(ge=1, le=7)


class PredictionResult(BaseModel):
    model_id: int
    target_variable: Literal["is_high_profit_order"]
    predicted_label: Literal["high_profit_order", "standard_profit_order"]
    predicted_probability: float = Field(
        ge=0,
        le=1,
        description="Confidence in predicted_label, not a fixed-class probability",
    )
    top_global_features: list[GlobalFeature] = Field(
        description="Model-level importance shared by predictions from this model"
    )


class ModelInfo(BaseModel):
    model_id: int
    target_variable: Literal["is_high_profit_order"]
    algorithm: str
    trained_at: datetime
    positive_class: Literal["high_profit_order"]
    negative_class: Literal["standard_profit_order"]
    prediction_probability_semantics: str
    feature_columns: list[str]
    top_global_features: list[GlobalFeature]


class ModelMetrics(BaseModel):
    model_id: int
    algorithm: str
    positive_class: Literal["high_profit_order"]
    negative_class: Literal["standard_profit_order"]
    accuracy: float
    precision_high_profit_order: float
    recall_high_profit_order: float
    f1_high_profit_order: float
    roc_auc: float
    cv_f1_scores: list[float]
    cv_mean_f1_high_profit_order: float
    cv_roc_auc_scores: list[float]
    cv_mean_roc_auc: float
    confusion_matrix: dict[str, Any]

"""Typed serving contracts for the registered satisfaction classifier."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class GlobalFeature(BaseModel):
    feature: str
    importance: float = Field(ge=0)


class PredictionRequest(BaseModel):
    entity_id: str = Field(
        min_length=1, description="Order or external audit identifier"
    )
    total_price: float = Field(ge=0)
    total_freight: float = Field(ge=0)
    item_count: int = Field(ge=1)
    product_count: int = Field(ge=1)
    seller_count: int = Field(ge=1)
    average_item_price: float = Field(ge=0)
    maximum_item_price: float = Field(ge=0)
    freight_ratio: float | None = Field(default=None, ge=0)
    payment_value: float | None = Field(default=None, ge=0)
    payment_installments: float | None = Field(default=None, ge=0)
    delivery_days: float | None = None
    delivery_delay_hours: float | None = None
    is_late: int | None = Field(default=None, ge=0, le=1)
    approval_hours: float | None = None
    carrier_handling_hours: float | None = None
    estimated_delivery_days: float | None = None
    shipping_limit_slack_days: float | None = None
    seller_distance_km: float | None = Field(default=None, ge=0)
    average_product_weight_g: float | None = Field(default=None, ge=0)
    average_product_volume_cm3: float | None = Field(default=None, ge=0)
    customer_state: str
    seller_state: str
    dominant_category: str
    primary_payment_type: str
    purchase_month: int = Field(ge=1, le=12)
    purchase_weekday: int = Field(ge=1, le=7)
    purchase_hour: int = Field(ge=0, le=23)


class PredictionResult(BaseModel):
    model_id: int
    target_variable: Literal["low_satisfaction"]
    predicted_label: Literal["low_satisfaction", "high_satisfaction"]
    predicted_probability: float = Field(ge=0, le=1)
    top_global_features: list[GlobalFeature] = Field(
        description=(
            "Model-level importance; identical for every prediction from this model."
        )
    )


class ModelInfo(BaseModel):
    model_id: int
    target_variable: str
    algorithm: str
    trained_at: datetime
    positive_class: Literal["low_satisfaction"]
    negative_class: Literal["high_satisfaction"]
    prediction_probability_semantics: str
    feature_columns: list[str]
    top_global_features: list[GlobalFeature]


class ModelMetrics(BaseModel):
    model_id: int
    algorithm: str
    positive_class: Literal["low_satisfaction"]
    negative_class: Literal["high_satisfaction"]
    accuracy: float
    precision_low_satisfaction: float
    recall_low_satisfaction: float
    f1_low_satisfaction: float
    roc_auc: float
    cv_f1_scores: list[float]
    cv_mean_f1_low_satisfaction: float
    cv_roc_auc_scores: list[float]
    cv_mean_roc_auc: float
    confusion_matrix: dict[str, Any]

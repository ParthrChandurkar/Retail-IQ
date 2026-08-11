"""Machine-learning registry and serving audit models."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"
    __table_args__ = {"schema": "ml"}

    model_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_variable: Mapped[str] = mapped_column(String, nullable=False)
    algorithm: Mapped[str] = mapped_column(String, nullable=False)
    trained_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    artifact_path: Mapped[str] = mapped_column(String, nullable=False)
    metrics_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class Prediction(Base):
    __tablename__ = "predictions"
    __table_args__ = {"schema": "ml"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("ml.model_registry.model_id"))
    entity_id: Mapped[str] = mapped_column(String, nullable=False)
    predicted_label: Mapped[str] = mapped_column(String, nullable=False)
    predicted_probability: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("now()"))


class FeatureImportance(Base):
    __tablename__ = "feature_importance"
    __table_args__ = {"schema": "ml"}

    model_id: Mapped[int] = mapped_column(
        ForeignKey("ml.model_registry.model_id"), primary_key=True
    )
    feature_name: Mapped[str] = mapped_column(String, primary_key=True)
    importance: Mapped[Decimal] = mapped_column(Numeric, nullable=False)

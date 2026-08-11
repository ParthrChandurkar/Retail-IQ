"""create model registry, prediction audit, and feature importance tables

Revision ID: 20260810_0004
Revises: 20260809_0003
Create Date: 2026-08-10 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260810_0004"
down_revision: str | None = "20260809_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "model_registry",
        sa.Column("model_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("target_variable", sa.String(), nullable=False),
        sa.Column("algorithm", sa.String(), nullable=False),
        sa.Column("trained_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("artifact_path", sa.String(), nullable=False),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("model_id"),
        schema="ml",
    )
    op.create_index(
        "ix_model_registry_active", "model_registry", ["is_active"], schema="ml"
    )
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("predicted_label", sa.String(), nullable=False),
        sa.Column("predicted_probability", sa.Numeric(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["model_id"], ["ml.model_registry.model_id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="ml",
    )
    op.create_table(
        "feature_importance",
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("feature_name", sa.String(), nullable=False),
        sa.Column("importance", sa.Numeric(), nullable=False),
        sa.ForeignKeyConstraint(["model_id"], ["ml.model_registry.model_id"]),
        sa.PrimaryKeyConstraint("model_id", "feature_name"),
        schema="ml",
    )


def downgrade() -> None:
    op.drop_table("feature_importance", schema="ml")
    op.drop_table("predictions", schema="ml")
    op.drop_index("ix_model_registry_active", table_name="model_registry", schema="ml")
    op.drop_table("model_registry", schema="ml")

"""grant Power BI read-only access to marts only

Revision ID: 20260809_0003
Revises: 20260809_0002
Create Date: 2026-08-09 00:00:00.000000
"""

import os
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260809_0003"
down_revision: str | None = "20260809_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _role_sql() -> str:
    password = os.getenv("POWERBI_READER_PASSWORD", "")
    if not password:
        raise RuntimeError(
            "POWERBI_READER_PASSWORD must be set before applying the Phase 5 migration"
        )
    bind = op.get_bind()
    literal = sa.String().literal_processor(bind.dialect)
    assert literal is not None
    quoted_password = literal(password)
    return f"""DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='powerbi_reader') THEN
        CREATE ROLE powerbi_reader LOGIN PASSWORD {quoted_password}
          NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION;
      ELSE
        ALTER ROLE powerbi_reader PASSWORD {quoted_password};
      END IF;
    END $$"""


def upgrade() -> None:
    """Create a least-privilege BI login restricted to marts."""
    bind = op.get_bind()
    database_name = bind.execute(sa.text("SELECT current_database()")).scalar_one()
    database = bind.dialect.identifier_preparer.quote(database_name)
    bind.exec_driver_sql(_role_sql())
    op.execute(sa.text(f"GRANT CONNECT ON DATABASE {database} TO powerbi_reader"))
    for schema in ("raw", "curated", "ml"):
        op.execute(sa.text(f"REVOKE ALL ON SCHEMA {schema} FROM powerbi_reader"))
        op.execute(
            sa.text(f"REVOKE ALL ON ALL TABLES IN SCHEMA {schema} FROM powerbi_reader")
        )
        op.execute(
            sa.text(
                f"REVOKE ALL ON ALL SEQUENCES IN SCHEMA {schema} FROM powerbi_reader"
            )
        )
    op.execute(sa.text("REVOKE CREATE ON SCHEMA marts FROM powerbi_reader"))
    op.execute(sa.text("GRANT USAGE ON SCHEMA marts TO powerbi_reader"))
    op.execute(sa.text("GRANT SELECT ON ALL TABLES IN SCHEMA marts TO powerbi_reader"))
    op.execute(
        sa.text(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA marts GRANT SELECT ON TABLES TO powerbi_reader"
        )
    )


def downgrade() -> None:
    """Remove database-local grants while retaining the cluster-global role."""
    bind = op.get_bind()
    database_name = bind.execute(sa.text("SELECT current_database()")).scalar_one()
    database = bind.dialect.identifier_preparer.quote(database_name)
    op.execute(
        sa.text(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA marts REVOKE SELECT ON TABLES FROM powerbi_reader"
        )
    )
    op.execute(
        sa.text("REVOKE SELECT ON ALL TABLES IN SCHEMA marts FROM powerbi_reader")
    )
    op.execute(sa.text("REVOKE USAGE ON SCHEMA marts FROM powerbi_reader"))
    op.execute(sa.text(f"REVOKE CONNECT ON DATABASE {database} FROM powerbi_reader"))

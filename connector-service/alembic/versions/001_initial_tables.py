"""Create initial tables: distributor_configs, products, connector_logs

Revision ID: 001
Revises:
Create Date: 2026-06-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # distributor_configs
    op.create_table(
        "distributor_configs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("distributor_type", sa.String(50), nullable=False),
        sa.Column("credentials", sa.LargeBinary(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="not_configured"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("settings", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "distributor_type IN ('dpk', 'furacao', 'rufato', 'isapa', 'pellegrino', 'laquila', 'rolemarmaster')",
            name="ck_distributor_type",
        ),
        sa.CheckConstraint(
            "status IN ('configured', 'not_configured', 'error', 'circuit_open')",
            name="ck_distributor_status",
        ),
    )
    op.create_index("idx_distconfig_user", "distributor_configs", ["user_id"])
    op.create_index("idx_distconfig_type", "distributor_configs", ["distributor_type"])
    op.create_index("uq_user_distributor", "distributor_configs", ["user_id", "distributor_type"], unique=True)

    # products
    op.create_table(
        "products",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("distributor_config_id", UUID(as_uuid=True), sa.ForeignKey("distributor_configs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("stock_quantity", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Numeric(8, 3), nullable=True),
        sa.Column("height", sa.Numeric(8, 2), nullable=True),
        sa.Column("width", sa.Numeric(8, 2), nullable=True),
        sa.Column("length", sa.Numeric(8, 2), nullable=True),
        sa.Column("photos", JSONB(), nullable=False, server_default="[]"),
        sa.Column("fiscal_data", JSONB(), nullable=False, server_default="{}"),
        sa.Column("raw_data", JSONB(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="available"),
        sa.Column("last_stock_check_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('available', 'unavailable')", name="ck_product_status"),
    )
    op.create_index("idx_products_distconfig", "products", ["distributor_config_id"])
    op.create_index("idx_products_sku", "products", ["sku"])
    op.create_index("idx_products_status", "products", ["status"])
    op.create_index("uq_distconfig_sku", "products", ["distributor_config_id", "sku"], unique=True)
    op.execute(
        "CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops)"
    )

    # connector_logs
    op.create_table(
        "connector_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("distributor_config_id", UUID(as_uuid=True), sa.ForeignKey("distributor_configs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("products_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("products_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("products_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_details", JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('running', 'success', 'partial', 'error')",
            name="ck_log_status",
        ),
    )
    op.create_index("idx_connlogs_distconfig", "connector_logs", ["distributor_config_id"])
    op.create_index("idx_connlogs_started", "connector_logs", ["started_at"])


def downgrade() -> None:
    op.drop_table("connector_logs")
    op.drop_table("products")
    op.drop_table("distributor_configs")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")

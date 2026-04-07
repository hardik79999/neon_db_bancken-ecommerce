"""repair status and payment columns

Revision ID: f2b4c6d8e9f0
Revises: ac1c88204436
Create Date: 2026-04-07 10:20:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2b4c6d8e9f0"
down_revision = "ac1c88204436"
branch_labels = None
depends_on = None


def _column_names(table_name):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade():
    order_columns = _column_names("orders")
    if "status" not in order_columns:
        if "action" in order_columns:
            op.alter_column(
                "orders",
                "action",
                new_column_name="status",
                existing_type=sa.String(length=32),
                existing_nullable=True,
            )
        else:
            op.add_column("orders", sa.Column("status", sa.String(length=32), nullable=True))
    op.execute("UPDATE orders SET status = COALESCE(status, 'pending')")
    op.alter_column("orders", "status", existing_type=sa.String(length=32), nullable=False)

    tracking_columns = _column_names("order_trackings")
    if "status" not in tracking_columns:
        if "action" in tracking_columns:
            op.alter_column(
                "order_trackings",
                "action",
                new_column_name="status",
                existing_type=sa.String(length=32),
                existing_nullable=True,
            )
        else:
            op.add_column("order_trackings", sa.Column("status", sa.String(length=32), nullable=True))
    op.execute("UPDATE order_trackings SET status = COALESCE(status, 'pending')")
    op.alter_column("order_trackings", "status", existing_type=sa.String(length=32), nullable=False)

    payment_columns = _column_names("payments")
    if "payment_method" not in payment_columns:
        op.add_column("payments", sa.Column("payment_method", sa.String(length=32), nullable=True))
    if "status" not in payment_columns:
        op.add_column("payments", sa.Column("status", sa.String(length=32), nullable=True))

    if "action" in _column_names("payments"):
        op.execute(
            """
            UPDATE payments
            SET
                payment_method = COALESCE(
                    payment_method,
                    CASE
                        WHEN action IN ('cod', 'card', 'upi', 'netbanking') THEN action
                        ELSE NULL
                    END
                ),
                status = COALESCE(
                    status,
                    CASE
                        WHEN action IN ('pending', 'completed', 'failed', 'refunded') THEN action
                        WHEN action IN ('cod', 'card', 'upi', 'netbanking') THEN 'completed'
                        ELSE NULL
                    END
                )
            """
        )
        op.drop_column("payments", "action")

    op.execute("UPDATE payments SET payment_method = COALESCE(payment_method, 'cod')")
    op.execute("UPDATE payments SET status = COALESCE(status, 'pending')")
    op.alter_column("payments", "payment_method", existing_type=sa.String(length=32), nullable=False)
    op.alter_column("payments", "status", existing_type=sa.String(length=32), nullable=False)


def downgrade():
    payment_columns = _column_names("payments")
    if "action" not in payment_columns:
        op.add_column("payments", sa.Column("action", sa.String(length=32), nullable=True))
        if "payment_method" in payment_columns:
            op.execute("UPDATE payments SET action = payment_method WHERE action IS NULL")
        if "status" in payment_columns:
            op.execute("UPDATE payments SET action = status WHERE action IS NULL")

    if "payment_method" in _column_names("payments"):
        op.drop_column("payments", "payment_method")
    if "status" in _column_names("payments"):
        op.drop_column("payments", "status")

    tracking_columns = _column_names("order_trackings")
    if "status" in tracking_columns and "action" not in tracking_columns:
        op.alter_column(
            "order_trackings",
            "status",
            new_column_name="action",
            existing_type=sa.String(length=32),
            existing_nullable=False,
        )

    order_columns = _column_names("orders")
    if "status" in order_columns and "action" not in order_columns:
        op.alter_column(
            "orders",
            "status",
            new_column_name="action",
            existing_type=sa.String(length=32),
            existing_nullable=False,
        )

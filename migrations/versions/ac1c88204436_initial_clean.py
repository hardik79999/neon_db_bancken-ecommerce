"""initial clean

Revision ID: ac1c88204436
Revises:
Create Date: 2026-04-06 18:51:04.229513

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ac1c88204436"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "categories",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "coupons",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("discount_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("discount_flat", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "discount_flat IS NULL OR discount_flat >= 0",
            name="ck_coupons_discount_flat_non_negative",
        ),
        sa.CheckConstraint(
            "discount_percentage IS NOT NULL OR discount_flat IS NOT NULL",
            name="ck_coupons_discount_required",
        ),
        sa.CheckConstraint(
            "discount_percentage IS NULL OR (discount_percentage >= 0 AND discount_percentage <= 100)",
            name="ck_coupons_discount_percentage_range",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "roles",
        sa.Column("role_name", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_name"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "users",
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=15), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_users_created_by"), ["created_by"], unique=False)
        batch_op.create_index(batch_op.f("ix_users_email"), ["email"], unique=True)
        batch_op.create_index(batch_op.f("ix_users_phone"), ["phone"], unique=True)
        batch_op.create_index(batch_op.f("ix_users_role_id"), ["role_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_users_updated_by"), ["updated_by"], unique=False)
        batch_op.create_index(batch_op.f("ix_users_username"), ["username"], unique=True)

    op.create_table(
        "addresses",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("phone_number", sa.String(length=15), nullable=False),
        sa.Column("street", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("pincode", sa.String(length=20), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("addresses", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_addresses_phone_number"), ["phone_number"], unique=False)
        batch_op.create_index(batch_op.f("ix_addresses_user_id"), ["user_id"], unique=False)

    op.create_table(
        "otps",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("otp_code", sa.String(length=10), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("is_used", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("otps", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_otps_user_id"), ["user_id"], unique=False)

    op.create_table(
        "products",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("stock", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
        sa.CheckConstraint("stock >= 0", name="ck_products_stock_non_negative"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_products_category_id"), ["category_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_products_created_by"), ["created_by"], unique=False)
        batch_op.create_index(batch_op.f("ix_products_seller_id"), ["seller_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_products_updated_by"), ["updated_by"], unique=False)

    op.create_table(
        "seller_categories",
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("is_approved", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("seller_id", "category_id", name="uq_seller_categories_seller_category"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("seller_categories", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_seller_categories_category_id"), ["category_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_seller_categories_seller_id"), ["seller_id"], unique=False)

    op.create_table(
        "cart_items",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_cart_items_quantity_positive"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", name="uq_cart_items_user_product"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("cart_items", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_cart_items_product_id"), ["product_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_cart_items_user_id"), ["user_id"], unique=False)

    op.create_table(
        "orders",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("address_id", sa.Integer(), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("total_amount >= 0", name="ck_orders_total_amount_non_negative"),
        sa.ForeignKeyConstraint(["address_id"], ["addresses.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_orders_address_id"), ["address_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_orders_created_by"), ["created_by"], unique=False)
        batch_op.create_index(batch_op.f("ix_orders_updated_by"), ["updated_by"], unique=False)
        batch_op.create_index(batch_op.f("ix_orders_user_id"), ["user_id"], unique=False)

    op.create_table(
        "product_images",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=255), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("product_images", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_product_images_product_id"), ["product_id"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_range"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", name="uq_reviews_user_product"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("reviews", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_reviews_product_id"), ["product_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_reviews_user_id"), ["user_id"], unique=False)

    op.create_table(
        "specifications",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("spec_key", sa.String(length=100), nullable=False),
        sa.Column("spec_value", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("specifications", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_specifications_product_id"), ["product_id"], unique=False)

    op.create_table(
        "wishlists",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", name="uq_wishlists_user_product"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("wishlists", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_wishlists_product_id"), ["product_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_wishlists_user_id"), ["user_id"], unique=False)

    op.create_table(
        "invoices",
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column("pdf_url", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("invoices", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_invoices_invoice_number"), ["invoice_number"], unique=True)
        batch_op.create_index(batch_op.f("ix_invoices_order_id"), ["order_id"], unique=True)

    op.create_table(
        "order_items",
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price_at_purchase", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("price_at_purchase >= 0", name="ck_order_items_price_non_negative"),
        sa.CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("order_items", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_order_items_order_id"), ["order_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_order_items_product_id"), ["product_id"], unique=False)

    op.create_table(
        "order_trackings",
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("message", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("order_trackings", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_order_trackings_order_id"), ["order_id"], unique=False)

    op.create_table(
        "payments",
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.String(length=100), nullable=True),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("payment_method", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("amount >= 0", name="ck_payments_amount_non_negative"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_payments_order_id"), ["order_id"], unique=True)
        batch_op.create_index(batch_op.f("ix_payments_transaction_id"), ["transaction_id"], unique=True)
        batch_op.create_index(batch_op.f("ix_payments_user_id"), ["user_id"], unique=False)


def downgrade():
    op.drop_table("payments")
    op.drop_table("order_trackings")
    op.drop_table("order_items")
    op.drop_table("invoices")
    op.drop_table("wishlists")
    op.drop_table("specifications")
    op.drop_table("reviews")
    op.drop_table("product_images")
    op.drop_table("orders")
    op.drop_table("cart_items")
    op.drop_table("seller_categories")
    op.drop_table("products")
    op.drop_table("otps")
    op.drop_table("addresses")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("coupons")
    op.drop_table("categories")

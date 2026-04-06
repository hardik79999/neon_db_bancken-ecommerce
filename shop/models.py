import enum
import uuid
from datetime import datetime, timedelta

from sqlalchemy import CheckConstraint, Numeric, String, UniqueConstraint, text
from sqlalchemy.types import TypeDecorator

from shop.extensions import db


class OrderStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(str, enum.Enum):
    cod = "cod"
    card = "card"
    upi = "upi"
    netbanking = "netbanking"


class OTPAction(str, enum.Enum):
    verification = "verification"
    password_reset = "password_reset"


class EnumString(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, enum_class, length=50, *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(length=length, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        if isinstance(value, str):
            return self.enum_class(value.strip().lower()).value
        raise TypeError(f"Expected {self.enum_class.__name__} or str, got {type(value).__name__}")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_class(value)

    def copy(self, **kwargs):
        return EnumString(self.enum_class, length=getattr(self.impl, "length", 50))


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=text("true"))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )


class AuditMixin:
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    updated_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )


# Auth / User
class Role(BaseModel):
    __tablename__ = "roles"

    role_name = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship("User", back_populates="role", lazy="selectin")

    def __repr__(self):
        return f"<Role {self.role_name}>"


class User(AuditMixin, BaseModel):
    __tablename__ = "users"

    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), unique=True, index=True)
    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    is_verified = db.Column(db.Boolean, nullable=False, default=False, server_default=text("false"))

    role = db.relationship("Role", back_populates="users", lazy="joined")
    creator = db.relationship(
        "User",
        foreign_keys="User.created_by",
        remote_side="User.id",
        back_populates="created_users",
        lazy="joined",
    )
    updater = db.relationship(
        "User",
        foreign_keys="User.updated_by",
        remote_side="User.id",
        back_populates="updated_users",
        lazy="joined",
    )
    created_users = db.relationship(
        "User",
        foreign_keys="User.created_by",
        back_populates="creator",
        lazy="selectin",
    )
    updated_users = db.relationship(
        "User",
        foreign_keys="User.updated_by",
        back_populates="updater",
        lazy="selectin",
    )
    addresses = db.relationship(
        "Address",
        foreign_keys="Address.user_id",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    otps = db.relationship(
        "Otp",
        foreign_keys="Otp.user_id",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    orders = db.relationship(
        "Order",
        foreign_keys="Order.user_id",
        back_populates="customer",
        lazy="selectin",
    )
    products = db.relationship(
        "Product",
        foreign_keys="Product.seller_id",
        back_populates="seller_user",
        lazy="selectin",
    )
    seller_category_requests = db.relationship(
        "SellerCategory",
        foreign_keys="SellerCategory.seller_id",
        back_populates="seller",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    cart_items = db.relationship(
        "CartItem",
        foreign_keys="CartItem.user_id",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    wishlist_items = db.relationship(
        "Wishlist",
        foreign_keys="Wishlist.user_id",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    reviews = db.relationship(
        "Review",
        foreign_keys="Review.user_id",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    payments = db.relationship(
        "Payment",
        foreign_keys="Payment.user_id",
        back_populates="user",
        lazy="selectin",
    )
    created_products = db.relationship(
        "Product",
        foreign_keys="Product.created_by",
        back_populates="creator",
        lazy="selectin",
    )
    updated_products = db.relationship(
        "Product",
        foreign_keys="Product.updated_by",
        back_populates="updater",
        lazy="selectin",
    )
    created_orders = db.relationship(
        "Order",
        foreign_keys="Order.created_by",
        back_populates="creator",
        lazy="selectin",
    )
    updated_orders = db.relationship(
        "Order",
        foreign_keys="Order.updated_by",
        back_populates="updater",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Otp(BaseModel):
    __tablename__ = "otps"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    otp_code = db.Column(db.String(10), nullable=False)
    action = db.Column(EnumString(OTPAction, length=32), nullable=False, default=OTPAction.verification)
    is_used = db.Column(db.Boolean, nullable=False, default=False, server_default=text("false"))
    expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(minutes=10),
    )

    user = db.relationship("User", back_populates="otps", lazy="joined")

    def __repr__(self):
        return f"<Otp user_id={self.user_id} action={self.action.value}>"


class Address(BaseModel):
    __tablename__ = "addresses"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False, index=True)
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    is_default = db.Column(db.Boolean, nullable=False, default=False, server_default=text("false"))

    user = db.relationship("User", back_populates="addresses", lazy="joined")
    orders = db.relationship(
        "Order",
        foreign_keys="Order.address_id",
        back_populates="shipping_address",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Address {self.full_name} {self.city}>"


# Product / Catalog
class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    products = db.relationship("Product", back_populates="category", lazy="selectin")
    seller_requests = db.relationship(
        "SellerCategory",
        back_populates="category",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Category {self.name}>"


class SellerCategory(BaseModel):
    __tablename__ = "seller_categories"
    __table_args__ = (
        UniqueConstraint("seller_id", "category_id", name="uq_seller_categories_seller_category"),
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_approved = db.Column(db.Boolean, nullable=False, default=False, server_default=text("false"))

    seller = db.relationship("User", back_populates="seller_category_requests", lazy="joined")
    category = db.relationship("Category", back_populates="seller_requests", lazy="joined")

    def __repr__(self):
        return f"<SellerCategory seller_id={self.seller_id} category_id={self.category_id}>"


class Product(AuditMixin, BaseModel):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
        CheckConstraint("stock >= 0", name="ck_products_stock_non_negative"),
    )

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0, server_default=text("0"))
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    category = db.relationship("Category", back_populates="products", lazy="joined")
    seller_user = db.relationship(
        "User",
        foreign_keys=[seller_id],
        back_populates="products",
        lazy="joined",
    )
    creator = db.relationship(
        "User",
        foreign_keys="Product.created_by",
        back_populates="created_products",
        lazy="joined",
    )
    updater = db.relationship(
        "User",
        foreign_keys="Product.updated_by",
        back_populates="updated_products",
        lazy="joined",
    )
    images = db.relationship(
        "ProductImage",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    specifications = db.relationship(
        "Specification",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    reviews = db.relationship(
        "Review",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    cart_items = db.relationship(
        "CartItem",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    wishlist_items = db.relationship(
        "Wishlist",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    order_items = db.relationship("OrderItem", back_populates="product", lazy="selectin")

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductImage(BaseModel):
    __tablename__ = "product_images"

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, nullable=False, default=False, server_default=text("false"))

    product = db.relationship("Product", back_populates="images", lazy="joined")

    def __repr__(self):
        return f"<ProductImage product_id={self.product_id} primary={self.is_primary}>"


class Specification(BaseModel):
    __tablename__ = "specifications"

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    spec_key = db.Column(db.String(100), nullable=False)
    spec_value = db.Column(db.String(255), nullable=False)

    product = db.relationship("Product", back_populates="specifications", lazy="joined")

    def __repr__(self):
        return f"<Specification {self.spec_key}={self.spec_value}>"


# Orders / Payments
class Coupon(BaseModel):
    __tablename__ = "coupons"
    __table_args__ = (
        CheckConstraint(
            "discount_percentage IS NULL OR (discount_percentage >= 0 AND discount_percentage <= 100)",
            name="ck_coupons_discount_percentage_range",
        ),
        CheckConstraint(
            "discount_flat IS NULL OR discount_flat >= 0",
            name="ck_coupons_discount_flat_non_negative",
        ),
        CheckConstraint(
            "discount_percentage IS NOT NULL OR discount_flat IS NOT NULL",
            name="ck_coupons_discount_required",
        ),
    )

    code = db.Column(db.String(50), nullable=False, unique=True)
    discount_percentage = db.Column(Numeric(5, 2))
    discount_flat = db.Column(Numeric(10, 2))
    expiry_date = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<Coupon {self.code}>"


class CartItem(BaseModel):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_items_user_product"),
        CheckConstraint("quantity > 0", name="ck_cart_items_quantity_positive"),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity = db.Column(db.Integer, nullable=False, default=1, server_default=text("1"))

    user = db.relationship("User", back_populates="cart_items", lazy="joined")
    product = db.relationship("Product", back_populates="cart_items", lazy="joined")

    def __repr__(self):
        return f"<CartItem user_id={self.user_id} product_id={self.product_id} quantity={self.quantity}>"


class Order(AuditMixin, BaseModel):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_orders_total_amount_non_negative"),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    address_id = db.Column(
        db.Integer,
        db.ForeignKey("addresses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(EnumString(OrderStatus, length=32), nullable=False, default=OrderStatus.pending)

    customer = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="orders",
        lazy="joined",
    )
    shipping_address = db.relationship(
        "Address",
        foreign_keys=[address_id],
        back_populates="orders",
        lazy="joined",
    )
    creator = db.relationship(
        "User",
        foreign_keys="Order.created_by",
        back_populates="created_orders",
        lazy="joined",
    )
    updater = db.relationship(
        "User",
        foreign_keys="Order.updated_by",
        back_populates="updated_orders",
        lazy="joined",
    )
    items = db.relationship(
        "OrderItem",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    tracking = db.relationship(
        "OrderTracking",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="OrderTracking.created_at",
    )
    payment = db.relationship(
        "Payment",
        back_populates="order",
        uselist=False,
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    invoice = db.relationship(
        "Invoice",
        back_populates="order",
        uselist=False,
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Order {self.uuid} status={self.status.value}>"


class OrderItem(BaseModel):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("price_at_purchase >= 0", name="ck_order_items_price_non_negative"),
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(Numeric(10, 2), nullable=False)

    order = db.relationship("Order", back_populates="items", lazy="joined")
    product = db.relationship("Product", back_populates="order_items", lazy="joined")

    def __repr__(self):
        return f"<OrderItem order_id={self.order_id} product_id={self.product_id}>"


class Payment(BaseModel):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payments_amount_non_negative"),
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    transaction_id = db.Column(db.String(100), unique=True, index=True)
    payment_method = db.Column(EnumString(PaymentMethod, length=32), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(EnumString(PaymentStatus, length=32), nullable=False, default=PaymentStatus.pending)

    order = db.relationship("Order", back_populates="payment", lazy="joined")
    user = db.relationship("User", back_populates="payments", lazy="joined")

    def __repr__(self):
        return f"<Payment order_id={self.order_id} status={self.status.value}>"


class Invoice(BaseModel):
    __tablename__ = "invoices"

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    invoice_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    pdf_url = db.Column(db.String(255))

    order = db.relationship("Order", back_populates="invoice", lazy="joined")

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"


class OrderTracking(BaseModel):
    __tablename__ = "order_trackings"

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = db.Column(EnumString(OrderStatus, length=32), nullable=False)
    message = db.Column(db.String(255))

    order = db.relationship("Order", back_populates="tracking", lazy="joined")

    def __repr__(self):
        return f"<OrderTracking order_id={self.order_id} status={self.status.value}>"


class Wishlist(BaseModel):
    __tablename__ = "wishlists"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_wishlists_user_product"),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user = db.relationship("User", back_populates="wishlist_items", lazy="joined")
    product = db.relationship("Product", back_populates="wishlist_items", lazy="joined")

    def __repr__(self):
        return f"<Wishlist user_id={self.user_id} product_id={self.product_id}>"


class Review(BaseModel):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_range"),
        UniqueConstraint("user_id", "product_id", name="uq_reviews_user_product"),
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    product = db.relationship("Product", back_populates="reviews", lazy="joined")
    user = db.relationship("User", back_populates="reviews", lazy="joined")

    def __repr__(self):
        return f"<Review product_id={self.product_id} rating={self.rating}>"

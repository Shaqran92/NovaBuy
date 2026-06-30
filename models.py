from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

db = SQLAlchemy()

# Order cancellation window in minutes
CANCEL_WINDOW_MINUTES = 10


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Profile fields
    full_name = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    avatar_color = db.Column(db.String(7), default='#7c3aed')

    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def initials(self):
        if self.full_name:
            parts = self.full_name.split()
            return ''.join(p[0].upper() for p in parts[:2])
        return self.username[0].upper()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, default=4.0)
    stock = db.Column(db.Integer, default=10)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product', backref='cart_items')

    def __repr__(self):
        return f'<CartItem {self.product_id} x{self.quantity}>'

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Processing')
    full_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id}>'

    @property
    def can_cancel(self):
        """Order can be cancelled within CANCEL_WINDOW_MINUTES minutes of placement."""
        if self.status == 'Cancelled':
            return False
        deadline = self.created_at + timedelta(minutes=CANCEL_WINDOW_MINUTES)
        return datetime.utcnow() < deadline

    @property
    def cancel_deadline(self):
        """Returns the cancellation deadline as ISO string for JS countdown."""
        deadline = self.created_at + timedelta(minutes=CANCEL_WINDOW_MINUTES)
        return deadline.isoformat() + 'Z'

    @property
    def seconds_remaining(self):
        """Seconds remaining before cancellation window closes."""
        deadline = self.created_at + timedelta(minutes=CANCEL_WINDOW_MINUTES)
        remaining = (deadline - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem {self.product_id} x{self.quantity}>'

    @property
    def subtotal(self):
        return self.price * self.quantity

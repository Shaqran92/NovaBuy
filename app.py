import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, CartItem, Order, OrderItem, CANCEL_WINDOW_MINUTES

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///ecommerce.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_globals():
    if current_user.is_authenticated:
        count = sum(item.quantity for item in current_user.cart_items)
        return {'cart_count': count, 'cancel_window': CANCEL_WINDOW_MINUTES}
    return {'cart_count': 0, 'cancel_window': CANCEL_WINDOW_MINUTES}


# ─── AUTH ROUTES ──────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        flash('Invalid email or password.', 'error')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ─── PROFILE ROUTES ──────────────────────────────────────────

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', '').strip()
        current_user.phone = request.form.get('phone', '').strip()
        current_user.address = request.form.get('address', '').strip()
        current_user.city = request.form.get('city', '').strip()
        current_user.state = request.form.get('state', '').strip()
        current_user.zip_code = request.form.get('zip_code', '').strip()

        # Password change (optional)
        new_password = request.form.get('new_password', '')
        if new_password:
            confirm_new = request.form.get('confirm_new_password', '')
            if new_password != confirm_new:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('profile'))
            current_user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    total_orders = Order.query.filter_by(user_id=current_user.id).count()
    total_spent = db.session.query(db.func.sum(Order.total)).filter(
        Order.user_id == current_user.id,
        Order.status != 'Cancelled'
    ).scalar() or 0

    return render_template('profile.html', total_orders=total_orders, total_spent=total_spent)


# ─── PRODUCT ROUTES ──────────────────────────────────────────

@app.route('/')
def home():
    featured = Product.query.filter_by(featured=True).limit(8).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    # Get product count per category
    category_counts = {}
    for cat in categories:
        category_counts[cat] = Product.query.filter_by(category=cat).count()
    all_products = Product.query.order_by(Product.created_at.desc()).limit(12).all()
    return render_template('home.html', featured=featured, categories=categories,
                           category_counts=category_counts, products=all_products)


@app.route('/products')
def products():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')

    query = Product.query

    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products_list = query.all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template('products.html', products=products_list, categories=categories,
                           current_category=category, current_sort=sort, search=search)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(4).all()
    return render_template('product_detail.html', product=product, related=related)


# ─── CART ROUTES ──────────────────────────────────────────────

@app.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.subtotal for item in items)
    return render_template('cart.html', items=items, total=total)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')

    next_url = request.form.get('next', url_for('products'))
    return redirect(next_url)


@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('cart'))
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))


@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('cart'))
    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return redirect(url_for('cart'))


# ─── ORDER ROUTES ─────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('products'))

    total = sum(item.subtotal for item in items)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip() or current_user.full_name or ''
        address = request.form.get('address', '').strip() or current_user.address or ''
        city = request.form.get('city', '').strip() or current_user.city or ''
        phone = request.form.get('phone', '').strip() or current_user.phone or ''

        if not all([full_name, address, city, phone]):
            flash('All fields are required.', 'error')
            return redirect(url_for('checkout'))

        order = Order(
            user_id=current_user.id,
            total=total,
            full_name=full_name,
            address=address,
            city=city,
            phone=phone
        )
        db.session.add(order)
        db.session.flush()

        for cart_item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            cart_item.product.stock -= cart_item.quantity

        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        flash('Order placed successfully! You can cancel within 10 minutes.', 'success')
        return redirect(url_for('order_detail', order_id=order.id))

    return render_template('checkout.html', items=items, total=total)


@app.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('orders'))

    if not order.can_cancel:
        flash('This order can no longer be cancelled. The 10-minute window has passed.', 'error')
        return redirect(url_for('order_detail', order_id=order.id))

    # Restore stock
    for item in order.items:
        item.product.stock += item.quantity

    order.status = 'Cancelled'
    order.cancelled_at = datetime.utcnow()
    db.session.commit()

    flash('Order cancelled successfully. Your items have been restocked.', 'success')
    return redirect(url_for('orders'))


@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)


@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('orders'))
    return render_template('order_detail.html', order=order)


# ─── INITIALIZE ──────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Run in debug mode only if development environment
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

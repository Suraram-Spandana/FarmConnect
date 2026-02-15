from flask import make_response
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import os
from dotenv import load_dotenv
import uuid

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devkey")

load_dotenv()

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
if not app.config['MYSQL_PASSWORD']:
    raise ValueError("MYSQL_PASSWORD not set in .env file")
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'farmconnect')

mysql = MySQL(app)

# Ensure images folder exists
if not os.path.exists('static/images'):
    os.makedirs('static/images')

# Home Page (All Users)
@app.route('/')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('index.html', products=products)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user_type = request.form['user_type']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return render_template('register.html', error="Email already registered")

        cursor.execute("INSERT INTO users(name, email, password, user_type) VALUES(%s, %s, %s, %s)",
                        (name, email, password, user_type))
        mysql.connection.commit()
        
        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_type'] = user['user_type']

            if user['user_type'] == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            return redirect(url_for('consumer_dashboard'))

        return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')

# Farmer Dashboard
@app.route('/farmer_dashboard')
def farmer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # ✅ Count new orders not seen
    cursor.execute("SELECT COUNT(*) AS unseen FROM orders WHERE farmer_id=%s AND farmer_seen=0", 
                   (session['user_id'],))
    notif = cursor.fetchone()['unseen']

    cursor.execute("SELECT * FROM products WHERE farmer_id=%s", (session['user_id'],))
    products = cursor.fetchall()
    cursor.close()

    return render_template(
        'farmer_dashboard.html',
        user_name=session['user_name'],
        products=products,
        notif=notif
    )


# Add Product (Image Upload ✅)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        qty = request.form['quantity']
        category = request.form['category']
        image_file = request.files.get('image')

        image_name = None
        if image_file and image_file.filename != "":
            image_name = secure_filename(image_file.filename)
            image_file.save(os.path.join('static/images/', image_name))

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO products(farmer_id, name, description, price, quantity, category, image) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (session['user_id'], name, description, price, qty, category, image_name)
        )
        mysql.connection.commit()

        return redirect(url_for('farmer_dashboard'))

    return render_template('add_product.html')
#delete product
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'user_id' not in session or session['user_type'] != 'farmer':
        flash("Unauthorized access!")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch product info
    cursor.execute("SELECT * FROM products WHERE id=%s AND farmer_id=%s", (product_id, session['user_id']))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        flash("Product not found or access denied.")
        return redirect(url_for('farmer_dashboard'))

    try:
        # Optionally delete from cart and orders first to avoid FK errors
        cursor.execute("DELETE FROM cart WHERE product_id=%s", (product_id,))
        cursor.execute("DELETE FROM orders WHERE product_id=%s", (product_id,))

        # Delete product
        cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
        mysql.connection.commit()

        # Delete product image if not default
        default_files = ['veg_default.png','fruits_default.png','grains_default.png','dairy_default.png','generic_default.png']
        if product['image'] and product['image'] not in default_files:
            img_path = os.path.join('static/images', product['image'])
            if os.path.exists(img_path):
                os.remove(img_path)

        flash("Product deleted successfully ✅")
    except Exception as e:
        mysql.connection.rollback()
        print("Error deleting product:", e)
        flash("Failed to delete product. Check for dependent orders or cart items.")

    cursor.close()
    return redirect(url_for('farmer_dashboard'))


# Edit Product
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id=%s AND farmer_id=%s", 
                   (product_id, session['user_id']))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        flash("Product not found or access denied.")
        return redirect(url_for('farmer_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        category = request.form.get('category') or 'generic'
        remove_requested = request.form.get('remove_image') == 'yes'

        # Default category images
        default_images = {
            'vegetables': 'veg_default.png',
            'fruits': 'fruits_default.png',
            'grains': 'grains_default.png',
            'dairy': 'dairy_default.png',
            'generic': 'generic_default.png'
        }

        image_file = request.files.get('image')
        new_image_name = product.get('image')  # Keep old image if no change

        # If farmer uploaded new image
        if image_file and image_file.filename != "":
            original = secure_filename(image_file.filename)
            new_image_name = f"{uuid.uuid4().hex}_{original}"
            image_file.save(os.path.join('static', 'images', new_image_name))

            # Remove old image if not a default
            old_img = product.get('image')
            if old_img not in default_images.values() and old_img:
                old_path = os.path.join('static', 'images', old_img)
                if os.path.exists(old_path):
                    os.remove(old_path)

        # If remove image checked → apply default image
        if remove_requested:
            old_img = product.get('image')
            if old_img not in default_images.values() and old_img:
                old_path = os.path.join('static', 'images', old_img)
                if os.path.exists(old_path):
                    os.remove(old_path)

            new_image_name = default_images.get(category, 'generic_default.png')

        # Update DB
        cursor.execute("""
            UPDATE products
            SET name=%s, description=%s, price=%s, quantity=%s, category=%s, image=%s
            WHERE id=%s AND farmer_id=%s
        """, (name, description, price, quantity, category, new_image_name, product_id, session['user_id']))
        
        mysql.connection.commit()
        cursor.close()

        flash("Product updated successfully!")
        return redirect(url_for('farmer_dashboard'))

    cursor.close()
    return render_template('edit_product.html', product=product)

# View All Products
@app.route('/view_products')
def view_products():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT p.*, u.name AS farmer_name
        FROM products p 
        JOIN users u ON p.farmer_id = u.id
    """)
    products = cursor.fetchall()
    cursor.close()
    
    return render_template('view_products.html', products=products)

# Consumer Dashboard
@app.route('/consumer_dashboard')
def consumer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'consumer':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT p.*, u.name AS farmer_name
        FROM products p
        JOIN users u ON p.farmer_id = u.id
    """)
    products = cursor.fetchall()
    cursor.close()

    return render_template('consumer_dashboard.html',
                           user_name=session['user_name'],
                           products=products)

#buy_product
# ---------------------------
# 1) Buy product -> redirect to checkout
# ---------------------------
@app.route('/buy_product/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        flash("Please login as consumer.")
        return redirect(url_for('login'))

    qty = int(request.form.get('quantity', 1))
    
    # Redirect to checkout with selected quantity
    return redirect(url_for('checkout', product_id=product_id, qty=qty))

    # redirect to checkout with quantity as query param
    return redirect(url_for('checkout', product_id=product_id, qty=qty))

# ---------------------------
# Add to Cart
# ---------------------------
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        flash("Please login as consumer.")
        return redirect(url_for('login'))

    quantity = int(request.form.get('quantity', 1))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Check product exists
    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    if not product:
        cursor.close()
        flash("Product not found.")
        return redirect(url_for('consumer_dashboard'))

    # Stock check
    if quantity > product['quantity']:
        cursor.close()
        flash("Not enough stock available.")
        return redirect(url_for('consumer_dashboard'))

    # Check if already in cart
    cursor.execute("""
        SELECT * FROM cart WHERE consumer_id=%s AND product_id=%s
    """, (session['user_id'], product_id))
    item = cursor.fetchone()

    if item:
        # Update quantity in cart
        cursor.execute("""
            UPDATE cart
            SET quantity = quantity + %s
            WHERE id = %s
        """, (quantity, item['id']))
    else:
        # Insert into cart
        cursor.execute("""
            INSERT INTO cart (consumer_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, (session['user_id'], product_id, quantity))

    mysql.connection.commit()
    cursor.close()

    flash("Added to cart successfully! 🛒✅")
    return redirect(url_for('consumer_dashboard'))


# ---------------------------
# 2) Checkout page (full address form, payment simulation)
# ---------------------------
@app.route('/checkout/<int:product_id>', methods=['GET', 'POST'])
def checkout(product_id):
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        flash("Please login as consumer.")
        return redirect(url_for('login'))

    qty = int(request.args.get('qty', 1)) if request.method == 'GET' else int(request.form.get('quantity', 1))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        flash("Product not found.")
        return redirect(url_for('view_products'))

    if qty > product['quantity']:
        cursor.close()
        flash("Requested quantity exceeds available stock.")
        return redirect(url_for('view_products'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        house_no = request.form.get('house_no')
        street = request.form.get('street')
        landmark = request.form.get('landmark')
        town = request.form.get('town')
        district = request.form.get('district')
        state = request.form.get('state')
        pincode = request.form.get('pincode')

        address_parts = []
        if full_name: address_parts.append(full_name)
        if house_no: address_parts.append(house_no)
        if street: address_parts.append(street)
        if landmark: address_parts.append("Landmark: " + landmark)
        if town: address_parts.append(town)
        if district: address_parts.append(district)
        if state: address_parts.append(state)
        if pincode: address_parts.append("PIN: " + pincode)
        
        address = ", ".join([p for p in address_parts if p])

        total_price = float(product['price']) * qty

        # Fetch farmer_id
        cursor.execute("SELECT farmer_id FROM products WHERE id=%s", (product_id,))
        farmer_row = cursor.fetchone()
        farmer_id = farmer_row['farmer_id']

        # Insert into Orders Table ✅
        cursor.execute("""
            INSERT INTO orders (product_id, consumer_id, farmer_id, quantity, total, address, phone, payment_status, status, farmer_seen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Paid', 'Pending', 0)
        """, (product_id, session['user_id'], farmer_id, qty, total_price, address, phone))

        # Reduce stock ✅
        cursor.execute("UPDATE products SET quantity = quantity - %s WHERE id=%s", (qty, product_id))

        mysql.connection.commit()
        cursor.close()

        flash("Payment successful and order placed! ✅")
        return redirect(url_for('orders'))

    cursor.close()
    return render_template('checkout.html', product=product, qty=qty)

# ---------------------------
# 3) Orders page (consumer) - shows address, status, payment_status and cancel option
# ---------------------------
# View Orders Page
@app.route('/orders')
def orders():
    if 'user_id' not in session or session['user_type'] != 'consumer':
        return redirect(url_for('login'))

    month = request.args.get('month')
    year = request.args.get('year')
    category = request.args.get('category')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    query = """
        SELECT o.id, o.product_id, o.quantity, o.total, o.order_date,
               o.address, o.phone, o.status, o.payment_status,
               p.name AS product_name, p.image AS product_image,
               u.name AS farmer_name
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users u ON p.farmer_id = u.id
        WHERE o.consumer_id = %s
    """

    filters = [session['user_id']]

    if month:
        query += " AND MONTH(o.order_date) = %s"
        filters.append(month)

    if year:
        query += " AND YEAR(o.order_date) = %s"
        filters.append(year)

    if category:
        query += " AND p.category = %s"
        filters.append(category)

    query += " ORDER BY o.order_date DESC"

    cursor.execute(query, tuple(filters))
    orders = cursor.fetchall()
    cursor.close()

    return render_template('orders.html', orders=orders,
                           selected_month=month,
                           selected_year=year,
                           selected_category=category)

# ---------------------------
# Cart Page - View Cart
# ---------------------------
@app.route('/cart')
def cart():
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        flash("Please login first.")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT c.id AS cart_id, c.quantity,
               p.id AS product_id, p.name, p.price, p.image, p.quantity AS stock,
               u.name AS farmer_name
        FROM cart c
        JOIN products p ON c.product_id = p.id
        JOIN users u ON p.farmer_id = u.id
        WHERE c.consumer_id = %s
    """, (session['user_id'],))
    items = cursor.fetchall()
    cursor.close()

    total_amount = sum(i['quantity'] * i['price'] for i in items)

    return render_template("cart.html", items=items, total_amount=total_amount)

@app.route('/remove_cart/<int:cart_id>', methods=['POST'])
def remove_cart(cart_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM cart WHERE id=%s AND consumer_id=%s", (cart_id, session['user_id']))
    mysql.connection.commit()
    cursor.close()

    flash("Item removed from cart.")
    return redirect(url_for('cart'))

#checkout_cart
# Checkout Cart (Place orders for all items in cart)
@app.route('/checkout_cart', methods=['POST'])
def checkout_cart():
    if 'user_id' not in session or session['user_type'] != 'consumer':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute("""
            SELECT c.id AS cart_id, c.quantity,
                   p.id AS product_id, p.farmer_id, p.name, p.price,
                   p.quantity AS available_stock,
                   (p.price * c.quantity) AS total
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.consumer_id=%s
        """, (session['user_id'],))

        items = cursor.fetchall()

        print("SESSION USER:", session.get('user_id'))
        print("SESSION TYPE:", session.get('user_type'))
        print("ITEM COUNT:", len(items))

        if not items:
            flash("Your cart is empty")
            cursor.close()
            return redirect(url_for('cart'))

        for item in items:
            cursor.execute("""
                INSERT INTO orders
                (product_id, consumer_id, farmer_id, quantity, total, address, phone, payment_status, status, farmer_seen)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Paid', 'Pending', 0)
            """, (
                item['product_id'],
                session['user_id'],
                item['farmer_id'],
                item['quantity'],
                item['total'],
                session.get('address', 'Address Not Provided'),
                session.get('phone', '0000000000')
            ))

            cursor.execute("""
                UPDATE products
                SET quantity = quantity - %s
                WHERE id = %s
            """, (item['quantity'], item['product_id']))

        cursor.execute("DELETE FROM cart WHERE consumer_id=%s", (session['user_id'],))
        mysql.connection.commit()
        cursor.close()

        print("✅ Checkout Cart executed ✅")
        flash("✅ Order placed successfully!")
        return redirect(url_for('orders'))

    except Exception as e:
        print("❌ SQL ERROR IN CHECKOUT:", e)
        mysql.connection.rollback()
        cursor.close()
        flash("Something went wrong while placing your order")
        return redirect(url_for('cart'))

# ---------------------------
# 4) Cancel order (consumer)
# ---------------------------
@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # ensure order belongs to consumer and is pending
    cursor.execute("SELECT * FROM orders WHERE id=%s AND consumer_id=%s", (order_id, session['user_id']))
    order = cursor.fetchone()
    if not order:
        cursor.close()
        flash("Order not found.")
        return redirect(url_for('orders'))

    if order['status'] != 'Pending':
        cursor.close()
        flash("Only pending orders can be canceled.")
        return redirect(url_for('orders'))

    # restore stock
    cursor.execute("UPDATE products SET quantity = quantity + %s WHERE id=%s", (order['quantity'], order['product_id']))
    # update order status
    cursor.execute("UPDATE orders SET status=%s WHERE id=%s", ('Cancelled', order_id))
    mysql.connection.commit()
    cursor.close()
    flash("Order canceled and stock restored.")
    return redirect(url_for('orders'))


# ---------------------------
# 5) Product detail page (click from order/product)
# ---------------------------
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT p.*, u.name AS farmer_name
        FROM products p
        JOIN users u ON p.farmer_id = u.id
        WHERE p.id=%s
    """, (product_id,))
    product = cursor.fetchone()
    cursor.close()
    if not product:
        flash("Product not found.")
        return redirect(url_for('view_products'))
    return render_template('product_detail.html', p=product)


# ---------------------------
# 6) Farmer orders (notifications) - show orders related to farmer's products
# ---------------------------
@app.route('/farmer_orders')
def farmer_orders():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))

    month = request.args.get('month')
    year = request.args.get('year')
    category = request.args.get('category')
    status = request.args.get('status')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    query = """
        SELECT o.id, o.product_id, o.quantity, o.total AS total_price,
               o.order_date, o.address, o.phone, o.status,
               o.payment_status, o.farmer_seen,
               p.name AS product_name, p.image AS product_image, p.category AS category,
               c.name AS consumer_name
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users c ON o.consumer_id = c.id
        WHERE p.farmer_id = %s
    """

    filters = [session['user_id']]

    if month:
        query += " AND MONTH(o.order_date) = %s"
        filters.append(month)

    if year:
        query += " AND YEAR(o.order_date) = %s"
        filters.append(year)

    if category:
        query += " AND p.category = %s"
        filters.append(category)

    if status:
        query += " AND o.status = %s"
        filters.append(status)

    query += " ORDER BY o.order_date DESC"

    cursor.execute(query, tuple(filters))
    orders = cursor.fetchall()

    # ✅ Mark all new unseen orders as seen once farmer views them
    cursor2 = mysql.connection.cursor()
    cursor2.execute("""
        UPDATE orders 
        SET farmer_seen = 1 
        WHERE farmer_seen = 0 
        AND product_id IN (SELECT id FROM products WHERE farmer_id = %s)
    """, (session['user_id'],))
    mysql.connection.commit()
    cursor2.close()

    cursor.close()

    print("📢 FARMER NEW ORDERS CHECK:", orders)

    return render_template(
        'farmer_orders.html',
        orders=orders,
        selected_month=month,
        selected_year=year,
        selected_category=category,
        selected_status=status
    )


# ---------------------------
# 7) Farmer marks an order as delivered
# ---------------------------
@app.route('/mark_delivered/<int:order_id>', methods=['POST'])
def mark_delivered(order_id):
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # find order & ensure the product belongs to this farmer
    cursor.execute("""
        SELECT o.*, p.farmer_id
        FROM orders o JOIN products p ON o.product_id = p.id
        WHERE o.id=%s
    """, (order_id,))
    row = cursor.fetchone()
    if not row or row['farmer_id'] != session['user_id']:
        cursor.close()
        flash("Order not found or access denied.")
        return redirect(url_for('farmer_orders'))

    # Only mark pending as delivered (or paid)
    cursor.execute("UPDATE orders SET status=%s WHERE id=%s", ('Delivered', order_id))
    mysql.connection.commit()
    cursor.close()
    flash("Order marked as delivered.")
    return redirect(url_for('farmer_orders'))

# Accept Order
@app.route('/accept_order/<int:order_id>', methods=['POST'])
def accept_order(order_id):
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE orders SET status='Accepted' WHERE id=%s", (order_id,))
    mysql.connection.commit()
    cursor.close()

    flash("Order Accepted ✅")
    return redirect(url_for('farmer_orders'))


# Reject Order
@app.route('/reject_order/<int:order_id>', methods=['POST'])
def reject_order(order_id):
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE orders SET status='Cancelled' WHERE id=%s", (order_id,))
    mysql.connection.commit()
    cursor.close()

    flash("Order Rejected ❌")
    return redirect(url_for('farmer_orders'))


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(debug=True)

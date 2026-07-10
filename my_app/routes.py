from flask import (
    Blueprint, render_template, redirect, url_for, request, flash, session, 
    send_file, jsonify, current_app
)
import sqlite3
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import google.generativeai as genai
import requests

from .db import DATABASE_NAME, get_dashboard_stats  # Import db helper functions

# A Blueprint is a way to organize a group of related views and other code.
# Instead of registering views and other code directly with an application,
# they are registered with a blueprint. Then the blueprint is registered with
# the application when it is available in the factory function.
bp = Blueprint('main', __name__)

ASK_AI_QUOTA_MESSAGE = (
    "The api key is Not working Currently\n"
    "Error: 429 Quota exceeded for quota metric 'Generate Content API requests per minute' and limit "
    "'GenerateContent request limit per minute for a region' of service "
    "'generativelanguage.googleapis.com' for consumer 'project_number:24940420888'. "
    "[reason: \"RATE_LIMIT_EXCEEDED\" domain: \"googleapis.com\" metadata { key: \"service\" value: "
    "\"generativelanguage.googleapis.com\" } metadata { key: \"quota_unit\" value: \"1/min/{project}/{region}\" } "
    "metadata { key: \"quota_metric\" value: \"generativelanguage.googleapis.com/generate_content_requests\" } "
    "metadata { key: \"quota_location\" value: \"asia-southeast1\" } metadata { key: \"quota_limit\" value: "
    "\"GenerateContentRequestsPerMinutePerProjectPerRegion\" } metadata { key: \"quota_limit_value\" value: \"0\" } "
    "metadata { key: \"consumer\" value: \"projects/24940420888\" } , links { description: \"Request a higher "
    "quota limit.\" url: \"https://cloud.google.com/docs/quotas/help/request_increase\" } ]"
)

def allowed_file(filename):
    """Checks if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# --- Main/Public Routes ---

@bp.route('/')
def index():
    return render_template('index.html')

# --- Wholesaler Registration ---

@bp.route('/register-wholesaler', methods=['GET', 'POST'])
def register_wholesaler():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        shop_name = request.form['shop_name']
        sourcing_info = request.form['sourcing_info']
        location = request.form['location']
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM wholesalers WHERE phone = ?', (phone,))
        if cursor.fetchone():
            flash('Phone number already registered. Please use a different number.', 'error')
            conn.close()
            return render_template('register_wholesaler.html')
        
        id_doc_path = None
        license_doc_path = None
        
        if 'id_proof' in request.files:
            id_file = request.files['id_proof']
            if id_file and allowed_file(id_file.filename):
                filename = secure_filename(f"{uuid.uuid4()}_{id_file.filename}")
                id_doc_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                id_file.save(id_doc_path)
        
        if 'license_doc' in request.files:
            license_file = request.files['license_doc']
            if license_file and allowed_file(license_file.filename):
                filename = secure_filename(f"{uuid.uuid4()}_{license_file.filename}")
                license_doc_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                license_file.save(license_doc_path)
        
        cursor.execute('''
            INSERT INTO wholesalers (name, phone, password, shop_name, id_doc_path, license_doc_path, sourcing_info, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, phone, password, shop_name, id_doc_path, license_doc_path, sourcing_info, location))
        conn.commit()
        conn.close()
        
        flash('Thank you for registering! Your application is pending approval.', 'success')
        return redirect(url_for('main.register_wholesaler'))
    
    return render_template('register_wholesaler.html')

# --- Admin Routes ---

@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['is_admin'] = True
            return redirect(url_for('main.admin_wholesalers'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

@bp.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('main.index'))

@bp.route('/admin/wholesalers')
def admin_wholesalers():
    if not session.get('is_admin'):
        return redirect(url_for('main.admin_login'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM wholesalers WHERE is_approved = 0')
    pending_wholesalers = cursor.fetchall()
    conn.close()
    
    return render_template('admin_wholesalers.html', wholesalers=pending_wholesalers)

@bp.route('/admin/approve/<int:wholesaler_id>')
def approve_wholesaler(wholesaler_id):
    if not session.get('is_admin'):
        return redirect(url_for('main.admin_login'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE wholesalers SET is_approved = 1 WHERE id = ?', (wholesaler_id,))
    conn.commit()
    conn.close()
    
    flash('Wholesaler approved successfully!', 'success')
    return redirect(url_for('main.admin_wholesalers'))

@bp.route('/admin/reject/<int:wholesaler_id>')
def reject_wholesaler(wholesaler_id):
    if not session.get('is_admin'):
        return redirect(url_for('main.admin_login'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wholesalers WHERE id = ?', (wholesaler_id,))
    conn.commit()
    conn.close()
    
    flash('Wholesaler application rejected and removed.', 'success')
    return redirect(url_for('main.admin_wholesalers'))

@bp.route('/download/<path:filename>')
def download_file(filename):
    if not session.get('is_admin'):
        return redirect(url_for('main.admin_login'))
    
    # Construct the full path to the file
    # Assuming filename includes 'static/uploads/...'
    full_path = os.path.join(current_app.root_path, filename)
    return send_file(full_path, as_attachment=True)

# --- Wholesaler Routes ---

@bp.route('/wholesaler/login', methods=['GET', 'POST'])
def wholesaler_login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, is_approved, password FROM wholesalers WHERE phone = ?', (phone,))
        wholesaler = cursor.fetchone()
        conn.close()
        
        if wholesaler:
            if wholesaler[3] == password:
                if wholesaler[2]:
                    session['wholesaler_id'] = wholesaler[0]
                    session['wholesaler_name'] = wholesaler[1]
                    return redirect(url_for('main.wholesaler_dashboard'))
                else:
                    flash('Your application is still pending approval.', 'warning')
            else:
                flash('Invalid password. Please try again.', 'error')
        else:
            flash('Phone number not found. Please register first.', 'error')
    
    return render_template('wholesaler_login.html')

@bp.route('/wholesaler/dashboard')
def wholesaler_dashboard():
    if 'wholesaler_id' not in session:
        return redirect(url_for('main.wholesaler_login'))
    
    wholesaler_id = session['wholesaler_id']
    stats = get_dashboard_stats(wholesaler_id)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products WHERE wholesaler_id = ? ORDER BY created_at DESC LIMIT 4', (wholesaler_id,))
    recent_products = cursor.fetchall()
    
    cursor.execute('''
        SELECT r.id, r.rating, r.comment, r.reply, v.name, r.created_at 
        FROM reviews r 
        JOIN vendors v ON r.vendor_id = v.id 
        WHERE r.wholesaler_id = ? 
        ORDER BY r.created_at DESC LIMIT 3
    ''', (wholesaler_id,))
    recent_reviews = cursor.fetchall()
    
    conn.close()
    
    return render_template('wholesaler_dashboard.html', 
                           stats=stats, 
                           recent_products=recent_products, 
                           recent_reviews=recent_reviews)

@bp.route('/wholesaler/profile')
def wholesaler_profile():
    if 'wholesaler_id' not in session:
        return redirect(url_for('main.wholesaler_login'))
    
    wholesaler_id = session['wholesaler_id']
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM wholesalers WHERE id = ?', (wholesaler_id,))
    wholesaler = cursor.fetchone()
    conn.close()
    
    if not wholesaler:
        flash('Wholesaler not found.', 'error')
        return redirect(url_for('main.wholesaler_login'))
    
    return render_template('wholesaler_profile.html', wholesaler=wholesaler)

@bp.route('/wholesaler/products')
def wholesaler_products():
    if 'wholesaler_id' not in session:
        return redirect(url_for('main.wholesaler_login'))
    
    wholesaler_id = session['wholesaler_id']
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE wholesaler_id = ? ORDER BY created_at DESC', (wholesaler_id,))
    products = cursor.fetchall()
    conn.close()
    
    return render_template('products_manage.html', products=products)

@bp.route('/wholesaler/orders')
def wholesaler_orders():
    if 'wholesaler_id' not in session:
        return redirect(url_for('main.wholesaler_login'))
    
    wholesaler_id = session['wholesaler_id']
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            o.id,
            o.wholesaler_id,
            o.vendor_id,
            COUNT(oi.id) as item_count,
            COALESCE(SUM(oi.quantity), 0) as total_quantity,
            o.total_amount,
            o.status,
            o.created_at,
            v.name as vendor_name,
            CASE
                WHEN COUNT(oi.id) = 0 THEN 'No items'
                WHEN COUNT(oi.id) = 1 THEN MAX(p.name)
                ELSE MAX(p.name) || ' +' || (COUNT(oi.id) - 1) || ' more'
            END as product_summary
        FROM orders o
        JOIN vendors v ON o.vendor_id = v.id
        LEFT JOIN order_items oi ON oi.order_id = o.id
        LEFT JOIN products p ON p.id = oi.product_id
        WHERE o.wholesaler_id = ?
        GROUP BY o.id, o.wholesaler_id, o.vendor_id, o.total_amount, o.status, o.created_at, v.name
        ORDER BY o.created_at DESC
    ''', (wholesaler_id,))
    orders = cursor.fetchall()
    conn.close()
    
    return render_template('orders_manage.html', orders=orders)

@bp.route('/wholesaler/analytics')
def wholesaler_analytics():
    if 'wholesaler_id' not in session:
        return redirect(url_for('main.wholesaler_login'))
    
    wholesaler_id = session['wholesaler_id']
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, total_orders, total_revenue, active_customers 
        FROM analytics 
        WHERE wholesaler_id = ? 
        ORDER BY date DESC LIMIT 30
    ''', (wholesaler_id,))
    analytics_data = cursor.fetchall()
    
    conn.close()
    
    return render_template('analytics.html', analytics_data=analytics_data)

@bp.route('/wholesaler/add-product', methods=['GET', 'POST'])
def add_product():
    if 'wholesaler_id' not in session:
        return redirect(url_for('main.wholesaler_login'))
    
    if request.method == 'POST':
        name = request.form['name']
        category = request.form.get('main_category') or request.form.get('category')
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        status = 'In Stock' if stock > 50 else 'Low Stock' if stock > 0 else 'Out of Stock'
        
        image_path = None
        if 'product_image' in request.files:
            image_file = request.files['product_image']
            if image_file and image_file.filename and allowed_file(image_file.filename):
                filename = secure_filename(f"product_{uuid.uuid4()}_{image_file.filename}")
                # Save relative path for use in templates
                relative_path = f"uploads/{filename}"
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image_file.save(full_path)
                image_path = relative_path

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (wholesaler_id, name, category, price, stock, image_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session['wholesaler_id'], name, category, price, stock, image_path, status))
        conn.commit()
        conn.close()

        flash('Product added successfully!', 'success')
        return redirect(url_for('main.wholesaler_dashboard'))

    return render_template('add_product.html')

@bp.route('/wholesaler/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'wholesaler_id' not in session:
        return redirect(url_for('main.wholesaler_login'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        category = request.form.get('main_category') or request.form.get('category')
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        status = 'In Stock' if stock > 50 else 'Low Stock' if stock > 0 else 'Out of Stock'
        
        cursor.execute('SELECT image_path FROM products WHERE id = ? AND wholesaler_id = ?', 
                       (product_id, session['wholesaler_id']))
        current_image = cursor.fetchone()[0]
        image_path = current_image

        if 'product_image' in request.files:
            image_file = request.files['product_image']
            if image_file and image_file.filename and allowed_file(image_file.filename):
                filename = secure_filename(f"product_{uuid.uuid4()}_{image_file.filename}")
                relative_path = f"uploads/{filename}"
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image_file.save(full_path)
                image_path = relative_path

        cursor.execute('''
            UPDATE products 
            SET name = ?, category = ?, price = ?, stock = ?, status = ?, image_path = ?
            WHERE id = ? AND wholesaler_id = ?
        ''', (name, category, price, stock, status, image_path, product_id, session['wholesaler_id']))
        conn.commit()
        conn.close()

        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.wholesaler_products'))
    
    cursor.execute('SELECT * FROM products WHERE id = ? AND wholesaler_id = ?', 
                   (product_id, session['wholesaler_id']))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('main.wholesaler_products'))
    
    return render_template('edit_product.html', product=product)

@bp.route('/wholesaler/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'wholesaler_id' not in session:
        return redirect(url_for('main.wholesaler_login'))
    
    wholesaler_id = session['wholesaler_id']
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        shop_name = request.form['shop_name']
        location = request.form['location']
        sourcing_info = request.form['sourcing_info']
        
        cursor.execute('''
            UPDATE wholesalers 
            SET name = ?, shop_name = ?, location = ?, sourcing_info = ?
            WHERE id = ?
        ''', (name, shop_name, location, sourcing_info, wholesaler_id))
        
        conn.commit()
        session['wholesaler_name'] = name
        flash('Profile updated successfully!', 'success')
        conn.close()
        return redirect(url_for('main.wholesaler_profile'))
    
    cursor.execute('SELECT * FROM wholesalers WHERE id = ?', (wholesaler_id,))
    wholesaler = cursor.fetchone()
    conn.close()
    
    if not wholesaler:
        flash('Wholesaler not found.', 'error')
        return redirect(url_for('main.wholesaler_login'))
    
    return render_template('edit_profile.html', wholesaler=wholesaler)

# --- Vendor Routes ---

# NEW VENDOR REGISTRATION ROUTE
@bp.route('/vendor/register', methods=['GET', 'POST'])
def register_vendor():
    if request.method == 'POST':
        # Personal Info
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        alternate_contact = request.form.get('alternate_contact')
        email = request.form.get('email')

        # Business Details
        shop_name = request.form.get('shop_name')
        goods_type = request.form.get('goods_type')
        working_hours = request.form.get('working_hours')
        street_area = request.form.get('street_area')

        # Location
        pincode = request.form.get('pincode')
        city = request.form.get('city')
        location = request.form.get('location')

        # Handle optional photo upload
        photo_path = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and allowed_file(photo_file.filename):
                filename = secure_filename(f"vendor_{uuid.uuid4()}_{photo_file.filename}")
                photo_path = os.path.join('uploads', filename).replace('\\', '/')
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                photo_file.save(full_path)

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM vendors WHERE phone = ?", (phone,))
        if cursor.fetchone():
            flash('This phone number is already registered.', 'error')
            conn.close()
            return redirect(url_for('main.register_vendor'))

        cursor.execute(
            """INSERT INTO vendors (name, phone, password, alternate_contact, email, shop_name, goods_type, working_hours, street_area, photo_path, pincode, city, location, is_approved)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, phone, password, alternate_contact, email, shop_name, goods_type, working_hours, street_area, photo_path, pincode, city, location, True)
        )
        conn.commit()
        conn.close()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.vendor_login'))

    return render_template('vendor_register.html')

@bp.route('/vendor')
def vendor():
    return redirect(url_for('main.vendor_login'))

@bp.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, password FROM vendors WHERE phone = ? AND is_approved = 1", (phone,))
        vendor = cursor.fetchone()
        conn.close()

        if vendor and vendor[2] == password:
            session['vendor_id'] = vendor[0]
            session['vendor_name'] = vendor[1]
            return redirect(url_for('main.vendor_dashboard'))
        else:
            flash('Invalid credentials or your account is not yet approved.', 'error')

    return render_template('vendor_login.html')

@bp.route('/vendor/logout')
def vendor_logout():
    session.pop('vendor_id', None)
    session.pop('vendor_name', None)
    session.pop('vendor_cart', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.vendor_login'))

@bp.route('/vendor/dashboard')
def vendor_dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # NEW: Fetch detailed top rated wholesalers
    cursor.execute('''
        SELECT 
            w.id,
            w.name,
            w.location,
            w.phone,
            w.trust_score,
            w.profile_photo,
            (SELECT GROUP_CONCAT(DISTINCT p.category) FROM products p WHERE p.wholesaler_id = w.id LIMIT 3) as specialties,
            (SELECT COUNT(r.id) FROM reviews r WHERE r.wholesaler_id = w.id) as review_count
        FROM wholesalers w
        WHERE w.is_approved = 1
        ORDER BY w.trust_score DESC
        LIMIT 4
    ''')
    top_wholesalers = cursor.fetchall()

    cursor.execute('''
        SELECT p.*, w.name as wholesaler_name, w.trust_score
        FROM products p
        JOIN wholesalers w ON p.wholesaler_id = w.id
        WHERE w.is_approved = 1 AND p.stock > 0
        ORDER BY p.views DESC
        LIMIT 8
    ''')
    featured_products = cursor.fetchall()

    # NEW QUERY: Fetch recently ordered items
    cursor.execute('''
        SELECT 
            p.id, 
            p.name, 
            p.image_path,
            oi.quantity,
            COUNT(p.id) as order_count
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        WHERE o.vendor_id = ?
        GROUP BY p.id
        ORDER BY MAX(o.created_at) DESC, order_count DESC
        LIMIT 4
    ''', (session['vendor_id'],))
    recent_orders = cursor.fetchall()

    # NEW: Fetch all distinct wholesalers for the filter dropdown
    cursor.execute('''
        SELECT DISTINCT name FROM wholesalers WHERE is_approved = 1 ORDER BY name
    ''')
    all_wholesalers = [row['name'] for row in cursor.fetchall()]

    # NEW: Fetch all distinct product categories for the filter
    cursor.execute('''
        SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category
    ''')
    all_categories = [row['category'] for row in cursor.fetchall()]

    # UPDATED: Fetch only 8 random budget-friendly products for the initial view
    cursor.execute('''
        SELECT 
            p.*, 
            w.name as wholesaler_name,
            w.trust_score,
            (p.price * 1.25) as original_price
        FROM products p
        JOIN wholesalers w ON p.wholesaler_id = w.id
        WHERE w.is_approved = 1 AND p.stock > 0
        ORDER BY RANDOM() LIMIT 8
    ''')
    budget_products = cursor.fetchall()

    conn.close()

    return render_template('modern_vendor_dashboard.html',
                           top_wholesalers=top_wholesalers,
                           featured_products=featured_products,
                           recent_orders=recent_orders,
                           all_wholesalers=all_wholesalers,
                           budget_products=budget_products,
                           all_categories=all_categories)

# CORRECTED THIS ENTIRE FUNCTION
@bp.route('/vendor/cart')
def vendor_cart():
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))
    
    cart = session.get('vendor_cart', {})
    
    # This will be the main data structure passed to the template
    wholesaler_data = {} 
    total_amount = 0
    
    if cart:
        conn = sqlite3.connect(DATABASE_NAME)
        # Use row_factory to access columns by name, makes code cleaner
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        # CORRECTED: Loop over cart.items() to get both product_id_str and quantity
        for product_id_str, quantity in cart.items():
            try:
                # CRITICAL FIX: Convert product_id from string (in session) to integer for DB query
                product_id = int(product_id_str)
            except ValueError:
                continue # Skip if the key in session is not a valid number

            cursor.execute('''
                SELECT p.*, w.name as wholesaler_name, w.id as wholesaler_id
                FROM products p
                JOIN wholesalers w ON p.wholesaler_id = w.id
                WHERE p.id = ?
            ''', (product_id,)) # Use the integer product_id here
            product = cursor.fetchone()
            
            if product:
                wholesaler_id = product['wholesaler_id']
                wholesaler_name = product['wholesaler_name']
                
                # If this is the first item from this wholesaler, create an entry
                if wholesaler_id not in wholesaler_data:
                    wholesaler_data[wholesaler_id] = {
                        'name': wholesaler_name,
                        'items': [],
                        'subtotal': 0
                    }
                
                item_total = product['price'] * quantity
                total_amount += item_total
                
                # Add the item to the correct wholesaler's list
                wholesaler_data[wholesaler_id]['items'].append({
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity,
                    'item_total': item_total,
                    'image_path': product['image_path']
                })
                # Update the subtotal for that wholesaler
                wholesaler_data[wholesaler_id]['subtotal'] += item_total

        conn.close()
    
    # Pass the new data structure to the template
    return render_template('vendor_cart.html', 
                           wholesaler_data=wholesaler_data, 
                           total_amount=total_amount,
                           lang=session.get('vendor_language', 'en'))

@bp.route('/vendor/profile', methods=['GET', 'POST'])
def vendor_profile():
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))

    vendor_id = session['vendor_id']
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    cursor = conn.cursor()

    # Handle form submission for profile updates
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        location = request.form.get('location')
        email = request.form.get('email')
        cursor.execute('''
            UPDATE vendors SET name = ?, phone = ?, location = ?, email = ? WHERE id = ?
        ''', (name, phone, location, email, vendor_id))
        conn.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.vendor_profile'))

    # Fetch comprehensive data for displaying the profile page
    
    # Query 1: Get all vendor details
    cursor.execute('SELECT * FROM vendors WHERE id = ?', (vendor_id,))
    vendor = cursor.fetchone()

    # Query 2: Get vendor statistics
    cursor.execute('''
        SELECT
            COUNT(id) as total_orders,
            COALESCE(SUM(total_amount), 0) as total_spent
        FROM orders
        WHERE vendor_id = ?
    ''', (vendor_id,))
    stats = cursor.fetchone()

    # Query 3: Get recent order items
    cursor.execute('''
        SELECT p.name, p.image_path, oi.quantity, o.created_at
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        WHERE o.vendor_id = ?
        ORDER BY o.created_at DESC
        LIMIT 3
    ''', (vendor_id,))
    recent_activity = cursor.fetchall()

    conn.close()
    
    # Pass all data to the template
    return render_template('vendor_profile.html', vendor=vendor, stats=stats, recent_activity=recent_activity)

# ADDED THIS MISSING ROUTE
@bp.route('/vendor/saved-payment-info')
def saved_payment_info():
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))
    
    vendor_id = session['vendor_id']
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM vendor_payment_methods WHERE vendor_id = ? ORDER BY is_default DESC, created_at DESC", 
        (vendor_id,)
    )
    
    payment_methods = []
    for row in cursor.fetchall():
        method = dict(row)
        method['details'] = json.loads(method['details'])
        payment_methods.append(method)

    # For now, recent transactions are static. This would be a more complex query.
    recent_transactions = [
        {'id': 12345, 'date': '2025-08-12', 'amount': 1250.00, 'status': 'Completed', 'method': 'UPI'},
        {'id': 12344, 'date': '2025-08-10', 'amount': 850.00, 'status': 'Completed', 'method': 'Bank Account'},
        {'id': 12340, 'date': '2025-08-05', 'amount': 2100.00, 'status': 'Completed', 'method': 'UPI'},
    ]

    conn.close()
    
    return render_template('saved_payment_info.html', payment_methods=payment_methods, transactions=recent_transactions)

@bp.route('/vendor/checkout', methods=['GET', 'POST'])
def vendor_checkout():
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))
    
    if request.method == 'POST':
        cart = session.get('vendor_cart', {})
        if not cart:
            flash('Your cart is empty', 'error')
            return redirect(url_for('main.vendor_cart'))
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        orders_by_wholesaler = {}
        created_order_ids = []
        
        for product_id, quantity in cart.items():
            cursor.execute('''
                SELECT p.id, p.price, w.id as wholesaler_id
                FROM products p
                JOIN wholesalers w ON p.wholesaler_id = w.id
                WHERE p.id = ?
            ''', (product_id,))
            product = cursor.fetchone()
            
            if product:
                wholesaler_id = product[2]
                if wholesaler_id not in orders_by_wholesaler:
                    orders_by_wholesaler[wholesaler_id] = []
                
                orders_by_wholesaler[wholesaler_id].append({
                    'product_id': product[0],
                    'quantity': quantity,
                    'price': product[1],
                    'total': product[1] * quantity
                })
        
        for wholesaler_id, items in orders_by_wholesaler.items():
            total_amount = sum(item['total'] for item in items)
            
            cursor.execute('''
                INSERT INTO orders (wholesaler_id, vendor_id, total_amount, status)
                VALUES (?, ?, ?, ?)
            ''', (wholesaler_id, session['vendor_id'], total_amount, 'pending'))
            
            order_id = cursor.lastrowid
            created_order_ids.append(order_id)
            
            for item in items:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, price, total)
                    VALUES (?, ?, ?, ?, ?)
                ''', (order_id, item['product_id'], item['quantity'], item['price'], item['total']))
        
        conn.commit()
        conn.close()
        
        session['vendor_cart'] = {}
        session.modified = True
        
        # Store order IDs for receipt generation (actual DB order IDs)
        session['last_order_ids'] = created_order_ids
        session['last_payment_method'] = request.form.get('payment_method', 'cod')
        # In a real app, capture the posted address; for now, store default shown in UI
        session['last_delivery_address'] = request.form.get('delivery_address', 'Home, 123 Street Name, City - 400001, Maharashtra, India')
        session.modified = True
        
        # Return JSON response for AJAX handling
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'message': 'Orders placed successfully!', 'order_ids': created_order_ids})
        
        return redirect(url_for('main.vendor_order_confirmation'))
    
    # GET request - show checkout page with cart data
    cart = session.get('vendor_cart', {})
    wholesaler_data = {} 
    total_amount = 0
    
    if cart:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        for product_id_str, quantity in cart.items():
            try:
                product_id = int(product_id_str)
            except ValueError:
                continue

            cursor.execute('''
                SELECT p.*, w.name as wholesaler_name, w.id as wholesaler_id
                FROM products p
                JOIN wholesalers w ON p.wholesaler_id = w.id
                WHERE p.id = ?
            ''', (product_id,))
            product = cursor.fetchone()
            
            if product:
                wholesaler_id = product['wholesaler_id']
                wholesaler_name = product['wholesaler_name']
                
                if wholesaler_id not in wholesaler_data:
                    wholesaler_data[wholesaler_id] = {
                        'name': wholesaler_name,
                        'items': [],
                        'subtotal': 0
                    }
                
                item_total = product['price'] * quantity
                total_amount += item_total
                
                wholesaler_data[wholesaler_id]['items'].append({
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity,
                    'item_total': item_total,
                    'image_path': product['image_path']
                })
                wholesaler_data[wholesaler_id]['subtotal'] += item_total

        conn.close()
    
    return render_template('vendor_checkout.html', 
                           wholesaler_data=wholesaler_data, 
                           total_amount=total_amount,
                           lang=session.get('vendor_language', 'en'))

@bp.route('/vendor/download-receipt')
def download_receipt():
    """Generate and download PDF receipt for the last order"""
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))
    
    order_ids = session.get('last_order_ids', [])
    if not order_ids:
        flash('No recent orders found', 'error')
        return redirect(url_for('main.vendor_orders'))
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from io import BytesIO
        import tempfile
        
        # Create a temporary file for the PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filename = temp_file.name
        temp_file.close()
        
        # Create PDF document
        doc = SimpleDocTemplate(temp_filename, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Get order data
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get vendor details
        cursor.execute('SELECT * FROM vendors WHERE id = ?', (session['vendor_id'],))
        vendor = cursor.fetchone()
        
        # Build PDF content
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#3b82f6'),
            alignment=1  # Center alignment
        )
        
        story.append(Paragraph("SAHAAYAK", title_style))
        story.append(Paragraph("Order Receipt", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Order info
        order_info = [
            ['Receipt Date:', datetime.now().strftime('%B %d, %Y')],
            ['Customer:', vendor['name'] if vendor else 'N/A'],
            ['Phone:', vendor['phone'] if vendor else 'N/A'],
            ['Payment:', (session.get('last_payment_method') or 'COD').upper()],
            ['Delivery:', session.get('last_delivery_address', 'N/A')],
            ['ETA:', '2-3 business days']
        ]
        
        order_table = Table(order_info, colWidths=[2*inch, 3*inch])
        order_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(order_table)
        story.append(Spacer(1, 20))
        
        # Orders details
        total_grand_total = 0
        for i, order_id in enumerate(order_ids):
            cursor.execute('''
                SELECT o.id, o.total_amount, o.created_at, w.name as wholesaler_name
                FROM orders o
                JOIN wholesalers w ON o.wholesaler_id = w.id
                WHERE o.id = ?
            ''', (order_id,))
            order = cursor.fetchone()
            
            if order:
                story.append(Paragraph(f"Order #{order['id']} - {order['wholesaler_name']}", styles['Heading3']))
                # Meta line
                try:
                    created_dt = datetime.strptime(order['created_at'], '%Y-%m-%d %H:%M:%S')
                    created_str = created_dt.strftime('%b %d, %Y %I:%M %p')
                except Exception:
                    created_str = str(order['created_at'])
                story.append(Paragraph(f"Placed on: {created_str}", styles['Normal']))
                story.append(Spacer(1, 6))
                
                cursor.execute('''
                    SELECT oi.quantity, oi.price, oi.total, p.name as product_name
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = ?
                ''', (order['id'],))
                items = cursor.fetchall()
                
                # Items table
                data = [['Item', 'Quantity', 'Price', 'Total']]
                for item in items:
                    data.append([
                        item['product_name'],
                        str(item['quantity']),
                        f"₹{item['price']:.2f}",
                        f"₹{item['total']:.2f}"
                    ])
                
                # Add subtotal row
                data.append(['', '', 'Subtotal:', f"₹{order['total_amount']:.2f}"])
                
                item_table = Table(data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
                item_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f9ff')),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(item_table)
                story.append(Spacer(1, 15))
                
                total_grand_total += order['total_amount']
        
        # Grand total
        grand_total_data = [['GRAND TOTAL:', f"₹{total_grand_total:.2f}"]]
        grand_total_table = Table(grand_total_data, colWidths=[5*inch, 2*inch])
        grand_total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(Spacer(1, 20))
        story.append(grand_total_table)

        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Thank you for your business!", styles['Normal']))
        story.append(Paragraph("Sahaayak - Connecting Communities", styles['Italic']))

        # Build PDF
        doc.build(story)
        conn.close()

        # Send file
        return send_file(temp_filename,
                 as_attachment=True,
                 download_name=f'sahaayak_receipt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                 mimetype='application/pdf')
        
    except ImportError:
        # If reportlab is not installed, create a simple text receipt
        flash('PDF generation not available. Please install reportlab library.', 'warning')
        return redirect(url_for('main.vendor_orders'))
    except Exception as e:
        flash(f'Error generating receipt: {str(e)}', 'error')
        return redirect(url_for('main.vendor_orders'))

@bp.route('/vendor/order-confirmation')
def vendor_order_confirmation():
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))

    order_ids = session.get('last_order_ids', [])
    if not order_ids:
        return redirect(url_for('main.vendor_orders'))

    delivery_address = session.get('last_delivery_address', 'Home, 123 Street Name, City - 400001, Maharashtra, India')
    payment_method = session.get('last_payment_method', 'cod')
    # Simple ETA: 2-3 days
    eta_text = '2-3 business days'

    return render_template('vendor_confirmation.html',
                           order_ids=order_ids,
                           delivery_address=delivery_address,
                           payment_method=payment_method,
                           eta_text=eta_text)

@bp.route('/vendor/orders')
def vendor_orders():
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))

    vendor_id = session['vendor_id']
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT o.id, o.total_amount, o.status, o.created_at as order_date, w.name as wholesaler_name
        FROM orders o
        JOIN wholesalers w ON o.wholesaler_id = w.id
        WHERE o.vendor_id = ?
        ORDER BY o.created_at DESC
    ''', (vendor_id,))
    orders_data = cursor.fetchall()

    orders = []
    for order_row in orders_data:
        order = dict(order_row)
        order['order_date'] = datetime.strptime(order['order_date'], '%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT oi.quantity, oi.price, oi.total, p.name as product_name, p.image_path
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order['id'],))
        order['items'] = [dict(item) for item in cursor.fetchall()]
        orders.append(order)

    cursor.execute('''
        SELECT
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
            COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_count,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
            COALESCE(SUM(total_amount), 0) as total_spent
        FROM orders
        WHERE vendor_id = ?
    ''', (vendor_id,))
    stats = cursor.fetchone()

    conn.close()

    return render_template('vendor_orders.html', orders=orders, stats=stats, lang=session.get('vendor_language', 'en'))


@bp.route('/vendor/order/<int:order_id>')
def vendor_order_detail(order_id):
    """Return rendered HTML fragment for an order's details (used by drawer)."""
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))

    vendor_id = session['vendor_id']
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM orders WHERE id = ? AND vendor_id = ?', (order_id, vendor_id))
    order_row = cursor.fetchone()
    if not order_row:
        conn.close()
        return "<p class='text-red-500'>Order not found or access denied.</p>", 404

    order = dict(order_row)
    try:
        order['order_date'] = datetime.strptime(order['created_at'], '%Y-%m-%d %H:%M:%S')
    except Exception:
        order['order_date'] = order.get('created_at')

    cursor.execute('''
        SELECT oi.quantity, oi.price, oi.total, p.name as product_name, p.image_path
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,))
    order['items'] = [dict(i) for i in cursor.fetchall()]
    # Fetch wholesaler name
    cursor.execute('SELECT name FROM wholesalers WHERE id = ?', (order['wholesaler_id'],))
    w = cursor.fetchone()
    order['wholesaler_name'] = w['name'] if w else 'Unknown'

    conn.close()
    return render_template('vendor_order_detail.html', order=order)


@bp.route('/vendor/upload-photo', methods=['POST'])
def upload_vendor_photo():
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401

    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Empty filename'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"vendor_{uuid.uuid4()}_{file.filename}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        full_path = os.path.join(upload_folder, filename)
        file.save(full_path)

        # Save relative path in DB
        rel_path = f"uploads/{filename}"
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('UPDATE vendors SET photo_path = ? WHERE id = ?', (rel_path, session['vendor_id']))
        conn.commit()
        conn.close()

        photo_url = url_for('static', filename=rel_path)
        return jsonify({'success': True, 'photo_url': photo_url})
    else:
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400


@bp.route('/vendor/category/<category_id>')
def vendor_category(category_id):
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))
    
    category_mapping = {
        'vegetables': 'Vegetables',
        'dry-ingredients': 'Dry Ingredients', 
        'dairy': 'Dairy Products',
        'breads': 'Bread & Bakery',
        'prepared': 'Ready-to-Eat',
        'oils-sauces': 'Oils & Condiments',
        'snacks': 'Snacks & Beverages',
        'spices': 'Spices & Condiments',
        'spreads': 'Spreads & Pantry',
        'packaging': 'Packaging',
        'grains': 'Grains & Cereals',
        'beverage': 'Snacks & Beverages',  # Map beverage to snacks for compatibility
        'desserts': 'Desserts',
        'seafood-meat': 'Seafood & Meat'
    }
    wholesaler_category = category_mapping.get(category_id, 'Produce')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.name, p.category, p.price, p.stock, p.image_path, w.name as wholesaler_name, w.location, w.trust_score
        FROM products p
        JOIN wholesalers w ON p.wholesaler_id = w.id
        WHERE p.category = ? AND w.is_approved = 1 AND p.stock > 0
        ORDER BY w.trust_score DESC, p.views DESC
    ''', (wholesaler_category,))
    products = cursor.fetchall()
    conn.close()
    
    category_display_names = {
        'vegetables': 'Fresh Vegetables',
        'dry-ingredients': 'Dry Ingredients & Staples', 
        'dairy': 'Dairy Products',
        'breads': 'Bread & Bakery Items',
        'prepared': 'Ready-to-Eat Meals',
        'oils-sauces': 'Oils & Condiments',
        'snacks': 'Snacks & Beverages',
        'spices': 'Spices & Seasonings',
        'spreads': 'Spreads & Pantry Items',
        'packaging': 'Packaging & Others',
        'grains': 'Grains & Cereals',
        'beverage': 'Beverage Supplies',
        'desserts': 'Desserts & Sweets',
        'seafood-meat': 'Seafood & Meat'
    }
    category_name = category_display_names.get(category_id, 'Products')
    
    return render_template('vendor_category_listing.html', 
                           products=products, 
                           category_name=category_name, 
                           category_id=category_id)

# NEW ROUTE FOR VIEWING A WHOLESALER'S PRODUCTS
@bp.route('/vendor/wholesaler/<int:wholesaler_id>')
def wholesaler_products_page(wholesaler_id):
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch wholesaler details
    cursor.execute('SELECT * FROM wholesalers WHERE id = ?', (wholesaler_id,))
    wholesaler = cursor.fetchone()

    # Fetch all products for this wholesaler
    cursor.execute('''
        SELECT *, (price * 1.25) as original_price FROM products 
        WHERE wholesaler_id = ? AND stock > 0 
        ORDER BY name
    ''', (wholesaler_id,))
    products = cursor.fetchall()

    conn.close()

    if not wholesaler:
        flash('Wholesaler not found.', 'error')
        return redirect(url_for('main.vendor_dashboard'))

    return render_template('wholesaler_products_page.html', wholesaler=wholesaler, products=products)

@bp.route('/vendor/search')
def vendor_search():
    if 'vendor_id' not in session:
        return redirect(url_for('main.vendor_login'))
    
    query = request.args.get('q', '').strip()
    
    # 1. Map common synonyms to (include_pattern, exclude_pattern) for strict ground-level matching
    SYNONYM_MAP = {
        'aloo': ('Potato (Aloo)', None),
        'aalu': ('Potato (Aloo)', None),
        'potato': ('Potato (Aloo)', 'Sweet'),
        'बटाटा': ('Potato (Aloo)', None),
        'आलू': ('Potato (Aloo)', None),
        
        'shakarkand': ('Sweet Potato', None),
        'shikark': ('Sweet Potato', None),
        'shakarkhan': ('Sweet Potato', None),
        'sweet potato': ('Sweet Potato', None),
        'शकरकंद': ('Sweet Potato', None),
        
        'onion': ('Onion (Pyaz)', None),
        'pyaz': ('Onion (Pyaz)', None),
        'pyaaz': ('Onion (Pyaz)', None),
        'kanda': ('Onion (Pyaz)', None),
        'कांदा': ('Onion (Pyaz)', None),
        'प्याज': ('Onion (Pyaz)', None),
        
        'tomato': ('Tomato (Tamatar)', None),
        'tamatar': ('Tomato (Tamatar)', None),
        'टमाटर': ('Tomato (Tamatar)', None),
        'टोमॅटो': ('Tomato (Tamatar)', None),
        
        'garlic': ('Garlic (Lahsun)', None),
        'lahsun': ('Garlic (Lahsun)', None),
        'lasun': ('Garlic (Lahsun)', None),
        'lehsun': ('Garlic (Lahsun)', None),
        'लसूण': ('Garlic (Lahsun)', None),
        'लहसुन': ('Garlic (Lahsun)', None),
        
        'ginger': ('Ginger (Adrak)', None),
        'adrak': ('Ginger (Adrak)', None),
        'आले': ('Ginger (Adrak)', None),
        'अदरक': ('Ginger (Adrak)', None),
        
        'capsicum': ('Capsicum (Shimla Mirch)', None),
        'shimla': ('Capsicum (Shimla Mirch)', None),
        'shimlamirch': ('Capsicum (Shimla Mirch)', None),
        'ढोबळी मिरची': ('Capsicum (Shimla Mirch)', None),
        'शिमला मिर्च': ('Capsicum (Shimla Mirch)', None),
        
        'okra': ('Lady Finger (Bhindi)', None),
        'bhindi': ('Lady Finger (Bhindi)', None),
        'bhendi': ('Lady Finger (Bhindi)', None),
        'lady finger': ('Lady Finger (Bhindi)', None),
        'ladyfinger': ('Lady Finger (Bhindi)', None),
        'भेंडी': ('Lady Finger (Bhindi)', None),
        'भिंडी': ('Lady Finger (Bhindi)', None),
        
        'spinach': ('Spinach (Palak)', None),
        'palak': ('Spinach (Palak)', None),
        'पालक': ('Spinach (Palak)', None),
        
        'fenugreek': ('Fenugreek (Methi)', None),
        'methi': ('Fenugreek (Methi)', None),
        'मेथी': ('Fenugreek (Methi)', None),
        
        'cucumber': ('Cucumber (Kheera)', None),
        'kheera': ('Cucumber (Kheera)', None),
        'काकडी': ('Cucumber (Kheera)', None),
        'खीरा': ('Cucumber (Kheera)', None),
        
        'peas': ('Green Peas (Matar)', None),
        'matar': ('Green Peas (Matar)', None),
        'मटार': ('Green Peas (Matar)', None),
        'मटर': ('Green Peas (Matar)', None),
    }

    if query:
        # Standardize Hindi/Marathi digits to English
        hindi_to_eng = {
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
        }
        cleaned_query = query.lower().strip()
        for h, e in hindi_to_eng.items():
            cleaned_query = cleaned_query.replace(h, e)

        # 2. Check for voice/command pattern: <quantity> [unit] <product>
        import re
        pattern = r'^(\d+)\s*(kg|kilo|kilos|gram|grams|gm|gms|packet|packets|pkt|pkts|किळो|किलो|केजी|ग्राम|पैकेट|पॅकेट|लीटर|litre|liter|ltr|l|ml)?s?\.?\s+(.+)$'
        match = re.match(pattern, cleaned_query)
        if match:
            try:
                quantity = int(match.group(1))
            except ValueError:
                quantity = 1
            user_unit = match.group(2)
            product_term = match.group(3).strip()

            # Find the best matching approved product in stock
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            query_conditions = []
            query_params = []
            
            if product_term in SYNONYM_MAP:
                inc, exc = SYNONYM_MAP[product_term]
                query_conditions.append("p.name LIKE ?")
                query_params.append(f"%{inc}%")
                if exc:
                    query_conditions.append("p.name NOT LIKE ?")
                    query_params.append(f"%{exc}%")
            else:
                query_conditions.append("p.name LIKE ?")
                query_params.append(f"%{product_term}%")

            cursor.execute(f'''
                SELECT p.id, p.name, p.stock, w.name as wholesaler_name 
                FROM products p 
                JOIN wholesalers w ON p.wholesaler_id = w.id 
                WHERE ({' AND '.join(query_conditions)}) AND w.is_approved = 1 AND p.stock > 0
                ORDER BY w.trust_score DESC, p.views DESC
                LIMIT 1
            ''', tuple(query_params))
            product = cursor.fetchone()

            if product:
                product_id, name, stock, wholesaler_name = product
                
                # Scale quantity based on packaging size if necessary (e.g., "200 g Paneer" -> 1 unit of Paneer (200g))
                import math
                scaled_qty = quantity
                if user_unit:
                    user_unit_norm = user_unit.lower().strip()
                    if user_unit_norm in ['kg', 'kilo', 'kilos', 'किळो', 'किलो', 'केजी']:
                        u_val = quantity * 1000
                        u_unit = 'g'
                    elif user_unit_norm in ['g', 'gm', 'gms', 'gram', 'grams', 'ग्राम']:
                        u_val = quantity
                        u_unit = 'g'
                    elif user_unit_norm in ['l', 'litre', 'liter', 'ltr', 'लीटर']:
                        u_val = quantity * 1000
                        u_unit = 'ml'
                    elif user_unit_norm in ['ml']:
                        u_val = quantity
                        u_unit = 'ml'
                    else:
                        u_unit = None
                        
                    if u_unit:
                        # Extract product unit from name e.g., "Paneer (200g)" or "Milk (1L)"
                        p_match = re.search(r'\((?:(\d+)\s*(g|gm|gms|kg|l|litre|liter|ltr|ml))\)', name, re.IGNORECASE)
                        if p_match:
                            p_qty = int(p_match.group(1))
                            p_unit = p_match.group(2).lower().strip()
                            
                            if p_unit in ['kg']:
                                p_val = p_qty * 1000
                                p_type = 'g'
                            elif p_unit in ['g', 'gm', 'gms']:
                                p_val = p_qty
                                p_type = 'g'
                            elif p_unit in ['l', 'litre', 'liter', 'ltr']:
                                p_val = p_qty * 1000
                                p_type = 'ml'
                            elif p_unit in ['ml']:
                                p_val = p_qty
                                p_type = 'ml'
                            else:
                                p_type = None
                                
                            if p_type == u_unit:
                                # Scale quantity to number of packages, rounded up
                                scaled_qty = max(1, math.ceil(u_val / p_val))

                actual_qty = min(scaled_qty, stock)
                
                # Update vendor cart
                cart = session.get('vendor_cart', {})
                product_id_str = str(product_id)
                current_qty = cart.get(product_id_str, 0)
                cart[product_id_str] = current_qty + actual_qty
                session['vendor_cart'] = cart
                session.modified = True
                conn.close()

                if actual_qty < scaled_qty:
                    flash(f"Added {actual_qty} units of {name} (from {wholesaler_name}) to your cart. Capped from {scaled_qty} units due to stock limits.", "warning")
                else:
                    flash(f"Added {actual_qty} units of {name} (from {wholesaler_name}) directly to your cart!", "success")
                return redirect(url_for('main.vendor_cart'))
            else:
                conn.close()
                flash(f"Could not auto-add '{product_term}' to cart. Product not found or out of stock.", "danger")
                # Fallback to search results for just the product term
                query = product_term

        # 3. Standard Search with Synonym Expansion
        cleaned_search = query.lower().strip()
        for h, e in hindi_to_eng.items():
            cleaned_search = cleaned_search.replace(h, e)

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        query_conditions = []
        query_params = []
        
        if cleaned_search in SYNONYM_MAP:
            inc, exc = SYNONYM_MAP[cleaned_search]
            query_conditions.append("p.name LIKE ?")
            query_params.append(f"%{inc}%")
            if exc:
                query_conditions.append("p.name NOT LIKE ?")
                query_params.append(f"%{exc}%")
        else:
            query_conditions.append("p.name LIKE ?")
            query_params.append(f"%{query}%")

        cursor.execute(f'''
            SELECT p.*, w.name as wholesaler_name, w.location, w.trust_score 
            FROM products p 
            JOIN wholesalers w ON p.wholesaler_id = w.id 
            WHERE ({' AND '.join(query_conditions)}) AND w.is_approved = 1 AND p.stock > 0
            ORDER BY w.trust_score DESC, p.views DESC
        ''', tuple(query_params))
        products = cursor.fetchall()
        conn.close()
    else:
        products = []
    
    return render_template('vendor_search_results.html', 
                           products=products, 
                           query=query,
                           lang=session.get('vendor_language', 'en'))

# --- API Routes ---

# NEW API ROUTE FOR SORTING WHOLESALERS
@bp.route('/api/sort-wholesalers', methods=['POST'])
def sort_wholesalers():
    if 'vendor_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    sort_by = request.get_json().get('sort_by', 'rating')

    order_clause = "ORDER BY w.trust_score DESC" # Default to rating/trust score
    if sort_by == 'price':
        # This query calculates the average price of products for each wholesaler and sorts by it
        order_clause = "ORDER BY avg_price ASC"

    query = f"""
        SELECT 
            w.id,
            w.name,
            w.location,
            w.phone,
            w.trust_score,
            w.profile_photo,
            (SELECT GROUP_CONCAT(DISTINCT p.category) FROM products p WHERE p.wholesaler_id = w.id LIMIT 3) as specialties,
            (SELECT COUNT(r.id) FROM reviews r WHERE r.wholesaler_id = w.id) as review_count,
            (SELECT AVG(p.price) FROM products p WHERE p.wholesaler_id = w.id) as avg_price
        FROM wholesalers w
        WHERE w.is_approved = 1
        {order_clause}
        LIMIT 4
    """

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    wholesalers = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(wholesalers)

# UPDATED API ROUTE FOR FILTERING BUDGET ITEMS
@bp.route('/api/filter-products', methods=['POST'])
def filter_products():
    if 'vendor_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    filters = request.get_json()
    max_budget = filters.get('maxBudget')
    category = filters.get('category')
    sort_by = filters.get('sortBy')
    limit = filters.get('limit') # New: Get the limit parameter

    query = """
        SELECT 
            p.*, 
            w.name as wholesaler_name, 
            w.trust_score,
            (p.price * 1.25) as original_price
        FROM products p
        JOIN wholesalers w ON p.wholesaler_id = w.id
        WHERE w.is_approved = 1 AND p.stock > 0
    """
    params = []

    if max_budget:
        query += " AND p.price <= ?"
        params.append(float(max_budget))

    if category and category != 'All Categories':
        query += " AND p.category = ?"
        params.append(category)

    if sort_by == 'Highest Discount':
        query += " ORDER BY (original_price - p.price) DESC"
    elif sort_by == 'Price Low to High':
        query += " ORDER BY p.price ASC"
    elif sort_by == 'Price High to Low':
        query += " ORDER BY p.price DESC"

    # New: Add the LIMIT clause if a limit is provided
    if limit:
        query += " LIMIT ?"
        params.append(int(limit))

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(products)

@bp.route('/api/update-stock', methods=['POST'])
def update_stock():
    if 'wholesaler_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    new_stock = data.get('stock')
    status = 'In Stock' if new_stock > 50 else 'Low Stock' if new_stock > 0 else 'Out of Stock'
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET stock = ?, status = ? WHERE id = ? AND wholesaler_id = ?', 
                   (new_stock, status, product_id, session['wholesaler_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'status': status})

@bp.route('/api/update-order-status', methods=['POST'])
def update_order_status():
    if 'wholesaler_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    order_id = data.get('order_id')
    new_status = data.get('status')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ? WHERE id = ? AND wholesaler_id = ?', 
                   (new_status, order_id, session['wholesaler_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@bp.route('/api/delete-product', methods=['POST'])
def delete_product():
    if 'wholesaler_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    product_id = request.get_json().get('product_id')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT image_path FROM products WHERE id = ? AND wholesaler_id = ?', 
                   (product_id, session['wholesaler_id']))
    result = cursor.fetchone()
    
    if result and result[0]:
        # Path is relative like 'uploads/filename.jpg', so we join it with 'my_app/static'
        image_path = os.path.join(current_app.static_folder, result[0].replace('/', os.sep))
        if os.path.exists(image_path):
            os.remove(image_path)
    
    cursor.execute('DELETE FROM products WHERE id = ? AND wholesaler_id = ?', 
                   (product_id, session['wholesaler_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@bp.route('/api/reply-review', methods=['POST'])
def reply_review():
    if 'wholesaler_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    review_id = data.get('review_id')
    reply_text = data.get('reply')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE reviews SET reply = ? WHERE id = ? AND wholesaler_id = ?', 
                   (reply_text, review_id, session['wholesaler_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@bp.route('/api/upload-profile-photo', methods=['POST'])
def upload_profile_photo():
    if 'wholesaler_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'profile_photo' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['profile_photo']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type or no file selected'}), 400
    
    filename = secure_filename(f"profile_{session['wholesaler_id']}_{uuid.uuid4()}_{file.filename}")
    relative_path = f"uploads/{filename}"
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(full_path)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT profile_photo FROM wholesalers WHERE id = ?', (session['wholesaler_id'],))
    old_photo = cursor.fetchone()
    
    cursor.execute('UPDATE wholesalers SET profile_photo = ? WHERE id = ?', 
                   (relative_path, session['wholesaler_id']))
    conn.commit()
    conn.close()
    
    if old_photo and old_photo[0]:
        old_path = os.path.join(current_app.static_folder, old_photo[0].replace('/', os.sep))
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass
    
    return jsonify({
        'success': True, 
        'photo_url': url_for('static', filename=relative_path, _external=True)
    })

@bp.route('/wholesaler/change-password', methods=['POST'])
def change_password():
    if 'wholesaler_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT password FROM wholesalers WHERE id = ?', (session['wholesaler_id'],))
    stored_password = cursor.fetchone()
    
    if not stored_password or stored_password[0] != current_password:
        conn.close()
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    cursor.execute('UPDATE wholesalers SET password = ? WHERE id = ?', 
                   (new_password, session['wholesaler_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Password changed successfully'})

# CORRECTED AND IMPROVED THIS FUNCTION
@bp.route('/vendor/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first', 'redirect': url_for('main.vendor_login')})

    product_id = request.form.get('product_id')
    try:
        quantity = int(request.form.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
        
    if not product_id or quantity < 1:
        return jsonify({'success': False, 'message': 'Invalid product or quantity'})

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT stock FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    
    if not product:
        conn.close()
        return jsonify({'success': False, 'message': 'Product not found'})
        
    stock = product[0]
    
    cart = session.get('vendor_cart', {})
    product_id_str = str(product_id)
    
    current_quantity_in_cart = cart.get(product_id_str, 0)
    
    if stock < current_quantity_in_cart + quantity:
        conn.close()
        return jsonify({'success': False, 'message': f'Not enough stock. Only {stock} available.'})

    cart[product_id_str] = current_quantity_in_cart + quantity
    session['vendor_cart'] = cart
    session.modified = True
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Item added to cart',
        'cart_count': sum(cart.values())
    })

# NEW ROUTE FOR REORDERING
@bp.route('/vendor/reorder', methods=['POST'])
def reorder_item():
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first', 'redirect': url_for('main.vendor_login')})

    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    # This logic is identical to add_to_cart, so we can reuse it
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT stock FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    
    if not product:
        conn.close()
        return jsonify({'success': False, 'message': 'Product not found'})
        
    stock = product[0]
    
    cart = session.get('vendor_cart', {})
    product_id_str = str(product_id)
    
    current_quantity_in_cart = cart.get(product_id_str, 0)
    
    if stock < current_quantity_in_cart + quantity:
        conn.close()
        return jsonify({'success': False, 'message': f'Not enough stock. Only {stock} available.'})

    cart[product_id_str] = current_quantity_in_cart + quantity
    session['vendor_cart'] = cart
    session.modified = True
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Item reordered and added to cart',
        'cart_count': sum(cart.values())
    })


@bp.route('/vendor/remove-from-cart', methods=['POST'])
def remove_from_cart():
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = request.form.get('product_id')
    cart = session.get('vendor_cart', {})
    if product_id in cart:
        del cart[product_id]
        session['vendor_cart'] = cart
        session.modified = True
    
    return jsonify({
        'success': True,
        'cart_count': sum(cart.values())
    })

@bp.route('/vendor/update-cart', methods=['POST'])
def update_cart():
    """Updates the quantity of a single item in the cart."""
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    product_id_str = request.form.get('product_id')
    quantity_str = request.form.get('quantity')

    if not product_id_str or not quantity_str:
        return jsonify({'success': False, 'message': 'Missing data'})

    try:
        quantity = int(quantity_str)
        if quantity < 1:
            # If quantity is less than 1, remove the item
            return remove_from_cart()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid quantity'})

    cart = session.get('vendor_cart', {})
    
    # Update the quantity for the specific product
    if product_id_str in cart:
        cart[product_id_str] = quantity
    
    session['vendor_cart'] = cart
    session.modified = True
    
    # Calculate updated totals
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    total_items = 0
    grand_total = 0
    item_subtotal = 0
    
    # Get the price of the updated product for item subtotal
    cursor.execute('SELECT price FROM products WHERE id = ?', (product_id_str,))
    updated_product = cursor.fetchone()
    if updated_product:
        item_subtotal = updated_product[0] * quantity
    
    for product_id, quantity_in_cart in cart.items():
        cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        if product:
            total_items += quantity_in_cart
            grand_total += product[0] * quantity_in_cart
    
    conn.close()
    
    return jsonify({
        'success': True,
        'totals': {
            'total_items': total_items,
            'grand_total': grand_total,
            'item_subtotal': item_subtotal,
            'updated_product_id': product_id_str
        }
    })

@bp.route('/vendor/clear-cart', methods=['POST'])
def clear_cart():
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    session['vendor_cart'] = {}
    session.modified = True
    
    return jsonify({'success': True})

@bp.route('/vendor/get-cart-count')
def get_cart_count():
    if 'vendor_id' not in session:
        return jsonify({'count': 0, 'total': 0})
    
    cart = session.get('vendor_cart', {})
    count = sum(cart.values())
    
    total = 0
    if cart:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        for product_id, quantity in cart.items():
            cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
            result = cursor.fetchone()
            if result:
                total += result[0] * quantity
        conn.close()
    
    return jsonify({'count': count, 'total': round(total, 2)})

# NEW CART SYNC ROUTES FOR FRONTEND/BACKEND INTEGRATION
@bp.route('/vendor/cart/sync', methods=['POST'])
def sync_cart():
    """Sync frontend cart with backend session"""
    if 'vendor_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        frontend_cart = request.json.get('cart', [])
        
        # Convert frontend cart format to backend session format
        backend_cart = {}
        for item in frontend_cart:
            backend_cart[str(item['id'])] = item['quantity']
        
        # Update session
        session['vendor_cart'] = backend_cart
        
        return jsonify({'success': True, 'synced_items': len(backend_cart)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/vendor/cart/get', methods=['GET'])
def get_cart():
    """Get full cart data with product details"""
    if 'vendor_id' not in session:
        return jsonify({'cart': [], 'count': 0, 'total': 0})
    
    cart = session.get('vendor_cart', {})
    cart_items = []
    total = 0
    
    if cart:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        for product_id, quantity in cart.items():
            cursor.execute('SELECT id, name, price, image_path FROM products WHERE id = ?', (product_id,))
            result = cursor.fetchone()
            if result:
                item_total = result[2] * quantity
                total += item_total
                cart_items.append({
                    'id': result[0],
                    'name': result[1],
                    'price': result[2],
                    'image_path': result[3],
                    'quantity': quantity,
                    'total': round(item_total, 2)
                })
        conn.close()
    
    return jsonify({
        'cart': cart_items,
        'count': sum(cart.values()),
        'total': round(total, 2)
    })

@bp.route('/api/test-vendor-creds')
def test_vendor_creds():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT phone, password FROM vendors WHERE is_approved = 1 LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'phone': row[0], 'password': row[1]}
    else:
        return {'error': 'No approved vendor found'}, 404

# NEW AI-POWERED ROUTE USING 9ROUTER
# NEW AI-POWERED ROUTE USING 9ROUTER WITH MULTI-MODEL FALLBACK
@bp.route('/api/ask-ai', methods=['POST'])
def ask_ai():
    if 'vendor_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    product_name = data.get('product_name')

    if not product_name:
        return jsonify({'error': 'Product name is required'}), 400

    # Construct prompt
    prompt = f"""
    Generate market insights for a street vendor in India for the product '{product_name}'.
    Follow these rules STRICTLY:
    1. Provide EXACTLY 5 points, each on a new line: Price, Trend, Demand, Profit, Tip.
    2. Use very short, direct phrases. No filler words or long sentences.
    3. For "Price", give a realistic price range in INR (e.g., Rs. 20-30/kg).
    4. For "Profit", give a realistic margin range (e.g., 20-35% margin).
    5. For "Tip", provide one short, actionable piece of advice.
    6. Do NOT add any introductory text, concluding text, explanations, or warnings.

    Example for "Potato":
    Price: Rs. 15-25/kg (check local mandi)
    Trend: Seasonal fluctuations expected
    Demand: High, especially evenings
    Profit: 20-35% margin possible
    Tip: Offer boiled/fried options
    """

    api_key = current_app.config.get('NINEROUTER_API_KEY')
    api_base = current_app.config.get('NINEROUTER_API_BASE', 'https://api.9router.com/v1')
    models = current_app.config.get('NINEROUTER_MODELS_CHATBOT') or [current_app.config.get('NINEROUTER_MODEL_DEFAULT', 'gpt-4o-mini')]

    url = f"{api_base.rstrip('/')}/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    errors = []
    for model_name in models:
        try:
            payload = {
                'model': model_name,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            # 9router Proxy Bug Workaround: Clean trailing SSE data and handle empty responses
            raw_text = response.text
            if not isinstance(raw_text, str):
                result_json = response.json()
            else:
                raw_text = raw_text.strip()
                if "data: [DONE]" in raw_text:
                    raw_text = raw_text.split("data: [DONE]")[0].strip()
                if not raw_text:
                    raise ValueError("Received empty response from proxy.")
                result_json = json.loads(raw_text)
                
            ai_response = result_json['choices'][0]['message']['content']
            return jsonify({'response': ai_response})
        except Exception as e:
            errors.append(f"Model '{model_name}' failed: {str(e)}")

    return jsonify({'error': f"AI Insights temporarily unavailable. Errors: {'; '.join(errors)}"}), 500

# MULTILINGUAL VOICE CHATBOT ROUTE USING 9ROUTER WITH MULTI-MODEL FALLBACK
@bp.route('/api/ask-chatbot', methods=['POST'])
def ask_chatbot():
    if 'vendor_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    query = data.get('query')
    lang = data.get('lang', 'en')  # 'en', 'hi', or 'mr'
    history = data.get('history', [])  # list of {"role": "user"/"assistant", "content": "..."}

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    model_config_keys = {
        'en': 'NINEROUTER_MODELS_ENGLISH',
        'hi': 'NINEROUTER_MODELS_HINDI',
        'mr': 'NINEROUTER_MODELS_MARATHI'
    }
    
    config_key = model_config_keys.get(lang, 'NINEROUTER_MODELS_CHATBOT')
    models = current_app.config.get(config_key) or current_app.config.get('NINEROUTER_MODELS_CHATBOT') or ['gpt-4o-mini']
    
    api_key = current_app.config.get('NINEROUTER_API_KEY')
    api_base = current_app.config.get('NINEROUTER_API_BASE', 'https://api.9router.com/v1')

    # Localized system instructions optimized for Indian street vendors/wholesalers
    system_prompts = {
        'en': "You are Sahaayak, a friendly and helpful AI market assistant for street vendors and wholesalers in India. "
              "Respond in English. Keep answers brief (max 3-4 sentences), practical, and focus on helping their vendor business "
              "(e.g., pricing, demand, storage tips, customer relations).",
        'hi': "आप सहायक (Sahaayak) हैं, जो भारत में रेहड़ी-पटरी वालों और थोक विक्रेताओं के लिए एक मददगार AI सहायक हैं। "
              "कृपया हिंदी में उत्तर दें (देवनागरी लिपि का प्रयोग करें)। उत्तर को संक्षिप्त (अधिकतम 3-4 वाक्य) और व्यावहारिक रखें। "
              "सरल और बोलचाल की भाषा का प्रयोग करें जो आसानी से समझ में आ सके।",
        'mr': "तुम्ही सहाय्यक (Sahaayak) आहात, जे भारतातील विक्रेते आणि घाऊक व्यापाऱ्यांसाठी एक मदतनीस AI सहाय्यक आहे. "
              "कृपया मराठीत उत्तर द्या (देवनागरी लिपी वापरा). उत्तर संक्षिप्त (कमाल ३-४ वाक्ये) और व्यावहारिक ठेवा. "
              "सोप्या आणि रोजच्या बोलचालीतील शब्दांचा वापर करा."
    }
    
    system_prompt = system_prompts.get(lang, system_prompts['en'])

    messages = [{'role': 'system', 'content': system_prompt}]
    
    for msg in history:
        messages.append({'role': msg.get('role'), 'content': msg.get('content')})
        
    messages.append({'role': 'user', 'content': query})

    url = f"{api_base.rstrip('/')}/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    errors = []
    for model_name in models:
        try:
            payload = {
                'model': model_name,
                'messages': messages
            }
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            # 9router Proxy Bug Workaround: Clean trailing SSE data and handle empty responses
            raw_text = response.text
            if not isinstance(raw_text, str):
                result_json = response.json()
            else:
                raw_text = raw_text.strip()
                if "data: [DONE]" in raw_text:
                    raw_text = raw_text.split("data: [DONE]")[0].strip()
                if not raw_text:
                    raise ValueError("Received empty response from proxy.")
                result_json = json.loads(raw_text)
                
            chatbot_response = result_json['choices'][0]['message']['content']
            return jsonify({'response': chatbot_response})
        except Exception as e:
            errors.append(f"Model '{model_name}' failed: {str(e)}")

    fallbacks = {
        'en': "I'm sorry, I'm having trouble connecting to the network right now. Please try again in a moment.",
        'hi': "क्षमा करें, मुझे इस समय नेटवर्क से जुड़ने में समस्या हो रही है। कृपया थोड़ी देर बाद पुनः प्रयास करें।",
        'mr': "क्षमस्व, मला सध्या नेटवर्कशी जोडण्यात अडचण येत आहे. कृपया थोड्या वेळाने पुन्हा प्रयत्न करा."
    }
    return jsonify({'response': fallbacks.get(lang, fallbacks['en']), 'error': f"All chatbot models failed: {'; '.join(errors)}"}), 500

# VOICE TRANSCRIPTION ENDPOINT USING 9ROUTER (GROQ/WHISPER MODELS)
@bp.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    if 'vendor_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['file']
    lang = request.form.get('lang', 'en')  # selected language preference

    # Mapping of lang code for Whisper 'language' parameter
    lang_mapping = {
        'en': 'en',
        'hi': 'hi',
        'mr': 'mr'
    }
    whisper_lang = lang_mapping.get(lang)

    api_key = current_app.config.get('NINEROUTER_API_KEY')
    api_base = current_app.config.get('NINEROUTER_API_BASE', 'https://api.9router.com/v1')
    models = current_app.config.get('NINEROUTER_MODELS_VOICE') or ['groq/whisper-large-v3', 'whisper-large-v3', 'openai/whisper-1']

    url = f"{api_base.rstrip('/')}/audio/transcriptions"
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    errors = []
    audio_data = audio_file.read()

    for model_name in models:
        try:
            files = {
                'file': ('audio.wav', audio_data, audio_file.content_type or 'audio/wav')
            }
            data = {
                'model': model_name
            }
            if whisper_lang:
                data['language'] = whisper_lang

            response = requests.post(url, files=files, data=data, headers=headers, timeout=20)
            if response.status_code == 200:
                result_json = response.json()
                transcript = result_json.get('text', '').strip()
                if transcript:
                    return jsonify({'text': transcript})
                else:
                    errors.append(f"Model '{model_name}' returned empty transcription text")
            else:
                errors.append(f"Model '{model_name}' failed with status {response.status_code}: {response.text}")
        except Exception as e:
            errors.append(f"Model '{model_name}' request error: {str(e)}")

    return jsonify({
        'error': 'Speech transcription failed across all fallback models.',
        'details': errors
    }), 500

# NEW ROUTE FOR SUBMITTING A DONATION
@bp.route('/api/submit-donation', methods=['POST'])
def submit_donation():
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first.'}), 401

    vendor_id = session['vendor_id']
    data = request.get_json()

    food_description = data.get('food_description')
    quantity = data.get('quantity')
    pickup_address = data.get('pickup_address')
    pickup_time = data.get('pickup_time')

    if not all([food_description, quantity, pickup_address, pickup_time]):
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO donations (vendor_id, food_description, quantity, pickup_address, pickup_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (vendor_id, food_description, quantity, pickup_address, pickup_time))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Donation request submitted successfully! We will contact you shortly.'})

# --- API Routes for Payment Methods ---

@bp.route('/api/payment-methods/add', methods=['POST'])
def add_payment_method():
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.json
    method_type = data.get('method_type')
    details_dict = data.get('details')
    
    if not method_type or not details_dict:
        return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
    details_json = json.dumps(details_dict)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vendor_payment_methods (vendor_id, method_type, details) VALUES (?, ?, ?)",
        (session['vendor_id'], method_type, details_json)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'new_method_id': new_id})

@bp.route('/api/payment-methods/delete', methods=['POST'])
def delete_payment_method():
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
    method_id = request.json.get('method_id')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM vendor_payment_methods WHERE id = ? AND vendor_id = ?",
        (method_id, session['vendor_id'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@bp.route('/api/payment-methods/set-default', methods=['POST'])
def set_default_payment_method():
    if 'vendor_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
    method_id = request.json.get('method_id')
    vendor_id = session['vendor_id']
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # First, unset any other default for this vendor
    cursor.execute("UPDATE vendor_payment_methods SET is_default = 0 WHERE vendor_id = ?", (vendor_id,))
    # Then, set the new default
    cursor.execute("UPDATE vendor_payment_methods SET is_default = 1 WHERE id = ? AND vendor_id = ?", (method_id, vendor_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@bp.route('/api/wholesaler/<int:wholesaler_id>/filter-products', methods=['POST'])
def filter_wholesaler_products(wholesaler_id):
    if 'vendor_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    filters = request.get_json()
    category = filters.get('category')
    sort_by = filters.get('sortBy')
    
    # Base query
    query = """
        SELECT id, name, category, price, stock, image_path, status,
               (price * 1.25) as original_price 
        FROM products
        WHERE wholesaler_id = ? AND stock > 0
    """
    params = [wholesaler_id]

    # Add category filter if specified
    if category and category != 'All Categories':
        query += " AND category = ?"
        params.append(category)

    # Add sorting logic
    if sort_by == 'Price: Low to High':
        query += " ORDER BY price ASC"
    elif sort_by == 'Price: High to Low':
        query += " ORDER BY price DESC"
    else: # Default sort (e.g., by name or relevance)
        query += " ORDER BY name ASC"

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(products)

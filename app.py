from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from database import get_db_connection, init_db

app = Flask(__name__)
CORS(app)

# Ensure database is initialized
init_db()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('assets', path)

# --- API Endpoints ---

# Products API
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, price, old_price, image, category, badge, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['price'], data.get('oldPrice'), data['image'], data['category'], data.get('badge'), data.get('stock', 100)))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": new_id, "message": "Product added successfully"}), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    conn = get_db_connection()
    conn.execute('''
        UPDATE products 
        SET name = ?, price = ?, old_price = ?, image = ?, category = ?, badge = ?, stock = ?
        WHERE id = ?
    ''', (data['name'], data['price'], data.get('oldPrice'), data['image'], data['category'], data.get('badge'), data.get('stock', 100), id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product updated successfully"})

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product deleted successfully"})

# Auth API
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        ''', (data['name'], data['email'], data['password']))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already exists"}), 400
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    
    # Check if email exists
    user_exists = conn.execute('SELECT * FROM users WHERE email = ?', (data['email'],)).fetchone()
    if not user_exists:
        conn.close()
        return jsonify({"message": "Tài khoản chưa được đăng ký!"}), 401
        
    # Check if password is correct
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                        (data['email'], data['password'])).fetchone()
    conn.close()
    
    if user:
        return jsonify(dict(user))
    return jsonify({"message": "Mật khẩu không chính xác!"}), 401

# Orders API
@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return jsonify([dict(o) for o in orders])

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (user_email, customer_name, customer_phone, customer_address, payment_method, total_price, items)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('user_email'), data['name'], data['phone'], data['address'], data['paymentMethod'], data['total'], json.dumps(data['items'])))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": order_id, "message": "Order created successfully"}), 201

@app.route('/api/user/orders', methods=['GET'])
def get_user_orders():
    email = request.args.get('email')
    if not email:
        return jsonify([]), 400
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE user_email = ? ORDER BY created_at DESC', (email,)).fetchall()
    conn.close()
    return jsonify([dict(o) for o in orders])

# Reviews API
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    conn = get_db_connection()
    reviews = conn.execute('''
        SELECT r.*, p.name as product_name 
        FROM reviews r 
        LEFT JOIN products p ON r.product_id = p.id
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in reviews])

@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reviews (product_id, user_name, rating, comment)
        VALUES (?, ?, ?, ?)
    ''', (data['product_id'], data['name'], data['rating'], data['comment']))
    conn.commit()
    rev_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": rev_id, "message": "Review added successfully"}), 201

@app.route('/api/reviews/<int:id>/reply', methods=['PUT'])
def reply_review(id):
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE reviews SET reply = ? WHERE id = ?', (data['reply'], id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Replied successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

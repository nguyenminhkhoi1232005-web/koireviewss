from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from database import get_db_connection, init_db, is_postgres

app = Flask(__name__)
CORS(app)

# Ensure database is initialized
init_db()

def row_to_dict(row, cursor=None):
    """Convert a database row to a dict (works for both SQLite Row and psycopg2 tuple)."""
    if row is None:
        return None
    if is_postgres():
        col_names = [desc[0] for desc in cursor.description]
        return dict(zip(col_names, row))
    else:
        return dict(row)

def rows_to_dicts(rows, cursor=None):
    if is_postgres():
        col_names = [desc[0] for desc in cursor.description]
        return [dict(zip(col_names, row)) for row in rows]
    else:
        return [dict(row) for row in rows]

def ph():
    """Return the correct SQL placeholder depending on the DB."""
    return '%s' if is_postgres() else '?'

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
    cur = conn.cursor()
    cur.execute('SELECT * FROM products')
    products = rows_to_dicts(cur.fetchall(), cur)
    cur.close()
    conn.close()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    p = ph()
    if is_postgres():
        cur.execute(f'''
            INSERT INTO products (name, price, old_price, image, category, badge, stock)
            VALUES ({p},{p},{p},{p},{p},{p},{p}) RETURNING id
        ''', (data['name'], data['price'], data.get('oldPrice'), data['image'], data['category'], data.get('badge'), data.get('stock', 100)))
        new_id = cur.fetchone()[0]
    else:
        cur.execute(f'''
            INSERT INTO products (name, price, old_price, image, category, badge, stock)
            VALUES ({p},{p},{p},{p},{p},{p},{p})
        ''', (data['name'], data['price'], data.get('oldPrice'), data['image'], data['category'], data.get('badge'), data.get('stock', 100)))
        new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Product added successfully"}), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    p = ph()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'''
        UPDATE products 
        SET name={p}, price={p}, old_price={p}, image={p}, category={p}, badge={p}, stock={p}
        WHERE id={p}
    ''', (data['name'], data['price'], data.get('oldPrice'), data['image'], data['category'], data.get('badge'), data.get('stock', 100), id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Product updated successfully"})

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    p = ph()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'DELETE FROM products WHERE id={p}', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Product deleted successfully"})

# Auth API
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    p = ph()
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f'INSERT INTO users (name, email, password) VALUES ({p},{p},{p})',
                    (data['name'], data['email'], data['password']))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception:
        conn.rollback()
        return jsonify({"message": "Email đã được sử dụng!"}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    p = ph()
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if email exists
    cur.execute(f'SELECT * FROM users WHERE email={p}', (data['email'],))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        conn.close()
        return jsonify({"message": "Tài khoản chưa được đăng ký!"}), 401

    # Check password
    cur.execute(f'SELECT * FROM users WHERE email={p} AND password={p}', (data['email'], data['password']))
    user_row = cur.fetchone()
    user = row_to_dict(user_row, cur)
    cur.close()
    conn.close()

    if user:
        return jsonify(user)
    return jsonify({"message": "Mật khẩu không chính xác!"}), 401

# Orders API
@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM orders')
    orders = rows_to_dicts(cur.fetchall(), cur)
    cur.close()
    conn.close()
    return jsonify(orders)

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    p = ph()
    conn = get_db_connection()
    cur = conn.cursor()
    if is_postgres():
        cur.execute(f'''
            INSERT INTO orders (user_email, customer_name, customer_phone, customer_address, payment_method, total_price, items)
            VALUES ({p},{p},{p},{p},{p},{p},{p}) RETURNING id
        ''', (data.get('user_email'), data['name'], data['phone'], data['address'], data['paymentMethod'], data['total'], json.dumps(data['items'])))
        order_id = cur.fetchone()[0]
    else:
        cur.execute(f'''
            INSERT INTO orders (user_email, customer_name, customer_phone, customer_address, payment_method, total_price, items)
            VALUES ({p},{p},{p},{p},{p},{p},{p})
        ''', (data.get('user_email'), data['name'], data['phone'], data['address'], data['paymentMethod'], data['total'], json.dumps(data['items'])))
        order_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": order_id, "message": "Order created successfully"}), 201

@app.route('/api/orders/<int:id>/status', methods=['PUT'])
def update_order_status(id):
    data = request.json
    status = data.get('status')
    if not status:
        return jsonify({"message": "Status is required"}), 400
    p = ph()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'UPDATE orders SET status={p} WHERE id={p}', (status, id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Order status updated successfully"})

@app.route('/api/user/orders', methods=['GET'])
def get_user_orders():
    email = request.args.get('email')
    if not email:
        return jsonify([]), 400
    p = ph()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM orders WHERE user_email={p} ORDER BY created_at DESC', (email,))
    orders = rows_to_dicts(cur.fetchall(), cur)
    cur.close()
    conn.close()
    return jsonify(orders)

# Reviews API
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    conn = get_db_connection()
    cur = conn.cursor()
    if is_postgres():
        cur.execute('''
            SELECT r.*, p.name as product_name 
            FROM reviews r LEFT JOIN products p ON r.product_id = p.id
        ''')
    else:
        cur.execute('''
            SELECT r.*, p.name as product_name 
            FROM reviews r LEFT JOIN products p ON r.product_id = p.id
        ''')
    reviews = rows_to_dicts(cur.fetchall(), cur)
    cur.close()
    conn.close()
    return jsonify(reviews)

@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    p = ph()
    conn = get_db_connection()
    cur = conn.cursor()
    if is_postgres():
        cur.execute(f'''
            INSERT INTO reviews (product_id, user_name, rating, comment) VALUES ({p},{p},{p},{p}) RETURNING id
        ''', (data['product_id'], data['name'], data['rating'], data['comment']))
        rev_id = cur.fetchone()[0]
    else:
        cur.execute(f'''
            INSERT INTO reviews (product_id, user_name, rating, comment) VALUES ({p},{p},{p},{p})
        ''', (data['product_id'], data['name'], data['rating'], data['comment']))
        rev_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": rev_id, "message": "Review added successfully"}), 201

@app.route('/api/reviews/<int:id>/reply', methods=['PUT'])
def reply_review(id):
    data = request.json
    p = ph()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'UPDATE reviews SET reply={p} WHERE id={p}', (data['reply'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Replied successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

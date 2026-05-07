import sqlite3
import os

DB_NAME = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')

    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            old_price INTEGER,
            image TEXT NOT NULL,
            category TEXT NOT NULL,
            badge TEXT
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            total_price INTEGER NOT NULL,
            status TEXT DEFAULT 'Đang xử lý',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            items TEXT NOT NULL
        )
    ''')

    # Check if products already exist
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        default_products = [
            ("iPhone 15 Pro Max 256GB - Titan Tự Nhiên", 32990000, 34990000, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Điện thoại", "Bán chạy"),
            ("Tai nghe Sony WH-1000XM5 - Wireless Noise Cancelling", 7490000, 8990000, "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Âm thanh", "Giảm giá"),
            ("MacBook Air M3 13 inch (8GB/256GB) - Space Gray", 27990000, 29990000, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Laptop", "Mới"),
            ("Apple Watch Ultra 2 - Dây Alpine Xanh", 21490000, 22990000, "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Đồng hồ", "Premium"),
            ("iPhone 15 Pro 128GB - Titan Xanh", 28490000, 29990000, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Điện thoại", "HOT"),
            ("Sony WH-CH720N - Tai nghe chồng ồn giá rẻ", 2990000, 3490000, "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Âm thanh", ""),
            ("MacBook Pro M3 Pro - 14 inch", 49990000, 52990000, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Laptop", "Pro"),
            ("iPad Pro M2 11 inch (Wifi + 5G)", 23990000, 25990000, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Máy tính bảng", "Đồ họa")
        ]
        cursor.executemany('INSERT INTO products (name, price, old_price, image, category, badge) VALUES (?, ?, ?, ?, ?, ?)', default_products)

    # Add default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('admin@koistore.com',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?)', ('Quản trị viên', 'admin@koistore.com', 'admin123', 1))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")

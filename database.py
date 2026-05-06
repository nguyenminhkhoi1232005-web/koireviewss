import sqlite3
import psycopg2
import psycopg2.extras
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        # Running on Render with PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        # Running locally with SQLite
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn

def is_postgres():
    return DATABASE_URL is not None

def init_db():
    if is_postgres():
        init_postgres()
    else:
        init_sqlite()

def init_postgres():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            old_price INTEGER,
            image TEXT NOT NULL,
            category TEXT NOT NULL,
            badge TEXT,
            stock INTEGER DEFAULT 100
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            product_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            reply TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_email TEXT,
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

    # Seed admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = %s', ('koireviewss@gmail.com',))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            'INSERT INTO users (name, email, password, is_admin) VALUES (%s, %s, %s, %s)',
            ('Quản trị viên', 'koireviewss@gmail.com', 'Mot23456Khoi@', True)
        )

    # Seed products
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        default_products = [
            ("iPhone 15 Pro Max 256GB - Titan Tự Nhiên", 32990000, 34990000, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Điện thoại", "Bán chạy", 50),
            ("Tai nghe Sony WH-1000XM5", 7490000, 8990000, "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Âm thanh", "Giảm giá", 30),
            ("MacBook Air M3 13 inch", 27990000, 29990000, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Laptop", "Mới", 20),
            ("Apple Watch Ultra 2", 21490000, 22990000, "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Đồng hồ", "Premium", 15),
            ("iPhone 15 Pro 128GB", 28490000, 29990000, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Điện thoại", "HOT", 45),
            ("Sony WH-CH720N", 2990000, 3490000, "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Âm thanh", "", 100),
            ("MacBook Pro M3 Pro 14 inch", 49990000, 52990000, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Laptop", "Pro", 10),
            ("iPad Pro M2 11 inch (Wifi + 5G)", 23990000, 25990000, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Máy tính bảng", "Đồ họa", 25)
        ]
        cursor.executemany(
            'INSERT INTO products (name, price, old_price, image, category, badge, stock) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            default_products
        )

    conn.commit()
    cursor.close()
    conn.close()


DB_NAME = 'database.db'

def init_sqlite():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            old_price INTEGER,
            image TEXT NOT NULL,
            category TEXT NOT NULL,
            badge TEXT,
            stock INTEGER DEFAULT 100
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            reply TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
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

    # Auto-migrate old databases
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 100')
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE orders ADD COLUMN user_email TEXT')
    except sqlite3.OperationalError:
        pass

    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        default_products = [
            ("iPhone 15 Pro Max 256GB - Titan Tự Nhiên", 32990000, 34990000, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Điện thoại", "Bán chạy", 50),
            ("Tai nghe Sony WH-1000XM5 - Wireless Noise Cancelling", 7490000, 8990000, "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Âm thanh", "Giảm giá", 30),
            ("MacBook Air M3 13 inch (8GB/256GB) - Space Gray", 27990000, 29990000, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Laptop", "Mới", 20),
            ("Apple Watch Ultra 2 - Dây Alpine Xanh", 21490000, 22990000, "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Đồng hồ", "Premium", 15),
            ("iPhone 15 Pro 128GB - Titan Xanh", 28490000, 29990000, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Điện thoại", "HOT", 45),
            ("Sony WH-CH720N - Tai nghe chồng ồn giá rẻ", 2990000, 3490000, "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Âm thanh", "", 100),
            ("MacBook Pro M3 Pro - 14 inch", 49990000, 52990000, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Laptop", "Pro", 10),
            ("iPad Pro M2 11 inch (Wifi + 5G)", 23990000, 25990000, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80", "Máy tính bảng", "Đồ họa", 25)
        ]
        cursor.executemany('INSERT INTO products (name, price, old_price, image, category, badge, stock) VALUES (?, ?, ?, ?, ?, ?, ?)', default_products)

    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('koireviewss@gmail.com',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?)', ('Quản trị viên', 'koireviewss@gmail.com', 'Mot23456Khoi@', 1))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")

import sqlite3
import os

DB_NAME = "campus.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    # --- PERFORMANS AYARLARI ---
    # WAL Modu: Okuma ve yazma işlemlerini ayırır (Aynı anda işlem yapılabilir)
    conn.execute("PRAGMA journal_mode=WAL;") 
    # Synchronous Normal: Yazma hızını artırır (Güvenlikten az ödün vererek)
    conn.execute("PRAGMA synchronous=NORMAL;")
    # Cache Size: Veritabanını RAM'de daha fazla tutar
    conn.execute("PRAGMA cache_size=-64000;") # 64MB Cache
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    
    # Kullanıcılar
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'student',
        avatar BLOB,
        frame TEXT DEFAULT '',
        name_style TEXT DEFAULT '',
        bg_style TEXT DEFAULT '',
        font_style TEXT DEFAULT '',
        title TEXT DEFAULT 'Çırak',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        change_count INTEGER DEFAULT 0
    )''')
    
    # Puanlar
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        amount INTEGER,
        reason TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Sosyal (Postlar)
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        content TEXT,
        image BLOB,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        poll_options TEXT
    )''')
    
    # Beğeniler
    c.execute('''CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        username TEXT,
        UNIQUE(post_id, username)
    )''')
    
    # Yorumlar
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        username TEXT,
        comment TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Anket Oyları
    c.execute('''CREATE TABLE IF NOT EXISTS poll_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        username TEXT,
        option_index INTEGER,
        UNIQUE(post_id, username)
    )''')
    
    # Hikayeler
    c.execute('''CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        content TEXT,
        image BLOB,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    )''')
    
    # Arkadaşlar
    c.execute('''CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        u1 TEXT,
        u2 TEXT,
        status TEXT DEFAULT 'pending'
    )''')
    
    # Mesajlar
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0
    )''')
    
    # Envanter (Satın alınanlar)
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        item_type TEXT,
        item_value TEXT,
        UNIQUE(username, item_type, item_value)
    )''')
    
    # Bildirimler
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        msg TEXT,
        is_read INTEGER DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

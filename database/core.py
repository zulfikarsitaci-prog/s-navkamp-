import os
import psycopg2
import streamlit as st

# --- NEON / POSTGRES BAĞLANTISI ---
def get_connection():
    # 1. Bağlantı linkini Secrets'tan almaya çalış
    # Genelde secrets.toml içinde [postgres] url="..." veya direkt "DATABASE_URL" olur.
    db_url = st.secrets.get("DATABASE_URL")
    if not db_url and "postgres" in st.secrets:
        db_url = st.secrets["postgres"].get("url")
    
    # 2. Bulamazsa ortam değişkenlerine bak (Localde çalışıyorsan)
    if not db_url:
        db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        st.error("🚨 HATA: Neon veritabanı linki bulunamadı! Lütfen .streamlit/secrets.toml dosyasını kontrol et.")
        return None

    try:
        return psycopg2.connect(db_url)
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

def run_query(query, params=(), fetch=False):
    conn = get_connection()
    if not conn: return None
    
    try:
        # KRİTİK DÜZELTME: SQLite (?) işaretlerini Postgres (%s) işaretine çevir
        # Bu sayede diğer dosyalarındaki (users.py vb.) kodları değiştirmene gerek kalmaz.
        safe_query = query.replace('?', '%s')
        
        cur = conn.cursor()
        cur.execute(safe_query, params)
        
        if fetch:
            # Veriyi çek ve liste olarak döndür (Eski sistemin bozulmaması için)
            result = cur.fetchall()
            conn.close()
            return result
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        # Hata olursa ekrana basma (kullanıcı görmesin), konsola yaz
        print(f"DB Query Error: {e}")
        return None

def create_tables():
    # Postgres için tablo oluşturma (Verilerin zaten varsa burası onlara zarar vermez)
    conn = get_connection()
    if not conn: return
    
    cur = conn.cursor()
    
    # SQLite 'AUTOINCREMENT' yerine Postgres 'SERIAL' kullanılır.
    # Eğer tablolar zaten Neon'da varsa bu komutlar atlanır.
    commands = [
        """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'student',
            avatar BYTEA,
            frame TEXT DEFAULT '',
            name_style TEXT DEFAULT '',
            bg_style TEXT DEFAULT '',
            font_style TEXT DEFAULT '',
            title TEXT DEFAULT 'Çırak',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            change_count INTEGER DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS scores (
            id SERIAL PRIMARY KEY,
            username TEXT,
            amount INTEGER,
            reason TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            username TEXT,
            content TEXT,
            image BYTEA,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            poll_options TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            username TEXT,
            item_type TEXT,
            item_value TEXT,
            UNIQUE(username, item_type, item_value)
        )""",
        # Diğer tabloların (likes, comments, stories vb.) Neon'da zaten olduğunu varsayıyoruz.
        # Eksikse benzer mantıkla eklenebilir.
    ]
    
    try:
        for cmd in commands:
            cur.execute(cmd)
        conn.commit()
    except Exception as e:
        print(f"Tablo Oluşturma Hatası: {e}")
    finally:
        conn.close()

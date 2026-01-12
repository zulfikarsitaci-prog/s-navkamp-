import sqlite3
import psycopg2
import os
import streamlit as st

# --- BAĞLANTI ---
@st.cache_resource(ttl=3600)
def get_db_connection():
    if "DATABASE_URL" in st.secrets:
        try: return psycopg2.connect(st.secrets["DATABASE_URL"])
        except: pass
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "education_platform.db")
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def run_query(query, params=(), fetch=False):
    conn = get_db_connection()
    if not conn: return False
    try:
        if hasattr(conn, 'closed') and conn.closed != 0:
            st.cache_resource.clear(); conn = get_db_connection()
    except: pass
    cursor = conn.cursor()
    if "psycopg2" in str(type(conn)):
        query = query.replace("?", "%s").replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    try:
        cursor.execute(query, params)
        if fetch: return cursor.fetchall()
        else: conn.commit(); return True
    except Exception as e:
        try: conn.rollback()
        except: pass
        return False
    finally: cursor.close()

def create_tables():
    tables = [
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT, avatar_data TEXT, frame TEXT, name_style TEXT, post_style TEXT, font_style TEXT, title TEXT, change_count INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)',
        'CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, image_data TEXT, timestamp TEXT, likes INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, status TEXT)',
        'CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT, author TEXT)',
        # --- YENİ: HİKAYELER TABLOSU ---
        'CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, image_data TEXT, timestamp TEXT, expires_at TEXT)'
    ]
    for t in tables: run_query(t)
    
    # Eksik sütun kontrolü
    cols = ["avatar_data", "frame", "name_style", "post_style", "font_style", "title", "change_count"]
    for col in cols:
        try: 
            dtype = "INTEGER DEFAULT 0" if col == "change_count" else "TEXT"
            run_query(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except: pass

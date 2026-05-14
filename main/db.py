import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash

def create_database():
    conn = sql.connect('library.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  password TEXT NOT NULL,
                  email TEXT NOT NULL,
                  Role TEXT NOT NULL, UNIQUE(username))''')
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  author TEXT NOT NULL,
                  year INTEGER NOT NULL,
                  genre TEXT NOT NULL,
                  description TEXT,
                  cover TEXT,
                  isbn TEXT,
                  language TEXT,
                  format TEXT,
                  pages TEXT)''')
    
    # Forzar la columna description si no existe
    try:
        c.execute("ALTER TABLE books ADD COLUMN description TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE books ADD COLUMN cover TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE books ADD COLUMN isbn TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE books ADD COLUMN language TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE books ADD COLUMN format TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE books ADD COLUMN pages TEXT")
    except:
        pass
        
    conn.commit()
    conn.close()

import os

def database_connect():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'library.db')
    return sql.connect(db_path)

def add_user(username, password, email, role):
    if user_exists(username): return False
    try:
        conn = database_connect()
        c = conn.cursor()
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password, email, Role) VALUES (?, ?, ?, ?)",
                  (username, hashed_password, email, role))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error add_user: {e}")
        return False

def user_exists(username):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    res = c.fetchone()
    conn.close()
    return res is not None

def initialize_users():
    if not user_exists("admin"):
        add_user("admin", "admin123", "admin@example.com", "admin")
        print("Admin creado.")
    if not user_exists("user"):
        add_user("user", "user123", "user@example.com", "user")
        print("Usuario 'user' creado.")
    else:
        # Asegurar que la contraseña sea user123 por si acaso
        from werkzeug.security import generate_password_hash
        conn = database_connect()
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE username = ?", (generate_password_hash("user123"), "user"))
        conn.commit()
        conn.close()
        print("Contraseña de 'user' actualizada.")

def get_user(username):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT id, username, email, Role FROM users WHERE username = ?", (username,))
    u = c.fetchone()
    conn.close()
    return dict(id=u[0], username=u[1], email=u[2], role=u[3]) if u else None

def get_all_users():
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT id, username, email, Role FROM users")
    users = c.fetchall()
    conn.close()
    return [dict(id=u[0], username=u[1], email=u[2], role=u[3]) for u in users]

def delete_user(username):
    conn = database_connect()
    c = conn.cursor()

    c.execute(
        "DELETE FROM users WHERE username = ?",
        (username,)
    )
    conn.commit()
    conn.close()

def verify_password(username, password):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    res = c.fetchone()
    conn.close()
    return check_password_hash(res[0], password) if res else False

def get_all_books():
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        rows = c.fetchall()
        conn.close()
        books = []
        for b in rows:
            # Manejo seguro de columnas
            desc = b[5] if len(b) > 5 else ""
            cover = b[6] if len(b) > 6 else None
            isbn = b[7] if len(b) > 7 else ""
            lang = b[8] if len(b) > 8 else ""
            fmt = b[9] if len(b) > 9 else ""
            pag = b[10] if len(b) > 10 else ""
            books.append(dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4], 
                              description=desc, cover=cover, isbn=isbn, language=lang, 
                              format=fmt, pages=pag))
        return books
    except Exception as e:
        print(f"Error get_all_books: {e}")
        return []

def get_book_by_id(id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id = ?", (id,))
    b = c.fetchone()
    conn.close()
    if b:
        desc = b[5] if len(b) > 5 else ""
        cover = b[6] if len(b) > 6 else None
        isbn = b[7] if len(b) > 7 else ""
        lang = b[8] if len(b) > 8 else ""
        fmt = b[9] if len(b) > 9 else ""
        pag = b[10] if len(b) > 10 else ""
        return dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4], 
                    description=desc, cover=cover, isbn=isbn, language=lang, 
                    format=fmt, pages=pag)
    return None

def add_book(title, author, year, genre, description="", cover=None, isbn="", language="", format="", pages=""):
    conn = database_connect()
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, year, genre, description, cover, isbn, language, format, pages) VALUES (?,?,?,?,?,?,?,?,?,?)",
              (title, author, year, genre, description, cover, isbn, language, format, pages))
    conn.commit()
    conn.close()

def book_exists(id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT 1 FROM books WHERE id = ?", (id,))
    res = c.fetchone()
    conn.close()
    return res is not None

def delete_book(id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def update_book_in_db(id, title=None, author=None, year=None, genre=None, description=None, cover=None, isbn=None, language=None, format=None, pages=None):
    conn = database_connect()
    c = conn.cursor()
    if title: c.execute("UPDATE books SET title=? WHERE id=?", (title, id))
    if author: c.execute("UPDATE books SET author=? WHERE id=?", (author, id))
    if year: c.execute("UPDATE books SET year=? WHERE id=?", (year, id))
    if genre: c.execute("UPDATE books SET genre=? WHERE id=?", (genre, id))
    if description is not None: c.execute("UPDATE books SET description=? WHERE id=?", (description, id))
    if cover is not None: c.execute("UPDATE books SET cover=? WHERE id=?", (cover, id))
    if isbn is not None: c.execute("UPDATE books SET isbn=? WHERE id=?", (isbn, id))
    if language is not None: c.execute("UPDATE books SET language=? WHERE id=?", (language, id))
    if format is not None: c.execute("UPDATE books SET format=? WHERE id=?", (format, id))
    if pages is not None: c.execute("UPDATE books SET pages=? WHERE id=?", (pages, id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    initialize_users()
    print("Base de datos lista.")

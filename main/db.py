import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash

def create_database():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'library.db')
    conn = sql.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  password TEXT NOT NULL,
                  email TEXT NOT NULL,
                  Role TEXT NOT NULL,
                  profile_pic TEXT, UNIQUE(username))''')
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
                  pages TEXT,
                  buy_link TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS post_comments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  post_id INTEGER NOT NULL,
                  user_id INTEGER NOT NULL,
                  content TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (post_id) REFERENCES posts(id),
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  book_id INTEGER NOT NULL,
                  UNIQUE(user_id, book_id),
                  FOREIGN KEY (user_id) REFERENCES users(id),
                  FOREIGN KEY (book_id) REFERENCES books(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS reviews
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  book_id INTEGER NOT NULL,
                  rating INTEGER NOT NULL,
                  comment TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(user_id, book_id),
                  FOREIGN KEY (user_id) REFERENCES users(id),
                  FOREIGN KEY (book_id) REFERENCES books(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS reading_status
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  book_id INTEGER NOT NULL,
                  status TEXT NOT NULL,
                  UNIQUE(user_id, book_id),
                  FOREIGN KEY (user_id) REFERENCES users(id),
                  FOREIGN KEY (book_id) REFERENCES books(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS follows
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  follower_id INTEGER NOT NULL,
                  followed_id INTEGER NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(follower_id, followed_id),
                  FOREIGN KEY (follower_id) REFERENCES users(id),
                  FOREIGN KEY (followed_id) REFERENCES users(id))''')
    
    # Forzar la columna description si no existe
    try:
        c.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
    except:
        pass
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
    try:
        c.execute("ALTER TABLE books ADD COLUMN buy_link TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE books ADD COLUMN tags TEXT")
    except:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  username TEXT,
                  action TEXT NOT NULL,
                  detail TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS wishlists
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  book_id INTEGER NOT NULL,
                  UNIQUE(user_id, book_id),
                  FOREIGN KEY (user_id) REFERENCES users(id),
                  FOREIGN KEY (book_id) REFERENCES books(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS book_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  book_id INTEGER NOT NULL,
                  content TEXT,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(user_id, book_id),
                  FOREIGN KEY (user_id) REFERENCES users(id),
                  FOREIGN KEY (book_id) REFERENCES books(id))''')

    conn.commit()
    conn.close()

import os

def database_connect():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'library.db')
    return sql.connect(db_path)

def add_user(username, password, email, role, profile_pic=None):
    if user_exists(username): return False
    try:
        conn = database_connect()
        c = conn.cursor()
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password, email, Role, profile_pic) VALUES (?, ?, ?, ?, ?)",
                  (username, hashed_password, email, role, profile_pic))
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
    c.execute("SELECT id, username, email, Role, profile_pic FROM users WHERE username = ?", (username,))
    u = c.fetchone()
    conn.close()
    if u:
        return dict(id=u[0], username=u[1], email=u[2], role=u[3], profile_pic=u[4] if len(u)>4 else None)
    return None

def get_all_users():
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT id, username, email, Role, profile_pic FROM users")
    users = c.fetchall()
    conn.close()
    return [dict(id=u[0], username=u[1], email=u[2], role=u[3], profile_pic=u[4] if len(u)>4 else None) for u in users]

def update_user_profile_pic(username, profile_pic):
    conn = database_connect()
    c = conn.cursor()
    c.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (profile_pic, username))
    conn.commit()
    conn.close()

def update_user(current_username, new_username=None, email=None, new_password=None):
    if new_username and new_username != current_username:
        if user_exists(new_username):
            return False # Username taken
            
    conn = database_connect()
    c = conn.cursor()
    if email:
        c.execute("UPDATE users SET email = ? WHERE username = ?", (email, current_username))
    if new_password:
        hashed_password = generate_password_hash(new_password)
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, current_username))
    if new_username and new_username != current_username:
        c.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, current_username))
    conn.commit()
    conn.close()
    return True

def delete_user(username):
    conn = database_connect()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def update_user_role(username, new_role):
    conn = database_connect()
    c = conn.cursor()
    c.execute("UPDATE users SET Role = ? WHERE username = ?", (new_role, username))
    conn.commit()
    conn.close()
    return True

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
            desc = b[5] if len(b) > 5 else ""
            cover = b[6] if len(b) > 6 else None
            isbn = b[7] if len(b) > 7 else ""
            lang = b[8] if len(b) > 8 else ""
            fmt = b[9] if len(b) > 9 else ""
            pag = b[10] if len(b) > 10 else ""
            buy = b[11] if len(b) > 11 else ""
            tags = b[12] if len(b) > 12 else ""
            books.append(dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4], 
                              description=desc, cover=cover, isbn=isbn, language=lang, 
                              format=fmt, pages=pag, buy_link=buy, tags=tags))
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
        buy = b[11] if len(b) > 11 else ""
        tags = b[12] if len(b) > 12 else ""
        return dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4], 
                    description=desc, cover=cover, isbn=isbn, language=lang, 
                    format=fmt, pages=pag, buy_link=buy, tags=tags)
    return None

def add_book(title, author, year, genre, description="", cover=None, isbn="", language="", format="", pages="", buy_link="", tags=""):
    conn = database_connect()
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, year, genre, description, cover, isbn, language, format, pages, buy_link, tags) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
              (title, author, year, genre, description, cover, isbn, language, format, pages, buy_link, tags))
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

def update_book_in_db(id, title=None, author=None, year=None, genre=None, description=None, cover=None, isbn=None, language=None, format=None, pages=None, buy_link=None, tags=None):
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
    if buy_link is not None: c.execute("UPDATE books SET buy_link=? WHERE id=?", (buy_link, id))
    if tags is not None: c.execute("UPDATE books SET tags=? WHERE id=?", (tags, id))
    conn.commit()
    conn.close()

# --- Nuevas Funciones para Interacciones ---

def toggle_favorite(user_id, book_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT 1 FROM favorites WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    if c.fetchone():
        c.execute("DELETE FROM favorites WHERE user_id = ? AND book_id = ?", (user_id, book_id))
        is_favorite = False
    else:
        c.execute("INSERT INTO favorites (user_id, book_id) VALUES (?, ?)", (user_id, book_id))
        is_favorite = True
    conn.commit()
    conn.close()
    return is_favorite

def get_user_favorites(user_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT book_id FROM favorites WHERE user_id = ?", (user_id,))
    favs = [row[0] for row in c.fetchall()]
    conn.close()
    return favs

def set_reading_status(user_id, book_id, status):
    conn = database_connect()
    c = conn.cursor()
    c.execute("INSERT INTO reading_status (user_id, book_id, status) VALUES (?, ?, ?) ON CONFLICT(user_id, book_id) DO UPDATE SET status = ?", (user_id, book_id, status, status))
    conn.commit()
    conn.close()

def get_user_reading_status(user_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT book_id, status FROM reading_status WHERE user_id = ?", (user_id,))
    statuses = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return statuses

def add_review(user_id, book_id, rating, comment):
    conn = database_connect()
    c = conn.cursor()
    c.execute("INSERT INTO reviews (user_id, book_id, rating, comment) VALUES (?, ?, ?, ?) ON CONFLICT(user_id, book_id) DO UPDATE SET rating = ?, comment = ?", (user_id, book_id, rating, comment, rating, comment))
    conn.commit()
    conn.close()

def get_book_reviews(book_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("""SELECT r.id, r.rating, r.comment, r.created_at, u.username, u.profile_pic 
                 FROM reviews r JOIN users u ON r.user_id = u.id 
                 WHERE r.book_id = ? ORDER BY r.created_at DESC""", (book_id,))
    reviews = []
    for row in c.fetchall():
        reviews.append({
            'id': row[0],
            'rating': row[1],
            'comment': row[2],
            'created_at': row[3],
            'username': row[4],
            'profile_pic': row[5]
        })
    conn.close()
    return reviews
def delete_review(review_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()

def follow_user(follower_id, followed_id):
    if follower_id == followed_id: return False
    conn = database_connect()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO follows (follower_id, followed_id) VALUES (?, ?)", (follower_id, followed_id))
    conn.commit()
    conn.close()
    return True

def unfollow_user(follower_id, followed_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("DELETE FROM follows WHERE follower_id = ? AND followed_id = ?", (follower_id, followed_id))
    conn.commit()
    conn.close()

def is_following(follower_id, followed_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?", (follower_id, followed_id))
    res = c.fetchone()
    conn.close()
    return res is not None

def add_post(user_id, content, book_id=None):
    conn = database_connect()
    c = conn.cursor()
    c.execute("INSERT INTO posts (user_id, content, book_id) VALUES (?, ?, ?)", (user_id, content, book_id))
    conn.commit()
    conn.close()

def get_user_posts(user_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("""
        SELECT p.id, p.content, p.created_at, b.title, b.id as book_id 
        FROM posts p 
        LEFT JOIN books b ON p.book_id = b.id 
        WHERE p.user_id = ? ORDER BY p.created_at DESC
    """, (user_id,))
    posts = []
    for row in c.fetchall():
        posts.append({
            'id': row[0],
            'content': row[1],
            'created_at': row[2],
            'book_title': row[3],
            'book_id': row[4]
        })
    conn.close()
    return posts

def get_all_posts(limit=50):
    conn = database_connect()
    c = conn.cursor()
    c.execute("""
        SELECT p.id, p.content, p.created_at, u.username, u.profile_pic, b.title as book_title, b.id as book_id
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN books b ON p.book_id = b.id
        ORDER BY p.created_at DESC LIMIT ?
    """, (limit,))
    posts = []
    for row in c.fetchall():
        posts.append({
            'id': row[0],
            'content': row[1],
            'created_at': row[2],
            'username': row[3],
            'profile_pic': row[4],
            'book_title': row[5],
            'book_id': row[6]
        })
    conn.close()
    return posts

def add_post_comment(post_id, user_id, content):
    conn = database_connect()
    c = conn.cursor()
    c.execute("INSERT INTO post_comments (post_id, user_id, content) VALUES (?, ?, ?)", (post_id, user_id, content))
    conn.commit()
    conn.close()

def get_post_comments(post_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("""
        SELECT c.id, c.content, c.created_at, u.username, u.profile_pic
        FROM post_comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ? ORDER BY c.created_at ASC
    """, (post_id,))
    comments = []
    for row in c.fetchall():
        comments.append({
            'id': row[0],
            'content': row[1],
            'created_at': row[2],
            'username': row[3],
            'profile_pic': row[4]
        })
    conn.close()
    return comments

def delete_post(post_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def get_user_feed(user_id, limit=20):
    conn = database_connect()
    c = conn.cursor()
    # Query for reviews, reading status updates and POSTS from followed users
    c.execute("""
        SELECT 'review' as type, r.created_at, u.username, u.profile_pic, b.title, b.id as book_id, r.rating as data, r.comment 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        JOIN books b ON r.book_id = b.id
        WHERE r.user_id IN (SELECT followed_id FROM follows WHERE follower_id = ?)
        UNION ALL
        SELECT 'status' as type, rs.id as created_at, u.username, u.profile_pic, b.title, b.id as book_id, rs.status as data, NULL 
        FROM reading_status rs
        JOIN users u ON rs.user_id = u.id
        JOIN books b ON rs.book_id = b.id
        WHERE rs.user_id IN (SELECT followed_id FROM follows WHERE follower_id = ?)
        UNION ALL
        SELECT 'post' as type, p.created_at, u.username, u.profile_pic, b.title, b.id as book_id, NULL as data, p.content as comment
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN books b ON p.book_id = b.id
        WHERE p.user_id IN (SELECT followed_id FROM follows WHERE follower_id = ?)
        ORDER BY created_at DESC LIMIT ?
    """, (user_id, user_id, user_id, limit))
    
    feed = []
    for row in c.fetchall():
        feed.append({
            'type': row[0],
            'timestamp': row[1],
            'username': row[2],
            'profile_pic': row[3],
            'book_title': row[4],
            'book_id': row[5],
            'data': row[6],
            'comment': row[7]
        })
    conn.close()
    return feed

def get_total_reviews_count():
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reviews")
    count = c.fetchone()[0]
    conn.close()
    return count

# --- Wishlist ---

def toggle_wishlist(user_id, book_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT 1 FROM wishlists WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    if c.fetchone():
        c.execute("DELETE FROM wishlists WHERE user_id = ? AND book_id = ?", (user_id, book_id))
        added = False
    else:
        c.execute("INSERT INTO wishlists (user_id, book_id) VALUES (?, ?)", (user_id, book_id))
        added = True
    conn.commit()
    conn.close()
    return added

def get_user_wishlist(user_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT book_id FROM wishlists WHERE user_id = ?", (user_id,))
    ids = [r[0] for r in c.fetchall()]
    conn.close()
    return ids

# --- Personal Notes ---

def update_book_note(user_id, book_id, content):
    conn = database_connect()
    c = conn.cursor()
    c.execute("""INSERT INTO book_notes (user_id, book_id, content, updated_at)
                 VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                 ON CONFLICT(user_id, book_id) DO UPDATE SET content = ?, updated_at = CURRENT_TIMESTAMP""",
              (user_id, book_id, content, content))
    conn.commit()
    conn.close()

def get_book_note(user_id, book_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT content FROM book_notes WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    r = c.fetchone()
    conn.close()
    return r[0] if r else ""

# --- Export ---

def export_books(format="json"):
    books = get_all_books()
    if format == "csv":
        import io, csv
        output = io.StringIO()
        w = csv.writer(output)
        w.writerow(['id', 'title', 'author', 'year', 'genre', 'isbn', 'language', 'format', 'pages', 'buy_link', 'tags'])
        for b in books:
            w.writerow([b['id'], b['title'], b['author'], b['year'], b['genre'], b.get('isbn',''), b.get('language',''), b.get('format',''), b.get('pages',''), b.get('buy_link',''), b.get('tags','')])
        return output.getvalue()
    import json
    return json.dumps(books, ensure_ascii=False, indent=2)

# --- Activity Logs ---

def log_activity(user_id, username, action, detail=""):
    conn = database_connect()
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs (user_id, username, action, detail) VALUES (?, ?, ?, ?)",
              (user_id, username, action, detail))
    conn.commit()
    conn.close()

def get_activity_logs(limit=50):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'user_id': r[1], 'username': r[2], 'action': r[3], 'detail': r[4], 'created_at': r[5]} for r in rows]

# --- Dashboard Stats ---

def get_dashboard_stats():
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM favorites")
    total_favorites = c.fetchone()[0]
    # Most active users (by reviews)
    c.execute("""
        SELECT u.username, COUNT(r.id) as cnt FROM reviews r
        JOIN users u ON r.user_id = u.id
        GROUP BY r.user_id ORDER BY cnt DESC LIMIT 5
    """)
    top_reviewers = [{'username': r[0], 'count': r[1]} for r in c.fetchall()]
    # Most favorited books
    c.execute("""
        SELECT b.title, COUNT(f.id) as cnt FROM favorites f
        JOIN books b ON f.book_id = b.id
        GROUP BY f.book_id ORDER BY cnt DESC LIMIT 5
    """)
    top_favorited = [{'title': r[0], 'count': r[1]} for r in c.fetchall()]
    # Recent activity
    c.execute("SELECT username, action, detail, created_at FROM activity_logs ORDER BY created_at DESC LIMIT 10")
    recent = [{'username': r[0], 'action': r[1], 'detail': r[2], 'created_at': r[3]} for r in c.fetchall()]
    conn.close()
    return {
        'total_books': total_books,
        'total_users': total_users,
        'total_reviews': total_reviews,
        'total_favorites': total_favorites,
        'top_reviewers': top_reviewers,
        'top_favorited': top_favorited,
        'recent_activity': recent
    }

if __name__ == "__main__":
    create_database()
    initialize_users()
    print("Base de datos lista.")

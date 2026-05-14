from db import *

def add_book(title, author, year, genre, description=None, cover=None, isbn=None, language=None, format=None, pages=None, buy_link=None, tags=None):
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("""
            INSERT INTO books (title, author, year, genre, description, cover, isbn, language, format, pages, buy_link, tags) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, author, year, genre, description, cover, isbn, language, format, pages, buy_link, tags))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error add_book: {e}")
        return False

def get_all_books():
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        rows = c.fetchall()
        books = []
        for r in rows:
            books.append({
                'id': r[0], 'title': r[1], 'author': r[2], 'year': r[3], 'genre': r[4],
                'description': r[5], 'cover': r[6], 'isbn': r[7], 'language': r[8],
                'format': r[9], 'pages': r[10], 'buy_link': r[11], 'tags': r[12] if len(r) > 12 else ''
            })
        conn.close()
        return books
    except Exception as e:
        print(f"Error get_all_books: {e}")
        return []

def get_book_by_id(book_id):
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        r = c.fetchone()
        conn.close()
        if r:
            return {
                'id': r[0], 'title': r[1], 'author': r[2], 'year': r[3], 'genre': r[4],
                'description': r[5], 'cover': r[6], 'isbn': r[7], 'language': r[8],
                'format': r[9], 'pages': r[10], 'buy_link': r[11], 'tags': r[12] if len(r) > 12 else ''
            }
        return None
    except Exception as e:
        print(f"Error get_book_by_id: {e}")
        return None

def book_exists(book_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("SELECT 1 FROM books WHERE id = ?", (book_id,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def delete_book(book_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

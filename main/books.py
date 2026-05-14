from db import *


books = [
    dict(id=1, title="To Kill a Mockingbird", author="Harper Lee", year=1960, genre="Fiction"),
    dict(id=2, title="1984", author="George Orwell", year=1949, genre="Dystopian"),
    dict(id=3, title="The Great Gatsby", author="F. Scott Fitzgerald", year=1925, genre="Fiction"),
]


def create_books_table():
    conn = database_connect()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  author TEXT NOT NULL,
                  year INTEGER NOT NULL,
                  genre TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def initialize_books():
    create_books_table()
    for book in books:
        add_book(book['title'], book['author'], book['year'], book['genre'])


def add_book(title, author, year, genre):
    try:
        conn = database_connect()
        c = conn.cursor()

        # Verificar si el libro ya existe por título
        conn_check = database_connect()
        c_check = conn_check.cursor()
        c_check.execute("SELECT id FROM books WHERE title = ?", (title,))
        existing_book = c_check.fetchone()
        conn_check.close()
        
        if existing_book:
            print(f"Book '{title}' already exists in the database.")
            return

        c.execute("INSERT INTO books (title, author, year, genre) VALUES (?, ?, ?, ?)",
                  (title, author, year, genre))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al agregar libro: {e}")

def get_book(book_id):
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = c.fetchone()
        conn.close()
        return book
    except Exception as e:
        print(f"Error al obtener libro por ID: {e}")
        return None

def get_book_by_id(book_id):
    """Alias para get_book, devuelve un diccionario"""
    book = get_book(book_id)
    if book:
        return dict(id=book[0], title=book[1], author=book[2], year=book[3], genre=book[4])
    return None

def get_all_books():
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        books = c.fetchall()
        conn.close()
        return [dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4]) for b in books]
    except Exception as e:
        print(f"Error al obtener todos los libros: {e}")
        return []

def delete_book(book_id):
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al eliminar libro: {e}")

def update_book(book_id, title=None, author=None, year=None, genre=None):
    try:
        conn = database_connect()
        c = conn.cursor()
        if title:
            c.execute("UPDATE books SET title = ? WHERE id = ?", (title, book_id))
        if author:
            c.execute("UPDATE books SET author = ? WHERE id = ?", (author, book_id))
        if year:
            c.execute("UPDATE books SET year = ? WHERE id = ?", (year, book_id))
        if genre:
            c.execute("UPDATE books SET genre = ? WHERE id = ?", (genre, book_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al actualizar libro: {e}")

def book_exists(book_id):
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT 1 FROM books WHERE id = ?", (book_id,))
        exists = c.fetchone() is not None
        conn.close()
        return exists
    except Exception as e:
        print(f"Error al verificar libro: {e}")
        return False

def search_books(keyword):
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?",
                  (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        results = c.fetchall()
        conn.close()
        return [dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4]) for b in results]
    except Exception as e:
        print(f"Error al buscar libros: {e}")
        return []

def filter_books_by_year(year):
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE year = ?", (year,))
        results = c.fetchall()
        conn.close()
        return [dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4]) for b in results]
    except Exception as e:
        print(f"Error al filtrar por año: {e}")
        return []

def filter_books_by_genre(genre):    
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE genre = ?", (genre,))
        results = c.fetchall()
        conn.close()
        return [dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4]) for b in results]
    except Exception as e:
        print(f"Error al filtrar por género: {e}")
        return []

def filter_books_by_author(author):   
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE author = ?", (author,))
        results = c.fetchall()
        conn.close()
        return [dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4]) for b in results]
    except Exception as e:
        print(f"Error al filtrar por autor: {e}")
        return []

def filter_books_by_title(title):    
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE title = ?", (title,))
        results = c.fetchall()
        conn.close()
        return [dict(id=b[0], title=b[1], author=b[2], year=b[3], genre=b[4]) for b in results]
    except Exception as e:
        print(f"Error al filtrar por título: {e}")
        return []

def get_book_id(title):   
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT id FROM books WHERE title = ?", (title,))
        book_id = c.fetchone()
        conn.close()
        return book_id[0] if book_id else None
    except Exception as e:
        print(f"Error al obtener ID del libro: {e}")
        return None

def get_book_title(book_id):
    try:
        conn = database_connect()
        c = conn.cursor()
        c.execute("SELECT title FROM books WHERE id = ?", (book_id,))
        title = c.fetchone()
        conn.close()
        return title[0] if title else None
    except Exception as e:
        print(f"Error al obtener título del libro: {e}")
        return None


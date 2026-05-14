import flask as fk
from flask import request, jsonify, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from books import *
from db import *
import os
from werkzeug.utils import secure_filename

# Configure folders relative to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = fk.Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'libreria_secret_key_123'
CORS(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['role'] != 'admin':
            flash('Acceso denegado. Se requieren permisos de administrador.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    return dict(current_user=session.get('user'))

@app.route('/debug/db')
def debug_db():
    from db import database_connect
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'library.db')
    return f"DB Path: {db_path} - Exists: {os.path.exists(db_path)}"

@app.route('/api/health')
def api_health():
    try:
        conn = database_connect()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "ok"
    except:
        db_status = "error"
    return jsonify({"status": "ok", "database": db_status, "version": "1.0"})

@app.route('/')
def index():
    return render_template('index.html', active_page='index')

@app.route('/catalog')
def catalog():
    favorites_ids = []
    if 'user' in session:
        favorites_ids = get_user_favorites(session['user']['id'])
    return render_template('catalog.html', active_page='catalog', favorites_ids=favorites_ids)

@app.route('/community')
@login_required
def community():
    posts = get_all_posts()
    # For each post, we could also get comments, but we'll load them via JS for better UX
    return render_template('community.html', posts=posts, active_page='community')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_password(username, password):
            user_data = get_user(username)
            session['user'] = user_data
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos')
            
    return render_template('login.html', active_page='login')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_panel():
    users = get_all_users()
    books = get_all_books()
    return render_template('admin.html', users=users, books=books, active_page='admin')

@app.route('/user/<username>')
@login_required
def user_dashboard(username):
    user = get_user(username)
    if user:
        books = get_all_books()
        favorites_ids = get_user_favorites(user['id'])
        reading_statuses = get_user_reading_status(user['id'])
        
        # Build lists
        fav_books = [b for b in books if b['id'] in favorites_ids]
        reading_books = [b for b in books if b['id'] in reading_statuses]
        
        # Social
        following = is_following(session['user']['id'], user['id'])
        is_own_profile = session['user']['username'] == username
        
        # Feed if it's own profile
        feed = []
        if is_own_profile:
            feed = get_user_feed(session['user']['id'])
        
        # User's own posts (always visible)
        posts = get_user_posts(user['id'])
            
        return render_template('user.html', 
                             user=user, 
                             fav_books=fav_books, 
                             reading_books=reading_books, 
                             reading_statuses=reading_statuses, 
                             following=following,
                             is_own_profile=is_own_profile,
                             feed=feed,
                             posts=posts,
                             active_page='user')
    return "User not found", 404

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = get_book_by_id(book_id)
    if book:
        reviews = get_book_reviews(book_id)
        is_favorite = False
        in_wishlist = False
        reading_status = 'none'
        note = ''
        
        if 'user' in session:
            user_id = session['user']['id']
            is_favorite = book_id in get_user_favorites(user_id)
            in_wishlist = book_id in get_user_wishlist(user_id)
            statuses = get_user_reading_status(user_id)
            reading_status = statuses.get(book_id, 'none')
            note = get_book_note(user_id, book_id)
            
        return render_template('book_details.html', book=book, reviews=reviews, is_favorite=is_favorite, in_wishlist=in_wishlist, reading_status=reading_status, note=note)
    return "Libro no encontrado", 404


# --- Admin & General API ---

@app.route('/api/books', methods=['GET'])
@limiter.limit("30 per minute")
def api_get_books():
    books = get_all_books()
    return jsonify(books)

@app.route('/api/books/<int:book_id>', methods=['GET'])
@limiter.limit("30 per minute")
def api_get_book(book_id):
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Libro no encontrado'}), 404
    return jsonify(book)

@app.route('/api/books', methods=['POST'])
@admin_required
def api_create_book():
    title = request.form.get('title')
    author = request.form.get('author')
    year = request.form.get('year')
    genre = request.form.get('genre')
    description = request.form.get('description', '')
    isbn = request.form.get('isbn', '')
    language = request.form.get('language', '')
    format = request.form.get('format', '')
    pages = request.form.get('pages', '')
    buy_link = request.form.get('buy_link', '')
    tags = request.form.get('tags', '')
    
    file = request.files.get('cover')
    cover_url = None
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        unique_filename = f"{os.urandom(8).hex()}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        cover_url = f"/static/uploads/{unique_filename}"
    
    add_book(title, author, year, genre, description, cover_url, isbn, language, format, pages, buy_link, tags)
    log_activity(session['user']['id'], session['user']['username'], 'create_book', f"Añadió '{title}' de {author}")
    return jsonify({'message': 'Book added successfully'})

@app.route('/api/books/<int:book_id>', methods=['PUT'])
@admin_required
def api_update_book(book_id):
    title = request.form.get('title')
    author = request.form.get('author')
    year = request.form.get('year')
    genre = request.form.get('genre')
    description = request.form.get('description')
    isbn = request.form.get('isbn')
    language = request.form.get('language')
    format = request.form.get('format')
    pages = request.form.get('pages')
    buy_link = request.form.get('buy_link')
    tags = request.form.get('tags')
    
    file = request.files.get('cover')
    cover_url = None
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        unique_filename = f"{os.urandom(8).hex()}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        cover_url = f"/static/uploads/{unique_filename}"
    
    conn = database_connect()
    c = conn.cursor()
    c.execute("""
        UPDATE books SET title=?, author=?, year=?, genre=?, description=?, 
        isbn=?, language=?, format=?, pages=?, buy_link=?, tags=?
        WHERE id=?
    """, (title, author, year, genre, description, isbn, language, format, pages, buy_link, tags, book_id))
    
    if cover_url:
        c.execute("UPDATE books SET cover=? WHERE id=?", (cover_url, book_id))
        
    conn.commit()
    conn.close()
    log_activity(session['user']['id'], session['user']['username'], 'update_book', f"Editó libro ID {book_id}")
    return jsonify({'message': 'Book updated successfully'})

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@admin_required
def api_delete_book(book_id):
    conn = database_connect()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    log_activity(session['user']['id'], session['user']['username'], 'delete_book', f"Eliminó libro ID {book_id}")
    return jsonify({'message': 'Book deleted successfully'})

@app.route('/api/users', methods=['GET'])
@admin_required
def api_get_users():
    users = get_all_users()
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
@admin_required
def api_create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'user')

    if not username or not password or not email:
        return jsonify({'error': 'Missing required fields'}), 400

    if user_exists(username):
        return jsonify({'error': 'Username already exists'}), 400

    add_user(username, password, email, role)
    log_activity(session['user']['id'], session['user']['username'], 'create_user', f"Creó usuario '{username}'")
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/users/<string:username>', methods=['DELETE'])
@admin_required
def api_delete_user(username):
    if not user_exists(username):
        return jsonify({'error': 'User not found'}), 404
    delete_user(username)
    log_activity(session['user']['id'], session['user']['username'], 'delete_user', f"Eliminó usuario '{username}'")
    return jsonify({'message': 'User deleted successfully'}), 200


@app.route('/api/follow/<int:followed_id>', methods=['POST'])
@login_required
def api_follow(followed_id):
    follower_id = session['user']['id']
    if follow_user(follower_id, followed_id):
        return jsonify({'message': 'Following user'}), 200
    return jsonify({'error': 'Cannot follow yourself'}), 400

@app.route('/api/follow/<int:followed_id>', methods=['DELETE'])
@login_required
def api_unfollow(followed_id):
    follower_id = session['user']['id']
    unfollow_user(follower_id, followed_id)
    return jsonify({'message': 'Unfollowed user'}), 200

@app.route('/api/posts', methods=['POST'])
@login_required
def api_create_post():
    data = request.json
    content = data.get('content')
    book_id = data.get('book_id')
    
    if not content:
        return jsonify({'error': 'El contenido es requerido'}), 400
        
    add_post(session['user']['id'], content, book_id)
    return jsonify({'message': 'Publicado correctamente'})

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@admin_required
def api_delete_post(post_id):
    delete_post(post_id)
    return jsonify({'message': 'Post eliminado'})

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
@login_required
def api_get_comments(post_id):
    comments = get_post_comments(post_id)
    return jsonify(comments)

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@login_required
def api_create_comment(post_id):
    data = request.json
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Contenido vacío'}), 400
    
    add_post_comment(post_id, session['user']['id'], content)
    return jsonify({'message': 'Comentario añadido'})
@login_required
def api_get_feed():
    user_id = session['user']['id']
    feed = get_user_feed(user_id)
    return jsonify(feed), 200

@app.route('/api/users/<string:username>/profile_pic', methods=['POST'])
@login_required
def upload_profile_pic(username):
    if session['user']['username'] != username and session['user']['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    file = request.files.get('croppedImage')
    if file and file.filename != '':
        filename = secure_filename(f"{username}_profile.png")
        unique_filename = f"{os.urandom(4).hex()}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        pic_url = f"/static/uploads/{unique_filename}"
        update_user_profile_pic(username, pic_url)
        
        # Actualizar la sesión si es el propio usuario
        if session['user']['username'] == username:
            session['user']['profile_pic'] = pic_url
            session.modified = True
            
        return jsonify({'message': 'Profile picture updated', 'url': pic_url}), 200
        
    return jsonify({'error': 'No image provided'}), 400

@app.route('/api/users/<string:username>/update', methods=['POST'])
@login_required
def update_profile(username):
    if session['user']['username'] != username and session['user']['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    success = update_user(username, new_username=new_username, email=email, new_password=password)
    if not success:
        return jsonify({'error': 'El nombre de usuario ya está en uso'}), 400
    
    # Update session if it's the logged-in user
    if session['user']['username'] == username:
        if email:
            session['user']['email'] = email
        if new_username and new_username != username:
            session['user']['username'] = new_username
        session.modified = True
        
    new_url = url_for('user_dashboard', username=new_username) if new_username else None
        
    return jsonify({'message': 'Profile updated successfully', 'redirect_url': new_url}), 200

# --- User Book Interactions API ---

@app.route('/api/books/<int:book_id>/favorite', methods=['POST'])
@login_required
def api_toggle_favorite(book_id):
    if not book_exists(book_id):
        return jsonify({'error': 'Book not found'}), 404
    
    user_id = session['user']['id']
    is_favorite = toggle_favorite(user_id, book_id)
    return jsonify({'is_favorite': is_favorite}), 200

@app.route('/api/books/<int:book_id>/status', methods=['POST'])
@login_required
def api_set_status(book_id):
    if not book_exists(book_id):
        return jsonify({'error': 'Book not found'}), 404
        
    data = request.get_json()
    status = data.get('status')
    if status not in ['to_read', 'reading', 'read', 'none']:
        return jsonify({'error': 'Invalid status'}), 400
        
    user_id = session['user']['id']
    if status == 'none':
        # Remove status - using SQL directly or helper. 
        # Helper not built for delete, let's just use raw connection for simplicity.
        conn = database_connect()
        c = conn.cursor()
        c.execute("DELETE FROM reading_status WHERE user_id = ? AND book_id = ?", (user_id, book_id))
        conn.commit()
        conn.close()
    else:
        set_reading_status(user_id, book_id, status)
        
    return jsonify({'message': 'Status updated', 'status': status}), 200

@app.route('/api/books/<int:book_id>/review', methods=['POST'])
@login_required
def api_add_review(book_id):
    if not book_exists(book_id):
        return jsonify({'error': 'Book not found'}), 404
        
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5: raise ValueError
    except:
        return jsonify({'error': 'Invalid rating'}), 400
        
    user_id = session['user']['id']
    add_review(user_id, book_id, rating, comment)
    return jsonify({'message': 'Review added successfully'}), 200

@app.route('/api/books/<int:book_id>/reviews', methods=['GET'])
def api_get_reviews(book_id):
    if not book_exists(book_id):
        return jsonify({'error': 'Book not found'}), 404
    reviews = get_book_reviews(book_id)
    return jsonify(reviews), 200

@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
@login_required
def api_delete_review(review_id):
    print(f"DEBUG: Intentando eliminar reseña ID {review_id} por el usuario {session['user']['username']}")
    if session['user']['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    delete_review(review_id)
    return jsonify({'message': 'Review deleted successfully'}), 200

@app.route('/api/stats/reviews', methods=['GET'])
def api_get_total_reviews():
    count = get_total_reviews_count()
    return jsonify({'count': count})

@app.route('/api/books/paginated', methods=['GET'])
def api_get_books_paginated():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    genre = request.args.get('genre', '')
    year = request.args.get('year', '')
    language = request.args.get('language', '')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    
    books = get_all_books()
    
    if genre and genre != 'all':
        books = [b for b in books if b.get('genre', '').lower() == genre.lower()]
    if year:
        books = [b for b in books if str(b.get('year', '')) == year]
    if language and language != 'all':
        books = [b for b in books if b.get('language', '').lower() == language.lower()]
    if search:
        s = search.lower()
        books = [b for b in books if s in b.get('title', '').lower() or s in b.get('author', '').lower()]
    
    if sort == 'newest': books.sort(key=lambda b: b.get('year', 0) or 0, reverse=True)
    elif sort == 'oldest': books.sort(key=lambda b: b.get('year', 0) or 0)
    elif sort == 'az': books.sort(key=lambda b: b.get('title', '').lower())
    
    total = len(books)
    start = (page - 1) * per_page
    end = start + per_page
    page_books = books[start:end]
    
    genres = sorted(set(b.get('genre', '') for b in books if b.get('genre')))
    languages = sorted(set(b.get('language', '') for b in books if b.get('language')))
    years = sorted(set(str(b.get('year', '')) for b in books if b.get('year')), reverse=True)
    
    return jsonify({
        'books': page_books,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': max(1, (total + per_page - 1) // per_page),
        'filters': {'genres': genres, 'languages': languages, 'years': years}
    })

@app.route('/api/stats/dashboard', methods=['GET'])
@admin_required
def api_dashboard_stats():
    return jsonify(get_dashboard_stats())

@app.route('/api/activity-logs', methods=['GET'])
@admin_required
def api_activity_logs():
    return jsonify(get_activity_logs(100))

@app.route('/api/users/<string:username>/role', methods=['PUT'])
@admin_required
def api_update_user_role(username):
    data = request.get_json()
    new_role = data.get('role')
    if new_role not in ('admin', 'user'):
        return jsonify({'error': 'Rol inválido'}), 400
    update_user_role(username, new_role)
    log_activity(session['user']['id'], session['user']['username'], 'update_user_role', f"Usuario {username} ahora es {new_role}")
    return jsonify({'message': 'Rol actualizado'})

@app.route('/api/docs')
def api_docs_page():
    return render_template('api_docs.html', active_page='api_docs')

@app.route('/api/export-books', methods=['GET'])
@admin_required
def api_export_books():
    fmt = request.args.get('format', 'json')
    data = export_books(fmt)
    mimetype = 'application/json' if fmt == 'json' else 'text/csv'
    filename = f'catalogo_vellum.{fmt}'
    return fk.Response(data, mimetype=mimetype, headers={'Content-Disposition': f'attachment; filename={filename}'})

@app.route('/api/books/<int:book_id>/wishlist', methods=['POST'])
@login_required
def api_toggle_wishlist(book_id):
    if not book_exists(book_id):
        return jsonify({'error': 'Libro no encontrado'}), 404
    added = toggle_wishlist(session['user']['id'], book_id)
    return jsonify({'in_wishlist': added})

@app.route('/api/books/<int:book_id>/note', methods=['GET', 'POST'])
@login_required
def api_book_note(book_id):
    user_id = session['user']['id']
    if request.method == 'POST':
        data = request.get_json()
        update_book_note(user_id, book_id, data.get('content', ''))
        return jsonify({'message': 'Nota guardada'})
    return jsonify({'content': get_book_note(user_id, book_id)})

@app.route('/api/books/fetch-by-isbn', methods=['GET'])
def api_fetch_by_isbn():
    import urllib.request, json as json_module
    isbn = request.args.get('isbn', '').replace('-', '')
    if not isbn:
        return jsonify({'error': 'ISBN requerido'}), 400
    try:
        # Open Library API (no requiere key)
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json_module.loads(resp.read())
        key = f"ISBN:{isbn}"
        if key not in data or not data[key]:
            return jsonify({'error': 'No se encontró libro con ese ISBN'}), 404
        info = data[key]
        return jsonify({
            'title': info.get('title', ''),
            'author': ', '.join(a.get('name', '') for a in info.get('authors', [])),
            'year': str(info.get('publish_date', ''))[:4],
            'genre': ', '.join(s.get('name', '') for s in info.get('subjects', [])[:3]),
            'description': '',
            'language': '',
            'pages': info.get('number_of_pages', '')
        })
    except Exception as e:
        print(f"Error fetching ISBN: {e}")
        return jsonify({'error': 'Error al buscar el ISBN'}), 502

if __name__ == '__main__':
    app.run(debug=True)

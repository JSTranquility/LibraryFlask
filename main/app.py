import flask as fk
from flask import request, jsonify, render_template, session, redirect, url_for, flash
from flask_cors import CORS
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
    return dict(user=session.get('user'))

@app.route('/')
def index():
    return render_template('index.html', active_page='index')

@app.route('/catalog')
def catalog():
    return render_template('catalog.html', active_page='catalog')

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
    # Solo permitir ver su propio perfil o si es admin
    if session['user']['username'] != username and session['user']['role'] != 'admin':
        return redirect(url_for('index'))
        
    user = get_user(username)
    if user:
        books = get_all_books()
        return render_template('user.html', user=user, books=books, active_page='user')
    return "User not found", 404

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = get_book_by_id(book_id)
    if book:
        return render_template('book_details.html', book=book)
    return "Libro no encontrado", 404

# --- API Endpoints ---
# (Se mantienen protegidos o abiertos según necesidad, por ahora abiertos para las plantillas JS)
@app.route('/api/books', methods=['GET'])
def api_get_books():
    books = get_all_books()
    return jsonify(books)

@app.route('/api/books', methods=['POST'])
def api_create_book():
    # Soporte para JSON o FormData
    if request.is_json:
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        year = data.get('year')
        genre = data.get('genre')
        description = data.get('description', '')
        cover_filename = None
    else:
        title = request.form.get('title')
        author = request.form.get('author')
        year = request.form.get('year')
        genre = request.form.get('genre')
        description = request.form.get('description', '')
        isbn = request.form.get('isbn', '')
        language = request.form.get('language', '')
        format = request.form.get('format', '')
        pages = request.form.get('pages', '')
        
        cover_file = request.files.get('cover')
        cover_filename = None
        if cover_file and cover_file.filename != '':
            filename = secure_filename(cover_file.filename)
            # Add unique prefix to avoid collisions
            unique_filename = f"{os.urandom(8).hex()}_{filename}"
            cover_file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
            cover_filename = f"/static/uploads/{unique_filename}"

    if not title or not author or not year or not genre:
        return jsonify({'error': 'Missing required fields'}), 400

    add_book(title, author, year, genre, description, cover_filename, isbn, language, format, pages)
    return jsonify({'message': 'Book created successfully'}), 201

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def api_update_book(book_id):
    if not book_exists(book_id):
        return jsonify({'error': 'Book not found'}), 404
    
    if request.is_json:
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        year = data.get('year')
        genre = data.get('genre')
        description = data.get('description')
        cover_filename = None
    else:
        title = request.form.get('title')
        author = request.form.get('author')
        year = request.form.get('year')
        genre = request.form.get('genre')
        description = request.form.get('description')
        isbn = request.form.get('isbn')
        language = request.form.get('language')
        format = request.form.get('format')
        pages = request.form.get('pages')
        
        cover_file = request.files.get('cover')
        cover_filename = None
        if cover_file and cover_file.filename != '':
            filename = secure_filename(cover_file.filename)
            unique_filename = f"{os.urandom(8).hex()}_{filename}"
            cover_file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
            cover_filename = f"/static/uploads/{unique_filename}"
    
    update_book_in_db(book_id, title, author, year, genre, description, cover_filename, isbn, language, format, pages)
    return jsonify({'message': 'Book updated successfully'}), 200

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def api_delete_book(book_id):
    if not book_exists(book_id):
        return jsonify({'error': 'Book not found'}), 404
    delete_book(book_id)
    return jsonify({'message': 'Book deleted successfully'}), 200

@app.route('/api/users', methods=['GET'])
def api_get_users():
    users = get_all_users()
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
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
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/users/<string:username>', methods=['DELETE'])
def api_delete_user(username):
    if not user_exists(username):
        return jsonify({'error': 'User not found'}), 404

    delete_user(username)

    return jsonify({'message': 'User deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)

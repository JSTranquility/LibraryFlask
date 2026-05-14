# Vellum

Aplicación web de biblioteca/catálogo literario construida con Python y Flask.

## Funcionalidades

- **Catálogo** con búsqueda, filtros combinados (género, idioma, año), paginación y toggle vista grid/lista
- **Detalle de libro** con reseñas, estado de lectura, favoritos y link de compra (Amazon)
- **Autenticación** de usuarios con roles (admin / user)
- **Panel de administración** con dashboard, gráficos, gestión de usuarios y libros, y registro de actividad
- **Comunidad** con posts, comentarios y sistema de seguidores
- **API REST pública** con endpoints documentados en `/api/docs`
- **Búsqueda por ISBN** usando Open Library API

## Estructura

```
├── main/
│   ├── app.py          # Aplicación Flask (rutas y API)
│   ├── books.py        # Lógica de libros
│   └── db.py           # Conexión y operaciones de base de datos
├── templates/          # Vistas HTML
│   └── includes/       # Fragmentos (navbar, footer)
├── static/             # CSS, imágenes
│   └── uploads/        # Imágenes subidas por usuarios
└── library.db          # Base de datos SQLite (se crea automáticamente)
```

## Requisitos

- Python 3.9+
- Flask
- Flask-CORS
- Werkzeug

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask flask-cors werkzeug
python .\main\app.py
```

Abrir en `http://127.0.0.1:5000/`

## Usuarios iniciales

| Usuario | Contraseña | Rol  |
|---------|-----------|------|
| admin   | admin123  | admin |
| user    | user123   | user |

## API Pública

La documentación interactiva está disponible en `/api/docs`. Endpoints públicos:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/books` | Todos los libros |
| GET | `/api/books/<id>` | Detalle de un libro |
| GET | `/api/books/paginated` | Catálogo paginado con filtros |
| GET | `/api/books/<id>/reviews` | Reseñas de un libro |
| GET | `/api/books/fetch-by-isbn` | Buscar por ISBN |
| GET | `/api/stats/reviews` | Total de reseñas |

## Notas

- La base de datos SQLite (`library.db`) se crea automáticamente al iniciar
- Los uploads de imágenes se guardan en `static/uploads/`
- El panel admin solo es accesible para usuarios con rol `admin`

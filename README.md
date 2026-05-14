# Librería

Aplicación web de biblioteca construida con Python y Flask.

## Descripción

Esta aplicación permite gestionar libros y usuarios con una interfaz web. Incluye:

- Catálogo de libros
- Detalles de cada libro
- Autenticación de usuarios
- Panel de administrador para gestionar usuarios y libros
- API REST básica para libros y usuarios

## Estructura del proyecto

- `main/app.py`: aplicación Flask principal
- `main/books.py`: lógica de libros y funciones de inicialización
- `main/db.py`: conexión y operaciones de base de datos
- `templates/`: vistas de Flask en HTML
- `static/`: archivos estáticos como CSS e imágenes
- `library.db`: base de datos SQLite local (se crea automáticamente)

## Requisitos

- Python 3.9+ recomendado
- Flask
- Flask-CORS
- Werkzeug

## Instalación

1. Crear y activar un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install flask flask-cors werkzeug
```

3. Iniciar la aplicación:

```powershell
python .\main\app.py
```

4. Abrir en el navegador:

```text
http://127.0.0.1:5000/
```

## Usuarios iniciales

La aplicación crea automáticamente los siguientes usuarios en la base de datos SQLite:

- `admin` / `admin123` (rol: admin)
- `user` / `user123` (rol: user)

## Notas

- Si la base de datos ya existe, no se sobrescribe.
- La aplicación usa `library.db` en la raíz del proyecto.
- El panel de administrador solo es accesible para el usuario con rol `admin`.

## Mejoras recomendadas

- Añadir un archivo `requirements.txt`
- Añadir validación de formularios en el frontend
- Proteger las rutas de API con autenticación
- Añadir encriptado HTTPS para producción

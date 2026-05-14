import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'main'))

from app import app as flask_app
from db import create_database, database_connect

@pytest.fixture
def app():
    create_database()
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    data = r.get_json()
    assert data['status'] == 'ok'

def test_get_books(client):
    r = client.get('/api/books')
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_get_book_not_found(client):
    r = client.get('/api/books/9999')
    assert r.status_code == 404

def test_paginated(client):
    r = client.get('/api/books/paginated?page=1&per_page=5')
    assert r.status_code == 200
    data = r.get_json()
    assert 'books' in data
    assert 'total' in data
    assert 'total_pages' in data

def test_reviews(client):
    r = client.get('/api/books/1/reviews')
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_stats_reviews(client):
    r = client.get('/api/stats/reviews')
    assert r.status_code == 200

def test_fetch_isbn_missing(client):
    r = client.get('/api/books/fetch-by-isbn')
    assert r.status_code == 400

def test_index(client):
    r = client.get('/')
    assert r.status_code == 200

def test_catalog(client):
    r = client.get('/catalog')
    assert r.status_code == 200

def test_login_page(client):
    r = client.get('/login')
    assert r.status_code == 200

def test_api_docs(client):
    r = client.get('/api/docs')
    assert r.status_code == 200

# Todo App

A Full Stack Todo Application built with Python, FastAPI and JWT Authentication.

## Live Demo
API: https://todoapp-pravalika.onrender.com
Docs: https://todoapp-pravalika.onrender.com/docs

## Tech Stack
- Python
- FastAPI
- SQLite
- SQLAlchemy
- JWT Tokens
- Bcrypt (password hashing)
- HTML + CSS + JavaScript (frontend)

## Endpoints

### Auth
- POST /signup — create new account
- POST /login — login and get JWT token

### Todos (requires login)
- POST /todos — create a todo
- GET /todos — get your todos
- PUT /todos/{id} — mark todo as completed
- DELETE /todos/{id} — delete a todo

## How to run
1. Install packages: pip install fastapi uvicorn sqlalchemy python-jose passlib bcrypt aiofiles
2. Run: python -m uvicorn main:app --reload
3. Open: http://127.0.0.1:8000/app

## GitHub
https://github.com/Paleti-Pravalika/todo-app

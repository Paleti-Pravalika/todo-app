from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from passlib.context import CryptContext

# Database setup
DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

# Tables
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schemas
class UserSignup(BaseModel):
    email: str
    password: str

# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Todo App is running!"}

# SIGNUP
@app.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    
    # Save user to database
    new_user = User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Account created successfully", "email": new_user.email}
from jose import jwt
from datetime import datetime, timedelta

# Secret key for JWT token
SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"

class UserLogin(BaseModel):
    email: str
    password: str

# LOGIN
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Check if email exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not found")
    
    # Check if password is correct
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Wrong password")
    
    # Create JWT token
    token_data = {
        "user_id": db_user.id,
        "email": db_user.email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"token": token, "email": db_user.email}
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get current logged in user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        email = payload.get("email")
        return {"user_id": user_id, "email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Todo schema
class TodoCreate(BaseModel):
    title: str
    description: str

# CREATE TODO
@app.post("/todos")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    new_todo = Todo(
        title=todo.title,
        description=todo.description,
        completed=False,
        user_id=current_user["user_id"]
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# GET ALL TODOS (only current user's todos)
@app.get("/todos")
def get_todos(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    todos = db.query(Todo).filter(Todo.user_id == current_user["user_id"]).all()
    return todos
# UPDATE TODO (mark as completed)
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user["user_id"]).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.completed = True
    db.commit()
    db.refresh(todo)
    return todo

# DELETE TODO
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user["user_id"]).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
import hashlib
import os

router = APIRouter()

DB_PATH = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            phone TEXT,
            role TEXT DEFAULT 'farmer'
        )
    ''')
    # Try to add phone column if it doesn't exist (for existing databases)
    try:
        conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists

    conn.execute('''
        CREATE TABLE IF NOT EXISTS soil_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            n REAL,
            p REAL,
            k REAL,
            ph REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    # Create default admin if not exists
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = 'admin@soil.com'")
    if not cursor.fetchone():
        hashed_admin = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            ("admin@soil.com", hashed_admin, "System Admin", "admin")
        )
    conn.commit()
    conn.close()

# Hash password
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class UserSignup(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "farmer" # 'farmer' or 'admin'

class UserLogin(BaseModel):
    email: str
    password: str

class UpdateProfile(BaseModel):
    user_id: int
    full_name: str
    email: str
    phone: str = None

class ChangePassword(BaseModel):
    user_id: int
    current_password: str
    new_password: str


@router.on_event("startup")
def startup():
    init_db()

@router.post("/auth/signup")
def signup(user: UserSignup):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed = hash_password(user.password)
        
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (user.email, hashed, user.full_name, user.role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {"message": "User created successfully", "user_id": user_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/login")
def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = hash_password(user.password)
    
    cursor.execute(
        "SELECT id, email, full_name, role, phone FROM users WHERE email = ? AND password_hash = ?",
        (user.email, hashed)
    )
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return {
            "message": "Login successful",
            "user": {
                "id": user_data['id'],
                "email": user_data['email'],
                "full_name": user_data['full_name'],
                "role": user_data['role'],
                "phone": user_data['phone']
            }
        }

    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.put("/auth/update-profile")
def update_profile(data: UpdateProfile):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET full_name = ?, email = ?, phone = ? WHERE id = ?",
            (data.full_name, data.email, data.phone, data.user_id)
        )
        conn.commit()
        
        # Fetch updated user
        cursor.execute("SELECT id, email, full_name, role, phone FROM users WHERE id = ?", (data.user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": user_data['id'],
                "email": user_data['email'],
                "full_name": user_data['full_name'],
                "role": user_data['role'],
                "phone": user_data['phone']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/auth/change-password")
def change_password(data: ChangePassword):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify current password
    current_hashed = hash_password(data.current_password)
    cursor.execute("SELECT id FROM users WHERE id = ? AND password_hash = ?", (data.user_id, current_hashed))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid current password")
    
    # Update password
    new_hashed = hash_password(data.new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hashed, data.user_id))
    conn.commit()
    conn.close()
    
    return {"message": "Password changed successfully"}


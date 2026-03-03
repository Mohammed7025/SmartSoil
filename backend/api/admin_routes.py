from fastapi import APIRouter, HTTPException
import sqlite3
from typing import List

router = APIRouter()
DB_PATH = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/admin/users")
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, role FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

@router.get("/admin/users/{user_id}/history")
def get_user_history(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Get User Profile
    cursor.execute("SELECT id, email, full_name, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
        
    # 2. Get Soil History
    cursor.execute("SELECT * FROM soil_history WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    history = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "user": dict(user),
        "history": history
    }

# Endpoint to save soil data (simulate a farmer saving their data)
from pydantic import BaseModel
class SoilData(BaseModel):
    user_id: int
    n: float
    p: float
    k: float
    ph: float

@router.post("/user/save_soil")
def save_soil_data(data: SoilData):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO soil_history (user_id, n, p, k, ph) VALUES (?, ?, ?, ?, ?)",
        (data.user_id, data.n, data.p, data.k, data.ph)
    )
    conn.commit()
    conn.close()
    return {"message": "Soil data saved"}

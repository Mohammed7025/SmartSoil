from fastapi import APIRouter, HTTPException, Depends, Header
import sqlite3
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()
DB_PATH = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Mock Auth Dependency (In a real app, use JWT)
async def get_current_admin(requester_id: Optional[int] = Header(None, alias="user-id")):
    if requester_id is None:
        raise HTTPException(status_code=401, detail="User ID required")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (requester_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return requester_id

@router.get("/admin/users")
def get_all_users(admin_id: int = Depends(get_current_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, role FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

@router.delete("/admin/users/{target_user_id}")
def delete_user(target_user_id: int, admin_id: int = Depends(get_current_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE id = ?", (target_user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
        
    # Delete user and history
    cursor.execute("DELETE FROM soil_history WHERE user_id = ?", (target_user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (target_user_id,))
    
    conn.commit()
    conn.close()
    return {"message": f"User {target_user_id} and their data deleted successfully"}

@router.get("/admin/users/{user_id}/history")
def get_user_history(user_id: int, admin_id: int = Depends(get_current_admin)):
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

@router.get("/admin/stats")
def get_system_stats(admin_id: int = Depends(get_current_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM users")
    total_users = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM soil_history")
    total_readings = cursor.fetchone()['total']
    
    # Mock activity logic for now
    cursor.execute("SELECT COUNT(DISTINCT user_id) as active FROM soil_history WHERE timestamp > date('now', '-7 days')")
    active_users = cursor.fetchone()['active']
    
    conn.close()
    return {
        "total_users": total_users,
        "total_readings": total_readings,
        "active_users_7d": active_users
    }

# Endpoint to save soil data (simulate a farmer saving their data)
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

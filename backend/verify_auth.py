import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_and_admin():
    print("--- Testing Auth & Admin ---")
    
    # 1. Signup Admin
    admin_email = "admin@smartsoil.com"
    password = "adminpassword"
    try:
        res = requests.post(f"{BASE_URL}/auth/signup", json={
            "email": admin_email,
            "password": password,
            "full_name": "Super Admin",
            "role": "admin"
        })
        print(f"Signup Admin: {res.status_code} - {res.json()}")
    except Exception as e:
        print(f"Signup Admin Failed (might already exist): {e}")

    # 2. Login Admin
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": admin_email,
            "password": password
        })
        print(f"Login Admin: {res.status_code}")
        if res.status_code == 200:
            user = res.json()['user']
            print(f"Logged in as: {user['full_name']} ({user['role']})")
            
            # 3. Test Admin Endpoint (List Users)
            # Note: My simple auth doesn't use tokens for the GET request yet, 
            # as I didn't implement JWT middleware for simplicity in this iteration.
            # The frontend checks the role from local storage, and the backend endpoint 
            # currently is open (prototype) or would need a token.
            # Let's check if the endpoint works.
            res_users = requests.get(f"{BASE_URL}/admin/users")
            print(f"Get Users: {res_users.status_code}")
            if res_users.status_code == 200:
                print(f"Users Found: {len(res_users.json())}")
                print(res_users.json())
        else:
            print("Login failed")
            
    except Exception as e:
        print(f"Login/Admin Test Failed: {e}")

if __name__ == "__main__":
    test_auth_and_admin()

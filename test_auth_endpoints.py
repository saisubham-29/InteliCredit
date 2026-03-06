import requests
import time

BASE_URL = "http://localhost:8000"

def test_auth():
    print("Testing Registration...")
    reg_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    try:
        res = requests.post(f"{BASE_URL}/register", json=reg_data)
        print(f"Registration Status: {res.status_code}")
        print(f"Registration Body: {res.json()}")
    except Exception as e:
        print(f"Registration Error: {e}")

    print("\nTesting Token Generation (Login)...")
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    try:
        res = requests.post(f"{BASE_URL}/token", data=login_data)
        print(f"Login Status: {res.status_code}")
        if res.status_code == 200:
            token = res.json()["access_token"]
            print(f"Token received: {token[:20]}...")
            
            print("\nTesting Protected Endpoint (/companies)...")
            headers = {"Authorization": f"Bearer {token}"}
            res_comp = requests.get(f"{BASE_URL}/companies", headers=headers)
            print(f"Companies Status: {res_comp.status_code}")
            print(f"Companies count: {len(res_comp.json())}")
        else:
            print(f"Login failed: {res.text}")
    except Exception as e:
        print(f"Login Error: {e}")

if __name__ == "__main__":
    test_auth()

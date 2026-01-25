#!/usr/bin/env python3
"""Quick API test."""
import httpx
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    response = httpx.get(f"{BASE_URL}/health")
    print(f"Health: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_register():
    """Test user registration."""
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!"
    }
    response = httpx.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"Register: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"  Success: {response.json()}")
        return True, response.json().get("access_token")
    else:
        print(f"  Error: {response.text}")
        return False, None

def test_login():
    """Test user login."""
    data = {
        "username": "testuser",
        "password": "TestPass123!"
    }
    response = httpx.post(f"{BASE_URL}/api/auth/login", data=data)
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"  Success: Token received")
        return True, result.get("access_token")
    else:
        print(f"  Error: {response.text}")
        return False, None

if __name__ == "__main__":
    print("Testing Cyber Sensei API...")
    print("=" * 50)
    
    # Test health
    health_ok = test_health()
    
    # Test registration
    reg_ok, token = test_register()
    
    # If registration failed, try login
    if not reg_ok:
        login_ok, token = test_login()
    
    print("=" * 50)
    if health_ok:
        print("✅ Health check passed")
    else:
        print("❌ Health check failed")
    
    if token:
        print("✅ Authentication working")
    else:
        print("❌ Authentication failed")

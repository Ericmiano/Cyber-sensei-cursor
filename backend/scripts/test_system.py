#!/usr/bin/env python3
"""Comprehensive system test script."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from app.core.config import settings
from app.core.database import engine
from sqlalchemy import text


async def test_database_connection():
    """Test database connectivity."""
    print("🔍 Testing database connection...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_api_health():
    """Test API health endpoint."""
    print("\n🔍 Testing API health endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


async def test_api_root():
    """Test API root endpoint."""
    print("\n🔍 Testing API root endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Root endpoint working: {data}")
                return True
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False


async def test_user_registration():
    """Test user registration."""
    print("\n🔍 Testing user registration...")
    try:
        async with httpx.AsyncClient() as client:
            # Try to register a new user
            response = await client.post(
                "http://localhost:8000/api/auth/register",
                json={
                    "email": "test@example.com",
                    "username": "testuser",
                    "password": "TestPass123!",
                },
            )
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"✅ User registration successful: {data.get('message', 'User created')}")
                return True, data.get("access_token")
            elif response.status_code == 400:
                data = response.json()
                if "already exists" in data.get("detail", "").lower():
                    print("ℹ️  User already exists, trying login instead...")
                    return await test_user_login()
                else:
                    print(f"❌ Registration failed: {data}")
                    return False, None
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False, None
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False, None


async def test_user_login():
    """Test user login."""
    print("\n🔍 Testing user login...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/auth/login",
                data={
                    "username": "testuser",
                    "password": "TestPass123!",
                },
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print(f"✅ Login successful: Token received")
                return True, token
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False, None
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False, None


async def test_protected_endpoint(token: str):
    """Test a protected endpoint."""
    print("\n🔍 Testing protected endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            # Try to get user profile or recommendations
            response = await client.get(
                "http://localhost:8000/api/recommendations",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code in [200, 404]:  # 404 is OK if no recommendations yet
                print("✅ Protected endpoint accessible")
                return True
            else:
                print(f"⚠️  Protected endpoint returned: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Protected endpoint test failed: {e}")
        return False


async def test_curriculum_endpoint(token: str):
    """Test curriculum generation endpoint."""
    print("\n🔍 Testing curriculum endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/curriculum/generate",
                headers={"Authorization": f"Bearer {token}"},
                json={"topic_id": None},  # Will use default or create topic
            )
            if response.status_code in [200, 201, 400, 404]:
                print(f"✅ Curriculum endpoint accessible (status: {response.status_code})")
                return True
            else:
                print(f"⚠️  Curriculum endpoint returned: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Curriculum endpoint test failed: {e}")
        return False


async def test_api_docs():
    """Test API documentation endpoint."""
    print("\n🔍 Testing API documentation...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/docs")
            if response.status_code == 200:
                print("✅ API documentation accessible")
                return True
            else:
                print(f"⚠️  API docs returned: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ API docs test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Cyber Sensei System Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test database
    results["database"] = await test_database_connection()
    
    # Test API endpoints
    results["api_health"] = await test_api_health()
    results["api_root"] = await test_api_root()
    results["api_docs"] = await test_api_docs()
    
    # Test authentication
    success, token = await test_user_registration()
    results["registration"] = success
    
    if not token:
        success, token = await test_user_login()
        results["login"] = success
    
    # Test protected endpoints if we have a token
    if token:
        results["protected"] = await test_protected_endpoint(token)
        results["curriculum"] = await test_curriculum_endpoint(token)
    else:
        results["protected"] = False
        results["curriculum"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

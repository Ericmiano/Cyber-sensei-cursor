#!/usr/bin/env python3
"""Demo script to test the API."""
import httpx
import json
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health():
    print_section("1. Health Check")
    response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_root():
    print_section("2. Root Endpoint")
    response = httpx.get(f"{BASE_URL}/", timeout=5.0)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_register():
    print_section("3. User Registration")
    data = {
        "email": "demo@example.com",
        "username": "demouser",
        "password": "DemoPass123!"
    }
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/register",
            json=data,
            timeout=10.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True, None
        else:
            print(f"Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"Exception: {e}")
        return False, None

def test_login():
    print_section("4. User Login")
    data = {
        "username": "demo@example.com",  # OAuth2 uses 'username' field for email
        "password": "DemoPass123!"
    }
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/login",
            data=data,  # form data, not JSON
            timeout=10.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            token = result.get("access_token")
            print(f"\nAccess Token: {token[:50]}..." if token else "No token")
            return True, token
        else:
            print(f"Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"Exception: {e}")
        return False, None

def test_protected_endpoint(token):
    print_section("5. Protected Endpoint (Recommendations)")
    try:
        response = httpx.get(
            f"{BASE_URL}/api/recommendations",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 404]  # 404 is OK if no recommendations
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_api_docs():
    print_section("6. API Documentation")
    try:
        response = httpx.get(f"{BASE_URL}/docs", timeout=5.0)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("API Documentation is available at: http://localhost:8000/docs")
            return True
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("  CYBER SENSEI API DEMO")
    print("=" * 60)
    
    results = {}
    
    # Test basic endpoints
    results["health"] = test_health()
    results["root"] = test_root()
    results["api_docs"] = test_api_docs()
    
    # Test authentication
    reg_success, _ = test_register()
    results["register"] = reg_success
    
    login_success, token = test_login()
    results["login"] = login_success
    
    # Test protected endpoint
    if token:
        results["protected"] = test_protected_endpoint(token)
    else:
        results["protected"] = False
        print_section("5. Protected Endpoint")
        print("Skipped - No authentication token")
    
    # Summary
    print_section("Test Summary")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = "PASS" if passed_test else "FAIL"
        print(f"  {status:4} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! System is working correctly.")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed. Check the output above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

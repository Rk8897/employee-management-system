"""
Test authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

def test_login():
    """Test login endpoint"""
    print("\n🔐 Testing Login...")
    
    # Test 1: Successful login
    print("\n1️⃣  Test: Successful Login")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    print_response("Successful Login", response)
    
    if response.status_code == 200:
        token = response.json()['token']
        print(f"\n✅ Token received: {token[:50]}...")
        
        # Test 2: Verify token
        print("\n2️⃣  Test: Verify Token")
        response = requests.get(
            f"{BASE_URL}/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        print_response("Token Verification", response)
        
        if response.status_code == 200:
            print("\n✅ Token is valid!")
        else:
            print("\n❌ Token verification failed!")
        
        return token
    else:
        print("\n❌ Login failed!")
        return None

def test_invalid_login():
    """Test invalid login"""
    print("\n\n3️⃣  Test: Invalid Login")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "admin",
            "password": "wrongpassword"
        }
    )
    print_response("Invalid Login (Wrong Password)", response)
    
    if response.status_code == 401:
        print("\n✅ Correctly rejected invalid credentials!")
    else:
        print("\n❌ Should have rejected invalid credentials!")

def test_missing_token():
    """Test accessing protected endpoint without token"""
    print("\n\n4️⃣  Test: Missing Token")
    response = requests.get(f"{BASE_URL}/api/auth/verify")
    print_response("Verify Without Token", response)
    
    if response.status_code == 401:
        print("\n✅ Correctly rejected request without token!")
    else:
        print("\n❌ Should have required token!")

def main():
    print("\n" + "="*60)
    print("  🧪 Authentication API Test Suite")
    print("="*60)
    
    try:
        # Test basic connectivity
        print("\n📡 Checking API connectivity...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is running!")
        else:
            print("❌ API is not responding correctly")
            return
        
        # Run tests
        token = test_login()
        test_invalid_login()
        test_missing_token()
        
        print("\n" + "="*60)
        print("  ✅ All Authentication Tests Completed!")
        print("="*60)
        
        if token:
            print(f"\n💾 Save this token for next tests:")
            print(f"{token}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("Make sure Flask app is running: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
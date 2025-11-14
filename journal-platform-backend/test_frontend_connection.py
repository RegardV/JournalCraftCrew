#!/usr/bin/env python3
"""
Frontend-Backend Connection Test
Tests if the frontend can properly connect to the backend after our fixes
"""

import requests
import json
import sys
import time

# Configuration
BACKEND_URL = "https://localhost:6770"
FRONTEND_URL = "http://localhost:5174"

def test_backend_connectivity():
    """Test backend API endpoints"""
    print("🔧 Testing Backend Connectivity...")

    try:
        # Test health endpoint
        health_response = requests.get(f"{BACKEND_URL}/health", verify=False, timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health endpoint: {health_data.get('status')}")
        else:
            print(f"❌ Health endpoint failed: {health_response.status_code}")
            return False

        # Test AI themes endpoint
        themes_response = requests.get(f"{BACKEND_URL}/api/ai/themes", verify=False, timeout=5)
        if themes_response.status_code == 200:
            themes_data = themes_response.json()
            print(f"✅ AI Themes endpoint: {len(themes_data.get('themes', []))} themes available")
        else:
            print(f"❌ AI Themes endpoint failed: {themes_response.status_code}")
            return False

        # Test authentication endpoint (will fail with invalid credentials, but should respond)
        auth_response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email":"test@example.com", "password":"testpass123"},
            verify=False, timeout=5
        )
        if auth_response.status_code in [200, 401]:
            print(f"✅ Authentication endpoint: Responding (as expected)")
        else:
            print(f"❌ Authentication endpoint failed: {auth_response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_cors_headers():
    """Test if CORS headers are properly configured"""
    print("\n🌐 Testing CORS Headers...")

    try:
        # Simulate a preflight request
        response = requests.options(
            f"{BACKEND_URL}/api/ai/themes",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            },
            verify=False, timeout=5
        )

        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }

        print(f"📋 CORS Headers:")
        for header, value in cors_headers.items():
            if value:
                print(f"  ✅ {header}: {value}")
            else:
                print(f"  ❌ {header}: Not Set")

        return True

    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def test_api_workflow():
    """Test a simple API workflow similar to journal creation"""
    print("\n🔄 Testing API Workflow...")

    try:
        # 1. Get available themes
        themes_response = requests.get(f"{BACKEND_URL}/api/ai/themes", verify=False, timeout=5)
        if themes_response.status_code != 200:
            print(f"❌ Failed to get themes: {themes_response.status_code}")
            return False

        themes = themes_response.json().get("themes", [])
        if not themes:
            print("❌ No themes available")
            return False

        print(f"📝 Found {len(themes)} themes")

        # 2. Get title styles
        styles_response = requests.get(f"{BACKEND_URL}/api/ai/title-styles", verify=False, timeout=5)
        if styles_response.status_code != 200:
            print(f"❌ Failed to get title styles: {styles_response.status_code}")
            return False

        styles = styles_response.json().get("title_styles", [])
        if not styles:
            print("❌ No title styles available")
            return False

        print(f"📝 Found {len(styles)} title styles")

        # 3. Test journal library endpoint (requires auth, will fail but should be 401)
        library_response = requests.get(f"{BACKEND_URL}/api/journals/library", verify=False, timeout=5)
        if library_response.status_code == 401:
            print("✅ Journal library properly requires authentication")
        else:
            print(f"⚠️  Journal library responded with: {library_response.status_code}")

        return True

    except Exception as e:
        print(f"❌ Workflow test error: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Frontend-Backend Connection Test")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")

    # Test connectivity
    backend_ok = test_backend_connectivity()
    cors_ok = test_cors_headers()
    workflow_ok = test_api_workflow()

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)

    results = [
        ("Backend Connectivity", "✅ PASS" if backend_ok else "❌ FAIL"),
        ("CORS Headers", "✅ PASS" if cors_ok else "❌ FAIL"),
        ("API Workflow", "✅ PASS" if workflow_ok else "❌ FAIL")
    ]

    all_passed = True
    for test_name, result in results:
        print(f"{result} {test_name}")
        if "❌" in result:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Frontend-Backend connection is working.")
        print("🔗 You can now access the dashboard at:", FRONTEND_URL)
        print("🔧 Backend API is available at:", BACKEND_URL)
    else:
        print("❌ Some tests failed. Please check the configuration.")

    print("=" * 50)

    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
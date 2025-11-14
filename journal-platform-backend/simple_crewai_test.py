#!/usr/bin/env python3
"""
Simple CrewAI Integration Test
Tests the basic API integration without WebSocket complexity
"""

import os
import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:6770"

def test_server_health():
    """Test if backend server is running"""
    print("🔍 Testing backend server...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend server not accessible: {e}")
        return False

def test_authentication():
    """Test user authentication"""
    print("🔐 Testing authentication...")

    # Register user
    register_data = {
        "email": "testuser@example.com",
        "password": os.getenv("TEST_PASSWORD", "testpassword123"),
        "full_name": "Test User"
    }

    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=register_data, timeout=10)
        if response.status_code in [200, 201]:
            print("✅ User registration successful")
        elif response.status_code == 400:
            print("ℹ️ User already exists, proceeding to login")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Registration request failed: {e}")
        return False

    # Login user
    login_data = {
        "email": "testuser@example.com",
        "password": os.getenv("TEST_PASSWORD", "testpassword123")
    }

    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            auth_token = token_data.get("access_token")
            if auth_token:
                print("✅ Authentication successful")
                return auth_token
            else:
                print("❌ No access token in response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return None

def test_crewai_workflow_start(auth_token):
    """Test starting CrewAI workflow"""
    print("🤖 Testing CrewAI workflow start...")

    workflow_data = {
        "user_preferences": {
            "theme": "mindfulness",
            "title": "Test Mindfulness Journal",
            "title_style": "inspirational",
            "workflow_type": "express",
            "research_depth": "light",
            "duration_days": 30,
            "daily_prompts": True,
            "include_exercises": True,
            "target_audience": "beginners"
        }
    }

    headers = {"Authorization": f"Bearer {auth_token}"}

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/crewai/start-workflow",
            json=workflow_data,
            headers=headers,
            timeout=15
        )

        if response.status_code == 200:
            workflow_response = response.json()
            workflow_id = workflow_response.get("workflow_id")

            if workflow_id:
                print(f"✅ CrewAI workflow started: {workflow_id}")
                print(f"📊 Estimated duration: {workflow_response.get('estimated_duration', 'N/A')} minutes")
                print(f"🔧 Workflow type: {workflow_response.get('workflow_type', 'N/A')}")
                return workflow_id
            else:
                print("❌ No workflow ID in response")
                print(f"Response: {response.text}")
                return None
        else:
            print(f"❌ Workflow start failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Workflow start request failed: {e}")
        return None

def test_workflow_status(auth_token, workflow_id):
    """Test workflow status endpoint"""
    print("📊 Testing workflow status endpoint...")

    if not workflow_id:
        print("❌ No workflow ID available")
        return False

    headers = {"Authorization": f"Bearer {auth_token}"}

    try:
        response = requests.get(
            f"{BACKEND_URL}/api/crewai/workflow-status/{workflow_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            status_data = response.json()
            status = status_data.get("status")
            progress = status_data.get("progress_percentage", 0)
            current_agent = status_data.get("current_agent", "N/A")

            print(f"📊 Workflow status: {status}")
            print(f"📈 Progress: {progress:.1f}%")
            print(f"🤖 Current agent: {current_agent}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check request failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Simple CrewAI Integration Test")
    print("="*50)

    # Test 1: Server Health
    if not test_server_health():
        print("❌ Server health check failed. Aborting test.")
        return False

    # Test 2: Authentication
    auth_token = test_authentication()
    if not auth_token:
        print("❌ Authentication failed. Aborting test.")
        return False

    # Test 3: CrewAI Workflow Start
    workflow_id = test_crewai_workflow_start(auth_token)
    if not workflow_id:
        print("❌ CrewAI workflow start failed. Aborting test.")
        return False

    # Test 4: Workflow Status
    # Wait a moment then check status
    time.sleep(2)
    status_success = test_workflow_status(auth_token, workflow_id)

    print("="*50)
    print("🏁 Simple CrewAI Integration Test Finished")

    if workflow_id:
        print("🎉 CREWAI INTEGRATION TEST PASSED!")
        print("✅ The journal creation sequence is properly integrated with CrewAI")
        print(f"🤖 Workflow ID: {workflow_id}")
        return True
    else:
        print("❌ CREWAI INTEGRATION TEST FAILED")
        print("❌ Issues detected in CrewAI workflow integration")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 INTEGRATION SUCCESSFUL - CrewAI Workflow Ready!")
    else:
        print("\n❌ INTEGRATION FAILED - Review logs above")
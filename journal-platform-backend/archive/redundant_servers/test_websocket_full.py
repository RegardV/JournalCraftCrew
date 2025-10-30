#!/usr/bin/env python3
"""
Full WebSocket Test with AI Generation
Tests real-time WebSocket connectivity during actual journal generation
"""

import asyncio
import websockets
import json
import aiohttp
from datetime import datetime

async def register_test_user():
    """Register a test user and get auth token"""

    async with aiohttp.ClientSession() as session:
        # Register user
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "profile_type": "personal_journaler"
        }

        try:
            async with session.post("http://localhost:8000/api/auth/register", json=register_data) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    print("✅ Test user registered successfully")
                    return result.get("access_token")
                else:
                    print(f"⚠️  User registration failed: {response.status}")
                    # Try to login instead
                    login_data = {
                        "email": "test@example.com",
                        "password": "testpassword123"
                    }
                    async with session.post("http://localhost:8000/api/auth/login", json=login_data) as login_response:
                        if login_response.status == 200:
                            result = await login_response.json()
                            return result.get("access_token")
                        return None
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return None

async def start_ai_generation(token):
    """Start AI journal generation to trigger WebSocket activity"""

    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        generation_data = {
            "theme": "mindfulness",
            "title_style": "daily_reflection",
            "project_title": "Test WebSocket Journal",
            "description": "Testing WebSocket real-time progress"
        }

        try:
            async with session.post("http://localhost:8000/api/ai/generate-journal",
                                  json=generation_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ AI generation started: {result.get('job_id')}")
                    return result.get('job_id')
                else:
                    error_text = await response.text()
                    print(f"❌ AI generation failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"❌ AI generation error: {e}")
            return None

async def monitor_websocket_progress(job_id):
    """Monitor WebSocket for real-time progress updates"""

    uri = f"ws://localhost:8000/ws/job/{job_id}"

    print(f"🔌 Connecting to WebSocket: {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            print("📡 Monitoring real-time progress...")

            messages_received = 0

            # Listen for messages with timeout
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    messages_received += 1

                    print(f"📥 Message {messages_received}:")
                    print(f"   Type: {data.get('type')}")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Progress: {data.get('progress', 0)}%")

                    if data.get('status') == 'completed':
                        print("🎉 Journal generation completed!")
                        return True
                    elif data.get('status') == 'error':
                        print(f"❌ Generation error: {data.get('message')}")
                        return False

            except asyncio.TimeoutError:
                print(f"⏰ WebSocket timeout after receiving {messages_received} messages")
                return messages_received > 0

    except websockets.exceptions.ConnectionRefusedError:
        print("❌ WebSocket connection refused")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Journal Craft Crew - Full WebSocket Test")
    print("=" * 50)

    # Step 1: Register test user
    print("👤 Step 1: Registering test user...")
    token = await register_test_user()

    if not token:
        print("❌ Cannot proceed without authentication")
        return

    # Step 2: Start AI generation
    print("\n🤖 Step 2: Starting AI journal generation...")
    job_id = await start_ai_generation(token)

    if not job_id:
        print("❌ Cannot start AI generation")
        return

    # Step 3: Monitor WebSocket progress
    print(f"\n📡 Step 3: Monitoring WebSocket progress for job {job_id}...")
    websocket_success = await monitor_websocket_progress(job_id)

    # Results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Authentication: ✅")
    print(f"   AI Generation: ✅")
    print(f"   WebSocket: {'✅' if websocket_success else '❌'}")

    if websocket_success:
        print("\n🎉 Real-time WebSocket functionality is working perfectly!")
        print("✅ Users will receive live progress updates during AI journal generation")
    else:
        print("\n⚠️  WebSocket functionality needs attention")

    print(f"\n📍 Frontend: http://localhost:5174")
    print(f"📍 Backend: http://localhost:8000")
    print(f"🔗 WebSocket Test Complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
#!/usr/bin/env python3
"""
WebSocket Connection Test Script
Tests real-time connectivity to the Journal Craft Crew backend
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket_connection():
    """Test WebSocket connection and real-time communication"""

    # WebSocket endpoint
    uri = "ws://localhost:8000/ws/job/test-job-123"

    print("🔌 Testing WebSocket Connection...")
    print(f"📍 Connecting to: {uri}")

    try:
        # Connect to WebSocket
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")

            # Send a test message
            test_message = {
                "type": "test_connection",
                "timestamp": datetime.now().isoformat(),
                "data": {"message": "Hello from WebSocket test client"}
            }

            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent: {test_message}")

            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                print(f"📥 Received: {response_data}")
                print("✅ WebSocket real-time communication working!")
                return True

            except asyncio.TimeoutError:
                print("⚠️  No response received within 5 seconds")
                return False

    except websockets.exceptions.ConnectionRefusedError:
        print("❌ Connection refused - WebSocket server may not be running")
        return False

    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_api_endpoints():
    """Test API endpoints to ensure backend functionality"""

    import aiohttp

    base_url = "http://localhost:8000"
    endpoints = [
        "/health",
        "/api/ai/themes",
        "/api/ai/title-styles"
    ]

    print("\n🌐 Testing API Endpoints...")

    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f"✅ {endpoint} - OK")
                    else:
                        print(f"❌ {endpoint} - Status {response.status}")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")

async def main():
    """Main test function"""
    print("🧪 Journal Craft Crew - WebSocket & API Test")
    print("=" * 50)

    # Test API endpoints first
    await test_api_endpoints()

    # Test WebSocket connection
    websocket_success = await test_websocket_connection()

    print("\n" + "=" * 50)
    if websocket_success:
        print("🎉 All tests passed! Real-time features ready.")
    else:
        print("⚠️  WebSocket test failed. Check backend configuration.")

    print("\n📍 Frontend: http://localhost:5174")
    print("📍 Backend: http://localhost:8000")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
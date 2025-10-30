#!/usr/bin/env python3
"""
Simple WebSocket Test with Real AI Generation
"""

import asyncio
import websockets
import json
import aiohttp
from datetime import datetime

async def test_realtime_generation():
    """Test real WebSocket connectivity during AI generation"""

    # Auth token from login
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl84MTVkYzQxZTAzYzEiLCJleHAiOjE3NjE4MjQ4NTZ9.HvnbIsk2EnTKxInI3SaSyadmw1oWhZC1TX3gwePZX10"
    headers = {"Authorization": f"Bearer {token}"}

    print("🤖 Starting AI journal generation...")

    # Step 1: Start AI generation
    async with aiohttp.ClientSession() as session:
        generation_data = {
            "theme": "mindfulness",
            "title_style": "daily_reflection",
            "project_title": "WebSocket Test Journal",
            "description": "Testing real-time WebSocket progress"
        }

        async with session.post("http://localhost:8000/api/ai/generate-journal",
                              json=generation_data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                job_id = result.get('job_id')
                print(f"✅ Generation started! Job ID: {job_id}")
                return job_id
            else:
                error_text = await response.text()
                print(f"❌ Generation failed: {error_text}")
                return None

async def monitor_websocket(job_id):
    """Monitor WebSocket for real-time updates"""

    uri = f"ws://localhost:8000/ws/job/{job_id}"
    print(f"🔌 Connecting to WebSocket: {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            print("📡 Listening for real-time updates...")

            message_count = 0
            start_time = datetime.now()

            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                    data = json.loads(message)
                    message_count += 1
                    elapsed = (datetime.now() - start_time).total_seconds()

                    print(f"\n📥 Message {message_count} (after {elapsed:.1f}s):")
                    print(f"   Type: {data.get('type', 'unknown')}")
                    print(f"   Status: {data.get('status', 'unknown')}")

                    if 'progress' in data:
                        print(f"   Progress: {data['progress']}%")

                    if 'message' in data:
                        print(f"   Message: {data['message']}")

                    if data.get('status') == 'completed':
                        print("\n🎉 Journal generation completed successfully!")
                        print(f"📊 Total messages received: {message_count}")
                        print(f"⏱️  Total time: {elapsed:.1f} seconds")
                        return True

                    elif data.get('status') == 'error':
                        print(f"\n❌ Generation failed: {data.get('message')}")
                        return False

            except asyncio.TimeoutError:
                print(f"\n⏰ WebSocket timeout after {message_count} messages")
                return message_count > 0

    except websockets.exceptions.ConnectionRefusedError:
        print("❌ WebSocket connection refused")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 WebSocket Real-Time Test")
    print("=" * 40)

    # Start AI generation
    job_id = await test_realtime_generation()

    if not job_id:
        print("❌ Cannot test WebSocket without AI generation")
        return

    # Monitor WebSocket progress
    print(f"\n📡 Monitoring WebSocket for job: {job_id}")
    success = await monitor_websocket(job_id)

    print("\n" + "=" * 40)
    if success:
        print("✅ WebSocket real-time connectivity TEST PASSED!")
        print("🎯 Users will receive live progress updates")
    else:
        print("⚠️  WebSocket test had issues")

    print(f"\n🌐 Frontend: http://localhost:5174")
    print(f"🔧 Backend: http://localhost:8000")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
#!/usr/bin/env python3
"""
Test script to verify AI workflow messages are working properly.
"""
import asyncio
import websockets
import json
import requests
import time

async def test_websocket_connection():
    """Test WebSocket connection and message flow."""

    # First, create a journal session to get a job_id
    try:
        # Create a simple test journal request without auth for testing
        response = requests.post(
            "http://localhost:6770/api/journals/create",
            json={
                "title": "Test Journal for AI Workflow",
                "theme": "Mindfulness and Personal Growth",
                "titleStyle": "Catchy Questions",
                "authorStyle": "inspirational narrative",
                "researchDepth": "medium",
                "customInstructions": "Test journal to verify AI workflow messages are displaying properly"
            },
            headers={"Content-Type": "application/json"}
        )

        print(f"Journal creation response status: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')

            if job_id:
                print(f"✅ Created journal job: {job_id}")

                # Test WebSocket connection
                ws_url = f"ws://localhost:6770/ws/journal/{job_id}"
                print(f"🔌 Connecting to WebSocket: {ws_url}")

                try:
                    async with websockets.connect(ws_url) as websocket:
                        print(f"✅ WebSocket connected for job: {job_id}")

                        # Listen for messages
                        message_count = 0
                        while message_count < 10:  # Listen for first 10 messages
                            try:
                                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                                print(f"📨 Message {message_count + 1}: {message}")

                                # Parse and display message structure
                                msg_data = json.loads(message)
                                print(f"   Type: {msg_data.get('type')}")
                                print(f"   Status: {msg_data.get('status')}")
                                print(f"   Progress: {msg_data.get('progress_percentage')}")
                                print(f"   Message: {msg_data.get('message')}")
                                print(f"   Agent: {msg_data.get('currentAgent')}")
                                print(f"   Thinking: {msg_data.get('thinking')}")
                                print(f"   Output: {msg_data.get('output')}")
                                print("---")

                                message_count += 1

                            except asyncio.TimeoutError:
                                print("⏰ No more messages received, ending test")
                                break
                            except websockets.exceptions.ConnectionClosed:
                                print("🔌 WebSocket connection closed")
                                break

                except Exception as e:
                    print(f"❌ WebSocket connection error: {e}")
            else:
                print("❌ No job_id in response")
        else:
            print(f"❌ Failed to create journal: {response.status_code}")

    except Exception as e:
        print(f"❌ Error in test: {e}")

if __name__ == "__main__":
    print("🧪 Testing AI Workflow WebSocket Messages")
    print("=" * 50)

    asyncio.run(test_websocket_connection())
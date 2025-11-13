#!/usr/bin/env python3
"""
Test CrewAI WebSocket Connection
Tests the real-time CrewAI workflow progress tracking
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_crewai_websocket():
    """Test the CrewAI WebSocket connection"""

    # Test workflow ID
    workflow_id = "test-workflow-123"

    try:
        print(f"🤖 Testing CrewAI WebSocket connection...")
        print(f"📍 Connecting to: ws://localhost:6770/ws/crewai/{workflow_id}")

        # Connect to CrewAI WebSocket
        uri = f"ws://localhost:6770/ws/crewai/{workflow_id}"
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to CrewAI WebSocket!")

            # Track messages
            message_count = 0
            message_types = set()

            # Listen for messages (timeout after 35 seconds)
            try:
                while message_count < 10:  # Collect up to 10 messages
                    try:
                        # Wait for message with timeout
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)

                        message_count += 1
                        message_type = data.get('type', 'unknown')
                        message_types.add(message_type)

                        print(f"\n📨 Message {message_count}: {message_type}")
                        print(f"   Timestamp: {data.get('timestamp', 'N/A')}")

                        if message_type == "workflow_start":
                            print(f"   🚀 Workflow Started: {workflow_id}")
                            agents = data.get('crew_agents', [])
                            print(f"   🤖 Crew Agents: {', '.join(agents)}")

                        elif message_type == "agent_progress":
                            agent = data.get('current_agent', 'Unknown')
                            progress = data.get('progress_percentage', 0)
                            step = data.get('current_step', 0)
                            total = data.get('total_steps', 0)
                            print(f"   🤖 Agent: {agent}")
                            print(f"   📊 Progress: {progress}% (Step {step}/{total})")
                            print(f"   💬 Message: {data.get('message', 'N/A')}")

                        elif message_type == "workflow_complete":
                            print(f"   🎉 Workflow Complete!")
                            result = data.get('result_data', {})
                            print(f"   📄 Output: {result.get('file_path', 'N/A')}")
                            print(f"   📊 Word Count: {result.get('word_count', 'N/A')}")
                            print(f"   📖 Pages: {result.get('pages', 'N/A')}")
                            break

                        elif message_type == "heartbeat":
                            print(f"   💓 Heartbeat: {data.get('message', 'N/A')}")

                        elif message_type == "error":
                            print(f"   ❌ Error: {data.get('message', 'N/A')}")

                        else:
                            print(f"   ℹ️  {data}")

                    except asyncio.TimeoutError:
                        print(f"⏰ Timeout waiting for message {message_count + 1}")
                        break

            except Exception as e:
                print(f"❌ Error receiving messages: {e}")

            print(f"\n📊 SUMMARY:")
            print(f"   Total Messages: {message_count}")
            print(f"   Message Types: {', '.join(sorted(message_types))}")
            print(f"   ✅ CrewAI WebSocket integration working!")

    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - is the backend server running?")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_standard_websocket():
    """Test the standard journal WebSocket for comparison"""

    job_id = "test-job-456"

    try:
        print(f"\n📡 Testing standard journal WebSocket...")
        print(f"📍 Connecting to: ws://localhost:6770/ws/journal/{job_id}")

        uri = f"ws://localhost:6770/ws/journal/{job_id}"
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to standard WebSocket!")

            # Listen for a few messages
            message_count = 0
            try:
                while message_count < 3:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                        data = json.loads(message)
                        message_count += 1

                        print(f"\n📨 Standard Message {message_count}: {data.get('type', 'unknown')}")
                        print(f"   💬 {data.get('message', 'N/A')}")

                    except asyncio.TimeoutError:
                        break

            except Exception as e:
                print(f"❌ Error receiving standard messages: {e}")

            print(f"   ✅ Standard WebSocket working!")

    except Exception as e:
        print(f"❌ Standard WebSocket error: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting CrewAI WebSocket Integration Tests")
    print("=" * 60)

    # Test CrewAI WebSocket
    await test_crewai_websocket()

    # Test standard WebSocket
    await test_standard_websocket()

    print("\n" + "=" * 60)
    print("🎯 Tests Complete!")
    print("\n💡 To test with the frontend:")
    print("   1. Go to: http://localhost:5173")
    print("   2. Click 'Create New Journal'")
    print("   3. Start a journal creation workflow")
    print("   4. Watch the real-time CrewAI progress!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
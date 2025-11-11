#!/usr/bin/env python3
"""
Integrated test of AI workflow with proper WebSocket callback connection.
"""
import asyncio
import websockets
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'journal-platform-backend'))

from crewai_integration import journal_service
from unified_backend import manager

async def test_integrated_workflow():
    """Test workflow by creating a job WITH WebSocket callback."""

    print("🧪 Integrated AI Workflow Test with WebSocket Callback")
    print("=" * 60)

    # Create test preferences
    preferences = {
        "title": "Test Journal for AI Workflow",
        "theme": "Mindfulness and Personal Growth",
        "titleStyle": "Catchy Questions",
        "authorStyle": "inspirational narrative",
        "researchDepth": "medium",
        "customInstructions": "Test journal to verify AI workflow messages are displaying properly"
    }

    print("📝 Creating WebSocket progress callback...")

    # Create WebSocket progress callback (same as in the API)
    async def websocket_progress_callback(progress_update: dict):
        """Send progress updates to WebSocket clients"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in progress_update:
                from datetime import datetime
                progress_update['timestamp'] = datetime.now().isoformat()

            # Send message to WebSocket clients for this job
            await manager.send_progress(job_id, progress_update)
            print(f"📡 Sent progress update: {progress_update.get('status', 'unknown')} - {progress_update.get('message', 'no message')}")
        except Exception as e:
            print(f"❌ Error sending WebSocket progress: {e}")

    print("📝 Creating test job with WebSocket callback...")

    # Start journal creation WITH WebSocket callback
    job_id = await journal_service.start_journal_creation(
        preferences,
        api_key=None,  # We'll use demo mode since no API key
        progress_callback=websocket_progress_callback
    )

    print(f"✅ Created job: {job_id}")

    # Connect to WebSocket for this job
    ws_url = f"ws://localhost:6770/ws/journal/{job_id}"
    print(f"🔌 Connecting to WebSocket: {ws_url}")

    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ WebSocket connected for job: {job_id}")

            # Listen for messages
            message_count = 0
            while message_count < 30:  # Listen for first 30 messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                    print(f"\n📨 Message {message_count + 1}:")
                    print(f"Raw: {message[:200]}...")  # Truncate for readability

                    # Parse and display message structure
                    try:
                        msg_data = json.loads(message)
                        print(f"   Type: {msg_data.get('type')}")
                        print(f"   Status: {msg_data.get('status')}")
                        print(f"   Progress: {msg_data.get('progress_percentage')}%")
                        print(f"   Message: {msg_data.get('message')}")
                        print(f"   Agent: {msg_data.get('currentAgent')}")
                        print(f"   Stage: {msg_data.get('current_stage')}")
                        print(f"   Sequence: {msg_data.get('sequence')}")

                        # Check for enhanced message format
                        has_progress_percentage = 'progress_percentage' in msg_data
                        has_thinking = 'thinking' in msg_data
                        has_output = 'output' in msg_data
                        has_agent_details = 'currentAgent' in msg_data

                        if has_progress_percentage and has_thinking and has_output:
                            print(f"   ✅ Enhanced message format detected!")
                            print(f"      Thinking: {msg_data.get('thinking', 'N/A')[:80]}...")
                            print(f"      Output: {msg_data.get('output', 'N/A')[:80]}...")
                        elif msg_data.get('type') in ['connection', 'heartbeat']:
                            print(f"   ℹ️  System message: {msg_data.get('type')}")
                        else:
                            print(f"   ⚠️ Missing some enhanced fields")
                            print(f"      progress_percentage: {has_progress_percentage}")
                            print(f"      thinking: {has_thinking}")
                            print(f"      output: {has_output}")
                            print(f"      agent details: {has_agent_details}")

                    except json.JSONDecodeError:
                        print(f"   ❌ Invalid JSON format")

                    print("-" * 60)
                    message_count += 1

                except asyncio.TimeoutError:
                    print("⏰ No more messages received, ending test")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 WebSocket connection closed")
                    break

            # Check final job status
            final_status = journal_service.get_job_status(job_id)
            print(f"\n🏁 Final job status: {final_status}")

    except Exception as e:
        print(f"❌ WebSocket connection error: {e}")
        print(f"   Job details: {journal_service.get_job_status(job_id)}")

if __name__ == "__main__":
    asyncio.run(test_integrated_workflow())
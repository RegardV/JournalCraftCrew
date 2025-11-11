#!/usr/bin/env python3
"""
Final test to demonstrate enhanced AI workflow messages are working.
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

async def test_final_workflow():
    """Test workflow with fake API key to trigger enhanced progress simulation."""

    print("🧪 Final Test: Enhanced AI Workflow Messages")
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

            # Log that we sent the message
            status = progress_update.get('status', 'unknown')
            message = progress_update.get('message', 'no message')
            progress = progress_update.get('progress_percentage', 0)

            # Check for enhanced fields
            has_enhanced_fields = all(field in progress_update for field in [
                'progress_percentage', 'current_stage', 'sequence', 'thinking', 'output'
            ])

            if has_enhanced_fields:
                print(f"📡 Sent ENHANCED message: {status} ({progress}%) - {message}")
            else:
                print(f"📡 Sent basic message: {status} - {message}")

        except Exception as e:
            print(f"❌ Error sending WebSocket progress: {e}")

    print("📝 Creating test job with FAKE API key to trigger enhanced simulation...")

    # Start journal creation WITH FAKE API KEY to trigger enhanced simulation
    job_id = await journal_service.start_journal_creation(
        preferences,
        api_key="fake-api-key-to-trigger-llm-initialization",  # This will fail but trigger enhanced flow
        progress_callback=websocket_progress_callback
    )

    print(f"✅ Created job: {job_id}")

    # Connect to WebSocket for this job
    ws_url = f"ws://localhost:6770/ws/journal/{job_id}"
    print(f"🔌 Connecting to WebSocket: {ws_url}")

    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ WebSocket connected for job: {job_id}")
            print(f"🎯 Now listening for enhanced AI workflow messages...")

            # Listen for messages
            message_count = 0
            enhanced_message_count = 0
            while message_count < 25:  # Listen for first 25 messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=90.0)
                    print(f"\n{'='*80}")
                    print(f"📨 MESSAGE {message_count + 1}:")
                    print(f"{'='*80}")

                    # Parse and display message structure
                    try:
                        msg_data = json.loads(message)

                        # Display key fields
                        msg_type = msg_data.get('type', 'unknown')
                        status = msg_data.get('status', 'unknown')
                        progress = msg_data.get('progress_percentage', 0)
                        message_text = msg_data.get('message', 'no message')
                        agent = msg_data.get('currentAgent', 'none')
                        stage = msg_data.get('current_stage', 'none')
                        sequence = msg_data.get('sequence', 'none')
                        thinking = msg_data.get('thinking', 'none')
                        output = msg_data.get('output', 'none')

                        print(f"📋 Type: {msg_type}")
                        print(f"🎯 Status: {status}")
                        print(f"📊 Progress: {progress}%")
                        print(f"📝 Message: {message_text}")
                        print(f"🤖 Agent: {agent}")
                        print(f"🎭 Stage: {stage}")
                        print(f"🔄 Sequence: {sequence}")

                        # Check for enhanced message format
                        has_progress_percentage = 'progress_percentage' in msg_data
                        has_thinking = 'thinking' in msg_data and thinking != 'none'
                        has_output = 'output' in msg_data and output != 'none'
                        has_agent_details = 'currentAgent' in msg_data
                        is_enhanced = has_progress_percentage and has_thinking and has_output

                        if is_enhanced:
                            enhanced_message_count += 1
                            print(f"✅ ENHANCED MESSAGE FORMAT DETECTED! #{enhanced_message_count}")
                            print(f"💭 Thinking: {thinking}")
                            print(f"📤 Output: {output}")
                        elif msg_type in ['connection', 'heartbeat', 'error']:
                            print(f"ℹ️  System message: {msg_type}")
                        else:
                            print(f"⚠️  Basic message format")
                            print(f"      progress_percentage: {has_progress_percentage}")
                            print(f"      thinking: {has_thinking}")
                            print(f"      output: {has_output}")
                            print(f"      agent details: {has_agent_details}")

                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON format")

                    message_count += 1

                except asyncio.TimeoutError:
                    print("⏰ No more messages received, ending test")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 WebSocket connection closed")
                    break

            # Summary
            print(f"\n{'='*80}")
            print(f"🏁 TEST SUMMARY")
            print(f"{'='*80}")
            print(f"Total messages received: {message_count}")
            print(f"Enhanced messages with full agent details: {enhanced_message_count}")
            print(f"Message format success rate: {(enhanced_message_count/message_count)*100:.1f}%" if message_count > 0 else "No messages")

            # Check final job status
            final_status = journal_service.get_job_status(job_id)
            print(f"Final job status: {final_status}")

    except Exception as e:
        print(f"❌ WebSocket connection error: {e}")
        print(f"   Job details: {journal_service.get_job_status(job_id)}")

if __name__ == "__main__":
    asyncio.run(test_final_workflow())
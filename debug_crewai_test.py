#!/usr/bin/env python3
"""
Comprehensive test to debug CrewAI execution and progress tracking.
"""
import asyncio
import json
import time
import websockets
import requests
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'journal-platform-backend'))

from crewai_integration import journal_service

async def test_crewai_execution():
    """Test the complete CrewAI workflow with detailed logging."""

    print("🔍 Comprehensive CrewAI Execution Test")
    print("=" * 60)

    # Test preferences
    preferences = {
        "title": "Debug Test Journal",
        "theme": "AI and Productivity",
        "titleStyle": "Catchy Questions",
        "authorStyle": "inspirational narrative",
        "researchDepth": "medium",  # Use medium for faster testing
        "customInstructions": "Debug test to verify CrewAI execution and progress tracking"
    }

    # Get the API key from environment or backend
    api_key = "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"

    print(f"📝 Preferences: {json.dumps(preferences, indent=2)}")
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
    print()

    # Step 1: Create job without WebSocket callback
    print("🚀 Step 1: Creating journal creation job...")
    job_id = await journal_service.start_journal_creation(
        preferences,
        api_key=api_key,
        progress_callback=None  # No callback for now
    )

    print(f"✅ Job created: {job_id}")
    print()

    # Step 2: Monitor job status directly
    print("📊 Step 2: Monitoring job status...")

    start_time = time.time()
    max_wait_time = 300  # 5 minutes max
    check_interval = 2   # Check every 2 seconds

    while True:
        elapsed = time.time() - start_time

        if elapsed > max_wait_time:
            print(f"⏰ Test timeout after {max_wait_time} seconds")
            break

        status = journal_service.get_job_status(job_id)

        if status:
            print(f"📈 [{elapsed:.1f}s] Status: {status.get('status')} | Progress: {status.get('progress')}% | Agent: {status.get('current_agent', 'N/A')}")

            if status.get('status') == 'completed':
                print("✅ Job completed!")
                print(f"📋 Final result: {status.get('result')}")
                print(f"📁 Logs: {len(status.get('logs', []))} entries")
                break
            elif status.get('status') == 'error':
                print(f"❌ Job failed: {status.get('error')}")
                break
        else:
            print(f"⚠️ No status available for job {job_id}")

        await asyncio.sleep(check_interval)

    # Step 3: Check actual files created
    print("\n📁 Step 3: Checking for generated files...")

    # Look for output directories
    import glob
    output_patterns = [
        "../LLM_output/**/*",
        "journal-platform-backend/LLM_output/**/*",
        "LLM_output/**/*"
    ]

    files_found = []
    for pattern in output_patterns:
        files = glob.glob(pattern, recursive=True)
        if files:
            files_found.extend(files)
            print(f"📂 Found {len(files)} files in {pattern}")
            for file in files[-5:]:  # Show last 5 files
                print(f"   - {file}")

    if not files_found:
        print("❌ No output files found")

    # Step 4: Test WebSocket connection separately
    print("\n🔌 Step 4: Testing WebSocket connection...")

    ws_url = f"ws://localhost:6770/ws/journal/{job_id}"

    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ Connected to WebSocket: {ws_url}")

            # Listen for a few messages
            message_count = 0
            while message_count < 5:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    msg_data = json.loads(message)

                    print(f"📨 WebSocket Message {message_count + 1}:")
                    print(f"   Type: {msg_data.get('type')}")
                    print(f"   Status: {msg_data.get('status')}")
                    print(f"   Progress: {msg_data.get('progress_percentage', 'N/A')}%")
                    print(f"   Message: {msg_data.get('message', 'N/A')[:100]}...")

                    message_count += 1

                except asyncio.TimeoutError:
                    print("⏰ No more WebSocket messages, ending test")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 WebSocket connection closed")
                    break

    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

    # Step 5: Summary
    total_time = time.time() - start_time
    final_status = journal_service.get_job_status(job_id)

    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"⏱️ Total time: {total_time:.1f} seconds")
    print(f"🆔 Job ID: {job_id}")
    print(f"📊 Final status: {final_status.get('status') if final_status else 'Unknown'}")
    print(f"📈 Final progress: {final_status.get('progress', 0) if final_status else 0}%")
    print(f"📁 Files created: {len(files_found)}")
    print(f"📝 Log entries: {len(final_status.get('logs', [])) if final_status else 0}")

    if final_status and final_status.get('result'):
        print(f"🎯 Has result: {type(final_status.get('result'))}")
        if isinstance(final_status.get('result'), dict):
            print(f"📄 Result keys: {list(final_status.get('result').keys())}")
    else:
        print("❌ No result found")

    print("\n🔍 DIAGNOSIS:")
    if final_status:
        if final_status.get('status') == 'completed' and not final_status.get('result'):
            print("⚠️ Job marked complete but no result - indicates CrewAI execution issue")
        elif final_status.get('status') == 'completed' and final_status.get('result'):
            print("✅ Job completed with result - CrewAI working correctly")
        elif final_status.get('status') == 'error':
            print(f"❌ Job failed with error: {final_status.get('error')}")
        else:
            print(f"⏳ Job still in progress: {final_status.get('status')}")
    else:
        print("❌ Unable to determine job status")

if __name__ == "__main__":
    asyncio.run(test_crewai_execution())
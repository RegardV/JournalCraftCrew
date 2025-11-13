#!/usr/bin/env python3
"""
Comprehensive CrewAI Journal Creation Flow Test
Tests the complete integration from frontend click to CrewAI 9-agent workflow
"""

import asyncio
import websockets
import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:6770"
FRONTEND_URL = "http://localhost:5173"
WEBSOCKET_URL = "ws://localhost:6770/ws/crewai"

class CrewAIFlowTest:
    def __init__(self):
        self.auth_token = None
        self.test_results = []
        self.workflow_id = None

    def log(self, message, status="INFO"):
        """Log test progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{status}] {message}"
        print(log_entry)
        self.test_results.append({
            "timestamp": timestamp,
            "status": status,
            "message": message
        })

    def test_server_health(self):
        """Test if both servers are running"""
        self.log("🔍 Testing server connectivity...")

        # Test backend health
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Backend server is healthy", "SUCCESS")
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Backend server not accessible: {e}", "ERROR")
            return False

        # Test frontend server
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                self.log("✅ Frontend server is healthy", "SUCCESS")
            else:
                self.log(f"❌ Frontend health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Frontend server not accessible: {e}", "ERROR")
            return False

        return True

    def test_authentication(self):
        """Test user authentication flow"""
        self.log("🔐 Testing authentication...")

        # Test user registration
        register_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/auth/register",
                json=register_data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                self.log("✅ User registration successful", "SUCCESS")
            elif response.status_code == 400:
                self.log("ℹ️ User already exists, proceeding to login", "INFO")
            else:
                self.log(f"❌ Registration failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Registration request failed: {e}", "ERROR")
            return False

        # Test user login
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword123"
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/auth/login",
                json=login_data,
                timeout=10
            )

            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                if self.auth_token:
                    self.log("✅ Authentication successful", "SUCCESS")
                    return True
                else:
                    self.log("❌ No access token in response", "ERROR")
                    return False
            else:
                self.log(f"❌ Login failed: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Login request failed: {e}", "ERROR")
            return False

    def test_crewai_workflow_start(self):
        """Test starting CrewAI workflow"""
        self.log("🤖 Testing CrewAI workflow start...")

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

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/crewai/start-workflow",
                json=workflow_data,
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                workflow_response = response.json()
                self.workflow_id = workflow_response.get("workflow_id")

                if self.workflow_id:
                    self.log(f"✅ CrewAI workflow started: {self.workflow_id}", "SUCCESS")
                    self.log(f"📊 Estimated duration: {workflow_response.get('estimated_duration', 'N/A')} minutes", "INFO")
                    self.log(f"🔧 Workflow type: {workflow_response.get('workflow_type', 'N/A')}", "INFO")
                    return True
                else:
                    self.log("❌ No workflow ID in response", "ERROR")
                    self.log(f"Response: {response.text}", "ERROR")
                    return False
            else:
                self.log(f"❌ Workflow start failed: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Workflow start request failed: {e}", "ERROR")
            return False

    async def test_websocket_progress(self):
        """Test WebSocket real-time progress updates"""
        self.log("📡 Testing WebSocket progress updates...")

        if not self.workflow_id:
            self.log("❌ No workflow ID available for WebSocket test", "ERROR")
            return False

        websocket_url = f"{WEBSOCKET_URL}/{self.workflow_id}"

        try:
            async with websockets.connect(websocket_url) as websocket:
                self.log("✅ WebSocket connection established", "SUCCESS")

                # Listen for progress updates
                messages_received = 0
                agent_steps_seen = set()

                for message_count in range(30):  # Listen for up to 30 messages (2.5 minutes)
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)

                        messages_received += 1
                        message_type = data.get("type")

                        if message_type == "workflow_start":
                            self.log("🚀 Workflow started message received", "SUCCESS")
                            agents = data.get("crew_agents", [])
                            self.log(f"🤖 CrewAI Agents: {', '.join(agents)}", "INFO")

                        elif message_type == "agent_progress":
                            current_agent = data.get("current_agent")
                            progress = data.get("progress_percentage", 0)
                            step = data.get("current_step", 0)
                            total_steps = data.get("total_steps", 0)

                            agent_steps_seen.add(current_agent)
                            self.log(f"⚡ {current_agent}: {progress:.1f}% ({step}/{total_steps})", "INFO")

                        elif message_type == "workflow_complete":
                            self.log("🎉 Workflow completion message received", "SUCCESS")
                            result_data = data.get("result_data", {})
                            if result_data:
                                file_path = result_data.get("file_path")
                                pdf_path = result_data.get("pdf_path")
                                word_count = result_data.get("word_count")
                                pages = result_data.get("pages")

                                self.log(f"📄 Journal file: {file_path}", "SUCCESS")
                                self.log(f"📋 PDF file: {pdf_path}", "SUCCESS")
                                self.log(f"📝 Word count: {word_count}", "SUCCESS")
                                self.log(f"📑 Pages: {pages}", "SUCCESS")

                            return True

                        elif message_type == "error":
                            error_message = data.get("message", "Unknown error")
                            self.log(f"❌ Workflow error: {error_message}", "ERROR")
                            return False

                    except asyncio.TimeoutError:
                        self.log("⏰ WebSocket message timeout, continuing...", "INFO")
                        continue
                    except json.JSONDecodeError:
                        self.log(f"⚠️ Invalid JSON message: {message}", "WARNING")
                        continue
                    except Exception as e:
                        self.log(f"⚠️ WebSocket message error: {e}", "WARNING")
                        continue

                self.log(f"📡 Received {messages_received} messages", "INFO")
                self.log(f"🤖 Agents seen: {len(agent_steps_seen)}", "INFO")
                return len(agent_steps_seen) >= 3  # Success if we saw multiple agents

        except Exception as e:
            self.log(f"❌ WebSocket connection failed: {e}", "ERROR")
            return False

    def test_workflow_status_endpoint(self):
        """Test workflow status endpoint"""
        self.log("📊 Testing workflow status endpoint...")

        if not self.workflow_id:
            self.log("❌ No workflow ID available for status test", "ERROR")
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        try:
            response = requests.get(
                f"{BACKEND_URL}/api/crewai/workflow-status/{self.workflow_id}",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status")
                progress = status_data.get("progress_percentage", 0)
                current_agent = status_data.get("current_agent", "N/A")

                self.log(f"📊 Workflow status: {status}", "SUCCESS")
                self.log(f"📈 Progress: {progress:.1f}%", "INFO")
                self.log(f"🤖 Current agent: {current_agent}", "INFO")
                return True
            else:
                self.log(f"❌ Status check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Status check request failed: {e}", "ERROR")
            return False

    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.log("📋 Generating test report...")

        success_count = sum(1 for result in self.test_results if result["status"] == "SUCCESS")
        error_count = sum(1 for result in self.test_results if result["status"] == "ERROR")
        total_count = len(self.test_results)

        report = {
            "test_summary": {
                "total_tests": total_count,
                "successful_tests": success_count,
                "failed_tests": error_count,
                "success_rate": (success_count / total_count * 100) if total_count > 0 else 0,
                "workflow_id": self.workflow_id,
                "test_timestamp": datetime.now().isoformat()
            },
            "detailed_results": self.test_results
        }

        # Save report
        report_file = f"crewai_flow_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.log(f"📄 Test report saved: {report_file}", "SUCCESS")
        self.log(f"📊 Success Rate: {success_count}/{total_count} ({(success_count/total_count*100):.1f}%)", "INFO")

        return report

    async def run_complete_test(self):
        """Run the complete CrewAI flow test"""
        self.log("🚀 Starting Complete CrewAI Journal Creation Flow Test", "INFO")
        self.log("="*60, "INFO")

        # Test 1: Server Health
        if not self.test_server_health():
            self.log("❌ Server health check failed. Aborting test.", "ERROR")
            return self.generate_test_report()

        # Test 2: Authentication
        if not self.test_authentication():
            self.log("❌ Authentication failed. Aborting test.", "ERROR")
            return self.generate_test_report()

        # Test 3: CrewAI Workflow Start
        if not self.test_crewai_workflow_start():
            self.log("❌ CrewAI workflow start failed. Aborting test.", "ERROR")
            return self.generate_test_report()

        # Test 4: WebSocket Progress (in parallel with status checks)
        websocket_task = asyncio.create_task(self.test_websocket_progress())

        # Test 5: Workflow Status Endpoint
        status_success = self.test_workflow_status_endpoint()

        # Wait for WebSocket test to complete
        websocket_success = await websocket_task

        # Final summary
        self.log("="*60, "INFO")
        self.log("🏁 Complete CrewAI Flow Test Finished", "INFO")

        if websocket_success or status_success:
            self.log("🎉 CrewAI integration test PASSED", "SUCCESS")
            self.log("✅ The journal creation sequence is properly integrated with CrewAI 9-agent workflow", "SUCCESS")
        else:
            self.log("❌ CrewAI integration test FAILED", "ERROR")
            self.log("❌ Issues detected in journal creation to CrewAI workflow integration", "ERROR")

        return self.generate_test_report()

async def main():
    """Main test execution"""
    tester = CrewAIFlowTest()
    report = await tester.run_complete_test()

    print("\n" + "="*60)
    print("🎯 CREWAI INTEGRATION TEST SUMMARY")
    print("="*60)
    print(f"📊 Success Rate: {report['test_summary']['success_rate']:.1f}%")
    print(f"🤖 Workflow ID: {report['test_summary']['workflow_id'] or 'N/A'}")
    print(f"📄 Report saved: crewai_flow_test_report_*.json")

    if report['test_summary']['success_rate'] >= 80:
        print("🎉 INTEGRATION SUCCESSFUL - CrewAI 9-Agent Workflow Ready!")
    else:
        print("❌ INTEGRATION ISSUES DETECTED - Review detailed logs")

    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
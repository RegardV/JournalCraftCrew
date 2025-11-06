#!/usr/bin/env python3
"""
Simple Archon Web Sync using curl commands
"""

import json
import subprocess
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_curl(url, method="GET", data=None, headers=None):
    """Run curl command and return response"""
    cmd = ["curl", "-s", "-w", "%{http_code}", url]

    if method != "GET":
        cmd.extend(["-X", method])

    if headers:
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])

    if data:
        cmd.extend(["-d", json.dumps(data)])
        cmd.extend(["-H", "Content-Type: application/json"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Extract status code (last 3 characters)
        if len(result.stdout) >= 3:
            status_code = int(result.stdout[-3:])
            response_body = result.stdout[:-3] if len(result.stdout) > 3 else ""

            return {
                "status_code": status_code,
                "body": response_body,
                "success": status_code < 400
            }

        return {"success": False, "error": "No response"}

    except Exception as e:
        logger.error(f"Curl error: {e}")
        return {"success": False, "error": str(e)}

class SimpleArchonSync:
    def __init__(self):
        self.base_url = "http://localhost:8181"
        self.project_id = "96ca376c-7c18-4115-a59c-5ef145c15ce8"

    def load_local_tasks(self) -> Dict[str, Any]:
        """Load tasks from local archon_tasks.json"""
        try:
            with open("archon_tasks.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load local tasks: {e}")
            return {"tasks": {}}

    def clear_existing_tasks(self) -> bool:
        """Clear existing tasks from web Archon"""
        try:
            # Get current tasks
            response = run_curl(f"{self.base_url}/api/tasks")

            if response["success"]:
                try:
                    current_data = json.loads(response["body"])
                    current_tasks = current_data.get("tasks", [])

                    logger.info(f"Found {len(current_tasks)} existing tasks to clear")

                    # Delete each task
                    deleted_count = 0
                    for task in current_tasks:
                        task_id = task.get("id")
                        if task_id:
                            delete_response = run_curl(f"{self.base_url}/api/tasks/{task_id}", method="DELETE")
                            if delete_response["success"]:
                                deleted_count += 1

                    logger.info(f"Deleted {deleted_count} existing tasks")
                    return True

                except json.JSONDecodeError as e:
                    logger.warning(f"Could not parse existing tasks: {e}")
                    return True  # Continue anyway
            else:
                logger.warning(f"Could not fetch existing tasks: {response.get('error', 'Unknown error')}")
                return True  # Continue anyway

        except Exception as e:
            logger.error(f"Error clearing web tasks: {e}")
            return False

    def push_task_to_web(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Push a single task to web Archon"""
        try:
            # Prepare task data for web API
            web_task = {
                "title": task_data.get("name", task_id)[:100],  # Limit title length
                "description": task_data.get("context", "")[:500],  # Limit description length
                "status": task_data.get("status", "pending"),
                "project_id": self.project_id,
                "metadata": {
                    "local_id": task_id,
                    "source": "local_archon",
                    "created_at": task_data.get("created_at"),
                    "updated_at": task_data.get("updated_at"),
                    "implementation_notes": task_data.get("implementation_notes", "")[:200]
                }
            }

            # Create task
            response = run_curl(
                f"{self.base_url}/api/tasks",
                method="POST",
                data=web_task
            )

            if response["success"]:
                logger.info(f"✅ Created task: {task_data.get('name', task_id)[:50]}... ({task_data.get('status')})")
                return True
            else:
                logger.error(f"❌ Failed to create task {task_id}: HTTP {response.get('status_code', 'Unknown')}")
                return False

        except Exception as e:
            logger.error(f"❌ Error pushing task {task_id}: {e}")
            return False

    def sync_all_tasks(self, clear_existing: bool = True) -> Dict[str, int]:
        """Sync all local tasks to web Archon"""
        logger.info("🚀 Starting Simple Archon Web Integration")
        logger.info(f"📡 Target: {self.base_url}")
        logger.info(f"📋 Project: {self.project_id}")

        # Load local tasks
        local_data = self.load_local_tasks()
        local_tasks = local_data.get("tasks", {})

        if not local_tasks:
            logger.error("❌ No local tasks found!")
            return {"success": 0, "failed": 0, "total": 0}

        logger.info(f"📊 Found {len(local_tasks)} local tasks")

        # Count by status
        status_counts = {}
        for task in local_tasks.values():
            status = task.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1

        logger.info(f"📈 Task breakdown: {status_counts}")

        # Clear existing tasks if requested
        if clear_existing:
            logger.info("🧹 Clearing existing web tasks...")
            self.clear_existing_tasks()

        # Push tasks
        success_count = 0
        failed_count = 0

        for task_id, task_data in local_tasks.items():
            success = self.push_task_to_web(task_id, task_data)
            if success:
                success_count += 1
            else:
                failed_count += 1

        # Summary
        total = len(local_tasks)
        logger.info(f"\n🎉 Sync Complete!")
        logger.info(f"   ✅ Successfully synced: {success_count}/{total}")
        logger.info(f"   ❌ Failed: {failed_count}/{total}")
        if total > 0:
            logger.info(f"   📊 Success rate: {(success_count/total*100):.1f}%")

        return {
            "success": success_count,
            "failed": failed_count,
            "total": total,
            "status_counts": status_counts
        }

def main():
    """Main function"""
    sync = SimpleArchonSync()

    print("🔗 Simple Archon Web Integration")
    print("=" * 50)
    print("This will sync your local tasks to the web Archon UI")
    print(f"Web UI: http://localhost:3737/")
    print(f"API: http://localhost:8181/docs")
    print("")

    # Perform sync
    results = sync.sync_all_tasks(clear_existing=True)

    if results["success"] > 0:
        print(f"\n✨ Success! {results['success']} tasks are now available in the web UI")
        print("🌐 Check your tasks at: http://localhost:3737/")

        # Verify sync
        print("\n🔍 Verifying sync...")
        verify_response = run_curl(f"{sync.base_url}/api/tasks")
        if verify_response["success"]:
            try:
                verify_data = json.loads(verify_response["body"])
                task_count = verify_data.get("pagination", {}).get("total", 0)
                print(f"✅ Verified: {task_count} tasks now in web UI")
            except:
                print("⚠️  Could not verify task count")
        else:
            print("⚠️  Could not verify sync")
    else:
        print(f"\n❌ Sync failed. Check the logs above.")

if __name__ == "__main__":
    main()
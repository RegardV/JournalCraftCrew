#!/usr/bin/env python3
"""
Archon Web Integration Script
Syncs local archon_tasks.json with the web Archon API
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArchonWebIntegration:
    def __init__(self):
        self.base_url = "http://localhost:8181"
        self.project_id = "96ca376c-7c18-4115-a59c-5ef145c15ce8"  # Journal Craft Crew project

    async def load_local_tasks(self) -> Dict[str, Any]:
        """Load tasks from local archon_tasks.json"""
        try:
            with open("archon_tasks.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load local tasks: {e}")
            return {"tasks": {}}

    async def clear_web_tasks(self) -> bool:
        """Clear existing tasks from web Archon"""
        try:
            # Get existing tasks first
            async with self.session() as client:
                # Get current tasks
                response = await client.get(f"{self.base_url}/api/tasks")
                if response.status_code == 200:
                    current_data = response.json()
                    current_tasks = current_data.get("tasks", [])

                    logger.info(f"Found {len(current_tasks)} existing tasks to clear")

                    # Delete each task
                    for task in current_tasks:
                        task_id = task.get("id")
                        if task_id:
                            delete_response = await client.delete(f"{self.base_url}/api/tasks/{task_id}")
                            if delete_response.status_code == 200:
                                logger.info(f"Deleted existing task: {task_id}")
                            else:
                                logger.warning(f"Failed to delete task {task_id}: {delete_response.status_code}")

                    return True
                else:
                    logger.warning(f"Could not fetch existing tasks: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Error clearing web tasks: {e}")
            return False

    async def push_task_to_web(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Push a single task to web Archon"""
        try:
            async with self.session() as client:
                # Prepare task data for web API
                web_task = {
                    "title": task_data.get("name", task_id),
                    "description": task_data.get("context", ""),
                    "status": task_data.get("status", "pending"),
                    "project_id": self.project_id,
                    "metadata": {
                        "local_id": task_id,
                        "source": "local_archon",
                        "created_at": task_data.get("created_at"),
                        "updated_at": task_data.get("updated_at"),
                        "history": task_data.get("history", []),
                        "implementation_notes": task_data.get("implementation_notes", "")
                    }
                }

                # Create task
                response = await client.post(
                    f"{self.base_url}/api/tasks",
                    json=web_task,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200 or response.status_code == 201:
                    created_task = response.json()
                    logger.info(f"✅ Created task: {task_data.get('name', task_id)[:50]}... ({task_data.get('status')})")
                    return True
                else:
                    logger.error(f"❌ Failed to create task {task_id}: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Error pushing task {task_id}: {e}")
            return False

    def session(self):
        """Create HTTP session"""
        import httpx
        return httpx.AsyncClient(timeout=30.0)

    async def sync_all_tasks(self, clear_existing: bool = True) -> Dict[str, int]:
        """Sync all local tasks to web Archon"""
        logger.info("🚀 Starting Archon Web Integration")
        logger.info(f"📡 Target: {self.base_url}")
        logger.info(f"📋 Project: {self.project_id}")

        # Load local tasks
        local_data = await self.load_local_tasks()
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
            cleared = await self.clear_web_tasks()
            if not cleared:
                logger.warning("⚠️  Could not clear existing tasks, continuing anyway...")

        # Push tasks
        success_count = 0
        failed_count = 0

        for task_id, task_data in local_tasks.items():
            success = await self.push_task_to_web(task_id, task_data)
            if success:
                success_count += 1
            else:
                failed_count += 1

        # Summary
        total = len(local_tasks)
        logger.info(f"\n🎉 Sync Complete!")
        logger.info(f"   ✅ Successfully synced: {success_count}/{total}")
        logger.info(f"   ❌ Failed: {failed_count}/{total}")
        logger.info(f"   📊 Success rate: {(success_count/total*100):.1f}%")

        return {
            "success": success_count,
            "failed": failed_count,
            "total": total,
            "status_counts": status_counts
        }

async def main():
    """Main function"""
    integration = ArchonWebIntegration()

    print("🔗 Archon Web Integration")
    print("=" * 50)
    print("This will sync your local tasks to the web Archon UI")
    print(f"Web UI: http://localhost:3737/")
    print(f"API: http://localhost:8181/docs")
    print("")

    # Confirm sync
    response = input("Do you want to continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Sync cancelled")
        return

    # Perform sync
    results = await integration.sync_all_tasks(clear_existing=True)

    if results["success"] > 0:
        print(f"\n✨ Success! {results['success']} tasks are now available in the web UI")
        print("🌐 Check your tasks at: http://localhost:3737/")
    else:
        print(f"\n❌ Sync failed. Check the logs above.")

if __name__ == "__main__":
    asyncio.run(main())
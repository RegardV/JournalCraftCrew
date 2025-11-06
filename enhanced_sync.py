#!/usr/bin/env python3
"""
Enhanced Archon Web Sync with Proper Status Mapping

This script provides a robust, repeatable process for syncing local Archon tasks
to the web Archon interface with proper status mapping and bi-directional sync.

Features:
- Proper status mapping (pending→todo, completed→done, in_progress→doing)
- Bi-directional sync capability
- Incremental updates (only sync changed tasks)
- Knowledge preservation and session continuity
- Integration with OpenSpec workflow

Usage:
    python enhanced_sync.py --to-web      # Push local tasks to web Archon
    python enhanced_sync.py --from-web    # Pull web progress to local
    python enhanced_sync.py --sync-all    # Bidirectional sync
    python enhanced_sync.py --status      # Show sync status
"""

import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedArchonSync:
    def __init__(self):
        self.base_url = "http://localhost:8181"
        self.project_id = "96ca376c-7c18-4115-a59c-5ef145c15ce8"

        # Status mapping: local_status -> web_status
        self.status_mapping = {
            "pending": "todo",
            "in_progress": "doing",
            "completed": "done",
            "todo": "todo",
            "doing": "doing",
            "done": "done"
        }

        # Reverse mapping: web_status -> local_status
        self.reverse_status_mapping = {
            "todo": "pending",
            "doing": "in_progress",
            "done": "completed"
        }

    def run_curl(self, url, method="GET", data=None, headers=None):
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

    def load_local_tasks(self) -> Dict[str, Any]:
        """Load tasks from local archon_tasks.json"""
        try:
            with open("archon_tasks.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load local tasks: {e}")
            return {"tasks": {}}

    def get_all_web_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from web Archon API (handles pagination)"""
        all_tasks = []
        page = 1
        per_page = 100  # Max page size for efficiency

        while True:
            response = self.run_curl(f"{self.base_url}/api/tasks?page={page}&per_page={per_page}")

            if not response["success"]:
                logger.error(f"Failed to fetch web tasks page {page}: {response.get('error', 'Unknown error')}")
                break

            try:
                data = json.loads(response["body"])
                tasks = data.get("tasks", [])

                if not tasks:
                    break

                all_tasks.extend(tasks)

                # Check if we have all tasks
                pagination = data.get("pagination", {})
                total = pagination.get("total", 0)
                if len(all_tasks) >= total:
                    break

                page += 1

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse web tasks response: {e}")
                break

        logger.info(f"Fetched {len(all_tasks)} tasks from web Archon")
        return all_tasks

    def map_status_to_web(self, local_status: str) -> str:
        """Map local task status to web Archon status"""
        return self.status_mapping.get(local_status, "todo")

    def map_status_to_local(self, web_status: str) -> str:
        """Map web Archon status to local task status"""
        return self.reverse_status_mapping.get(web_status, "pending")

    def update_web_task_status(self, task_id: str, new_status: str) -> bool:
        """Update a single task's status in web Archon"""
        data = {"status": new_status}

        response = self.run_curl(
            f"{self.base_url}/api/tasks/{task_id}",
            method="PUT",
            data=data
        )

        return response["success"]

    def sync_to_web(self, force_update: bool = False) -> Dict[str, int]:
        """Sync local tasks to web Archon with proper status mapping"""
        logger.info("🚀 Starting Enhanced Local → Web Archon Sync")
        logger.info(f"📡 Target: {self.base_url}")
        logger.info(f"📋 Project: {self.project_id}")

        # Load local data
        local_data = self.load_local_tasks()
        local_tasks = local_data.get("tasks", {})

        if not local_tasks:
            logger.error("❌ No local tasks found!")
            return {"updated": 0, "unchanged": 0, "total": 0}

        # Get web tasks
        web_tasks = self.get_all_web_tasks()
        web_tasks_by_local_id = {
            task.get("metadata", {}).get("local_id"): task
            for task in web_tasks
            if task.get("metadata", {}).get("local_id")
        }

        # Count local statuses
        local_status_counts = {}
        for task in local_tasks.values():
            status = task.get("status", "pending")
            local_status_counts[status] = local_status_counts.get(status, 0) + 1

        logger.info(f"📊 Local tasks: {len(local_tasks)} total")
        logger.info(f"📈 Local status breakdown: {local_status_counts}")

        # Sync tasks
        updated_count = 0
        unchanged_count = 0
        status_mismatches = 0

        for task_id, task_data in local_tasks.items():
            local_status = task_data.get("status", "pending")
            expected_web_status = self.map_status_to_web(local_status)

            if task_id in web_tasks_by_local_id:
                # Task exists in web, check if status needs updating
                web_task = web_tasks_by_local_id[task_id]
                current_web_status = web_task.get("status", "todo")

                if current_web_status != expected_web_status or force_update:
                    # Update task status
                    success = self.update_web_task_status(web_task["id"], expected_web_status)
                    if success:
                        updated_count += 1
                        status_mismatches += 1
                        logger.info(f"✅ Updated: {task_data.get('name', task_id)[:50]}... ({current_web_status} → {expected_web_status})")
                    else:
                        logger.error(f"❌ Failed to update: {task_data.get('name', task_id)[:50]}...")
                else:
                    unchanged_count += 1
            else:
                logger.warning(f"⚠️  Task not found in web: {task_id}")

        # Summary
        total = len(local_tasks)
        logger.info(f"\n🎉 Sync Complete!")
        logger.info(f"   ✅ Status updated: {updated_count}/{total}")
        logger.info(f"   ✅ Already correct: {unchanged_count}/{total}")
        logger.info(f"   🔄 Status mismatches fixed: {status_mismatches}")

        if total > 0:
            logger.info(f"   📊 Update rate: {(updated_count/total*100):.1f}%")

        return {
            "updated": updated_count,
            "unchanged": unchanged_count,
            "total": total,
            "status_mismatches": status_mismatches
        }

    def sync_from_web(self) -> Dict[str, int]:
        """Sync web Archon progress back to local tasks"""
        logger.info("🔄 Starting Web → Local Archon Sync")

        local_data = self.load_local_tasks()
        local_tasks = local_data.get("tasks", {})

        web_tasks = self.get_all_web_tasks()

        updated_count = 0

        for web_task in web_tasks:
            local_id = web_task.get("metadata", {}).get("local_id")
            if not local_id or local_id not in local_tasks:
                continue

            local_task = local_tasks[local_id]
            web_status = web_task.get("status", "todo")
            expected_local_status = self.map_status_to_local(web_status)

            if local_task.get("status") != expected_local_status:
                # Update local task status
                old_status = local_task.get("status")
                local_task["status"] = expected_local_status
                local_task["updated_at"] = datetime.now().isoformat()

                # Add to history
                if "history" not in local_task:
                    local_task["history"] = []
                local_task["history"].append({
                    "status": expected_local_status,
                    "timestamp": datetime.now().isoformat(),
                    "source": "web_sync",
                    "previous_status": old_status,
                    "web_status": web_status
                })

                updated_count += 1
                logger.info(f"✅ Updated local: {local_task.get('name', local_id)[:50]}... ({old_status} → {expected_local_status})")

        # Save updated local data
        if updated_count > 0:
            try:
                local_data["last_web_sync"] = datetime.now().isoformat()
                with open("archon_tasks.json", 'w') as f:
                    json.dump(local_data, f, indent=2)
                logger.info(f"✅ Saved {updated_count} local task updates")
            except Exception as e:
                logger.error(f"❌ Failed to save local updates: {e}")

        logger.info(f"\n🎉 Web → Local Sync Complete!")
        logger.info(f"   ✅ Local tasks updated: {updated_count}")

        return {"updated": updated_count, "total": len(web_tasks)}

    def show_sync_status(self):
        """Show comprehensive sync status"""
        logger.info("📊 Enhanced Archon Sync Status")
        logger.info("=" * 50)

        # Load local data
        local_data = self.load_local_tasks()
        local_tasks = local_data.get("tasks", {})

        # Get web tasks
        web_tasks = self.get_all_web_tasks()

        # Count local statuses
        local_status_counts = {}
        for task in local_tasks.values():
            status = task.get("status", "pending")
            local_status_counts[status] = local_status_counts.get(status, 0) + 1

        # Count web statuses
        web_status_counts = {}
        web_tasks_by_local_id = {}
        for task in web_tasks:
            status = task.get("status", "todo")
            web_status_counts[status] = web_status_counts.get(status, 0) + 1

            local_id = task.get("metadata", {}).get("local_id")
            if local_id:
                web_tasks_by_local_id[local_id] = task

        logger.info(f"\n📋 Task Counts:")
        logger.info(f"   Local tasks: {len(local_tasks)}")
        logger.info(f"   Web tasks: {len(web_tasks)}")
        logger.info(f"   Matched tasks: {len(web_tasks_by_local_id)}")

        logger.info(f"\n📈 Local Status Breakdown:")
        for status, count in local_status_counts.items():
            logger.info(f"   {status}: {count}")

        logger.info(f"\n🌐 Web Status Breakdown:")
        for status, count in web_status_counts.items():
            logger.info(f"   {status}: {count}")

        # Show sync timestamps
        last_local_sync = local_data.get("last_sync_from_openspec")
        last_web_sync = local_data.get("last_web_sync")

        if last_local_sync:
            logger.info(f"\n🕒 Last OpenSpec → Local sync: {last_local_sync}")
        if last_web_sync:
            logger.info(f"\n🕒 Last Web → Local sync: {last_web_sync}")

        # Analysis
        if local_tasks and web_tasks:
            sync_coverage = len(web_tasks_by_local_id) / len(local_tasks) * 100
            logger.info(f"\n📊 Sync Coverage: {sync_coverage:.1f}% of local tasks in web system")

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Archon Web Sync",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --to-web      # Sync local tasks to web Archon with proper status mapping
  %(prog)s --from-web    # Pull web progress to local tasks
  %(prog)s --sync-all    # Bidirectional sync
  %(prog)s --status      # Show comprehensive sync status
  %(prog)s --force       # Force update all task statuses
        """
    )

    parser.add_argument('--to-web', action='store_true',
                       help='Sync local tasks to web Archon')
    parser.add_argument('--from-web', action='store_true',
                       help='Sync web progress to local tasks')
    parser.add_argument('--sync-all', action='store_true',
                       help='Perform bidirectional sync')
    parser.add_argument('--status', action='store_true',
                       help='Show sync status')
    parser.add_argument('--force', action='store_true',
                       help='Force update all task statuses')

    args = parser.parse_args()

    if not any([args.to_web, args.from_web, args.sync_all, args.status]):
        parser.print_help()
        return

    try:
        sync = EnhancedArchonSync()

        if args.status:
            sync.show_sync_status()
        elif args.to_web:
            sync.sync_to_web(force_update=args.force)
        elif args.from_web:
            sync.sync_from_web()
        elif args.sync_all:
            sync.sync_to_web()
            sync.sync_from_web()

    except KeyboardInterrupt:
        logger.info("\n⏹️  Sync interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error during sync: {e}")

if __name__ == "__main__":
    main()
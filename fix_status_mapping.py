#!/usr/bin/env python3
"""
Fix Status Mapping Script

This script matches existing web Archon tasks to local tasks based on title similarity
and updates their statuses to properly reflect completed vs pending tasks.
"""

import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, List
import difflib

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

def get_all_web_tasks() -> List[Dict[str, Any]]:
    """Get all tasks from web Archon API (handles pagination)"""
    all_tasks = []
    page = 1
    per_page = 100

    while True:
        response = run_curl(f"http://localhost:8181/api/tasks?page={page}&per_page={per_page}")

        if not response["success"]:
            logger.error(f"Failed to fetch web tasks page {page}")
            break

        try:
            data = json.loads(response["body"])
            tasks = data.get("tasks", [])

            if not tasks:
                break

            all_tasks.extend(tasks)

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

def load_local_tasks() -> Dict[str, Any]:
    """Load tasks from local archon_tasks.json"""
    try:
        with open("archon_tasks.json", 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load local tasks: {e}")
        return {"tasks": {}}

def normalize_title(title: str) -> str:
    """Normalize title for comparison"""
    # Remove backticks, underscores, and convert to lowercase
    normalized = title.replace("`", "").replace("_", " ").lower()
    # Remove extra spaces
    return " ".join(normalized.split())

def update_web_task_status(task_id: str, new_status: str) -> bool:
    """Update a single task's status in web Archon"""
    data = {"status": new_status}

    response = run_curl(
        f"http://localhost:8181/api/tasks/{task_id}",
        method="PUT",
        data=data
    )

    return response["success"]

def main():
    """Main function to fix status mapping"""
    logger.info("🔧 Fixing Status Mapping Between Local and Web Archon")
    logger.info("=" * 60)

    # Load local data
    local_data = load_local_tasks()
    local_tasks = local_data.get("tasks", {})

    # Get web tasks
    web_tasks = get_all_web_tasks()

    # Count local statuses
    local_status_counts = {}
    for task in local_tasks.values():
        status = task.get("status", "pending")
        local_status_counts[status] = local_status_counts.get(status, 0) + 1

    logger.info(f"📊 Local tasks: {len(local_tasks)} total")
    logger.info(f"📈 Local status breakdown: {local_status_counts}")

    # Create mapping of normalized local task names to tasks
    local_tasks_by_name = {}
    for task_id, task_data in local_tasks.items():
        normalized_name = normalize_title(task_data.get("name", task_id))
        local_tasks_by_name[normalized_name] = {
            "id": task_id,
            "data": task_data,
            "status": task_data.get("status", "pending")
        }

    # Match web tasks to local tasks
    updated_count = 0
    matched_count = 0
    unmatched_count = 0
    done_count = 0
    todo_count = 0

    for web_task in web_tasks:
        web_title = normalize_title(web_task.get("title", ""))
        web_status = web_task.get("status", "todo")

        # Try to find exact match first
        if web_title in local_tasks_by_name:
            local_task = local_tasks_by_name[web_title]
            expected_status = "done" if local_task["status"] == "completed" else "todo"

            if web_status != expected_status:
                success = update_web_task_status(web_task["id"], expected_status)
                if success:
                    updated_count += 1
                    if expected_status == "done":
                        done_count += 1
                    else:
                        todo_count += 1
                    logger.info(f"✅ Updated: {web_task['title'][:50]}... ({web_status} → {expected_status})")
                else:
                    logger.error(f"❌ Failed to update: {web_task['title'][:50]}...")
            else:
                logger.info(f"✅ Already correct: {web_task['title'][:50]}... ({expected_status})")

            matched_count += 1
        else:
            # Try fuzzy matching for close matches
            best_match = None
            best_ratio = 0.0

            for local_name, local_task in local_tasks_by_name.items():
                ratio = difflib.SequenceMatcher(None, web_title, local_name).ratio()
                if ratio > best_ratio and ratio > 0.8:  # 80% similarity threshold
                    best_ratio = ratio
                    best_match = local_task

            if best_match:
                expected_status = "done" if best_match["status"] == "completed" else "todo"

                if web_status != expected_status:
                    success = update_web_task_status(web_task["id"], expected_status)
                    if success:
                        updated_count += 1
                        if expected_status == "done":
                            done_count += 1
                        else:
                            todo_count += 1
                        logger.info(f"✅ Updated (fuzzy): {web_task['title'][:50]}... ({web_status} → {expected_status}) [ratio: {best_ratio:.2f}]")
                    else:
                        logger.error(f"❌ Failed to update: {web_task['title'][:50]}...")

                matched_count += 1
                logger.info(f"🔗 Matched: {web_task['title'][:30]}... → {best_match['data']['name'][:30]}... [ratio: {best_ratio:.2f}]")
            else:
                unmatched_count += 1
                logger.warning(f"⚠️  Unmatched: {web_task['title'][:50]}...")

    # Summary
    logger.info(f"\n🎉 Status Mapping Fix Complete!")
    logger.info(f"   📊 Web tasks processed: {len(web_tasks)}")
    logger.info(f"   ✅ Successfully matched: {matched_count}")
    logger.info(f"   ⚠️  Unmatched tasks: {unmatched_count}")
    logger.info(f"   🔄 Status updates applied: {updated_count}")
    logger.info(f"   ✅ Tasks marked as done: {done_count}")
    logger.info(f"   📋 Tasks marked as todo: {todo_count}")

    if matched_count > 0:
        logger.info(f"   📊 Match rate: {(matched_count/len(web_tasks)*100):.1f}%")

    # Verify final status distribution
    logger.info(f"\n🔍 Verifying final status distribution...")
    final_web_tasks = get_all_web_tasks()
    final_status_counts = {}
    for task in final_web_tasks:
        status = task.get("status", "todo")
        final_status_counts[status] = final_status_counts.get(status, 0) + 1

    logger.info(f"📈 Final web status breakdown: {final_status_counts}")
    logger.info(f"📋 Expected: done={local_status_counts.get('completed', 0)}, todo={local_status_counts.get('pending', 0)}")

    return updated_count

if __name__ == "__main__":
    main()
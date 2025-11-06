#!/usr/bin/env python3
"""
OpenSpec Integration Script

Syncs OpenSpec project management with Archon task tracking and knowledge base.
Provides unified workflow between structured planning and AI-powered development assistance.

Usage:
    python openspec_sync.py --to-archon    # Push OpenSpec tasks to Archon
    python openspec_sync.py --from-archon  # Pull Archon progress to OpenSpec
    python openspec_sync.py --status       # Show sync status
    python openspec_sync.py --sync-all     # Bidirectional sync
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

def load_openspec_data():
    """Load OpenSpec project data"""
    data = {"tasks": {}, "changes": {}, "projects": {}}

    # Find current OpenSpec change
    openspec_dir = Path("openspec")
    if openspec_dir.exists():
        # Load current change tasks
        changes_dir = openspec_dir / "changes"
        if changes_dir.exists():
            for change_dir in changes_dir.iterdir():
                if change_dir.is_dir():
                    tasks_file = change_dir / "tasks.md"
                    if tasks_file.exists():
                        data["changes"][change_dir.name] = {
                            "path": str(tasks_file),
                            "tasks": parse_tasks_md(tasks_file)
                        }

        # Load archived change tasks (THIS IS THE MISSING PIECE!)
        archive_dir = changes_dir / "archive"
        if archive_dir.exists():
            for change_dir in archive_dir.iterdir():
                if change_dir.is_dir():
                    tasks_file = change_dir / "tasks.md"
                    if tasks_file.exists():
                        data["changes"][change_dir.name] = {
                            "path": str(tasks_file),
                            "tasks": parse_tasks_md(tasks_file)
                        }

    return data

def parse_tasks_md(tasks_file):
    """Parse OpenSpec tasks.md file"""
    tasks = {}

    try:
        with open(tasks_file, 'r') as f:
            content = f.read()

        # Simple markdown parsing for tasks
        lines = content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            # Identify sections
            if line.startswith('## '):
                current_section = line[3:].strip()
                continue

            # Parse tasks
            if line.startswith('- [') and ']' in line:
                status_char = line[3:4]
                task_text = line.split(']', 1)[1].strip()

                status = "pending"
                if status_char == 'x':
                    status = "completed"
                elif status_char == '-':
                    status = "in_progress"

                task_id = task_text.lower().replace(" ", "_").replace("-", "_")[:50]
                tasks[task_id] = {
                    "text": task_text,
                    "status": status,
                    "section": current_section
                }

    except Exception as e:
        print(f"⚠️  Error parsing {tasks_file}: {e}")

    return tasks

def load_archon_data():
    """Load Archon task tracking data"""
    data = {"tasks": {}, "knowledge": {}, "sessions": {}}

    if os.path.exists("archon_tasks.json"):
        try:
            with open("archon_tasks.json", 'r') as f:
                task_data = json.load(f)
                data["tasks"] = task_data.get("tasks", {})
                data["sessions"] = task_data.get("sessions", {})
        except Exception as e:
            print(f"⚠️  Error loading archon_tasks.json: {e}")

    if os.path.exists("archon_knowledge.json"):
        try:
            with open("archon_knowledge.json", 'r') as f:
                data["knowledge"] = json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading archon_knowledge.json: {e}")

    return data

def sync_to_archon():
    """Push OpenSpec tasks to Archon"""
    print("🔄 Syncing OpenSpec tasks to Archon...")

    openspec_data = load_openspec_data()
    archon_data = load_archon_data()

    tasks_synced = 0
    tasks_updated = 0
    total_openspec_tasks = 0
    completed_openspec_tasks = 0
    archived_changes = 0

    for change_name, change_data in openspec_data["changes"].items():
        # Check if this is an archived change
        is_archived = "archive" in change_name
        if is_archived:
            archived_changes += 1
            print(f"\n📁 Processing ARCHIVED change: {change_name}")
        else:
            print(f"\n📂 Processing change: {change_name}")

        for task_id, task_info in change_data["tasks"].items():
            total_openspec_tasks += 1
            if task_info["status"] == "completed":
                completed_openspec_tasks += 1

            # Check if task exists in Archon
            if task_id not in archon_data["tasks"]:
                # Create new task in Archon
                archon_data["tasks"][task_id] = {
                    "name": task_info["text"],
                    "status": task_info["status"],
                    "created_at": datetime.now().isoformat(),
                    "context": f"OpenSpec change: {change_name} - {task_info['section']}",
                    "source": "openspec",
                    "history": []
                }
                tasks_synced += 1
                status_emoji = "✅" if task_info["status"] == "completed" else "⏳"
                print(f"   {status_emoji} Created: {task_info['text'][:50]}... ({task_info['status']})")
            else:
                # Update existing task status
                archon_task = archon_data["tasks"][task_id]
                if archon_task["status"] != task_info["status"]:
                    old_status = archon_task["status"]
                    archon_task["status"] = task_info["status"]
                    archon_task["updated_at"] = datetime.now().isoformat()

                    archon_task["history"].append({
                        "status": task_info["status"],
                        "timestamp": datetime.now().isoformat(),
                        "source": "openspec_sync",
                        "previous_status": old_status
                    })

                    tasks_updated += 1
                    status_emoji = "✅" if task_info["status"] == "completed" else "⏳"
                    print(f"   {status_emoji} Updated: {task_info['text'][:50]}... ({old_status} → {task_info['status']})")

    # Summary statistics
    print(f"\n📊 Sync Summary:")
    print(f"   • OpenSpec changes processed: {len(openspec_data['changes'])} ({archived_changes} archived)")
    print(f"   • Total OpenSpec tasks: {total_openspec_tasks}")
    print(f"   • Completed in OpenSpec: {completed_openspec_tasks}")
    print(f"   • New tasks created: {tasks_synced}")
    print(f"   • Existing tasks updated: {tasks_updated}")

    # Show current Archon status
    current_archon_completed = sum(1 for task in archon_data["tasks"].values() if task["status"] == "completed")
    current_archon_total = len(archon_data["tasks"])
    print(f"   • Current Archon tasks: {current_archon_completed}/{current_archon_total} completed")

    # Save updated Archon data
    if tasks_synced > 0 or tasks_updated > 0:
        try:
            task_data = {
                "tasks": archon_data["tasks"],
                "sessions": archon_data["sessions"],
                "last_updated": datetime.now().isoformat(),
                "last_sync_from_openspec": datetime.now().isoformat()
            }
            with open("archon_tasks.json", 'w') as f:
                json.dump(task_data, f, indent=2)

            print(f"\n✅ Sync complete: {tasks_synced} new, {tasks_updated} updated")
        except Exception as e:
            print(f"❌ Error saving Archon data: {e}")
    else:
        print("\n✅ All OpenSpec tasks already in sync")

    return tasks_synced + tasks_updated

def sync_from_archon():
    """Pull Archon progress to OpenSpec"""
    print("🔄 Syncing Archon progress to OpenSpec...")

    openspec_data = load_openspec_data()
    archon_data = load_archon_data()

    updates_needed = 0

    for change_name, change_data in openspec_data["changes"].items():
        print(f"\n📂 Updating change: {change_name}")

        # Read current tasks.md content
        tasks_file = Path(change_data["path"])
        if not tasks_file.exists():
            print(f"   ⚠️  Tasks file not found: {tasks_file}")
            continue

        with open(tasks_file, 'r') as f:
            content = f.read()

        lines = content.split('\n')
        updated_lines = []
        task_updates = 0

        for line in lines:
            original_line = line
            line_stripped = line.strip()

            # Parse task line
            if line_stripped.startswith('- [') and ']' in line_stripped:
                # Extract task text
                task_text = line_stripped.split(']', 1)[1].strip()
                task_id = task_text.lower().replace(" ", "_").replace("-", "_")[:50]

                # Check Archon status
                if task_id in archon_data["tasks"]:
                    archon_task = archon_data["tasks"][task_id]
                    archon_status = archon_task["status"]

                    # Convert to checkbox status
                    checkbox_char = " "
                    if archon_status == "completed":
                        checkbox_char = "x"
                    elif archon_status == "in_progress":
                        checkbox_char = "-"

                    # Update checkbox if different
                    current_checkbox = line_stripped[3:4]
                    if current_checkbox != checkbox_char:
                        # Update the checkbox
                        prefix = line_stripped[:3]
                        suffix = line_stripped[4:]
                        line = line.replace(line_stripped, f"{prefix}{checkbox_char}{suffix}")
                        task_updates += 1

                        # Add Archon context as comment
                        if archon_task.get("context"):
                            comment = f"<!-- Archon context: {archon_task['context']} -->"
                            if comment not in content:
                                updated_lines.append(comment)

            updated_lines.append(line)

        # Write updated content if changes made
        if task_updates > 0:
            try:
                with open(tasks_file, 'w') as f:
                    f.write('\n'.join(updated_lines))

                print(f"   ✅ Updated {task_updates} task statuses")
                updates_needed += task_updates

            except Exception as e:
                print(f"   ❌ Error updating {tasks_file}: {e}")

    if updates_needed > 0:
        print(f"\n✅ Updated {updates_needed} task statuses in OpenSpec")
    else:
        print("\n✅ OpenSpec already up to date")

    return updates_needed

def show_sync_status():
    """Show sync status between OpenSpec and Archon"""
    print("📊 OpenSpec ↔ Archon Sync Status")
    print("=" * 50)

    openspec_data = load_openspec_data()
    archon_data = load_archon_data()

    # Count OpenSpec tasks
    openspec_task_count = sum(
        len(change_data["tasks"])
        for change_data in openspec_data["changes"].values()
    )

    # Count Archon tasks
    archon_task_count = len(archon_data["tasks"])

    # Count OpenSpec-sourced tasks in Archon
    openspec_sourced_in_archon = sum(
        1 for task in archon_data["tasks"].values()
        if task.get("source") == "openspec"
    )

    print(f"\n📋 Task Counts:")
    print(f"   OpenSpec tasks: {openspec_task_count}")
    print(f"   Archon tasks: {archon_task_count}")
    print(f"   OpenSpec → Archon: {openspec_sourced_in_archon}")

    # Show last sync times
    archon_tasks_file = Path("archon_tasks.json")
    if archon_tasks_file.exists():
        try:
            with open(archon_tasks_file, 'r') as f:
                data = json.load(f)
                last_sync = data.get("last_sync_from_openspec")
                if last_sync:
                    sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                    print(f"\n🕒 Last OpenSpec → Archon sync: {sync_time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"\n⚠️  Could not read sync timestamp: {e}")

    # Show knowledge accumulation
    knowledge_patterns = len(archon_data["knowledge"].get("completed_patterns", []))
    print(f"\n🧠 Accumulated Knowledge Patterns: {knowledge_patterns}")

    # Show recent Archon activity
    if archon_data["sessions"]:
        recent_sessions = sorted(
            archon_data["sessions"].values(),
            key=lambda x: x.get("started_at", ""),
            reverse=True
        )[:3]

        if recent_sessions:
            print(f"\n🕒 Recent Archon Sessions:")
            for session in recent_sessions:
                started = session.get("started_at", "")[:16] if session.get("started_at") else "Unknown"
                status = session.get("status", "unknown")
                print(f"   • {started} - {status}")

def sync_all():
    """Perform bidirectional sync"""
    print("🔄 Performing bidirectional sync...")

    to_archon = sync_to_archon()
    from_archon = sync_from_archon()

    print(f"\n✅ Sync Complete:")
    print(f"   • {to_archon} new tasks synced to Archon")
    print(f"   • {from_archon} task statuses updated in OpenSpec")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="OpenSpec ↔ Archon Integration Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --to-archon       # Push OpenSpec tasks to Archon
  %(prog)s --from-archon     # Pull Archon progress to OpenSpec
  %(prog)s --status          # Show sync status
  %(prog)s --sync-all        # Bidirectional sync
        """
    )

    parser.add_argument('--to-archon', action='store_true',
                       help='Sync OpenSpec tasks to Archon')
    parser.add_argument('--from-archon', action='store_true',
                       help='Sync Archon progress to OpenSpec')
    parser.add_argument('--status', action='store_true',
                       help='Show sync status')
    parser.add_argument('--sync-all', action='store_true',
                       help='Perform bidirectional sync')

    args = parser.parse_args()

    if not any([args.to_archon, args.from_archon, args.status, args.sync_all]):
        parser.print_help()
        return

    try:
        if args.status:
            show_sync_status()
        elif args.to_archon:
            sync_to_archon()
        elif args.from_archon:
            sync_from_archon()
        elif args.sync_all:
            sync_all()

    except KeyboardInterrupt:
        print("\n⏹️  Sync interrupted by user")
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
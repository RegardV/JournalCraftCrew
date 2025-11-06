#!/usr/bin/env python3
"""
Unified Development Assistant CLI Tool

A command-line interface for developers to access Archon-powered development guidance
with integrated task tracking and knowledge accumulation for building the Journal Craft Crew platform.

Usage:
    # Research Commands
    python dev_assistant_cli.py storage
    python dev_assistant_cli.py auth
    python dev_assistant_cli.py deployment
    python dev_assistant_cli.py architecture "FastAPI microservices design"
    python dev_assistant_cli.py patterns "React" "file upload"

    # Task Tracking Commands
    python dev_assistant_cli.py track "Implement JournalLibrary component" --status pending --context "React frontend"
    python dev_assistant_cli.py research "React file tree components" --for-task "Implement JournalLibrary component"
    python dev_assistant_cli.py status
    python dev_assistant_cli.py complete "Implement JournalLibrary component" --notes "Component created with file tree and PDF viewer"

Features:
    - ✅ Research guidance with automatic task association
    - ✅ Project status tracking with AI context
    - ✅ Knowledge accumulation across sessions
    - ✅ Pattern learning from completed tasks
    - ✅ Session-based development tracking
"""

import asyncio
import sys
import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# Import the development assistant
try:
    from app.services.development_assistant import (
        research_file_storage,
        research_authentication,
        research_deployment,
        get_architecture_advice,
        research_implementation
    )
    ASSISTANT_AVAILABLE = True
except ImportError as e:
    print(f"❌ Development assistant not available: {e}")
    ASSISTANT_AVAILABLE = False

def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_results(results: dict, title: str):
    """Print formatted research results."""
    print(f"\n📊 Results for: {title}")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if results.get('success', False):
        print(f"✅ Research successful!")
        print(f"📄 Total results: {results.get('total_results', 0)}")

        # Print recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")

        # Print categories if available
        categories = results.get('categories', {})
        if categories:
            print(f"\n📂 Categories Found:")
            for category, items in categories.items():
                if items:
                    print(f"   • {category.replace('_', ' ').title()}: {len(items)} items")

        # Print best practices if available
        best_practices = results.get('best_practices', [])
        if best_practices:
            print(f"\n⭐ Best Practices:")
            for i, practice in enumerate(best_practices[:3], 1):  # Show top 3
                content = practice.get('content', practice.get('title', ''))
                if content:
                    # Truncate long content
                    if len(content) > 100:
                        content = content[:100] + "..."
                    print(f"   {i}. {content}")

        # Print patterns if available
        patterns = results.get('patterns', [])
        if patterns:
            print(f"\n🔧 Implementation Patterns:")
            for i, pattern in enumerate(patterns[:3], 1):  # Show top 3
                content = pattern.get('content', pattern.get('title', ''))
                if content:
                    if len(content) > 100:
                        content = content[:100] + "..."
                    print(f"   {i}. {content}")

    else:
        print(f"❌ Research failed: {results.get('message', 'Unknown error')}")

        if results.get('fallback_used', False):
            print(f"\n⚠️  Using fallback mode - Archon knowledge base temporarily unavailable")
            print(f"💡 Manual research suggested for: {title}")

# ==============================
# TASK TRACKING SYSTEM
# ==============================

ARCHON_TASKS_FILE = "archon_tasks.json"
ARCHON_KNOWLEDGE_FILE = "archon_knowledge.json"

def load_archon_data():
    """Load Archon task tracking data"""
    data = {"tasks": {}, "knowledge": {}, "sessions": {}}

    if os.path.exists(ARCHON_TASKS_FILE):
        try:
            with open(ARCHON_TASKS_FILE, 'r') as f:
                task_data = json.load(f)
                data["tasks"] = task_data.get("tasks", {})
                data["sessions"] = task_data.get("sessions", {})
        except Exception as e:
            print(f"⚠️  Warning: Could not load tasks file: {e}")

    if os.path.exists(ARCHON_KNOWLEDGE_FILE):
        try:
            with open(ARCHON_KNOWLEDGE_FILE, 'r') as f:
                data["knowledge"] = json.load(f)
        except Exception as e:
            print(f"⚠️  Warning: Could not load knowledge file: {e}")

    return data

def save_archon_data(data):
    """Save Archon task tracking data"""
    try:
        # Save tasks
        task_data = {
            "tasks": data["tasks"],
            "sessions": data["sessions"],
            "last_updated": datetime.now().isoformat()
        }
        with open(ARCHON_TASKS_FILE, 'w') as f:
            json.dump(task_data, f, indent=2)

        # Save knowledge separately
        with open(ARCHON_KNOWLEDGE_FILE, 'w') as f:
            json.dump(data["knowledge"], f, indent=2)

        return True
    except Exception as e:
        print(f"❌ Error saving Archon data: {e}")
        return False

def track_task(task_name, status="pending", research_findings=None, context=None, implementation_notes=None):
    """Track a task in Archon's knowledge base"""
    data = load_archon_data()

    task_id = task_name.lower().replace(" ", "_").replace("-", "_")

    if task_id not in data["tasks"]:
        data["tasks"][task_id] = {
            "name": task_name,
            "created_at": datetime.now().isoformat(),
            "status": status,
            "history": []
        }
    else:
        data["tasks"][task_id]["status"] = status

    # Update task with new information
    task = data["tasks"][task_id]
    task["updated_at"] = datetime.now().isoformat()

    if research_findings:
        task["research_findings"] = research_findings

    if context:
        task["context"] = context

    if implementation_notes:
        task["implementation_notes"] = implementation_notes

    # Add to history
    task["history"].append({
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "research_findings": research_findings,
        "context": context,
        "implementation_notes": implementation_notes
    })

    # Store in knowledge base for pattern learning
    if status == "completed" and research_findings:
        if "completed_patterns" not in data["knowledge"]:
            data["knowledge"]["completed_patterns"] = []

        data["knowledge"]["completed_patterns"].append({
            "task_name": task_name,
            "pattern_type": context,
            "research_findings": research_findings,
            "implementation_notes": implementation_notes,
            "completed_at": datetime.now().isoformat()
        })

    save_archon_data(data)
    return task_id

def get_project_context():
    """Get AI-powered project status and suggestions"""
    data = load_archon_data()

    # Analyze current state
    total_tasks = len(data["tasks"])
    completed_tasks = sum(1 for task in data["tasks"].values() if task.get("status") == "completed")
    in_progress_tasks = sum(1 for task in data["tasks"].values() if task.get("status") == "in_progress")
    pending_tasks = sum(1 for task in data["tasks"].values() if task.get("status") == "pending")

    context = {
        "summary": {
            "total_tasks": total_tasks,
            "completed": completed_tasks,
            "in_progress": in_progress_tasks,
            "pending": pending_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        },
        "recent_activity": [],
        "suggestions": [],
        "knowledge_patterns": data["knowledge"].get("completed_patterns", [])
    }

    # Get recent activity
    recent_sessions = sorted(
        data["sessions"].values(),
        key=lambda x: x.get("ended_at", ""),
        reverse=True
    )[:3]

    context["recent_activity"] = recent_sessions

    # Generate suggestions based on patterns
    patterns = data["knowledge"].get("completed_patterns", [])
    if patterns:
        # Find related patterns
        context["suggestions"] = [
            f"Consider similar patterns from: {p['task_name']}"
            for p in patterns[-3:]  # Last 3 completed patterns
        ]

    return context

def start_session():
    """Start a new development session"""
    data = load_archon_data()
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    data["sessions"][session_id] = {
        "started_at": datetime.now().isoformat(),
        "tasks_worked_on": [],
        "research_conducted": [],
        "status": "active"
    }

    save_archon_data(data)
    return session_id

def end_session(session_id, summary=None, next_priorities=None):
    """End a development session with learning capture"""
    data = load_archon_data()

    if session_id in data["sessions"]:
        data["sessions"][session_id].update({
            "ended_at": datetime.now().isoformat(),
            "status": "completed",
            "summary": summary,
            "next_priorities": next_priorities
        })

        save_archon_data(data)
        return True

    return False

async def cmd_track_task(task_name, status=None, context=None):
    """Track a task in Archon's knowledge base"""
    print_header(f"Task Tracking: {task_name}")

    task_id = track_task(
        task_name=task_name,
        status=status or "pending",
        context=context
    )

    print(f"✅ Task tracked successfully!")
    print(f"🆔 Task ID: {task_id}")
    print(f"📊 Status: {status or 'pending'}")

    if context:
        print(f"📝 Context: {context}")

async def cmd_status():
    """Show project status with Archon context"""
    print_header("Project Status & Context")

    context = get_project_context()

    print(f"\n📊 Project Summary:")
    summary = context["summary"]
    print(f"   • Total Tasks: {summary['total_tasks']}")
    print(f"   • Completed: {summary['completed']}")
    print(f"   • In Progress: {summary['in_progress']}")
    print(f"   • Pending: {summary['pending']}")
    print(f"   • Completion Rate: {summary['completion_rate']:.1f}%")

    if context["recent_activity"]:
        print(f"\n🕒 Recent Sessions:")
        for session in context["recent_activity"]:
            started = session.get("started_at", "")[:16] if session.get("started_at") else "Unknown"
            status = session.get("status", "unknown")
            print(f"   • {started} - {status}")

    if context["suggestions"]:
        print(f"\n💡 AI Suggestions:")
        for suggestion in context["suggestions"]:
            print(f"   • {suggestion}")

    if context["knowledge_patterns"]:
        print(f"\n🧠 Learned Patterns: {len(context['knowledge_patterns'])} patterns available")

    # Show current tasks
    data = load_archon_data()
    if data["tasks"]:
        print(f"\n📋 Current Tasks:")
        for task_id, task in data["tasks"].items():
            status_icon = {"completed": "✅", "in_progress": "🔄", "pending": "⏳"}.get(task.get("status"), "❓")
            print(f"   {status_icon} {task['name']} ({task.get('status', 'unknown')})")

async def cmd_research_with_tracking(topic, for_task=None):
    """Research with automatic task association"""
    print_header(f"Research with Tracking: {topic}")

    if not ASSISTANT_AVAILABLE:
        print("❌ Development assistant not available")
        return

    # Track the research
    if for_task:
        track_task(for_task, status="in_progress", context=f"Researching: {topic}")

    print(f"🔍 Researching: {topic}")
    if for_task:
        print(f"🔗 Associated with task: {for_task}")

    results = await get_architecture_advice(topic)
    print_results(results, topic)

    # Store research findings
    if for_task and results.get('success'):
        findings = results.get('recommendations', [])[:3]  # Top 3 recommendations
        track_task(
            for_task,
            status="in_progress",
            research_findings=findings,
            context=f"Research completed: {topic}"
        )

        print(f"\n🔗 Research findings linked to task: {for_task}")

async def cmd_complete_task(task_name, implementation_notes=None):
    """Mark a task as completed with learning capture"""
    print_header(f"Completing Task: {task_name}")

    data = load_archon_data()
    task_id = task_name.lower().replace(" ", "_").replace("-", "_")

    if task_id in data["tasks"]:
        task = data["tasks"][task_id]

        # Mark as completed
        track_task(
            task_name=task_name,
            status="completed",
            research_findings=task.get("research_findings"),
            context=task.get("context"),
            implementation_notes=implementation_notes
        )

        print(f"✅ Task completed successfully!")
        print(f"📝 Implementation notes captured")

        if implementation_notes:
            print(f"📄 Notes: {implementation_notes}")

        # Show what was learned
        if task.get("research_findings"):
            print(f"🧠 Research findings preserved for future projects")

    else:
        print(f"❌ Task not found: {task_name}")
        print(f"💡 Use 'track' command to create the task first")

async def cmd_storage():
    """Research file storage solutions."""
    print_header("File Storage Solutions Research")

    if not ASSISTANT_AVAILABLE:
        print("❌ Development assistant not available")
        return

    print("🔍 Researching file storage solutions (Google Drive, Dropbox, AWS S3, etc.)...")
    results = await research_file_storage()
    print_results(results, "File Storage Solutions")

async def cmd_auth():
    """Research authentication patterns."""
    print_header("Authentication Patterns Research")

    if not ASSISTANT_AVAILABLE:
        print("❌ Development assistant not available")
        return

    print("🔍 Researching authentication patterns (Firebase, OAuth, JWT, etc.)...")
    results = await research_authentication()
    print_results(results, "Authentication Patterns")

async def cmd_deployment():
    """Research VPS deployment strategies."""
    print_header("VPS Deployment Strategies Research")

    if not ASSISTANT_AVAILABLE:
        print("❌ Development assistant not available")
        return

    print("🔍 Researching VPS deployment strategies (Docker, security, monitoring, etc.)...")
    results = await research_deployment()
    print_results(results, "VPS Deployment Strategies")

async def cmd_architecture(context: str):
    """Get architecture guidance."""
    print_header(f"Architecture Guidance: {context}")

    if not ASSISTANT_AVAILABLE:
        print("❌ Development assistant not available")
        return

    print(f"🔍 Getting architecture guidance for: {context}")
    results = await get_architecture_advice(context)
    print_results(results, f"Architecture Guidance - {context}")

async def cmd_patterns(technology: str, use_case: str):
    """Research implementation patterns."""
    print_header(f"Implementation Patterns: {technology} - {use_case}")

    if not ASSISTANT_AVAILABLE:
        print("❌ Development assistant not available")
        return

    print(f"🔍 Researching {technology} implementation patterns for: {use_case}")
    results = await research_implementation(technology, use_case)
    print_results(results, f"{technology} Implementation Patterns - {use_case}")

async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Development Assistant CLI - Get Archon-powered development guidance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s storage                    # Research file storage solutions
  %(prog)s auth                       # Research authentication patterns
  %(prog)s deployment                 # Research VPS deployment strategies
  %(prog)s architecture "microservices"  # Get architecture guidance
  %(prog)s patterns "React" "file upload"  # Research implementation patterns
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Storage command
    subparsers.add_parser('storage', help='Research file storage solutions')

    # Auth command
    subparsers.add_parser('auth', help='Research authentication patterns')

    # Deployment command
    subparsers.add_parser('deployment', help='Research VPS deployment strategies')

    # Architecture command
    arch_parser = subparsers.add_parser('architecture', help='Get architecture guidance')
    arch_parser.add_argument('context', help='Architecture topic or question')

    # Patterns command
    patterns_parser = subparsers.add_parser('patterns', help='Research implementation patterns')
    patterns_parser.add_argument('technology', help='Technology to research')
    patterns_parser.add_argument('use_case', help='Specific use case')

    # ==============================
    # TASK TRACKING COMMANDS
    # ==============================

    # Track task command
    track_parser = subparsers.add_parser('track', help='Track a task in Archon knowledge base')
    track_parser.add_argument('task_name', help='Name of the task to track')
    track_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed'], help='Task status')
    track_parser.add_argument('--context', help='Task context or description')

    # Status command
    subparsers.add_parser('status', help='Show project status with AI context')

    # Research with tracking command
    research_parser = subparsers.add_parser('research', help='Research with automatic task association')
    research_parser.add_argument('topic', help='Research topic')
    research_parser.add_argument('--for-task', help='Associate research with this task')

    # Complete task command
    complete_parser = subparsers.add_parser('complete', help='Mark task as completed with learning capture')
    complete_parser.add_argument('task_name', help='Name of task to complete')
    complete_parser.add_argument('--notes', help='Implementation notes')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    try:
        if args.command == 'storage':
            await cmd_storage()
        elif args.command == 'auth':
            await cmd_auth()
        elif args.command == 'deployment':
            await cmd_deployment()
        elif args.command == 'architecture':
            await cmd_architecture(args.context)
        elif args.command == 'patterns':
            await cmd_patterns(args.technology, args.use_case)

        # Task tracking commands
        elif args.command == 'track':
            await cmd_track_task(args.task_name, args.status, args.context)
        elif args.command == 'status':
            await cmd_status()
        elif args.command == 'research':
            await cmd_research_with_tracking(args.topic, args.for_task)
        elif args.command == 'complete':
            await cmd_complete_task(args.task_name, args.notes)
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()

    except KeyboardInterrupt:
        print(f"\n⏹️  Research interrupted by user")
    except Exception as e:
        print(f"❌ Error executing command: {e}")

if __name__ == "__main__":
    if not ASSISTANT_AVAILABLE:
        print("❌ Development Assistant CLI not available")
        print("💡 Make sure the app/services/development_assistant.py module is accessible")
        sys.exit(1)

    asyncio.run(main())
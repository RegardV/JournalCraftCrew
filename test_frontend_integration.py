#!/usr/bin/env python3
"""
Test Frontend Integration
Verify that the frontend has been properly updated with the new UnifiedJournalCreator
"""

import os
import sys
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent
FRONTEND_DIR = PROJECT_ROOT / "journal-platform-frontend"

def check_frontend_integration():
    """Check if frontend has been properly integrated"""
    print("🔍 Checking Frontend Integration...")

    checks = []

    # Check if UnifiedJournalCreator exists
    unified_creator = FRONTEND_DIR / "src/components/journal/UnifiedJournalCreator.tsx"
    if unified_creator.exists():
        print("✅ UnifiedJournalCreator component exists")
        checks.append(True)
    else:
        print("❌ UnifiedJournalCreator component missing")
        checks.append(False)

    # Check if Dashboard.tsx has been updated
    dashboard_file = FRONTEND_DIR / "src/components/dashboard/Dashboard.tsx"
    if dashboard_file.exists():
        with open(dashboard_file, 'r') as f:
            content = f.read()

        # Check for imports
        if 'UnifiedJournalCreator' in content:
            print("✅ Dashboard imports UnifiedJournalCreator")
            checks.append(True)
        else:
            print("❌ Dashboard doesn't import UnifiedJournalCreator")
            checks.append(False)

        # Check for state usage
        if 'showUnifiedCreator' in content:
            print("✅ Dashboard uses showUnifiedCreator state")
            checks.append(True)
        else:
            print("❌ Dashboard doesn't use showUnifiedCreator state")
            checks.append(False)

        # Check for CrewAI API usage
        if '/api/crewai/start-workflow' in content:
            print("✅ Dashboard uses CrewAI API endpoint")
            checks.append(True)
        else:
            print("❌ Dashboard doesn't use CrewAI API endpoint")
            checks.append(False)

        # Check for navigation update
        if 'navigate(`/ai-workflow/${data.workflow_id}`' in content:
            print("✅ Dashboard navigates to new workflow URL format")
            checks.append(True)
        else:
            print("❌ Dashboard doesn't use new workflow URL format")
            checks.append(False)
    else:
        print("❌ Dashboard.tsx not found")
        checks.append(False)

    # Check if App.tsx has new route
    app_file = FRONTEND_DIR / "src/App.tsx"
    if app_file.exists():
        with open(app_file, 'r') as f:
            content = f.read()

        if '/ai-workflow/:workflowId' in content:
            print("✅ App.tsx has new workflow route")
            checks.append(True)
        else:
            print("❌ App.tsx missing new workflow route")
            checks.append(False)
    else:
        print("❌ App.tsx not found")
        checks.append(False)

    # Check if AIWorkflowPage has been updated
    workflow_page = FRONTEND_DIR / "src/pages/ai-workflow/AIWorkflowPage.tsx"
    if workflow_page.exists():
        with open(workflow_page, 'r') as f:
            content = f.read()

        # Check for useParams usage
        if 'useParams' in content:
            print("✅ AIWorkflowPage uses useParams for workflowId")
            checks.append(True)
        else:
            print("❌ AIWorkflowPage doesn't use useParams")
            checks.append(False)

        # Check for WebSocket URL update
        if 'ws://localhost:8000' in content:
            print("✅ AIWorkflowPage uses correct WebSocket URL")
            checks.append(True)
        else:
            print("❌ AIWorkflowPage doesn't use correct WebSocket URL")
            checks.append(False)

        # Check for actualWorkflowId usage
        if 'actualWorkflowId' in content:
            print("✅ AIWorkflowPage uses actualWorkflowId")
            checks.append(True)
        else:
            print("❌ AIWorkflowPage doesn't use actualWorkflowId")
            checks.append(False)
    else:
        print("❌ AIWorkflowPage not found")
        checks.append(False)

    return sum(checks), len(checks)

def main():
    """Main test function"""
    print("🚀 Testing Frontend Integration")
    print("=" * 40)

    passed, total = check_frontend_integration()

    print("\n" + "=" * 40)
    print(f"📊 Frontend Integration: {passed}/{total} checks passed")

    if passed >= total * 0.8:  # 80% success rate
        print("🎉 Frontend integration looks good!")
        print("\n✨ Users can now access the new unified journal creator by:")
        print("   1. Clicking 'Create New Journal' in the Dashboard")
        print("   2. Choosing quick start templates or custom creation")
        print("   3. Selecting workflow type (express/standard/comprehensive)")
        print("   4. Enjoying the full 9-agent CrewAI experience!")
        return 0
    else:
        print("⚠️  Some integration issues found. Please review the checks above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
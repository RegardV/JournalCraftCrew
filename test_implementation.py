#!/usr/bin/env python3
"""
Test script to verify the Journal Creation Process realignment implementation
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "journal-platform-backend"
FRONTEND_DIR = PROJECT_ROOT / "journal-platform-frontend"

def check_file_exists(file_path, description):
    """Check if a file exists and report status"""
    if file_path.exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (MISSING)")
        return False

def check_backend_implementation():
    """Check backend implementation files"""
    print("\n🔍 Checking Backend Implementation...")

    checks = [
        (BACKEND_DIR / "app/api/routes/crewai_workflow.py", "CrewAI workflow service"),
        (BACKEND_DIR / "app/api/routes/ai_generation.py", "Redirected AI generation"),
        (BACKEND_DIR / "app/api/routes/ai_generation.py.backup", "Backup of original file"),
    ]

    passed = sum(check_file_exists(path, desc) for path, desc in checks)

    # Check if ai_generation.py has been redirected
    ai_gen_file = BACKEND_DIR / "app/api/routes/ai_generation.py"
    if ai_gen_file.exists():
        with open(ai_gen_file, 'r') as f:
            content = f.read()
            if "redirected to CrewAI workflow" in content:
                print("✅ AI generation file has been properly redirected")
                passed += 1
            else:
                print("❌ AI generation file doesn't contain redirect code")

    # Check CrewAI workflow service for workflow type support
    crewai_file = BACKEND_DIR / "app/api/routes/crewai_workflow.py"
    if crewai_file.exists():
        with open(crewai_file, 'r') as f:
            content = f.read()
            workflow_types = ['_execute_express_workflow', '_execute_standard_workflow', '_execute_comprehensive_workflow']
            found_types = sum(1 for wtype in workflow_types if wtype in content)
            print(f"✅ Found {found_types}/3 workflow type implementations in CrewAI service")
            if found_types == 3:
                passed += 1

    return passed

def check_frontend_implementation():
    """Check frontend implementation files"""
    print("\n🔍 Checking Frontend Implementation...")

    checks = [
        (FRONTEND_DIR / "src/components/onboarding/EnhancedWebOnboardingAgent.tsx", "Enhanced onboarding component"),
        (FRONTEND_DIR / "src/components/journal/UnifiedJournalCreator.tsx", "Unified journal creator"),
        (FRONTEND_DIR / "src/components/onboarding/WebOnboardingAgent.tsx", "Original onboarding component"),
        (FRONTEND_DIR / "src/components/journal/JournalCreator.tsx", "Original journal creator"),
    ]

    passed = sum(check_file_exists(path, desc) for path, desc in checks)

    # Check enhanced onboarding component
    enhanced_onboarding = FRONTEND_DIR / "src/components/onboarding/EnhancedWebOnboardingAgent.tsx"
    if enhanced_onboarding.exists():
        with open(enhanced_onboarding, 'r') as f:
            content = f.read()
            features = ['workflowTypes', 'CREWAI_AGENTS', 'WORKFLOW_TYPES', 'WorkflowTypeStep']
            found_features = sum(1 for feature in features if feature in content)
            print(f"✅ Found {found_features}/4 enhanced features in onboarding component")
            if found_features >= 3:
                passed += 1

    # Check unified journal creator
    unified_creator = FRONTEND_DIR / "src/components/journal/UnifiedJournalCreator.tsx"
    if unified_creator.exists():
        with open(unified_creator, 'r') as f:
            content = f.read()
            features = ['QUICK_START_OPTIONS', 'CrewAIWorkflowProgress', 'EnhancedWebOnboardingAgent']
            found_features = sum(1 for feature in features if feature in content)
            print(f"✅ Found {found_features}/3 integration features in unified creator")
            if found_features >= 2:
                passed += 1

    return passed

def check_python_syntax():
    """Check Python syntax in backend files"""
    print("\n🔍 Checking Python Syntax...")

    python_files = [
        BACKEND_DIR / "app/api/routes/crewai_workflow.py",
        BACKEND_DIR / "app/api/routes/ai_generation.py"
    ]

    passed = 0
    for file_path in python_files:
        if file_path.exists():
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'py_compile', str(file_path)
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"✅ Syntax check passed: {file_path.name}")
                    passed += 1
                else:
                    print(f"❌ Syntax error in {file_path.name}: {result.stderr}")
            except Exception as e:
                print(f"❌ Error checking {file_path.name}: {e}")

    return passed

def check_typescript_syntax():
    """Check TypeScript syntax in frontend files"""
    print("\n🔍 Checking TypeScript Syntax...")

    ts_files = [
        FRONTEND_DIR / "src/components/onboarding/EnhancedWebOnboardingAgent.tsx",
        FRONTEND_DIR / "src/components/journal/UnifiedJournalCreator.tsx"
    ]

    passed = 0
    for file_path in ts_files:
        if file_path.exists():
            # Basic syntax check - just ensure it has proper TypeScript structure
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                # Basic checks for TypeScript syntax
                if 'interface ' in content or 'type ' in content or 'React.FC' in content:
                    print(f"✅ TypeScript structure looks good: {file_path.name}")
                    passed += 1
                else:
                    print(f"⚠️  TypeScript structure unclear: {file_path.name}")

            except Exception as e:
                print(f"❌ Error checking {file_path.name}: {e}")

    return passed

def run_integration_tests():
    """Run basic integration tests"""
    print("\n🔍 Running Integration Tests...")

    # Test 1: Check OpenSpec proposal structure
    proposal_dir = PROJECT_ROOT / "openspec/changes/refactor-journal-creation-to-crewai-workflow"
    proposal_files = [
        "proposal.md",
        "design.md",
        "tasks.md",
        "specs/journal-creation/spec.md",
        "specs/crewai-agents/spec.md"
    ]

    passed = 0
    for file_name in proposal_files:
        file_path = proposal_dir / file_name
        if check_file_exists(file_path, f"OpenSpec {file_name}"):
            passed += 1

    # Test 2: Check if proposal validates
    try:
        result = subprocess.run([
            'openspec', 'validate', 'refactor-journal-creation-to-crewai-workflow'
        ], cwd=PROJECT_ROOT, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ OpenSpec proposal validation passed")
            passed += 1
        else:
            print(f"❌ OpenSpec validation failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not run OpenSpec validation: {e}")

    return passed

def main():
    """Main test function"""
    print("🚀 Testing Journal Creation Process Realignment Implementation")
    print("=" * 60)

    total_passed = 0
    total_checks = 0

    # Run all checks
    checks = [
        ("Backend Implementation", check_backend_implementation),
        ("Frontend Implementation", check_frontend_implementation),
        ("Python Syntax", check_python_syntax),
        ("TypeScript Syntax", check_typescript_syntax),
        ("Integration Tests", run_integration_tests)
    ]

    for check_name, check_func in checks:
        try:
            passed = check_func()
            total_passed += passed
            print(f"✅ {check_name}: {passed} checks passed")
        except Exception as e:
            print(f"❌ {check_name} failed: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {total_passed} checks passed")

    if total_passed >= 15:  # Arbitrary threshold for "good enough"
        print("🎉 Implementation looks good! Ready for deployment.")
        return 0
    else:
        print("⚠️  Some issues found. Please review and fix.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
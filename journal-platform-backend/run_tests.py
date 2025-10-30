#!/usr/bin/env python3
"""
Test Runner Script for Journal Platform
Phase 3.5: API Testing Suite
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with return code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Journal Platform Test Runner")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "all", "coverage", "fast"],
        default="fast",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--marker",
        help="pytest marker to run specific test categories"
    )
    parser.add_argument(
        "--file",
        help="specific test file to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="verbose output"
    )

    args = parser.parse_args()

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    print("🚀 Journal Platform Test Runner")
    print(f"📁 Working directory: {project_dir}")

    # Set environment variables for testing
    env = os.environ.copy()
    env["TESTING"] = "true"
    env["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
    env["LOG_LEVEL"] = "INFO"

    success = True

    if args.type == "unit":
        # Run unit tests only
        cmd = ["python", "-m", "pytest", "-m", "unit", "-v"]
        if args.verbose:
            cmd.append("-vv")
        success = run_command(cmd, "Running Unit Tests")

    elif args.type == "integration":
        # Run integration tests only
        cmd = ["python", "-m", "pytest", "-m", "integration", "-v"]
        if args.verbose:
            cmd.append("-vv")
        success = run_command(cmd, "Running Integration Tests")

    elif args.type == "coverage":
        # Run tests with coverage
        cmd = [
            "python", "-m", "pytest",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml",
            "--cov-fail-under=80",
            "-v"
        ]
        if args.verbose:
            cmd.append("-vv")
        success = run_command(cmd, "Running Tests with Coverage")

    elif args.type == "all":
        # Run all tests
        cmd = ["python", "-m", "pytest", "tests/", "-v"]
        if args.verbose:
            cmd.append("-vv")
        success = run_command(cmd, "Running All Tests")

    elif args.marker:
        # Run tests with specific marker
        cmd = ["python", "-m", "pytest", f"-m={args.marker}", "-v"]
        if args.verbose:
            cmd.append("-vv")
        success = run_command(cmd, f"Running Tests with Marker: {args.marker}")

    elif args.file:
        # Run specific test file
        cmd = ["python", "-m", "pytest", args.file, "-v"]
        if args.verbose:
            cmd.append("-vv")
        success = run_command(cmd, f"Running Test File: {args.file}")

    else:  # fast (default)
        # Run fast tests (exclude slow tests)
        cmd = [
            "python", "-m", "pytest",
            "-m", "not slow",
            "-v",
            "--tb=short"
        ]
        if args.verbose:
            cmd.append("-vv")
        success = run_command(cmd, "Running Fast Tests (Excluding Slow Tests)")

    # Print test results summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests completed successfully!")
        if args.type == "coverage":
            print("📊 Coverage report generated in htmlcov/ directory")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

    # Print next steps
    print(f"\n📋 Test Runner Options:")
    print(f"   • Run unit tests:     python run_tests.py --type unit")
    print(f"   • Run integration:    python run_tests.py --type integration")
    print(f"   • Run with coverage: python run_tests.py --type coverage")
    print(f"   • Run specific marker: python run_tests.py --marker auth")
    print(f"   • Run specific file: python run_tests.py --file tests/test_auth_api.py")
    print(f"   • Verbose output:    python run_tests.py --verbose")


if __name__ == "__main__":
    main()
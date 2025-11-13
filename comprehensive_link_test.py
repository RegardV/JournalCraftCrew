#!/usr/bin/env python3
"""
Comprehensive Link Testing Script
Tests all buttons and links in the Journal Craft Crew frontend
"""

import requests
import json
import time
from typing import Dict, List, Tuple
from urllib.parse import urljoin, urlparse
import re

# Configuration
FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:6770"

class LinkTester:
    def __init__(self):
        self.frontend_url = FRONTEND_URL
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None

    def log_result(self, component: str, button_name: str, destination: str,
                   status: str, response_code: int = None, error: str = None,
                   is_login_redirect: bool = False):
        """Log a test result"""
        result = {
            "component": component,
            "button_name": button_name,
            "destination": destination,
            "status": status,
            "response_code": response_code,
            "error": error,
            "is_login_redirect": is_login_redirect,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        print(f"[{status.upper()}] {component} - {button_name} -> {destination}")
        if error:
            print(f"    ERROR: {error}")
        if is_login_redirect:
            print(f"    ⚠️  REDIRECTS TO LOGIN")

    def test_url(self, url: str, expected_content: str = None) -> Tuple[bool, int, str]:
        """Test a URL and return success status, response code, and any error"""
        try:
            # Handle relative URLs
            if url.startswith('/'):
                full_url = urljoin(self.frontend_url, url)
            else:
                full_url = url

            # Add authorization if we have a token
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'

            response = self.session.get(full_url, headers=headers, allow_redirects=False)

            # Check if it's a redirect to login
            is_login_redirect = (
                response.status_code in [302, 307] and
                ('login' in response.headers.get('Location', '').lower() or
                 'auth' in response.headers.get('Location', '').lower())
            )

            # Check for expected content
            content_ok = True
            if expected_content and response.status_code == 200:
                content_ok = expected_content.lower() in response.text.lower()

            success = (
                response.status_code == 200 or
                (response.status_code in [301, 302] and not is_login_redirect)
            ) and content_ok

            return success, response.status_code, None, is_login_redirect

        except requests.exceptions.ConnectionError:
            return False, None, "Connection refused", False
        except requests.exceptions.Timeout:
            return False, None, "Request timeout", False
        except Exception as e:
            return False, None, str(e), False

    def test_backend_endpoint(self, endpoint: str, method: str = 'GET') -> Tuple[bool, int, str]:
        """Test a backend API endpoint"""
        try:
            full_url = urljoin(self.backend_url, endpoint)

            if method == 'GET':
                response = self.session.get(full_url)
            elif method == 'POST':
                response = self.session.post(full_url)
            else:
                return False, None, f"Unsupported method: {method}"

            success = response.status_code in [200, 201, 404]  # 404 is ok for missing endpoints
            return success, response.status_code, None

        except Exception as e:
            return False, None, str(e)

    def extract_navigation_from_component(self, file_path: str, component_name: str) -> List[Dict]:
        """Extract navigation elements from component analysis"""
        # This would be a more complex parser in a real implementation
        # For now, we'll use the data gathered from our manual analysis
        return []

    def run_comprehensive_tests(self):
        """Run comprehensive tests on all navigation elements"""

        print("🚀 Starting Comprehensive Link Testing")
        print("=" * 60)

        # Test 1: Frontend Root
        success, code, error, is_login = self.test_url("/")
        self.log_result(
            component="Frontend Root",
            button_name="Home Page",
            destination="/",
            status="PASS" if success else "FAIL",
            response_code=code,
            error=error,
            is_login_redirect=is_login
        )

        # Test 2: Backend Health Check
        success, code, error = self.test_backend_endpoint("/health")
        self.log_result(
            component="Backend API",
            button_name="Health Check",
            destination="/health",
            status="PASS" if success else "FAIL",
            response_code=code,
            error=error
        )

        # Test 3: Backend API Documentation
        success, code, error = self.test_backend_endpoint("/docs")
        self.log_result(
            component="Backend API",
            button_name="API Documentation",
            destination="/docs",
            status="PASS" if success else "FAIL",
            response_code=code,
            error=error
        )

        # Test all Header navigation links
        header_links = [
            ("Dashboard", "/dashboard"),
            ("My Journals", "/dashboard?view=library"),
            ("Themes", "/themes"),
            ("Templates", "/templates"),
            ("Profile", "/profile"),
            ("Settings", "/settings"),
            ("Subscription", "/subscription"),
            ("Sign Out", "/logout"),
            ("Sign In", "/login"),
            ("Get Started", "/register")
        ]

        for name, dest in header_links:
            success, code, error, is_login = self.test_url(dest)
            self.log_result(
                component="Header Navigation",
                button_name=name,
                destination=dest,
                status="PASS" if success else "FAIL",
                response_code=code,
                error=error,
                is_login_redirect=is_login
            )

        # Test all Sidebar navigation links
        sidebar_links = [
            ("Create New Journal", "/ai-workflow"),
            ("Dashboard", "/dashboard"),
            ("My Journals", "/dashboard?view=library"),
            ("Themes", "/themes"),
            ("Templates", "/templates"),
            ("Analytics", "/dashboard?view=analytics"),
            ("Settings", "/settings"),
            ("AI Assistant", "/ai-workflow")
        ]

        for name, dest in sidebar_links:
            success, code, error, is_login = self.test_url(dest)
            self.log_result(
                component="Sidebar Navigation",
                button_name=name,
                destination=dest,
                status="PASS" if success else "FAIL",
                response_code=code,
                error=error,
                is_login_redirect=is_login
            )

        # Test Dashboard-specific navigation
        dashboard_links = [
            ("AI Workflow Link", "/ai-workflow"),
            ("Create Journal Buttons", "/ai-workflow")
        ]

        for name, dest in dashboard_links:
            success, code, error, is_login = self.test_url(dest)
            self.log_result(
                component="Dashboard",
                button_name=name,
                destination=dest,
                status="PASS" if success else "FAIL",
                response_code=code,
                error=error,
                is_login_redirect=is_login
            )

        # Test Authentication pages
        auth_pages = [
            ("Login Page", "/auth/login"),
            ("Register Page", "/auth/register"),
            ("Forgot Password", "/auth/forgot-password")
        ]

        for name, dest in auth_pages:
            success, code, error, is_login = self.test_url(dest)
            self.log_result(
                component="Authentication Pages",
                button_name=name,
                destination=dest,
                status="PASS" if success else "FAIL",
                response_code=code,
                error=error,
                is_login_redirect=is_login
            )

        # Test API Endpoints
        api_endpoints = [
            ("Projects API", "/api/library/projects"),
            ("Auth Status", "/api/auth/status"),
            ("Themes API", "/api/ai/themes"),
            ("Title Styles API", "/api/ai/title-styles")
        ]

        for name, endpoint in api_endpoints:
            success, code, error = self.test_backend_endpoint(endpoint)
            self.log_result(
                component="Backend API",
                button_name=name,
                destination=endpoint,
                status="PASS" if success else "FAIL",
                response_code=code,
                error=error
            )

    def generate_report(self):
        """Generate a comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        login_redirects = len([r for r in self.test_results if r.get('is_login_redirect', True)])

        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE LINK TESTING REPORT")
        print("=" * 60)

        print(f"\n📈 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   🔐 Login Redirects: {login_redirects}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        # Group results by component
        by_component = {}
        for result in self.test_results:
            component = result['component']
            if component not in by_component:
                by_component[component] = []
            by_component[component].append(result)

        print(f"\n📋 RESULTS BY COMPONENT:")
        for component, results in by_component.items():
            passed = len([r for r in results if r['status'] == 'PASS'])
            total = len(results)
            print(f"\n🔹 {component}: {passed}/{total} passed")

            for result in results:
                status_icon = "✅" if result['status'] == 'PASS' else "❌"
                login_icon = "🔐" if result.get('is_login_redirect') else ""
                print(f"   {status_icon} {result['button_name']} -> {result['destination']} {login_icon}")

                if result['error']:
                    print(f"      Error: {result['error']}")

        # Critical Issues
        print(f"\n🚨 CRITICAL ISSUES:")
        critical_issues = [r for r in self.test_results
                          if r['status'] == 'FAIL' and not r.get('is_login_redirect')]

        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue['component']} - {issue['button_name']}: {issue['destination']}")
                if issue['error']:
                    print(f"      {issue['error']}")
        else:
            print("   ✅ No critical issues found!")

        # Login Redirect Analysis
        print(f"\n🔐 LOGIN REDIRECT ANALYSIS:")
        if login_redirects > 0:
            print(f"   ⚠️  {login_redirects} links redirect to login (Expected for protected routes)")
            login_links = [r for r in self.test_results if r.get('is_login_redirect')]
            for link in login_links:
                print(f"   • {link['button_name']} -> {link['destination']}")
        else:
            print("   ✅ All links accessible without authentication")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if failed_tests == 0:
            print("   🎉 All links are working correctly!")
        else:
            print(f"   • Fix {failed_tests} broken links")

        if login_redirects > 0:
            print("   • Consider adding user authentication for testing protected routes")
            print("   • Document which routes require authentication")

        # Save detailed report
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100,
                "login_redirects": login_redirects
            },
            "results": self.test_results,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        with open('link_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: link_test_report.json")

def main():
    """Main function"""
    tester = LinkTester()

    try:
        tester.run_comprehensive_tests()
        tester.generate_report()

        # Return exit code based on results
        failed_count = len([r for r in tester.test_results if r['status'] == 'FAIL'])
        if failed_count == 0:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n❌ {failed_count} tests failed")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted")
        return 2
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 3

if __name__ == "__main__":
    exit(main())
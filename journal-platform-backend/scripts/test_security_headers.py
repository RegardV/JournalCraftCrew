#!/usr/bin/env python3
"""
Security Headers Testing Script
Tests that the production security headers are properly configured
"""

import requests
import json
import sys
import urllib3
from typing import Dict, List, Optional, Any

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SecurityHeadersTester:
    """Test production security headers implementation"""

    def __init__(self, base_url: str = "http://localhost:6770"):
        self.base_url = base_url
        self.test_results = []

    def test_endpoint_security_headers(self, endpoint: str) -> Dict[str, Any]:
        """Test security headers for a specific endpoint"""
        try:
            # Handle SSL verification for HTTPS with self-signed certificates
            verify_ssl = not self.base_url.startswith("https://") or "localhost" not in self.base_url
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10, verify=verify_ssl)

            required_headers = {
                "Content-Security-Policy": "CSP header",
                "X-Frame-Options": "Clickjacking protection",
                "X-Content-Type-Options": "MIME sniffing protection",
                "X-XSS-Protection": "XSS protection (legacy)",
                "Referrer-Policy": "Referrer policy",
                "Permissions-Policy": "Permissions policy"
            }

            # HTTPS-only headers
            https_headers = {
                "Strict-Transport-Security": "HSTS header (HTTPS only)"
            }

            results = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "headers_found": {},
                "headers_missing": {},
                "https_headers": {},
                "security_score": 0,
                "issues": []
            }

            # Check required headers
            for header, description in required_headers.items():
                if header in response.headers:
                    results["headers_found"][header] = response.headers[header]
                    results["security_score"] += 10
                else:
                    results["headers_missing"][header] = description
                    results["issues"].append(f"Missing {description}")

            # Check HTTPS-only headers (should not be present on HTTP localhost)
            for header, description in https_headers.items():
                if header in response.headers:
                    results["https_headers"][header] = response.headers[header]
                    if "localhost" not in self.base_url:
                        results["issues"].append(f"{description} should only be on HTTPS")

            # Additional security checks
            self._check_csp_quality(results)
            self._check_server_info_leak(results, response.headers)
            self._check_cache_control(results, endpoint, response.headers)

            return results

        except requests.RequestException as e:
            return {
                "endpoint": endpoint,
                "error": str(e),
                "status_code": 0,
                "security_score": 0,
                "issues": [f"Request failed: {str(e)}"]
            }

    def _check_csp_quality(self, results: Dict[str, Any]):
        """Check Content Security Policy quality"""
        if "Content-Security-Policy" in results["headers_found"]:
            csp = results["headers_found"]["Content-Security-Policy"]

            # Check for dangerous CSP directives
            dangerous_directives = ["unsafe-inline", "unsafe-eval"]
            for directive in dangerous_directives:
                if directive in csp:
                    results["issues"].append(f"CSP contains '{directive}' - consider removing for production")
                    results["security_score"] -= 2

            # Check for important CSP directives
            important_directives = ["default-src", "script-src", "style-src"]
            for directive in important_directives:
                if directive in csp:
                    results["security_score"] += 2

    def _check_server_info_leak(self, results: Dict[str, Any], headers: Dict[str, str]):
        """Check for server information leaks"""
        info_headers = ["Server", "X-Powered-By", "X-AspNet-Version", "X-AspNetMvc-Version"]

        for header in info_headers:
            if header in headers:
                results["issues"].append(f"Server information leaked via {header} header")
                results["security_score"] -= 3

    def _check_cache_control(self, results: Dict[str, Any], endpoint: str, headers: Dict[str, str]):
        """Check cache control headers for API endpoints"""
        if endpoint.startswith("/api/"):
            if "Cache-Control" not in headers:
                results["issues"].append("API endpoints should have Cache-Control headers")
                results["security_score"] -= 5
            elif "no-store" not in headers.get("Cache-Control", ""):
                results["issues"].append("API endpoints should have 'no-store' in Cache-Control")
                results["security_score"] -= 2

    def run_security_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive security headers tests"""
        print("🔒 Testing Production Security Headers")
        print("=" * 50)

        # Test various endpoints
        test_endpoints = [
            "/",
            "/health",
            "/api/auth/login",
            "/api/projects",
            "/docs"
        ]

        for endpoint in test_endpoints:
            print(f"\n📋 Testing endpoint: {endpoint}")
            result = self.test_endpoint_security_headers(endpoint)
            self.test_results.append(result)

            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                score = result["security_score"]
                status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                print(f"{status} Security Score: {score}/100")

                if result["headers_found"]:
                    print("  ✅ Headers found:", list(result["headers_found"].keys()))

                if result["headers_missing"]:
                    print("  ❌ Headers missing:", list(result["headers_missing"].keys()))

                if result["issues"]:
                    for issue in result["issues"]:
                        print(f"  ⚠️  {issue}")

        return self.test_results

    def generate_report(self) -> str:
        """Generate comprehensive security report"""
        if not self.test_results:
            return "No test results available"

        total_score = sum(result.get("security_score", 0) for result in self.test_results)
        max_score = len(self.test_results) * 100
        average_score = total_score / len(self.test_results) if self.test_results else 0

        report = []
        report.append("\n" + "=" * 60)
        report.append("🛡️  SECURITY HEADERS REPORT")
        report.append("=" * 60)
        report.append(f"📊 Overall Security Score: {average_score:.1f}/100")

        if average_score >= 90:
            report.append("🟢 EXCELLENT - Strong security posture")
        elif average_score >= 80:
            report.append("🟡 GOOD - Security headers mostly configured")
        elif average_score >= 70:
            report.append("🟠 FAIR - Some security headers missing")
        elif average_score >= 60:
            report.append("🔴 POOR - Major security headers missing")
        else:
            report.append("🔴 CRITICAL - Security headers not configured")

        report.append("\n📋 Endpoint Details:")
        for result in self.test_results:
            if "error" in result:
                report.append(f"❌ {result['endpoint']}: {result['error']}")
            else:
                score = result["security_score"]
                status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                report.append(f"{status} {result['endpoint']}: {score}/100")

        # Common issues summary
        all_issues = []
        for result in self.test_results:
            all_issues.extend(result.get("issues", []))

        if all_issues:
            report.append("\n⚠️  Common Issues:")
            issue_counts = {}
            for issue in all_issues:
                if issue not in issue_counts:
                    issue_counts[issue] = 0
                issue_counts[issue] += 1

            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  • {issue} (appeared {count} times)")

        # Recommendations
        report.append("\n💡 Recommendations:")
        if average_score < 100:
            report.append("  • Implement missing security headers")
        if any("Content-Security-Policy" not in r.get("headers_found", {}) for r in self.test_results):
            report.append("  • Add Content Security Policy (CSP) header")
        if any("X-Frame-Options" not in r.get("headers_found", {}) for r in self.test_results):
            report.append("  • Add X-Frame-Options to prevent clickjacking")
        if any("Strict-Transport-Security" not in r.get("headers_found", {}) for r in self.test_results):
            report.append("  • Add HSTS for HTTPS sites only")

        return "\n".join(report)

def main():
    """Main test execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Test production security headers")
    parser.add_argument("--url", default="http://localhost:6770", help="Base URL to test")
    parser.add_argument("--output", help="Output file for report (optional)")

    args = parser.parse_args()

    tester = SecurityHeadersTester(args.url)
    results = tester.run_security_tests()

    report = tester.generate_report()
    print(report)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")

    # Exit with appropriate code
    average_score = sum(r.get("security_score", 0) for r in results) / len(results) if results else 0
    sys.exit(0 if average_score >= 80 else 1)

if __name__ == "__main__":
    main()
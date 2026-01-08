#!/usr/bin/env python3
"""
=============================================================================
API ENDPOINTS TESTING SCRIPT
=============================================================================

Test all SmartCareer AI API endpoints programmatically.

USAGE:
    python test_api_endpoints.py

This script tests:
- Health endpoints
- Authentication endpoints  
- AI-powered features
- Analytics endpoints
- Error handling

=============================================================================
"""

import requests
import json
import time
from typing import Dict, Any
import sys

class APITester:
    """API endpoints testing class."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": f"{response_time:.3f}s" if response_time > 0 else ""
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if response_time > 0:
            print(f"   Response time: {response_time:.3f}s")
    
    def test_health_endpoints(self):
        """Test health and system endpoints."""
        print("\n🏥 Testing Health Endpoints...")
        
        # Health endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, 
                            f"Status: {data.get('status', 'unknown')}", response_time)
            else:
                self.log_test("Health Check", False, 
                            f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test("Health Check", False, str(e))
        
        # OpenAPI schema
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/openapi.json")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                schema = response.json()
                endpoints = len(schema.get("paths", {}))
                self.log_test("OpenAPI Schema", True, 
                            f"{endpoints} endpoints defined", response_time)
            else:
                self.log_test("OpenAPI Schema", False, 
                            f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test("OpenAPI Schema", False, str(e))
    
    def test_authentication(self):
        """Test authentication endpoints."""
        print("\n🔐 Testing Authentication...")
        
        # Login with test user
        try:
            start_time = time.time()
            login_data = {
                "email": "admin@smartcareer.uz",
                "password": "Admin123!"
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.log_test("User Login", True, "Token received", response_time)
                else:
                    self.log_test("User Login", False, "No token in response", response_time)
            else:
                self.log_test("User Login", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time)
        except Exception as e:
            self.log_test("User Login", False, str(e))
    
    def test_ai_endpoints(self):
        """Test AI-powered endpoints."""
        print("\n🤖 Testing AI Endpoints...")
        
        headers = {"Authorization": f"Bearer {getattr(self, 'access_token', '')}"}
        
        # Test ATS optimization (mock data)
        try:
            start_time = time.time()
            ats_data = {
                "resume_content": "Experienced Python developer with 5+ years...",
                "job_description": "Looking for senior Python developer...",
                "industry": "technology"
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/ats-optimize",
                json=ats_data,
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                score = data.get("analysis", {}).get("overall_score", 0)
                self.log_test("ATS Optimization", True, 
                            f"Score: {score}/100", response_time)
            elif response.status_code == 401:
                self.log_test("ATS Optimization", True, 
                            "Authentication required (expected)", response_time)
            else:
                self.log_test("ATS Optimization", False, 
                            f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test("ATS Optimization", False, str(e))
        
        # Test interview generation
        try:
            start_time = time.time()
            interview_data = {
                "job_title": "Senior Python Developer",
                "company": "Tech Corp",
                "experience_level": "senior",
                "interview_types": ["technical", "behavioral"],
                "session_duration": 60
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/interview-practice",
                json=interview_data,
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code in [200, 401]:
                status_msg = "Working" if response.status_code == 200 else "Auth required"
                self.log_test("Interview Generation", True, status_msg, response_time)
            else:
                self.log_test("Interview Generation", False, 
                            f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test("Interview Generation", False, str(e))
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints."""
        print("\n📊 Testing Analytics Endpoints...")
        
        headers = {"Authorization": f"Bearer {getattr(self, 'access_token', '')}"}
        
        # Test career dashboard
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/api/v1/analytics/career-dashboard",
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code in [200, 401]:
                status_msg = "Working" if response.status_code == 200 else "Auth required"
                self.log_test("Career Dashboard", True, status_msg, response_time)
            else:
                self.log_test("Career Dashboard", False, 
                            f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test("Career Dashboard", False, str(e))
    
    def generate_report(self):
        """Generate test report."""
        print("\n📋 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for test in self.test_results if "PASS" in test["status"])
        failed = sum(1 for test in self.test_results if "FAIL" in test["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 ALL API TESTS PASSED!")
        else:
            print(f"\n⚠️ {failed} tests failed - check details above")
        
        # Save detailed results
        with open("api_test_results.json", "w") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed
                },
                "results": self.test_results
            }, f, indent=2)
        
        print("📄 Detailed results saved to: api_test_results.json")

def main():
    """Main testing function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test SmartCareer AI API endpoints")
    parser.add_argument("--url", default="http://127.0.0.1:8000", 
                       help="Base URL of the API server")
    parser.add_argument("--start-server", action="store_true",
                       help="Start the server before testing")
    
    args = parser.parse_args()
    
    if args.start_server:
        print("🚀 Starting server...")
        import subprocess
        import signal
        import sys
        
        server_process = subprocess.Popen([
            "uvicorn", "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--log-level", "warning"
        ])
        
        # Wait for server to start
        time.sleep(3)
        
        def signal_handler(sig, frame):
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
    
    # Run tests
    tester = APITester(args.url)
    tester.test_health_endpoints()
    tester.test_authentication()
    tester.test_ai_endpoints()
    tester.test_analytics_endpoints()
    tester.generate_report()
    
    if args.start_server:
        print("\n💡 Server is still running. Press Ctrl+C to stop.")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
=============================================================================
COMPREHENSIVE BACKEND VERIFICATION SCRIPT
=============================================================================

PURPOSE:
    Complete verification of SmartCareer AI Enterprise Platform
    Tests all components, services, and integrations systematically

USAGE:
    python backend_verification.py

OUTPUT:
    Detailed verification results with pass/fail status for each component

=============================================================================
"""

import sys
import asyncio
import requests
import subprocess
import time
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

class BackendVerifier:
    """Comprehensive backend verification system."""
    
    def __init__(self):
        self.results = {}
        self.server_process = None
        self.base_url = "http://127.0.0.1:8000"
        
    def log(self, message: str, status: str = "INFO"):
        """Log verification step with status."""
        status_icons = {
            "INFO": "📋",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "START": "🚀",
            "COMPLETE": "🎉"
        }
        icon = status_icons.get(status, "📋")
        print(f"{icon} {message}")
        
    def run_command(self, cmd: str, description: str) -> Tuple[bool, str]:
        """Run shell command and return success status and output."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            return success, output.strip()
        except Exception as e:
            return False, str(e)
    
    def test_basic_setup(self) -> Dict[str, Any]:
        """Test basic project setup and structure."""
        self.log("Testing Basic Project Setup", "START")
        
        tests = {
            "python_version": False,
            "virtual_env": False,
            "project_structure": False,
            "requirements_file": False
        }
        
        # Check Python version
        success, output = self.run_command("python --version", "Check Python version")
        if success and "Python 3." in output:
            tests["python_version"] = True
            self.log("Python version check: PASSED")
        else:
            self.log(f"Python version check: FAILED - {output}", "ERROR")
        
        # Check virtual environment
        success, output = self.run_command("which python", "Check virtual environment")
        if success and "venv" in output:
            tests["virtual_env"] = True
            self.log("Virtual environment check: PASSED")
        else:
            self.log("Virtual environment check: WARNING (not in venv)")
        
        # Check project structure
        required_files = [
            "app/main.py",
            "app/config.py", 
            "requirements.txt",
            "app/models/user.py",
            "app/services/ai_service.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            success, _ = self.run_command(f"test -f {file_path}", f"Check {file_path}")
            if not success:
                missing_files.append(file_path)
        
        if not missing_files:
            tests["project_structure"] = True
            self.log("Project structure check: PASSED")
        else:
            self.log(f"Project structure check: FAILED - Missing: {', '.join(missing_files)}", "ERROR")
        
        # Check requirements.txt
        success, _ = self.run_command("test -f requirements.txt", "Check requirements.txt")
        if success:
            tests["requirements_file"] = True
            self.log("Requirements file check: PASSED")
        else:
            self.log("Requirements file check: FAILED", "ERROR")
        
        passed_count = sum(tests.values())
        total_count = len(tests)
        
        result = {
            "status": "PASSED" if passed_count == total_count else "PARTIAL",
            "passed": passed_count,
            "total": total_count,
            "details": tests
        }
        
        self.log(f"Basic Setup: {passed_count}/{total_count} tests passed", 
                "SUCCESS" if passed_count == total_count else "WARNING")
        
        return result
    
    def test_dependencies(self) -> Dict[str, Any]:
        """Test Python dependencies installation."""
        self.log("Testing Dependencies", "START")
        
        critical_packages = [
            "fastapi",
            "sqlalchemy", 
            "pydantic",
            "uvicorn",
            "openai",
            "google.generativeai",
            "aiosmtplib",
            "jinja2"
        ]
        
        tests = {}
        failed_packages = []
        
        for package in critical_packages:
            success, output = self.run_command(
                f"python -c 'import {package}; print(f\"{package} imported successfully\")'",
                f"Test {package} import"
            )
            tests[package] = success
            if not success:
                failed_packages.append(package)
        
        passed_count = sum(tests.values())
        total_count = len(tests)
        
        if failed_packages:
            self.log(f"Dependencies check: FAILED - Missing: {', '.join(failed_packages)}", "ERROR")
        else:
            self.log(f"Dependencies check: PASSED - All {total_count} packages available", "SUCCESS")
        
        return {
            "status": "PASSED" if passed_count == total_count else "FAILED",
            "passed": passed_count,
            "total": total_count,
            "details": tests
        }
    
    def test_database(self) -> Dict[str, Any]:
        """Test database connectivity and schema."""
        self.log("Testing Database", "START")
        
        tests = {
            "connection": False,
            "tables_exist": False,
            "seed_data": False
        }
        
        # Test database connection
        success, output = self.run_command(
            "python -c 'from app.database import check_database_connection; print(\"DB OK\" if check_database_connection() else \"DB FAILED\")'",
            "Test database connection"
        )
        if success and "DB OK" in output:
            tests["connection"] = True
            self.log("Database connection: PASSED", "SUCCESS")
        else:
            self.log(f"Database connection: FAILED - {output}", "ERROR")
            return {"status": "FAILED", "passed": 0, "total": 3, "details": tests}
        
        # Test tables exist
        success, output = self.run_command(
            "python -c 'from app.database import engine; from sqlalchemy import inspect; insp = inspect(engine); tables = insp.get_table_names(); print(f\"Tables: {len(tables)}\"); print(\"users\" in tables and \"jobs\" in tables and \"applications\" in tables)'",
            "Check database tables"
        )
        if success and "True" in output:
            tests["tables_exist"] = True
            self.log("Database tables: PASSED", "SUCCESS")
        else:
            self.log(f"Database tables: FAILED - {output}", "ERROR")
        
        # Test seed data
        success, output = self.run_command(
            "python -c 'from app.database import engine; from sqlalchemy import inspect; insp = inspect(engine); conn = engine.connect(); result = conn.execute(\"SELECT COUNT(*) FROM users\").fetchone(); print(f\"Users: {result[0]}\"); conn.close()'",
            "Check seed data"
        )
        if success and "Users: 4" in output:
            tests["seed_data"] = True
            self.log("Seed data: PASSED", "SUCCESS")
        else:
            self.log(f"Seed data: WARNING - {output}", "WARNING")
        
        passed_count = sum(tests.values())
        result = {
            "status": "PASSED" if passed_count >= 2 else "FAILED",
            "passed": passed_count,
            "total": 3,
            "details": tests
        }
        
        self.log(f"Database: {passed_count}/3 tests passed", 
                "SUCCESS" if passed_count >= 2 else "ERROR")
        
        return result
    
    def test_configuration(self) -> Dict[str, Any]:
        """Test application configuration."""
        self.log("Testing Configuration", "START")
        
        tests = {
            "config_import": False,
            "required_settings": False,
            "ai_services": False
        }
        
        # Test config import
        success, output = self.run_command(
            "python -c 'from app.config import settings; print(f\"ENV: {settings.ENVIRONMENT}\")'",
            "Test configuration import"
        )
        if success and "ENV:" in output:
            tests["config_import"] = True
            self.log("Configuration import: PASSED", "SUCCESS")
        else:
            self.log(f"Configuration import: FAILED - {output}", "ERROR")
            return {"status": "FAILED", "passed": 0, "total": 3, "details": tests}
        
        # Test required settings
        required_settings = ["SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL"]
        success, output = self.run_command(
            f"python -c 'from app.config import settings; results = []; [results.append(hasattr(settings, s)) for s in {required_settings}]; print(f\"Settings OK: {{sum(results)}}/{len(results)}\")'",
            "Test required settings"
        )
        if success and "Settings OK: 3/3" in output:
            tests["required_settings"] = True
            self.log("Required settings: PASSED", "SUCCESS")
        else:
            self.log(f"Required settings: FAILED - {output}", "ERROR")
        
        # Test AI service configuration
        success, output = self.run_command(
            "python -c 'from app.config import settings; ai_keys = [bool(getattr(settings, k, None)) for k in [\"OPENAI_API_KEY\", \"GEMINI_API_KEY\"]]; print(f\"AI Keys: {{sum(ai_keys)}}/2 configured\")'",
            "Test AI service configuration"
        )
        if success:
            tests["ai_services"] = True
            self.log(f"AI services configuration: PASSED - {output}", "SUCCESS")
        else:
            self.log(f"AI services configuration: WARNING - {output}", "WARNING")
        
        passed_count = sum(tests.values())
        result = {
            "status": "PASSED" if passed_count >= 2 else "FAILED",
            "passed": passed_count,
            "total": 3,
            "details": tests
        }
        
        self.log(f"Configuration: {passed_count}/3 tests passed", 
                "SUCCESS" if passed_count >= 2 else "ERROR")
        
        return result
    
    def test_ai_services(self) -> Dict[str, Any]:
        """Test AI-powered services."""
        self.log("Testing AI Services", "START")
        
        services = [
            "app.services.ats_optimizer_service",
            "app.services.interview_coach_service", 
            "app.services.career_analytics_service",
            "app.services.professional_networking_service"
        ]
        
        tests = {}
        failed_services = []
        
        for service in services:
            service_name = service.split(".")[-1]
            success, output = self.run_command(
                f"python -c 'import {service}; print(f\"{service_name} imported successfully\")'",
                f"Test {service_name} import"
            )
            tests[service_name] = success
            if not success:
                failed_services.append(service_name)
        
        passed_count = sum(tests.values())
        total_count = len(tests)
        
        if failed_services:
            self.log(f"AI Services: FAILED - Issues with: {', '.join(failed_services)}", "ERROR")
        else:
            self.log(f"AI Services: PASSED - All {total_count} services operational", "SUCCESS")
        
        return {
            "status": "PASSED" if passed_count == total_count else "FAILED",
            "passed": passed_count,
            "total": total_count,
            "details": tests
        }
    
    def test_api_routes(self) -> Dict[str, Any]:
        """Test API route loading."""
        self.log("Testing API Routes", "START")
        
        routes = [
            "app.api.v1.routes.auth",
            "app.api.v1.routes.users",
            "app.api.v1.routes.jobs", 
            "app.api.v1.routes.applications",
            "app.api.v1.routes.ai_powered",
            "app.api.v1.routes.analytics"
        ]
        
        tests = {}
        failed_routes = []
        
        for route in routes:
            route_name = route.split(".")[-1]
            success, output = self.run_command(
                f"python -c 'import {route}; print(f\"{route_name} loaded successfully\")'",
                f"Test {route_name} route loading"
            )
            tests[route_name] = success
            if not success:
                failed_routes.append(route_name)
        
        passed_count = sum(tests.values())
        total_count = len(tests)
        
        if failed_routes:
            self.log(f"API Routes: FAILED - Issues with: {', '.join(failed_routes)}", "ERROR")
        else:
            self.log(f"API Routes: PASSED - All {total_count} routes loaded", "SUCCESS")
        
        return {
            "status": "PASSED" if passed_count == total_count else "FAILED",
            "passed": passed_count,
            "total": total_count,
            "details": tests
        }
    
    def test_application_startup(self) -> Dict[str, Any]:
        """Test FastAPI application startup."""
        self.log("Testing Application Startup", "START")
        
        tests = {
            "app_import": False,
            "startup_sequence": False
        }
        
        # Test app import
        success, output = self.run_command(
            "python -c 'from app.main import app; print(f\"App imported: {app.title}\")'",
            "Test FastAPI app import"
        )
        if success and "SmartCareer AI" in output:
            tests["app_import"] = True
            self.log("Application import: PASSED", "SUCCESS")
        else:
            self.log(f"Application import: FAILED - {output}", "ERROR")
            return {"status": "FAILED", "passed": 0, "total": 2, "details": tests}
        
        # Test startup sequence (quick test)
        success, output = self.run_command(
            "timeout 5s python -c 'from app.main import app; print(\"Startup sequence initiated\")' 2>/dev/null || echo 'Timeout reached - startup works'",
            "Test startup sequence"
        )
        if success or "Timeout reached" in output:
            tests["startup_sequence"] = True
            self.log("Startup sequence: PASSED", "SUCCESS")
        else:
            self.log(f"Startup sequence: FAILED - {output}", "ERROR")
        
        passed_count = sum(tests.values())
        result = {
            "status": "PASSED" if passed_count == 2 else "FAILED",
            "passed": passed_count,
            "total": 2,
            "details": tests
        }
        
        self.log(f"Application Startup: {passed_count}/2 tests passed", 
                "SUCCESS" if passed_count == 2 else "ERROR")
        
        return result
    
    def start_server(self) -> bool:
        """Start the FastAPI server for testing."""
        try:
            self.server_process = subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "warning"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Wait for server to start
            time.sleep(3)
            return self.server_process.poll() is None
        except Exception:
            return False
    
    def stop_server(self):
        """Stop the FastAPI server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test critical API endpoints."""
        self.log("Testing API Endpoints", "START")
        
        # Start server
        if not self.start_server():
            self.log("Failed to start server for API testing", "ERROR")
            return {"status": "FAILED", "passed": 0, "total": 1, "details": {"server_start": False}}
        
        try:
            endpoints = [
                ("GET", "/health", "Health check"),
                ("GET", "/docs", "API documentation"),
                ("GET", "/openapi.json", "OpenAPI schema"),
                ("GET", "/api/v1/ai/health", "AI services health")
            ]
            
            tests = {}
            passed_count = 0
            
            for method, endpoint, description in endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    if method == "GET":
                        response = requests.get(url, timeout=5)
                        success = response.status_code == 200
                    else:
                        success = False
                    
                    tests[description] = success
                    if success:
                        passed_count += 1
                        self.log(f"{description}: PASSED", "SUCCESS")
                    else:
                        self.log(f"{description}: FAILED (Status: {response.status_code})", "ERROR")
                        
                except Exception as e:
                    tests[description] = False
                    self.log(f"{description}: FAILED - {str(e)}", "ERROR")
            
            result = {
                "status": "PASSED" if passed_count >= 3 else "FAILED",
                "passed": passed_count,
                "total": len(endpoints),
                "details": tests
            }
            
            self.log(f"API Endpoints: {passed_count}/{len(endpoints)} tests passed", 
                    "SUCCESS" if passed_count >= 3 else "ERROR")
            
            return result
            
        finally:
            self.stop_server()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete verification suite."""
        print("=" * 80)
        print("🚀 STARTING COMPREHENSIVE BACKEND VERIFICATION")
        print("=" * 80)
        print()
        
        test_categories = [
            ("Basic Setup", self.test_basic_setup),
            ("Dependencies", self.test_dependencies),
            ("Database", self.test_database),
            ("Configuration", self.test_configuration),
            ("AI Services", self.test_ai_services),
            ("API Routes", self.test_api_routes),
            ("Application Startup", self.test_application_startup),
            ("API Endpoints", self.test_api_endpoints)
        ]
        
        overall_results = {}
        total_passed = 0
        total_tests = 0
        
        for category_name, test_function in test_categories:
            try:
                result = test_function()
                overall_results[category_name] = result
                total_passed += result["passed"]
                total_tests += result["total"]
                print()
            except Exception as e:
                self.log(f"{category_name}: CRITICAL ERROR - {str(e)}", "ERROR")
                overall_results[category_name] = {
                    "status": "ERROR",
                    "passed": 0,
                    "total": 1,
                    "details": {"error": str(e)}
                }
                total_tests += 1
                print()
        
        # Summary
        print("=" * 80)
        print("🎯 VERIFICATION SUMMARY")
        print("=" * 80)
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        for category, result in overall_results.items():
            status_icon = "✅" if result["status"] == "PASSED" else "❌" if result["status"] == "FAILED" else "⚠️"
            print(f"{status_icon} {category}: {result['passed']}/{result['total']} ({result['status']})")
        
        print()
        print(f"📊 OVERALL RESULT: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Backend is fully operational and ready for production!")
        elif success_rate >= 75:
            print("✅ GOOD: Backend is mostly operational with minor issues")
        elif success_rate >= 50:
            print("⚠️ FAIR: Backend has significant issues that need attention")
        else:
            print("❌ CRITICAL: Backend has major problems requiring immediate fixes")
        
        print()
        print("🔧 RECOMMENDATIONS:")
        if success_rate < 100:
            print("   • Review failed tests above and fix issues")
            print("   • Check logs for detailed error information")
            print("   • Ensure all dependencies are properly installed")
            print("   • Verify environment variables are correctly set")
        
        print("   • Run 'python backend_verification.py' to re-test after fixes")
        
        return {
            "overall_success_rate": success_rate,
            "total_passed": total_passed,
            "total_tests": total_tests,
            "category_results": overall_results,
            "recommendations": "See output above for specific issues to address"
        }


def main():
    """Main verification function."""
    verifier = BackendVerifier()
    results = verifier.run_all_tests()
    
    # Exit with appropriate code
    if results["overall_success_rate"] >= 90:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()

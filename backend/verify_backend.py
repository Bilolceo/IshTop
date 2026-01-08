#!/usr/bin/env python3
"""
=============================================================================
SMARTCAREER AI BACKEND VERIFICATION SCRIPT
=============================================================================

Comprehensive verification of all backend components and services.

USAGE:
    python verify_backend.py

This script performs:
- Dependency validation
- Database connectivity checks
- AI service verification
- API endpoint testing
- Authentication validation
- Performance benchmarking
- Deployment readiness assessment

=============================================================================
AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class BackendVerifier:
    """Comprehensive backend verification system."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": {},
            "summary": {},
            "recommendations": []
        }
        
    async def run_full_verification(self) -> Dict[str, Any]:
        """Run complete backend verification suite."""
        print("🚀 STARTING COMPREHENSIVE BACKEND VERIFICATION")
        print("=" * 60)
        
        # Core system tests
        await self.test_dependencies()
        await self.test_database()
        await self.test_configuration()
        
        # AI services tests
        await self.test_ai_services()
        
        # API tests
        await self.test_api_endpoints()
        
        # Business logic tests
        await self.test_business_logic()
        
        # Performance tests
        await self.test_performance()
        
        # Deployment readiness
        await self.test_deployment_readiness()
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    async def test_dependencies(self):
        """Test Python dependencies."""
        print("\n📦 Testing Dependencies...")
        
        tests = {
            "fastapi": "FastAPI web framework",
            "sqlalchemy": "Database ORM",
            "pydantic": "Data validation",
            "uvicorn": "ASGI server",
            "openai": "OpenAI API client",
            "google.generativeai": "Google Gemini API",
            "redis": "Redis client",
            "alembic": "Database migrations",
            "bcrypt": "Password hashing",
            "python-jose": "JWT tokens",
            "aiosmtplib": "Email sending",
            "jinja2": "Email templates"
        }
        
        passed = 0
        failed = 0
        
        for module, description in tests.items():
            try:
                __import__(module)
                print(f"  ✅ {module}: {description}")
                passed += 1
            except ImportError as e:
                print(f"  ❌ {module}: Missing - {description}")
                self.results["recommendations"].append(f"Install missing dependency: pip install {module}")
                failed += 1
        
        self.results["tests"]["dependencies"] = {
            "passed": passed,
            "failed": failed,
            "total": len(tests),
            "status": "PASS" if failed == 0 else "FAIL"
        }
    
    async def test_database(self):
        """Test database connectivity and schema."""
        print("\n🗄️ Testing Database...")
        
        try:
            from app.config import settings
            from app.database import check_database_connection, engine
            from sqlalchemy import inspect
            from app.models.base import Base
            
            # Test connection
            connection_ok = check_database_connection()
            if not connection_ok:
                raise Exception("Database connection failed")
            
            print("  ✅ Database connection: OK")
            
            # Test schema
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            expected_tables = ["users", "jobs", "resumes", "applications", "payments"]
            
            missing_tables = [t for t in expected_tables if t not in tables]
            if missing_tables:
                print(f"  ⚠️ Missing tables: {missing_tables}")
                self.results["recommendations"].append(f"Run database migrations to create missing tables: {missing_tables}")
            
            print(f"  ✅ Database schema: {len(tables)} tables found")
            
            self.results["tests"]["database"] = {
                "connection": "PASS",
                "tables_found": len(tables),
                "expected_tables": expected_tables,
                "missing_tables": missing_tables,
                "status": "PASS" if not missing_tables else "WARN"
            }
            
        except Exception as e:
            print(f"  ❌ Database test failed: {e}")
            self.results["tests"]["database"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_configuration(self):
        """Test application configuration."""
        print("\n⚙️ Testing Configuration...")
        
        try:
            from app.config import settings
            
            required_configs = {
                "SECRET_KEY": "Application security key",
                "JWT_SECRET_KEY": "JWT token signing key", 
                "DATABASE_URL": "Database connection URL",
                "DEBUG": "Debug mode setting"
            }
            
            optional_configs = {
                "OPENAI_API_KEY": "OpenAI API access",
                "GEMINI_API_KEY": "Google Gemini API access",
                "REDIS_URL": "Redis cache URL",
                "SMTP_USER": "Email configuration"
            }
            
            # Check required configs
            missing_required = []
            for config, description in required_configs.items():
                value = getattr(settings, config, None)
                if value:
                    print(f"  ✅ {config}: Set - {description}")
                else:
                    print(f"  ❌ {config}: Missing - {description}")
                    missing_required.append(config)
            
            # Check optional configs
            for config, description in optional_configs.items():
                value = getattr(settings, config, None)
                if value:
                    print(f"  ✅ {config}: Set - {description}")
                else:
                    print(f"  ⚠️ {config}: Not set - {description}")
            
            status = "PASS" if not missing_required else "FAIL"
            
            self.results["tests"]["configuration"] = {
                "required_configs": len(required_configs) - len(missing_required),
                "missing_required": missing_required,
                "optional_configs_checked": len(optional_configs),
                "status": status
            }
            
            if missing_required:
                self.results["recommendations"].extend([
                    f"Set missing required configuration: {config}" 
                    for config in missing_required
                ])
            
        except Exception as e:
            print(f"  ❌ Configuration test failed: {e}")
            self.results["tests"]["configuration"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_ai_services(self):
        """Test AI services functionality."""
        print("\n🤖 Testing AI Services...")
        
        ai_services = [
            ("ATS Optimizer", "app.services.ats_optimizer_service", "ats_optimizer"),
            ("Interview Coach", "app.services.interview_coach_service", "interview_coach"),
            ("Career Analytics", "app.services.career_analytics_service", "career_analytics"),
            ("Professional Networking", "app.services.professional_networking_service", "professional_networking")
        ]
        
        passed = 0
        failed = 0
        
        for name, module, instance in ai_services:
            try:
                module_obj = __import__(module, fromlist=[instance])
                service = getattr(module_obj, instance)
                print(f"  ✅ {name}: Service loaded and operational")
                passed += 1
            except Exception as e:
                print(f"  ❌ {name}: Service failed - {e}")
                failed += 1
        
        self.results["tests"]["ai_services"] = {
            "passed": passed,
            "failed": failed,
            "total": len(ai_services),
            "status": "PASS" if failed == 0 else "FAIL"
        }
    
    async def test_api_endpoints(self):
        """Test API endpoints functionality."""
        print("\n🔗 Testing API Endpoints...")
        
        try:
            from app.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            if response.status_code == 200:
                print("  ✅ Health endpoint: Working")
                health_status = "PASS"
            else:
                print(f"  ❌ Health endpoint: Failed ({response.status_code})")
                health_status = "FAIL"
            
            # Test API docs
            response = client.get("/docs")
            if response.status_code == 200:
                print("  ✅ API documentation: Available")
                docs_status = "PASS"
            else:
                print(f"  ❌ API documentation: Failed ({response.status_code})")
                docs_status = "FAIL"
            
            # Test OpenAPI schema
            response = client.get("/openapi.json")
            if response.status_code == 200:
                schema = response.json()
                endpoints = len(schema.get("paths", {}))
                print(f"  ✅ OpenAPI schema: {endpoints} endpoints defined")
                schema_status = "PASS"
            else:
                print(f"  ❌ OpenAPI schema: Failed ({response.status_code})")
                schema_status = "FAIL"
                endpoints = 0
            
            self.results["tests"]["api_endpoints"] = {
                "health_endpoint": health_status,
                "api_docs": docs_status,
                "openapi_schema": schema_status,
                "endpoints_count": endpoints,
                "status": "PASS" if all(s == "PASS" for s in [health_status, docs_status, schema_status]) else "FAIL"
            }
            
        except Exception as e:
            print(f"  ❌ API endpoint test failed: {e}")
            self.results["tests"]["api_endpoints"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_business_logic(self):
        """Test core business logic."""
        print("\n💼 Testing Business Logic...")
        
        try:
            # Test user authentication
            from app.core.security import create_access_token, verify_token
            from app.models.user import UserRole
            
            # Create test token
            test_payload = {"sub": "test_user", "role": UserRole.STUDENT.value}
            token = create_access_token(test_payload)
            
            # Verify token
            decoded = verify_token(token)
            if decoded.sub == "test_user":
                print("  ✅ Authentication: JWT tokens working")
                auth_status = "PASS"
            else:
                print("  ❌ Authentication: JWT verification failed")
                auth_status = "FAIL"
            
            # Test password hashing
            from app.core.security import get_password_hash, verify_password
            
            test_password = "TestPassword123!"
            hashed = get_password_hash(test_password)
            verified = verify_password(test_password, hashed)
            
            if verified:
                print("  ✅ Password security: Hashing and verification working")
                password_status = "PASS"
            else:
                print("  ❌ Password security: Verification failed")
                password_status = "FAIL"
            
            self.results["tests"]["business_logic"] = {
                "authentication": auth_status,
                "password_security": password_status,
                "status": "PASS" if auth_status == "PASS" and password_status == "PASS" else "FAIL"
            }
            
        except Exception as e:
            print(f"  ❌ Business logic test failed: {e}")
            self.results["tests"]["business_logic"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_performance(self):
        """Test system performance."""
        print("\n⚡ Testing Performance...")
        
        try:
            from app.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test response times
            import time
            
            # Health endpoint performance
            start_time = time.time()
            response = client.get("/health")
            health_time = time.time() - start_time
            
            if response.status_code == 200 and health_time < 1.0:
                print(f"  ✅ Health endpoint performance: {health_time:.3f}s")
                perf_status = "PASS"
            else:
                print(f"  ⚠️ Health endpoint performance: {health_time:.3f}s (slow)")
                perf_status = "WARN"
            
            # Memory usage check
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 200:  # Less than 200MB
                print(f"  ✅ Memory usage: {memory_mb:.1f}MB")
                memory_status = "PASS"
            else:
                print(f"  ⚠️ Memory usage: {memory_mb:.1f}MB (high)")
                memory_status = "WARN"
            
            self.results["tests"]["performance"] = {
                "health_response_time": round(health_time, 3),
                "memory_usage_mb": round(memory_mb, 1),
                "performance_status": perf_status,
                "memory_status": memory_status,
                "status": "PASS" if perf_status == "PASS" and memory_status == "PASS" else "WARN"
            }
            
        except Exception as e:
            print(f"  ❌ Performance test failed: {e}")
            self.results["tests"]["performance"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_deployment_readiness(self):
        """Test deployment readiness."""
        print("\n🚀 Testing Deployment Readiness...")
        
        deployment_checks = {
            "requirements.txt": "Dependencies file exists",
            "Dockerfile": "Docker containerization ready",
            "render-build.sh": "Render deployment script",
            ".env.production": "Production environment template",
            ".gitignore": "Security exclusions configured",
            "README.md": "Documentation complete",
            "pyproject.toml": "Project configuration",
            "pytest.ini": "Testing configuration"
        }
        
        passed = 0
        failed = 0
        
        for file_path, description in deployment_checks.items():
            if os.path.exists(file_path):
                print(f"  ✅ {file_path}: {description}")
                passed += 1
            else:
                print(f"  ❌ {file_path}: Missing - {description}")
                failed += 1
        
        # Check if virtual environment exists
        venv_exists = os.path.exists("venv") or os.path.exists("venv/bin/activate")
        if venv_exists:
            print("  ✅ Virtual environment: Configured")
            passed += 1
        else:
            print("  ⚠️ Virtual environment: Not found (create with: python -m venv venv)")
            failed += 1
        
        self.results["tests"]["deployment_readiness"] = {
            "passed": passed,
            "failed": failed,
            "total": len(deployment_checks) + 1,
            "status": "PASS" if failed == 0 else "WARN"
        }
    
    def generate_summary(self):
        """Generate test summary and recommendations."""
        print("\n📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"].values() 
                          if test.get("status") == "PASS")
        failed_tests = sum(1 for test in self.results["tests"].values() 
                          if test.get("status") == "FAIL")
        warn_tests = sum(1 for test in self.results["tests"].values() 
                        if test.get("status") == "WARN")
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warn_tests}")
        
        # Overall status
        if failed_tests == 0 and warn_tests == 0:
            overall_status = "🎉 ALL TESTS PASSED"
            color = "GREEN"
        elif failed_tests == 0:
            overall_status = "⚠️ READY WITH WARNINGS"
            color = "YELLOW"
        else:
            overall_status = "❌ ISSUES FOUND"
            color = "RED"
        
        print(f"\n🏆 OVERALL STATUS: {overall_status}")
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warn_tests,
            "overall_status": overall_status,
            "recommendations": self.results["recommendations"]
        }
        
        if self.results["recommendations"]:
            print("
💡 RECOMMENDATIONS:"            for rec in self.results["recommendations"]:
                print(f"   • {rec}")
        
        print("
📄 Detailed results saved to: verification_results.json"        )
        
        # Save detailed results
        with open("verification_results.json", "w") as f:
            json.dump(self.results, f, indent=2)


async def main():
    """Main verification function."""
    verifier = BackendVerifier()
    results = await verifier.run_full_verification()
    
    return results


if __name__ == "__main__":
    # Run verification
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    elif results["summary"]["warnings"] > 0:
        sys.exit(2)  # Warnings but no failures
    else:
        sys.exit(0)  # All passed


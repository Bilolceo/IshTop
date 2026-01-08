#!/usr/bin/env python3
"""
=============================================================================
QUICK BACKEND HEALTH CHECK
=============================================================================

Fast verification of essential backend components.

USAGE:
    python check_backend.py

This script performs basic checks:
- Application startup
- Database connection
- AI services loading
- API endpoints accessibility

=============================================================================
"""

import sys
import json
from datetime import datetime, timezone

def check_backend():
    """Quick backend health check."""
    print("🔍 SmartCareer AI Backend Health Check")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {},
        "status": "unknown"
    }
    
    # 1. Check Python environment
    print("🐍 Checking Python environment...")
    try:
        import sys
        print(f"   ✅ Python {sys.version.split()[0]}")
        results["checks"]["python"] = "PASS"
    except Exception as e:
        print(f"   ❌ Python check failed: {e}")
        results["checks"]["python"] = "FAIL"
        return results
    
    # 2. Check core imports
    print("📦 Checking core dependencies...")
    core_deps = ["fastapi", "sqlalchemy", "pydantic", "uvicorn"]
    for dep in core_deps:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
            results["checks"][f"dep_{dep}"] = "PASS"
        except ImportError:
            print(f"   ❌ {dep} - MISSING")
            results["checks"][f"dep_{dep}"] = "FAIL"
    
    # 3. Check configuration
    print("⚙️ Checking configuration...")
    try:
        from app.config import settings
        required = ["SECRET_KEY", "DATABASE_URL"]
        for setting in required:
            if hasattr(settings, setting) and getattr(settings, setting):
                print(f"   ✅ {setting}")
                results["checks"][f"config_{setting}"] = "PASS"
            else:
                print(f"   ❌ {setting} - MISSING")
                results["checks"][f"config_{setting}"] = "FAIL"
    except Exception as e:
        print(f"   ❌ Configuration check failed: {e}")
        results["checks"]["configuration"] = "FAIL"
    
    # 4. Check database
    print("🗄️ Checking database connection...")
    try:
        from app.database import check_database_connection
        if check_database_connection():
            print("   ✅ Database connection OK")
            results["checks"]["database"] = "PASS"
        else:
            print("   ❌ Database connection FAILED")
            results["checks"]["database"] = "FAIL"
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        results["checks"]["database"] = "FAIL"
    
    # 5. Check AI services
    print("🤖 Checking AI services...")
    ai_services = ["ats_optimizer", "interview_coach", "career_analytics", "professional_networking"]
    for service in ai_services:
        try:
            module = f"app.services.{service}_service"
            service_module = __import__(module, fromlist=[service])
            service_instance = getattr(service_module, service)
            print(f"   ✅ {service.replace('_', ' ').title()}")
            results["checks"][f"ai_{service}"] = "PASS"
        except Exception as e:
            print(f"   ❌ {service.replace('_', ' ').title()} - FAILED")
            results["checks"][f"ai_{service}"] = "FAIL"
    
    # 6. Check API application
    print("🔗 Checking API application...")
    try:
        from app.main import app
        print("   ✅ FastAPI application loads")
        results["checks"]["fastapi_app"] = "PASS"
    except Exception as e:
        print(f"   ❌ FastAPI app failed: {e}")
        results["checks"]["fastapi_app"] = "FAIL"
    
    # Calculate overall status
    failed_checks = [k for k, v in results["checks"].items() if v == "FAIL"]
    
    if not failed_checks:
        results["status"] = "HEALTHY"
        print("\n🎉 BACKEND IS HEALTHY!")
        print("   All core components are working correctly.")
    else:
        results["status"] = "ISSUES_FOUND"
        print(f"\n⚠️ ISSUES FOUND: {len(failed_checks)} failed checks")
        print("   Check the details above and fix the issues.")
    
    # Save results
    with open("backend_health.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: backend_health.json")
    
    return results

if __name__ == "__main__":
    results = check_backend()
    # Exit with status code based on results
    if results["status"] == "HEALTHY":
        sys.exit(0)
    else:
        sys.exit(1)


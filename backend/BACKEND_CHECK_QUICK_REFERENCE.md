
================================================================================
🔍 QUICK BACKEND CHECK COMMANDS - SmartCareer AI
================================================================================

Run these commands in your backend directory to verify everything is working:

--------------------------------------------------------------------------------
🎯 ONE-LINE VERIFICATION (RECOMMENDED)
--------------------------------------------------------------------------------
cd /home/abv/Project/smartcarier/backend && source venv/bin/activate && python backend_verification.py

--------------------------------------------------------------------------------
🚀 QUICK HEALTH CHECKS
--------------------------------------------------------------------------------
# Basic imports
python -c 'from app.main import app; print("✅ App OK")'

# Database connection  
python -c 'from app.database import check_database_connection; print("✅ DB OK" if check_database_connection() else "❌ DB FAILED")'

# AI services
python -c 'from app.services.ats_optimizer_service import ats_optimizer; from app.services.interview_coach_service import interview_coach; print("✅ AI Services OK")'

# Start and test server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level warning &
sleep 3
curl -s http://127.0.0.1:8000/health | python -c 'import sys, json; print("✅ Health:", json.load(sys.stdin)["status"])'
pkill -f uvicorn

--------------------------------------------------------------------------------
📊 COMPONENT STATUS CHECKS
--------------------------------------------------------------------------------
# Dependencies
pip check && echo "✅ Dependencies OK"

# Configuration
python -c 'from app.config import settings; print(f"✅ Config: {settings.ENVIRONMENT}")'

# API routes
python -c 'from app.api.v1.routes import ai_powered, analytics; print("✅ API Routes OK")'

--------------------------------------------------------------------------------
🎉 SUCCESS INDICATORS
--------------------------------------------------------------------------------
✅ All commands complete without errors
✅ Database connection works
✅ AI services import successfully  
✅ Server starts and responds to health checks
✅ No 'ModuleNotFoundError' or 'ImportError' messages
✅ Verification script shows 90%+ success rate

--------------------------------------------------------------------------------
🚨 IF YOU SEE ERRORS
--------------------------------------------------------------------------------
❌ ModuleNotFoundError → pip install -r requirements.txt
❌ Database errors → Check DATABASE_URL in .env
❌ AI service errors → Check OPENAI_API_KEY and GEMINI_API_KEY
❌ Server errors → Check port 8000 availability
❌ Import errors → source venv/bin/activate

--------------------------------------------------------------------------------
📞 SUPPORT
--------------------------------------------------------------------------------
If issues persist:
1. Run: python backend_verification.py (detailed diagnostics)
2. Check the troubleshooting section in the verification guide
3. Review error messages for specific guidance
4. Ensure all environment variables are set correctly

Your SmartCareer AI Enterprise Platform is designed for reliability! 🚀
================================================================================


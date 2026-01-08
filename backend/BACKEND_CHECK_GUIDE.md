# 🔍 SmartCareer AI Backend Verification Guide

This comprehensive guide shows you how to verify that your SmartCareer AI backend is working correctly.

## 🚀 Quick Health Check

Run the fast health check script:

```bash
cd backend
source venv/bin/activate
python check_backend.py
```

**Expected Output:**
```
🔍 SmartCareer AI Backend Health Check
==================================================
🐍 Checking Python environment...
   ✅ Python 3.14.2
📦 Checking core dependencies...
   ✅ fastapi
   ✅ sqlalchemy
   ✅ pydantic
   ✅ uvicorn
⚙️ Checking configuration...
   ✅ SECRET_KEY
   ✅ DATABASE_URL
🗄️ Checking database connection...
   ✅ Database connection OK
🤖 Checking AI services...
   ✅ Ats Optimizer
   ✅ Interview Coach
   ✅ Career Analytics
   ✅ Professional Networking
🔗 Checking API application...
   ✅ FastAPI application loads

🎉 BACKEND IS HEALTHY!
   All core components are working correctly.
```

## 🔬 Comprehensive Verification

Run the full verification suite:

```bash
python verify_backend.py
```

This performs:
- ✅ Dependency validation
- ✅ Database connectivity and schema checks
- ✅ Configuration validation
- ✅ AI service functionality tests
- ✅ API endpoint testing
- ✅ Business logic verification
- ✅ Performance benchmarking
- ✅ Deployment readiness assessment

## 🔗 API Endpoints Testing

### Manual Testing

1. **Start the server:**
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level warning
```

2. **Test health endpoint:**
```bash
curl http://127.0.0.1:8000/health
```

3. **Test API documentation:**
```bash
curl -s http://127.0.0.1:8000/docs | head -20
```

4. **Test authentication:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@smartcareer.uz", "password": "Admin123!"}'
```

### Automated API Testing

Run the comprehensive API test suite:

```bash
python test_api_endpoints.py --start-server
```

This will:
- Start the server automatically
- Test all health endpoints
- Test authentication flow
- Test AI-powered features
- Test analytics endpoints
- Generate detailed test report

## 🧪 Unit Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/ -v          # Unit tests only
pytest tests/integration/ -v   # Integration tests only
pytest tests/ -k "test_auth"   # Specific test pattern
```

## 📊 Monitoring & Logs

### Application Logs

```bash
# View live logs
uvicorn app.main:app --reload --log-level info

# View logs with timestamps
tail -f logs/app.log
```

### Health Monitoring

```bash
# Continuous health check
while true; do
  curl -s http://127.0.0.1:8000/health | jq .status
  sleep 30
done
```

### Performance Monitoring

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://127.0.0.1:8000/health
```

## 🗄️ Database Verification

### Connection Test

```bash
python -c "
from app.database import check_database_connection
from app.config import settings
print('Database URL:', settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0], '***'))
print('Connection:', 'OK' if check_database_connection() else 'FAILED')
"
```

### Schema Validation

```bash
python -c "
from app.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Database tables:', tables)
for table in ['users', 'jobs', 'resumes', 'applications']:
    if table in tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f'{table}: {len(columns)} columns')
    else:
        print(f'{table}: MISSING')
"
```

## 🤖 AI Services Testing

### Individual Service Tests

```python
# Test ATS Optimizer
from app.services.ats_optimizer_service import ats_optimizer
result = await ats_optimizer.analyze_resume_for_ats(
    resume_content="Your resume text here",
    job_description="Job description here",
    industry="technology"
)
print("ATS Score:", result.overall_score)

# Test Interview Coach
from app.services.interview_coach_service import interview_coach
session = await interview_coach.generate_interview_session(
    user_id="test_user",
    job_title="Developer",
    company="Tech Corp"
)
print("Questions generated:", len(session.questions))

# Test Career Analytics
from app.services.career_analytics_service import career_analytics
metrics = await career_analytics.calculate_career_metrics(
    user_id="test_user",
    application_history=[]
)
print("Career metrics calculated")
```

## 🚀 Deployment Readiness Check

### Container Testing

```bash
# Build Docker image
docker build -t smartcareer-backend .

# Test container
docker run -p 8000:8000 smartcareer-backend &
sleep 5
curl http://localhost:8000/health
docker stop $(docker ps -q)
```

### Environment Variables

```bash
# Check required environment variables
echo "SECRET_KEY: ${SECRET_KEY:+SET}${SECRET_KEY:-NOT SET}"
echo "DATABASE_URL: ${DATABASE_URL:+SET}${DATABASE_URL:-NOT SET}"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}${OPENAI_API_KEY:-NOT SET}"
```

### Production Configuration

```bash
# Validate production settings
python -c "
from app.config import settings
print('Environment:', settings.ENVIRONMENT)
print('Debug mode:', settings.DEBUG)
print('Database type:', 'PostgreSQL' if 'postgresql' in str(settings.DATABASE_URL) else 'SQLite')
print('AI provider:', 'OpenAI' if settings.OPENAI_API_KEY else 'None')
"
```

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt
```

**2. Database Connection Issues**
```bash
# Check database URL
echo $DATABASE_URL

# Test connection manually
python -c "import sqlalchemy; engine = sqlalchemy.create_engine('$DATABASE_URL'); engine.execute('SELECT 1')"
```

**3. AI Service Failures**
```bash
# Check API keys
echo "OpenAI: ${OPENAI_API_KEY:+SET}${OPENAI_API_KEY:-NOT SET}"
echo "Gemini: ${GEMINI_API_KEY:+SET}${GEMINI_API_KEY:-NOT SET}"

# Test AI services individually
python -c "from app.services.ai_service import AIService; ai = AIService(); print('AI OK')"
```

**4. API Endpoint Issues**
```bash
# Check server is running
curl http://127.0.0.1:8000/health

# Check API documentation
curl http://127.0.0.1:8000/docs

# View server logs
tail -f logs/app.log
```

## 📋 Verification Checklist

- [ ] **Dependencies**: All Python packages installed
- [ ] **Database**: Connection working, tables created
- [ ] **Configuration**: All required settings configured
- [ ] **AI Services**: All 4 services operational
- [ ] **API Endpoints**: Health, auth, and AI endpoints working
- [ ] **Authentication**: JWT tokens working
- [ ] **Business Logic**: Core features functional
- [ ] **Performance**: Response times acceptable
- [ ] **Deployment**: Docker, environment variables ready
- [ ] **Monitoring**: Health checks and logging working

## 🎯 Quick Commands Reference

```bash
# Health check
python check_backend.py

# Full verification
python verify_backend.py

# API testing
python test_api_endpoints.py --start-server

# Run tests
pytest tests/ -v

# Start server
uvicorn app.main:app --reload

# Check database
python -c "from app.database import check_database_connection; print(check_database_connection())"

# View logs
tail -f logs/app.log

# Health monitoring
curl http://127.0.0.1:8000/health
```

## 📞 Support

If you encounter issues:

1. Run the health check: `python check_backend.py`
2. Check the detailed verification: `python verify_backend.py`
3. Review logs and error messages
4. Verify environment variables and dependencies
5. Test individual components manually

The backend is designed to be robust and provide clear error messages for troubleshooting.

---

**✅ Your SmartCareer AI backend is now fully verified and ready for production!**

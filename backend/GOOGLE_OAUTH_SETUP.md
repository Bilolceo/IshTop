# 🔐 Google OAuth Setup - Complete Guide

## ❗ Problem
```
{"detail":"Google OAuth not configured. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env"}
```

## ✅ Solution: Get Google OAuth Credentials

---

## 📋 Table of Contents
1. [Web Console Method (Recommended)](#web-console-method-recommended)
2. [CLI Methods (Advanced)](#cli-methods-advanced)
3. [Environment Configuration](#environment-configuration)
4. [Testing](#testing)
5. [Troubleshooting](#troubleshooting)
6. [Production Deployment](#production-deployment)

---

## 🌐 Web Console Method (Recommended)

### Qadam 1: Google Cloud Console'ga Kirish
1. https://console.cloud.google.com ga boring
2. Google hisobingiz bilan kiring

### Qadam 2: Yangi Project Yaratish (yoki mavjudni tanlash)
1. Yuqoridagi "Select a project" tugmasini bosing
2. "New Project" ni tanlang
3. Project name: `SmartCareer AI` (yoki istalgan nom)
4. "Create" bosing

### Qadam 3: OAuth Consent Screen Sozlash
1. Chap menudan **"APIs & Services"** → **"OAuth consent screen"** ga boring
2. User type: **External** ni tanlang → **Create**
3. App information:
   - **App name**: `SmartCareer AI`
   - **User support email**: O'zingizning emailingiz
   - **Developer contact**: O'zingizning emailingiz
4. **Save and Continue**
5. Scopes: **Save and Continue** (default scopes yetarli)
6. Test users: O'zingizni qo'shing (agar test rejimida bo'lsa)
7. **Save and Continue** → **Back to Dashboard**

### Step 4: Create OAuth 2.0 Client ID
1. **"APIs & Services"** → **"Credentials"** ga boring
2. Yuqorida **"+ CREATE CREDENTIALS"** → **"OAuth client ID"** ni tanlang
3. Application type: **Web application**
4. Name: `SmartCareer AI Web`
5. **Authorized JavaScript origins**:
   ```
   http://localhost:3000
   http://localhost:8000
   ```
6. **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/v1/auth/callback/google
   ```
7. **Create** bosing

### Qadam 5: Credentials Nusxalash
Yangi oyna ochiladi:
- **Client ID**: `123456789-abcdefghijklmnop.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnopqrstuvwxyz`

**⚠️ IMPORTANT:** Client Secret faqat bir marta ko'rsatiladi! Nusxalab oling!

### Step 6: Add to Backend .env File
Open `backend/.env` and add the following:

```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google
OAUTH_ENABLED=true
```

### Step 7: Restart Backend
```powershell
# Backend processni to'xtating (Ctrl+C)
# Keyin qayta ishga tushiring:
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 8: Testing
1. Open browser: http://localhost:3000/login
2. Click "Google" button
3. Sign in with your Google account
4. Grant permissions
5. You should be redirected to dashboard! ✅

---

## 🖥️ CLI Methods (Advanced)

### Prerequisites
If you have Google Cloud CLI (`gcloud`) installed:

```bash
# Install gcloud (if not installed)
# Windows: https://cloud.google.com/sdk/docs/install
# Or: winget install Google.CloudSDK

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### REST API Method (Most Reliable)
```bash
# 1. Get access token
ACCESS_TOKEN=$(gcloud auth print-access-token)

# 2. Set your project ID
PROJECT_ID="your-project-id"

# 3. Create OAuth 2.0 Client ID
curl -X POST \
  "https://apigee.googleapis.com/v1/organizations/${PROJECT_ID}/oauth2/clients" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SmartCareer AI Web",
    "redirectUris": [
      "http://localhost:8000/api/v1/auth/callback/google"
    ],
    "grantTypes": ["authorization_code"],
    "scopes": ["openid", "email", "profile"]
  }'
```

**Note:** `gcloud iam oauth-clients` creates IAM OAuth clients, not OAuth 2.0 Client IDs needed for web applications.

---

## 🧪 Testing

## ⚙️ Environment Configuration

After getting your credentials, add them to `backend/.env`:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google
OAUTH_ENABLED=true
```

## 🧪 Testing

1. Restart your backend server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Open browser: http://localhost:3000/login
3. Click "Google" button
4. Sign in with your Google account
5. Grant permissions
6. You should be redirected to dashboard! ✅

## 🚨 Troubleshooting

### "redirect_uri_mismatch"
- Add to **Authorized redirect URIs** in Google Cloud Console:
  ```
  http://localhost:8000/api/v1/auth/callback/google
  ```

### "access_denied"
- Add yourself as a test user in OAuth Consent Screen

### "invalid_client"
- Check Client ID or Client Secret
- Verify `.env` file configuration

### "OAuth not configured" Error
- Ensure all environment variables are set
- Check that `OAUTH_ENABLED=true`
- Restart the backend server

---

## 🚀 Production Deployment

For production deployment:

1. **Add production URLs** in Google Cloud Console:
   ```
   https://api.your-domain.com/api/v1/auth/callback/google
   ```

2. **Update .env** file:
   ```env
   GOOGLE_REDIRECT_URI=https://api.your-domain.com/api/v1/auth/callback/google
   FRONTEND_URL=https://your-domain.com
   OAUTH_ENABLED=true
   ```

3. **Verify HTTPS**: OAuth requires HTTPS in production

4. **Update CORS origins** to include your production domain

---

## 📚 Additional Resources

- **Google Cloud Console**: https://console.cloud.google.com/apis/credentials
- **OAuth 2.0 Guide**: https://developers.google.com/identity/protocols/oauth2
- **SmartCareer AI Docs**: Check main README.md for additional setup guides

---

**Need help?** Check the other setup files or open an issue on GitHub!


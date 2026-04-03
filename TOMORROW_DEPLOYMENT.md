# DEPLOYMENT CHECKLIST - TOMORROW

## 🎯 TOMORROW'S TASKS (Copy-paste ready)

### ✅ PRE-DEPLOYMENT VERIFICATION (5 min)

**Verify app is still running:**
```bash
cd C:\Users\Aryan\ salunkhe\OneDrive\MY_PROJECTS\transit_delay_predictor
flutter run -d chrome
```
Expected: App opens in Chrome, shows "✓ Supabase initialized"

---

## 🔧 PHASE 1: BACKEND DEPLOYMENT TO VERCEL (10 min)

**Step 1: Create Vercel Account**
- Go to https://vercel.com
- Sign up with email or GitHub
- Create account

**Step 2: Connect GitHub Repository**
- In Vercel dashboard: Click "Add New" → "Project"
- Import your GitHub repository
- Select transit_delay_predictor repo

**Step 3: Configure Build Settings**
- Root Directory: `.`
- Build Command: Leave empty
- Output Directory: Leave empty
- Environment Variables: ADD THESE:

```
SUPABASE_URL=https://qctizaedswrcoscaxiwm.supabase.co
SUPABASE_KEY=sb_publishable_FOMkNQrlhQ6XwuIHD35TYQ_vuXJwnaF
```

**Step 4: Deploy**
- Click "Deploy"
- Wait 2-3 minutes
- Note your Vercel domain (e.g., transit-delay-predictor-ax1.vercel.app)

**Step 5: Verify Deployment**
```bash
# Test health endpoint (replace with your Vercel domain)
curl https://transit-delay-predictor-ax1.vercel.app/api/health
```
Expected output: `{"status":"ok"}`

---

## 🔑 PHASE 2: API KEYS CONFIGURATION (5 min)

### GET YOUR API KEYS

**Option A: Use Mock Keys (For Testing Without Real APIs)**
```
GOOGLE_MAPS_API_KEY=test_key_google_maps
HERE_API_KEY=test_key_here
TOMTOM_API_KEY=test_key_tomtom
OPENWEATHER_API_KEY=test_key_openweather
ONESIGNAL_API_KEY=test_key_onesignal
SENTRY_DSN=test_key_sentry
```

**Option B: Get Real Keys (Recommended)**

1. **Google Maps API Key**
   - Go to https://console.cloud.google.com
   - Create new project "Transit-X"
   - Enable "Routes API"
   - Create API key
   - Copy key

2. **HERE Maps API Key**
   - Go to https://developer.here.com
   - Sign up free account
   - Create new project
   - Copy API key

3. **TomTom API Key**
   - Go to https://developer.tomtom.com
   - Sign up free account
   - Create API key
   - Copy key

4. **OpenWeather API Key**
   - Go to https://openweathermap.org/api
   - Sign up free account
   - Go to API keys section
   - Copy key

5. **OneSignal API Key** (Optional, for notifications)
   - Go to https://onesignal.com
   - Sign up free account
   - Create app
   - Copy REST API key

6. **Sentry DSN** (Optional, for error tracking)
   - Go to https://sentry.io
   - Sign up free account
   - Create project for "Python"
   - Copy DSN

### ADD KEYS TO VERCEL

1. In Vercel dashboard → Your Project → Settings → Environment Variables
2. Add each key:
   - `GOOGLE_MAPS_API_KEY=your_actual_key`
   - `HERE_API_KEY=your_actual_key`
   - `TOMTOM_API_KEY=your_actual_key`
   - `OPENWEATHER_API_KEY=your_actual_key`
   - `ONESIGNAL_API_KEY=your_actual_key` (if using)
   - `SENTRY_DSN=your_actual_key` (if using)
3. Click "Save"
4. Redeploy: Click "Redeploy"

---

## 🧪 PHASE 3: INTEGRATION TESTS (10 min)

**Test 1: Health Check**
```bash
curl https://your-vercel-domain.vercel.app/api/health
```
Expected: `{"status":"ok"}`

**Test 2: Get Nearby Stops**
```bash
curl "https://your-vercel-domain.vercel.app/api/stops?latitude=19.0176&longitude=72.8235&radius=5000"
```
Expected: JSON list of nearby stops

**Test 3: Get Verified Delays**
```bash
curl "https://your-vercel-domain.vercel.app/api/verified-delays?latitude=19.0176&longitude=72.8235&radius=5000"
```
Expected: JSON list of verified delays (may be empty if no reports yet)

**Test 4: Make a Prediction**
```bash
curl -X POST https://your-vercel-domain.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "stop_id": "stop-001",
    "latitude": 19.0176,
    "longitude": 72.8235
  }'
```
Expected: Prediction result with confidence score

**Test 5: Check Supabase for Data**
1. Go to Supabase dashboard
2. Click "SQL Editor"
3. Run: `SELECT COUNT(*) FROM user_reports;`
4. Should see any reports you submitted from the app

---

## 🎬 PHASE 4: UPDATE APP WITH BACKEND URL (5 min)

**Important:** If your Vercel domain is different:

1. Open `lib/services/supabase_service.dart`
2. Find the line with API endpoint
3. Replace with your Vercel domain:
```dart
final String backendUrl = 'https://your-vercel-domain.vercel.app/api';
```
4. Save
5. In Flutter: Press `R` (hot reload) in terminal

---

## ✅ FINAL VERIFICATION (5 min)

**Test from Flutter App:**

1. Keep the app running in Chrome
2. Go to Reports screen in the app
3. Submit a test report
4. Check Supabase: should see new row in `user_reports` table
5. Check backend logs in Vercel dashboard

**Expected Results:**
- ✅ Report written to database
- ✅ Backend logs show API call
- ✅ No errors in browser console

---

## 🎉 DEPLOYMENT COMPLETE!

When all tests pass:
- ✅ Backend deployed to Vercel
- ✅ API keys configured
- ✅ All endpoints tested
- ✅ Database connection verified
- ✅ App communicating with backend

**Next Steps (Optional - not required):**
- Train ML model (optional - fallback works without it)
- Set up OneSignal for push notifications
- Build for iOS/Android stores

---

## 🆘 TROUBLESHOOTING

**Issue: "Connection refused" when testing API**
- Solution: Check if Vercel deployment completed (wait 2-3 min)
- Check if environment variables saved correctly
- Check if you're using correct Vercel domain

**Issue: "502 Bad Gateway" from Vercel**
- Solution: Check Vercel logs (Deployments → View logs)
- Usually means Python error - check requirements.txt installed all deps

**Issue: "API key not found" error**
- Solution: Make sure environment variables added to Vercel
- Must redeploy after adding variables

**Issue: Database connection fails**
- Solution: Check Supabase credentials in code are correct
- Verify Supabase project is active

---

## 📋 COPY-PASTE QUICK REFERENCE

**Your Supabase Credentials (Already in code):**
```
URL: https://qctizaedswrcoscaxiwm.supabase.co
Anon Key: sb_publishable_FOMkNQrlhQ6XwuIHD35TYQ_vuXJwnaF
```

**Vercel Deploy Command (if using CLI):**
```bash
npm i -g vercel
vercel login
vercel deploy --prod
```

**Database Test Query (in Supabase SQL Editor):**
```sql
SELECT * FROM user_reports ORDER BY created_at DESC LIMIT 10;
```

**Flutter Hot Reload:**
```
Press 'R' in terminal where Flutter is running
```

---

## ⏱️ ESTIMATED TIMELINE

| Task | Duration | Status |
|------|----------|--------|
| Vercel setup | 5 min | 🛑 TODO |
| Add API keys | 5 min | 🛑 TODO |
| Test endpoints | 10 min | 🛑 TODO |
| Update app config | 5 min | 🛑 TODO |
| Final verification | 5 min | 🛑 TODO |
| **TOTAL** | **30 min** | 🛑 NOT STARTED |

---

**Good luck tomorrow! You've built an amazing app!** 🚀

*Last checked: April 2, 2026*

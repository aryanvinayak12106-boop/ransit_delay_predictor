# 🚀 Quick Start Guide - 5 Minutes to Running

This guide gets your app running in 5 minutes using existing sample data.

---

## Step 1: Prerequisites (1 minute)

You need:
- 🔧 Flutter 3.0.0+ installed → [flutter.dev](https://flutter.dev)
- 🖥️ Android Studio / Xcode for emulator
- 📱 Android emulator OR iOS simulator (or physical device)
- 🌐 Supabase account (free at [supabase.com](https://supabase.com))

Check your setup:
```bash
flutter --version
dart --version
```

---

## Step 2: Get Your Supabase Keys (2 minutes)

1. Go to [supabase.com](https://supabase.com) → Sign in
2. Create new project (or use existing):
   - Project name: `transit_delay_predictor`
   - Database password: Save it!
   - Region: Closest to you
3. Wait for database setup (~2 minutes)
4. Go to **Settings** → **API** on left sidebar
5. Copy:
   - `Project URL` (ends with `.supabase.co`)
   - `anon public key` (starts with `eyJ`)
6. Save these in a notepad

---

## Step 3: Update Configuration (1 minute)

Open `lib/config/constants.dart`:

```dart
// Around line 15-20, replace with your keys:
const String supabaseUrl = 'YOUR_PROJECT_URL';
const String supabaseAnonKey = 'YOUR_ANON_KEY';
const String openWeatherMapApiKey = 'sk-test-123456'; // Keep this for now
const String googleMapsApiKey = 'AIzaSy...'; // Keep this for now
```

Save the file.

---

## Step 4: Get Dependencies (1 minute)

Open terminal in project root:

```bash
cd transit_delay_predictor
flutter clean
flutter pub get
```

Wait for packages to download (~1 minute).

---

## Step 5: Run the App! (1 minute)

```bash
flutter run
```

When prompted, select:
- Android emulator, or
- iOS simulator, or
- Your physical device (must have USB debugging enabled)

Wait for app to build and install...

---

## ✅ What You'll See

When the app launches on your device:

1. **Permission Dialog** → Tap "Allow" (location needed)
2. **Home Screen** with:
   - Google Map showing 5 sample transit stops (blue markers)
   - Bottom carousel listing nearby stops
   - Location indicator at center
3. **Try These**:
   - 🗺️ **Tap any stop marker** → Delay breakdown appears at bottom
   - 📍 **Tap a stop in carousel** → Details screen opens
   - 💾 **Press "Save Route"** → Saves this stop as favorite
   - 📊 **Press "Report Delay"** → Popup to report actual delay (optional)
   - ⭐ **Go to Dashboard** → See your saved routes

---

## 🐛 Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| **"API key invalid"** | Check you copied the full keys correctly (no spaces) |
| **Map shows blank (no stops)** | Check internet connection, wait 5 seconds |
| **Location not working** | Tap Settings → check location permission is "Allow" |
| **App crashes on startup** | Run `flutter clean` then `flutter pub get` |
| **"Could not find Supabase"** | Restart emulator/device and try again |

---

## 📚 Next: Configuration (When Ready)

Once the app works, follow **SETUP_GUIDE.md** for:
- ✅ Database setup (already done if app runs!)
- 🗺️ Google Maps API key (required for real map)
- 🌤️ OpenWeatherMap API key (required for real predictions)
- 🔔 Notification setup (optional)
- 🚀 Building for App Store/Play Store

---

## File Locations You'll Need

| What | Where |
|------|-------|
| Keys to update | `lib/config/constants.dart` (lines 15-20) |
| Full setup guide | `SETUP_GUIDE.md` |
| Troubleshooting | `IMPLEMENTATION_NOTES.md` → Troubleshooting |
| API docs | `API_REFERENCE.md` |
| All files list | `FILE_INVENTORY.md` |

---

## 🎯 What Works Out of the Box

- ✅ **Map** shows sample stops (5 pre-loaded)
- ✅ **Locations** work with emulator/real device
- ✅ **Delay predictions** calculated (using mock weather)
- ✅ **Delay breakdown** shows factors
- ✅ **Save routes** to dashboard
- ✅ **Report delays** (saved mock)
- ✅ **Notifications** trigger on app

## ⚠️ What Needs Real API Keys

- 🗺️ **Real maps** (currently displays sample only)
- 🌤️ **Real weather forecasts**
- 📍 **Real events** from database
- 📧 **Push notifications** (needs Firebase)

These are in **SETUP_GUIDE.md** Step 2-3 when ready.

---

## Summary

| Step | Time | What Happens |
|------|------|--------------|
| 1. Prerequisites | 1m | Verify Flutter is installed |
| 2. Supabase keys | 2m | Get your API credentials |
| 3. Update config | 1m | Add keys to constants.dart |
| 4. Get dependencies | 1m | Download packages |
| 5. Run app | 1m | Launch on emulator/device |
| **Total** | **~6 minutes** | **Working app!** |

---

**Questions?** Check the docs:
- Architecture → `IMPLEMENTATION_NOTES.md`
- Full setup →  `SETUP_GUIDE.md`
- APIs → `API_REFERENCE.md`
- All files → `FILE_INVENTORY.md`

🎉 **You're almost there! Run `flutter run` now!**

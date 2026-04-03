# ⚡ 30-Minute Quick Start

**Pre-requirement**: Flutter SDK (download first: https://flutter.dev)  
**Time**: ~30 minutes total

## Summary

| Step | Task | Time |
|------|------|------|
| 1 | Install Flutter SDK | 10 min |
| 2 | Add Flutter to PATH | 2 min |
| 3 | Run setup.ps1 script | 5 min |
| 4 | Start Android Emulator | 3 min |
| 5 | flutter run | 5 min |
| **Total** | **Ready to use app** | **~30 min** |

---

## Step 1: Install Flutter (10 min)

**Download**: Go to https://flutter.dev/docs/get-started/install/windows
- Click "Windows" tab
- Download latest stable version

**Extract**:
- Extract ZIP to `C:\flutter` (use 7-Zip or WinRAR if needed)
- Verify folder exists: `C:\flutter\bin\flutter.bat`

**Add to PATH** (Critical!):
1. Press `Win + X` → Select **System**
2. Click **Advanced system settings** (left sidebar)
3. Click **Environment Variables** button (bottom right)
4. Under **User variables**, select **Path** → Click **Edit**
5. Click **New** → Type: `C:\flutter\bin`
6. Click **OK** → **OK** → **OK**

**Restart PowerShell**:
- Close ALL PowerShell/Command Prompt windows
- Open fresh PowerShell window
- Test: `flutter --version` (must show version)

---

## Step 2: Run Setup Script (5 min)

Navigate to project folder in PowerShell:
```powershell
cd "C:\Users\Aryan salunkhe\OneDrive\MY_PROJECTS\transit_delay_predictor"
```

Run setup script:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\setup.ps1
```

**Important**: When asked about Android licenses, **type `y` and press Enter** multiple times.

Wait for:
- ✅ Dependencies downloaded
- ✅ Licenses accepted
- ✅ Emulator list displayed

---

## Step 3: Start Emulator (3 min)

**Option A**: Command line (faster)
```powershell
emulator -list-avds
```
Pick an emulator name (e.g., `Pixel_5_API_33`), then:
```powershell
emulator -avd Pixel_5_API_33
```

**Option B**: Android Studio UI
1. Open **Android Studio**
2. **Tools** → **Device Manager**
3. Click **Play button** ▶️ on any emulator
4. Wait for home screen

---

## Step 4: Launch App (5 min)

In PowerShell (same window):
```powershell
flutter run
```

When asked about device, **pick the emulator**.

Wait 2-3 minutes for first build. You'll see:
- `════════════════════════════════════════════`
- `Flutter run key commands.`
- App appears on emulator

---

## What You'll See on Launch

✅ **Working**:
- Map with your location (blue dot)
- Bus stop markers (blue/yellow/red based on delay)
- Tap marker → Shows delay breakdown
- All 5 tabs: Home, Details, Routes, Settings, Reports
- Material 3 design (light/dark mode)
- Can add saved routes
- Can submit delay reports

⚠️ **Limited (no backend)**:
- Delays are simulated (heuristic-only)
- Flood warnings use mock data
- Reports saved to local database only
- No real-time crowd verification

---

## Project Map

```
transit_delay_predictor/
├── lib/                    ← All app code
│   ├── main.dart           ← App entry point
│   ├── screens/
│   │   ├── home_screen.dart       ← Map + markers
│   │   ├── details_screen.dart    ← Delay details
│   │   ├── saved_routes_screen.dart
│   │   ├── settings_screen.dart
│   │   └── reports_screen.dart
│   ├── services/           ← API calls
│   ├── providers/          ← State management
│   ├── models/             ← Data classes
│   └── widgets/            ← Reusable UI
├── pubspec.yaml            ← Dependencies
├── setup.ps1               ← Automated setup script
├── .env                    ← API credentials (optional)
└── Documentation files
```

---

## If Flutter Install Fails

See `INSTALLATION_GUIDE.md` (detailed troubleshooting section):
- `flutter: command not found` → PATH issue
- Android SDK problems → Install Android Studio
- License issues → Run `flutter doctor --android-licenses`

---

## After It Works

**Optional**: Add API credentials to `.env` file:
- Google Maps API key
- HERE Maps API key
- TomTom API key
- OpenWeather API key

*(App works fine without these for testing)*

**Optional**: Deploy backend to Vercel:
- See `VERCEL_BACKEND_GUIDE.md`

**Optional**: Deploy database to Supabase:
- See `SYSTEM_ARCHITECTURE.md`

---

## Key Command Reference

```powershell
# Check setup
flutter doctor

# Get dependencies
flutter pub get

# Run app
flutter run

# Run on specific device
flutter run -d emulator-5554

# Hot reload (after app running, press 'r')
flutter run -t lib/main.dart

# Clean and rebuild
flutter clean
flutter pub get
flutter run

# Check available emulators
emulator -list-avds

# Start specific emulator
emulator -avd [emulator-name]
```

---

**Ready?** Start with Step 1 (Flutter download), then come back here! 🚀

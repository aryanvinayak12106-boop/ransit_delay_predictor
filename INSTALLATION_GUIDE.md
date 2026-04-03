# 🚀 Transit-X Installation Guide (Windows)

## ❌ **PROBLEM: Flutter is NOT installed**

Your computer is missing Flutter. Follow these steps:

---

## ✅ **STEP 1: Download Flutter SDK** (5 minutes)

### Option A: Direct Download (Recommended)
1. Go to: **https://flutter.dev/docs/get-started/install/windows**
2. Click **"Windows"** tab
3. Download the **latest stable version** (file will be ~500MB)
4. Extract the ZIP file to: **`C:\flutter`**
   - (Create folder if it doesn't exist)
5. You should see: `C:\flutter\bin\flutter.bat`

### Option B: Using Chocolatey (If you have it)
```powershell
choco install flutter
```

---

## ✅ **STEP 2: Add Flutter to Your PATH** (3 minutes)

This tells Windows where to find Flutter commands.

### On Windows 11/10:
1. Press **Windows Key** → Search **"environment"**
2. Click **"Edit the system environment variables"**
3. Click **"Environment Variables"** button (bottom right)
4. Under "User variables", click **"New"**
5. Variable name: `FLUTTER_HOME`
6. Variable value: `C:\flutter`
7. Click **OK**

### Then edit PATH:
8. In "User variables", find **`PATH`** → Click **Edit**
9. Click **New** → Add: `C:\flutter\bin`
10. Click **OK** three times
11. **Close all PowerShell windows and reopen them**

---

## ✅ **STEP 3: Verify Flutter Installation** (1 minute)

Open a **NEW PowerShell window** and run:

```powershell
flutter --version
```

### Expected Output:
```
Flutter 3.16.0 • channel stable
Dart 3.2.0
```

✅ If you see version numbers, **Flutter is installed!**

---

## ✅ **STEP 4: Accept Android Licenses** (2 minutes)

```powershell
flutter doctor --android-licenses
```

Type **`y`** and press Enter for each license.

---

## ✅ **STEP 5: Check System Health** (3 minutes)

```powershell
flutter doctor
```

### Expected Output:
```
[✓] Flutter (Channel stable, X.X.X)
[✓] Android toolchain
[✓] Windows powershell
[!] Android Studio (optional issues are OK)
```

⚠️ Some warnings are fine. Just make sure there are no ❌ marks.

---

## 📦 **STEP 6: Get Project Dependencies** (5 minutes)

```powershell
cd "C:\Users\Aryan salunkhe\OneDrive\MY_PROJECTS\transit_delay_predictor"

flutter pub get
```

Wait for it to finish. You should see:
```
✓ Got dependencies
✓ Packages installed
```

---

## 🎮 **STEP 7: Start Android Emulator** (2 minutes)

Option A: **Using Android Studio (Easy)**
1. Open Android Studio
2. Go to: **Tools → Device Manager**
3. Click the **Play ▶️ button** next to your device
4. Wait 2 minutes for emulator to start

Option B: **Using Command Line**
```powershell
emulator -list-avds
emulator -avd "Pixel_6_API_33"
```

---

## 🚀 **STEP 8: Run the App!** (1 minute)

In PowerShell:
```powershell
cd "C:\Users\Aryan salunkhe\OneDrive\MY_PROJECTS\transit_delay_predictor"

flutter run
```

When prompted:
```
Multiple devices found:
1 (emulator)
2 (chrome web)
Which device do you want to target (or "q" to quit)?
```

Type **`1`** and press Enter.

---

## ✅ **Success Checklist**

- [x] Downloaded Flutter to `C:\flutter`
- [x] Added `C:\flutter\bin` to PATH
- [x] `flutter --version` works
- [x] Ran `flutter doctor`
- [x] Ran `flutter pub get`
- [x] Emulator is running
- [x] `flutter run` launched app

---

## 🆘 **If Something Goes Wrong**

### Error: "flutter command not found"
- **Solution**: Restart PowerShell after adding to PATH
- Or run: `$env:Path -split ';' | Select-String flutter`

### Error: "Android SDK not found"
- **Solution**: Download Android Studio from https://developer.android.com/studio

### Error: "No emulator found"
- **Solution**: Create device in Android Studio → Device Manager

### Error: "Port in use"
- **Solution**: Kill the process:
```powershell
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

---

## 📞 **Need Help?**

Once Flutter is installed, try:
```powershell
flutter doctor -v
```

Share the output if you're stuck!

---

**Ready to install Flutter? Follow the steps above, then come back!** ⬆️

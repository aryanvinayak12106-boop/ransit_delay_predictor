@echo off
REM Transit-X Setup Script for Windows PowerShell
REM Run this script to verify all requirements are installed

echo.
echo ========================================
echo   Transit-X Setup Checker
echo ========================================
echo.

echo [1/4] Checking Flutter...
flutter --version
if ERRORLEVEL 1 (
    echo     ❌ Flutter not found!
    echo     Download from: https://flutter.dev/docs/get-started/install/windows
    exit /b 1
) else (
    echo     ✅ Flutter installed
)

echo.
echo [2/4] Checking Dart...
dart --version
if ERRORLEVEL 1 (
    echo     ❌ Dart not found!
    exit /b 1
) else (
    echo     ✅ Dart installed
)

echo.
echo [3/4] Checking Android SDK...
flutter doctor -v
if ERRORLEVEL 1 (
    echo     ⚠️  Android setup may need configuration
)

echo.
echo [4/4] Getting Flutter dependencies...
cd /d "c:\Users\Aryan salunkhe\OneDrive\MY_PROJECTS\transit_delay_predictor"
flutter pub get
if ERRORLEVEL 1 (
    echo     ❌ Failed to get dependencies
    exit /b 1
) else (
    echo     ✅ Dependencies installed
)

echo.
echo ========================================
echo   ✅ Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start Android Emulator in Android Studio
echo 2. Run: flutter run
echo 3. Choose emulator when prompted
echo.
pause

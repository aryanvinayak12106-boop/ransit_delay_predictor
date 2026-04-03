# Transit-X Setup Script (PowerShell)
# Run this AFTER Flutter is installed
# Right-click → Run with PowerShell

Write-Host ""
Write-Host "======================================"
Write-Host "  Transit-X Setup Script"
Write-Host "======================================"
Write-Host ""

# Check Flutter
Write-Host "[1/5] Checking Flutter..." -ForegroundColor Cyan
flutter --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Flutter not found!" -ForegroundColor Red
    Write-Host "Install Flutter from: https://flutter.dev/docs/get-started/install/windows" -ForegroundColor Yellow
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Flutter OK" -ForegroundColor Green
Write-Host ""

# Accept Android licenses
Write-Host "[2/5] Accepting Android licenses..." -ForegroundColor Cyan
Write-Host "This will ask for confirmation. Type 'y' and press Enter for each." -ForegroundColor Yellow
flutter doctor --android-licenses
Write-Host "✅ Licenses accepted" -ForegroundColor Green
Write-Host ""

# Check system health
Write-Host "[3/5] Checking system health..." -ForegroundColor Cyan
flutter doctor
Write-Host ""

# Get dependencies
Write-Host "[4/5] Getting Flutter dependencies..." -ForegroundColor Cyan
cd "C:\Users\Aryan salunkhe\OneDrive\MY_PROJECTS\transit_delay_predictor"
flutter pub get
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to get dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# List available devices
Write-Host "[5/5] Available devices:" -ForegroundColor Cyan
flutter devices
Write-Host ""

Write-Host "======================================"
Write-Host "  ✅ Setup Complete!"
Write-Host "======================================"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start Android Emulator (in Android Studio)"
Write-Host "2. Run: flutter run"
Write-Host "3. Choose emulator when prompted"
Write-Host ""
Read-Host "Press Enter to exit"

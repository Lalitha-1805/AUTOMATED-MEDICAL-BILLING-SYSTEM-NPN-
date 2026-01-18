@echo off
REM Install Poppler for Windows (Required for PDF extraction)
REM This script downloads and installs Poppler

echo.
echo ============================================================
echo  Installing Poppler for PDF extraction...
echo ============================================================
echo.

REM Check if Chocolatey is installed
choco --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Chocolatey detected - installing Poppler via Chocolatey...
    choco install poppler -y
    goto done
) else (
    echo Chocolatey not found - Using alternative installation method...
    goto manual_install
)

:manual_install
echo.
echo Please follow these manual installation steps:
echo.
echo 1. Download Poppler for Windows:
echo    https://github.com/oschwartz10612/poppler-windows/releases/
echo.
echo 2. Extract to: C:\Program Files\poppler
echo.
echo 3. Add to PATH:
echo    - Right-click This PC or My Computer
echo    - Click Properties
echo    - Click Advanced system settings
echo    - Click Environment Variables
echo    - Under System variables, click New
echo    - Variable name: PATH (or edit existing)
echo    - Add: C:\Program Files\poppler\Library\bin
echo.
echo 4. Restart your terminal/IDE and try again
echo.
goto done

:done
echo.
echo ============================================================
echo  Installation complete!
echo  Verify: poppler-util --version
echo ============================================================
echo.
pause

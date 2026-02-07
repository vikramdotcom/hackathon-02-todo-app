@echo off
REM Phase IV - Minikube Setup Script (Windows)
REM Initializes Minikube cluster with appropriate configuration

setlocal enabledelayedexpansion

echo =========================================
echo Phase IV - Minikube Setup
echo =========================================
echo.

REM Configuration
set CPUS=4
set MEMORY=8192
set DISK_SIZE=20g
set DRIVER=docker

echo [34mConfiguration:[0m
echo   CPUs: %CPUS%
echo   Memory: %MEMORY%MB
echo   Disk Size: %DISK_SIZE%
echo   Driver: %DRIVER%
echo.

REM Check if Minikube is already running
minikube status >nul 2>&1
if %errorlevel% equ 0 (
    echo [33m⚠ Minikube is already running[0m
    echo.
    set /p RECREATE="Do you want to delete and recreate the cluster? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo Deleting existing cluster...
        minikube delete
    ) else (
        echo Using existing cluster
        echo.
        echo [32m✓ Minikube cluster ready[0m
        exit /b 0
    )
)

REM Start Minikube
echo Starting Minikube cluster...
echo.

minikube start --cpus=%CPUS% --memory=%MEMORY% --disk-size=%DISK_SIZE% --driver=%DRIVER%

echo.
echo [32m✓ Minikube cluster started[0m
echo.

REM Enable required addons
echo Enabling required addons...
echo.

echo   - Enabling Ingress controller...
minikube addons enable ingress

echo   - Enabling Metrics server...
minikube addons enable metrics-server

echo.
echo [32m✓ Addons enabled[0m
echo.

REM Verify cluster
echo Verifying cluster...
echo.

kubectl cluster-info
echo.

kubectl get nodes
echo.

REM Get Minikube IP
for /f "tokens=*" %%i in ('minikube ip') do set MINIKUBE_IP=%%i
echo [34mMinikube IP:[0m %MINIKUBE_IP%
echo.

REM Instructions for hosts file
echo =========================================
echo Next Steps
echo =========================================
echo.
echo 1. Add the following to your hosts file:
echo.
echo    [33m%MINIKUBE_IP% todo.local[0m
echo.
echo    On Windows (Run as Administrator):
echo    notepad C:\Windows\System32\drivers\etc\hosts
echo.
echo 2. Build Docker images:
echo    scripts\build-images.bat
echo.
echo 3. Deploy the application:
echo    scripts\deploy.bat
echo.
echo [32m✓ Minikube setup complete![0m

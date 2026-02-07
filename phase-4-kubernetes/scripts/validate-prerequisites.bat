@echo off
REM Phase IV - Prerequisite Validation Script (Windows)
REM Validates that all required tools are installed and configured

setlocal enabledelayedexpansion

echo =========================================
echo Phase IV - Prerequisite Validation
echo =========================================
echo.

set PASSED=0
set FAILED=0

REM Check Docker
echo Checking Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VERSION=%%i
    echo [32m✓[0m Docker installed: !DOCKER_VERSION!
    set /a PASSED+=1
) else (
    echo [31m✗[0m Docker not found
    echo   Install from: https://www.docker.com/get-started
    set /a FAILED+=1
)

REM Check Minikube
echo Checking Minikube...
minikube version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('minikube version ^| findstr /C:"minikube version"') do set MINIKUBE_VERSION=%%i
    echo [32m✓[0m Minikube installed: !MINIKUBE_VERSION!
    set /a PASSED+=1
) else (
    echo [31m✗[0m Minikube not found
    echo   Install from: https://minikube.sigs.k8s.io/docs/start/
    set /a FAILED+=1
)

REM Check kubectl
echo Checking kubectl...
kubectl version --client >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('kubectl version --client --short 2^>nul') do set KUBECTL_VERSION=%%i
    echo [32m✓[0m kubectl installed: !KUBECTL_VERSION!
    set /a PASSED+=1
) else (
    echo [31m✗[0m kubectl not found
    echo   Install from: https://kubernetes.io/docs/tasks/tools/
    set /a FAILED+=1
)

REM Check Helm
echo Checking Helm...
helm version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('helm version --short') do set HELM_VERSION=%%i
    echo [32m✓[0m Helm installed: !HELM_VERSION!
    set /a PASSED+=1
) else (
    echo [31m✗[0m Helm not found
    echo   Install from: https://helm.sh/docs/intro/install/
    set /a FAILED+=1
)

echo.
echo Checking Docker daemon...
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Docker daemon running
    set /a PASSED+=1
) else (
    echo [31m✗[0m Docker daemon not running
    echo   Start Docker Desktop
    set /a FAILED+=1
)

echo.
echo =========================================
echo Validation Summary
echo =========================================
echo [32mPassed:[0m %PASSED%
echo [31mFailed:[0m %FAILED%
echo.

if %FAILED% equ 0 (
    echo [32m✓ All prerequisites met![0m
    echo.
    echo Next steps:
    echo   1. Run: scripts\setup-minikube.bat
    echo   2. Run: scripts\deploy.bat
    exit /b 0
) else (
    echo [31m✗ Some prerequisites are missing[0m
    echo.
    echo Please install missing tools and try again.
    exit /b 1
)

@echo off
REM Phase IV - Docker Image Build Script (Windows)
REM Builds Docker images for frontend and backend using Minikube's Docker daemon

setlocal enabledelayedexpansion

echo =========================================
echo Phase IV - Building Docker Images
echo =========================================
echo.

REM Version tagging
REM Usage: build-images.bat [version]
REM If no version provided, uses git commit SHA or timestamp

set VERSION=%1

if "!VERSION!"=="" (
    REM Try to get git commit SHA
    git rev-parse --git-dir >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=*" %%i in ('git rev-parse --short HEAD') do set VERSION=%%i
        echo [34mUsing git commit SHA as version: !VERSION![0m
    ) else (
        REM Fallback to timestamp
        for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set datetime=%%i
        set VERSION=!datetime:~0,8!-!datetime:~8,6!
        echo [34mUsing timestamp as version: !VERSION![0m
    )
) else (
    echo [34mUsing provided version: !VERSION![0m
)

REM Always tag as latest as well
set TAG_LATEST=true

echo.

REM Check if Minikube is running
minikube status >nul 2>&1
if %errorlevel% neq 0 (
    echo [31m✗ Minikube is not running[0m
    echo Please start Minikube first: scripts\setup-minikube.bat
    exit /b 1
)

echo [32m✓ Minikube is running[0m
echo.

REM Configure Docker to use Minikube's daemon
echo Configuring Docker to use Minikube's daemon...
for /f "tokens=*" %%i in ('minikube docker-env --shell cmd') do %%i
echo [32m✓ Docker configured[0m
echo.

REM Build frontend image
echo =========================================
echo Building Frontend Image
echo =========================================
echo.

cd ..\phase-3-ai-chatbot\frontend

echo Building todo-frontend:!VERSION!...
docker build -f ..\..\phase-4-kubernetes\docker\frontend\Dockerfile -t todo-frontend:!VERSION! .

if %errorlevel% neq 0 (
    echo [31m✗ Frontend build failed[0m
    exit /b 1
)

if "!TAG_LATEST!"=="true" (
    echo Tagging as latest...
    docker tag todo-frontend:!VERSION! todo-frontend:latest
)

echo.
echo [32m✓ Frontend image built successfully[0m
echo   - todo-frontend:!VERSION!
if "!TAG_LATEST!"=="true" (
    echo   - todo-frontend:latest
)
echo.

REM Build backend image
echo =========================================
echo Building Backend Image
echo =========================================
echo.

cd ..\backend

echo Building todo-backend:!VERSION!...
docker build -f ..\..\phase-4-kubernetes\docker\backend\Dockerfile -t todo-backend:!VERSION! .

if %errorlevel% neq 0 (
    echo [31m✗ Backend build failed[0m
    exit /b 1
)

if "!TAG_LATEST!"=="true" (
    echo Tagging as latest...
    docker tag todo-backend:!VERSION! todo-backend:latest
)

echo.
echo [32m✓ Backend image built successfully[0m
echo   - todo-backend:!VERSION!
if "!TAG_LATEST!"=="true" (
    echo   - todo-backend:latest
)
echo.

REM Return to phase-4-kubernetes directory
cd ..\..\phase-4-kubernetes

REM Verify images
echo =========================================
echo Verifying Images
echo =========================================
echo.

docker images | findstr "todo-"

echo.
echo [32m✓ All images built successfully![0m
echo.
echo Image versions:
echo   Frontend: todo-frontend:!VERSION!
echo   Backend: todo-backend:!VERSION!
echo.
echo Next steps:
echo   1. Create secrets: kubectl apply -f k8s\secret.yaml
echo   2. Deploy application: scripts\deploy.bat
echo.
echo To deploy with specific version:
echo   helm install todo-app .\helm\todo-app -n todo-app ^
echo     --set frontend.image.tag=!VERSION! ^
echo     --set backend.image.tag=!VERSION!

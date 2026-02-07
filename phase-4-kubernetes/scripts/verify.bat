@echo off
REM Phase IV - End-to-End Verification Script (Windows)
REM Validates the complete deployment and functionality

setlocal enabledelayedexpansion

set PASSED=0
set FAILED=0
set WARNINGS=0

echo =========================================
echo Phase IV - End-to-End Verification
echo =========================================
echo.

REM 1. Prerequisites
echo =========================================
echo 1. Prerequisites
echo =========================================
echo.

echo Checking Minikube running...
minikube status >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Minikube running
    set /a PASSED+=1
) else (
    echo [31m✗[0m Minikube not running
    set /a FAILED+=1
)

echo Checking kubectl configured...
kubectl cluster-info >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m kubectl configured
    set /a PASSED+=1
) else (
    echo [31m✗[0m kubectl not configured
    set /a FAILED+=1
)

echo Checking Docker daemon...
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Docker daemon
    set /a PASSED+=1
) else (
    echo [31m✗[0m Docker daemon
    set /a FAILED+=1
)

echo.

REM 2. Namespace and Resources
echo =========================================
echo 2. Namespace and Resources
echo =========================================
echo.

echo Checking Namespace exists...
kubectl get namespace todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Namespace exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Namespace exists
    set /a FAILED+=1
)

echo Checking ConfigMap exists...
kubectl get configmap todo-app-config -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m ConfigMap exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m ConfigMap exists
    set /a FAILED+=1
)

echo Checking Secret exists...
kubectl get secret todo-app-secrets -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Secret exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Secret exists
    set /a FAILED+=1
)

echo Checking PVC exists...
kubectl get pvc postgres-pvc -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m PVC exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m PVC exists
    set /a FAILED+=1
)

echo.

REM 3. Deployments
echo =========================================
echo 3. Deployments
echo =========================================
echo.

echo Checking Frontend deployment exists...
kubectl get deployment frontend -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Frontend deployment exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Frontend deployment exists
    set /a FAILED+=1
)

echo Checking Backend deployment exists...
kubectl get deployment backend -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Backend deployment exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Backend deployment exists
    set /a FAILED+=1
)

echo Checking Database deployment exists...
kubectl get deployment database -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Database deployment exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Database deployment exists
    set /a FAILED+=1
)

echo.

REM 4. Services
echo =========================================
echo 4. Services
echo =========================================
echo.

echo Checking Frontend service exists...
kubectl get service frontend -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Frontend service exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Frontend service exists
    set /a FAILED+=1
)

echo Checking Backend service exists...
kubectl get service backend -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Backend service exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Backend service exists
    set /a FAILED+=1
)

echo Checking Database service exists...
kubectl get service database -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Database service exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Database service exists
    set /a FAILED+=1
)

echo.

REM 5. Ingress
echo =========================================
echo 5. Ingress
echo =========================================
echo.

echo Checking Ingress exists...
kubectl get ingress todo-app-ingress -n todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Ingress exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Ingress exists
    set /a FAILED+=1
)

echo.

REM 6. Pod Health
echo =========================================
echo 6. Pod Health
echo =========================================
echo.

for /f "tokens=*" %%i in ('kubectl get deployment frontend -n todo-app -o jsonpath^="{.spec.replicas}" 2^>nul') do set FRONTEND_DESIRED=%%i
for /f "tokens=*" %%i in ('kubectl get deployment frontend -n todo-app -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set FRONTEND_READY=%%i
for /f "tokens=*" %%i in ('kubectl get deployment backend -n todo-app -o jsonpath^="{.spec.replicas}" 2^>nul') do set BACKEND_DESIRED=%%i
for /f "tokens=*" %%i in ('kubectl get deployment backend -n todo-app -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set BACKEND_READY=%%i
for /f "tokens=*" %%i in ('kubectl get deployment database -n todo-app -o jsonpath^="{.spec.replicas}" 2^>nul') do set DATABASE_DESIRED=%%i
for /f "tokens=*" %%i in ('kubectl get deployment database -n todo-app -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set DATABASE_READY=%%i

if "%FRONTEND_READY%"=="%FRONTEND_DESIRED%" (
    echo [32m✓[0m Frontend pods ready ^(%FRONTEND_READY%/%FRONTEND_DESIRED%^)
    set /a PASSED+=1
) else (
    echo [31m✗[0m Frontend pods ready ^(%FRONTEND_READY%/%FRONTEND_DESIRED%^)
    set /a FAILED+=1
)

if "%BACKEND_READY%"=="%BACKEND_DESIRED%" (
    echo [32m✓[0m Backend pods ready ^(%BACKEND_READY%/%BACKEND_DESIRED%^)
    set /a PASSED+=1
) else (
    echo [31m✗[0m Backend pods ready ^(%BACKEND_READY%/%BACKEND_DESIRED%^)
    set /a FAILED+=1
)

if "%DATABASE_READY%"=="%DATABASE_DESIRED%" (
    echo [32m✓[0m Database pods ready ^(%DATABASE_READY%/%DATABASE_DESIRED%^)
    set /a PASSED+=1
) else (
    echo [31m✗[0m Database pods ready ^(%DATABASE_READY%/%DATABASE_DESIRED%^)
    set /a FAILED+=1
)

echo.

REM 7. Ingress Accessibility
echo =========================================
echo 7. Ingress Accessibility
echo =========================================
echo.

for /f "tokens=*" %%i in ('minikube ip') do set MINIKUBE_IP=%%i

echo Checking Hosts file entry...
findstr /C:"%MINIKUBE_IP%" C:\Windows\System32\drivers\etc\hosts | findstr "todo.local" >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Hosts file entry
    set /a PASSED+=1
) else (
    echo [33m⚠[0m Hosts file entry ^(Add: %MINIKUBE_IP% todo.local^)
    set /a WARNINGS+=1
)

echo.

REM Summary
echo =========================================
echo Verification Summary
echo =========================================
echo.
echo [32mPassed:[0m %PASSED%
echo [31mFailed:[0m %FAILED%
echo [33mWarnings:[0m %WARNINGS%
echo.

if %FAILED% equ 0 (
    if %WARNINGS% equ 0 (
        echo [32m✓ All checks passed![0m
        echo.
        echo Your Todo App is fully deployed and operational.
        echo.
        echo Access the application:
        echo   Frontend: http://todo.local
        echo   Backend API: http://todo.local/api
        echo   Health Check: http://todo.local/api/health
        exit /b 0
    ) else (
        echo [33m⚠ Deployment successful with warnings[0m
        echo.
        echo The application is deployed but some optional features may not be available.
        echo Review the warnings above and address them if needed.
        exit /b 0
    )
) else (
    echo [31m✗ Deployment has issues[0m
    echo.
    echo Please review the failed checks above and troubleshoot:
    echo   1. Check pod logs: kubectl logs ^<pod-name^> -n todo-app
    echo   2. Describe resources: kubectl describe ^<resource^> -n todo-app
    echo   3. Check events: kubectl get events -n todo-app
    echo   4. Review TROUBLESHOOTING.md for common issues
    exit /b 1
)

@echo off
REM Phase IV - Health Check Script (Windows)
REM Comprehensive health check for all components

setlocal enabledelayedexpansion

set NAMESPACE=todo-app
set PASSED=0
set FAILED=0
set WARNINGS=0

echo =========================================
echo Health Check - Todo App
echo =========================================
echo.

REM 1. Cluster Health
echo =========================================
echo 1. Cluster Health
echo =========================================
echo.

echo Checking Minikube running...
minikube status >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Minikube running
    set /a PASSED+=1
) else (
    echo [31m✗[0m Minikube not running
    echo   Error: Start Minikube with: scripts\setup-minikube.bat
    set /a FAILED+=1
)

echo Checking kubectl configured...
kubectl cluster-info >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m kubectl configured
    set /a PASSED+=1
) else (
    echo [31m✗[0m kubectl not configured
    echo   Error: Check kubectl configuration
    set /a FAILED+=1
)

echo Checking Metrics server available...
kubectl top nodes >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Metrics server available
    set /a PASSED+=1
) else (
    echo [33m⚠[0m Metrics server not available
    echo   Warning: Enable with: minikube addons enable metrics-server
    set /a WARNINGS+=1
)

echo.

REM 2. Namespace Health
echo =========================================
echo 2. Namespace Health
echo =========================================
echo.

kubectl get namespace %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Namespace exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Namespace not found
    echo   Error: Deploy the application first
    set /a FAILED+=1
    goto summary
)

echo.

REM 3. Deployment Health
echo =========================================
echo 3. Deployment Health
echo =========================================
echo.

echo Checking Frontend deployment exists...
kubectl get deployment frontend -n %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Frontend deployment exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Frontend deployment not found
    echo   Error: Deploy with: scripts\deploy.bat
    set /a FAILED+=1
)

echo Checking Backend deployment exists...
kubectl get deployment backend -n %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Backend deployment exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Backend deployment not found
    echo   Error: Deploy with: scripts\deploy.bat
    set /a FAILED+=1
)

echo Checking Database deployment exists...
kubectl get deployment database -n %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Database deployment exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Database deployment not found
    echo   Error: Deploy with: scripts\deploy.bat
    set /a FAILED+=1
)

REM Get deployment status
for /f "tokens=*" %%i in ('kubectl get deployment frontend -n %NAMESPACE% -o jsonpath^="{.spec.replicas}" 2^>nul') do set FRONTEND_DESIRED=%%i
for /f "tokens=*" %%i in ('kubectl get deployment frontend -n %NAMESPACE% -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set FRONTEND_READY=%%i
for /f "tokens=*" %%i in ('kubectl get deployment backend -n %NAMESPACE% -o jsonpath^="{.spec.replicas}" 2^>nul') do set BACKEND_DESIRED=%%i
for /f "tokens=*" %%i in ('kubectl get deployment backend -n %NAMESPACE% -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set BACKEND_READY=%%i
for /f "tokens=*" %%i in ('kubectl get deployment database -n %NAMESPACE% -o jsonpath^="{.spec.replicas}" 2^>nul') do set DATABASE_DESIRED=%%i
for /f "tokens=*" %%i in ('kubectl get deployment database -n %NAMESPACE% -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set DATABASE_READY=%%i

if "%FRONTEND_READY%"=="" set FRONTEND_READY=0
if "%BACKEND_READY%"=="" set BACKEND_READY=0
if "%DATABASE_READY%"=="" set DATABASE_READY=0

echo.
echo [34mDeployment Status:[0m
echo   Frontend: !FRONTEND_READY!/!FRONTEND_DESIRED! ready
echo   Backend: !BACKEND_READY!/!BACKEND_DESIRED! ready
echo   Database: !DATABASE_READY!/!DATABASE_DESIRED! ready
echo.

if "!FRONTEND_READY!"=="!FRONTEND_DESIRED!" (
    if not "!FRONTEND_DESIRED!"=="0" (
        echo [32m✓[0m Frontend deployment healthy
        set /a PASSED+=1
    )
) else (
    echo [31m✗[0m Frontend deployment unhealthy
    echo   Error: Check logs with: scripts\view-logs.bat frontend
    set /a FAILED+=1
)

if "!BACKEND_READY!"=="!BACKEND_DESIRED!" (
    if not "!BACKEND_DESIRED!"=="0" (
        echo [32m✓[0m Backend deployment healthy
        set /a PASSED+=1
    )
) else (
    echo [31m✗[0m Backend deployment unhealthy
    echo   Error: Check logs with: scripts\view-logs.bat backend
    set /a FAILED+=1
)

if "!DATABASE_READY!"=="!DATABASE_DESIRED!" (
    if not "!DATABASE_DESIRED!"=="0" (
        echo [32m✓[0m Database deployment healthy
        set /a PASSED+=1
    )
) else (
    echo [31m✗[0m Database deployment unhealthy
    echo   Error: Check logs with: scripts\view-logs.bat database
    set /a FAILED+=1
)

echo.

REM 4. Service Health
echo =========================================
echo 4. Service Health
echo =========================================
echo.

echo Checking Frontend service exists...
kubectl get service frontend -n %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Frontend service exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Frontend service not found
    set /a FAILED+=1
)

echo Checking Backend service exists...
kubectl get service backend -n %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Backend service exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Backend service not found
    set /a FAILED+=1
)

echo Checking Database service exists...
kubectl get service database -n %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Database service exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Database service not found
    set /a FAILED+=1
)

echo.

REM 5. Ingress Health
echo =========================================
echo 5. Ingress Health
echo =========================================
echo.

echo Checking Ingress exists...
kubectl get ingress todo-app-ingress -n %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Ingress exists
    set /a PASSED+=1
) else (
    echo [31m✗[0m Ingress not found
    set /a FAILED+=1
)

echo Checking Ingress controller running...
kubectl get pods -n ingress-nginx -l app.kubernetes.io/component^=controller >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Ingress controller running
    set /a PASSED+=1
) else (
    echo [33m⚠[0m Ingress controller not running
    echo   Warning: Enable with: minikube addons enable ingress
    set /a WARNINGS+=1
)

echo Checking Hosts file configured...
for /f "tokens=*" %%i in ('minikube ip 2^>nul') do set MINIKUBE_IP=%%i
if not "!MINIKUBE_IP!"=="" (
    findstr /C:"!MINIKUBE_IP!" C:\Windows\System32\drivers\etc\hosts | findstr "todo.local" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [32m✓[0m Hosts file configured
        set /a PASSED+=1
    ) else (
        echo [33m⚠[0m Hosts file not configured
        echo   Warning: Add: !MINIKUBE_IP! todo.local to hosts file
        set /a WARNINGS+=1
    )
)

echo.

REM 6. Resource Usage
echo =========================================
echo 6. Resource Usage
echo =========================================
echo.

kubectl top nodes >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Metrics available
    set /a PASSED+=1
    echo.
    echo [34mCurrent Resource Usage:[0m
    kubectl top pods -n %NAMESPACE% 2>nul || echo   No pod metrics available yet
) else (
    echo [33m⚠[0m Metrics not available
    echo   Warning: Wait for metrics-server to be ready
    set /a WARNINGS+=1
)

echo.

:summary
REM Summary
echo =========================================
echo Health Check Summary
echo =========================================
echo.
echo [32mPassed:[0m !PASSED!
echo [31mFailed:[0m !FAILED!
echo [33mWarnings:[0m !WARNINGS!
echo.

REM Recommendations
if !FAILED! gtr 0 (
    echo =========================================
    echo Troubleshooting Recommendations
    echo =========================================
    echo.
    echo Critical issues detected. Try these steps:
    echo   1. Check pod logs: scripts\view-logs.bat all
    echo   2. Check pod status: kubectl get pods -n %NAMESPACE%
    echo   3. Describe failed pods: kubectl describe pod ^<pod-name^> -n %NAMESPACE%
    echo   4. Check events: kubectl get events -n %NAMESPACE% --sort-by^='.lastTimestamp'
    echo   5. Review troubleshooting guide: TROUBLESHOOTING.md
    echo.
)

if !WARNINGS! gtr 0 (
    if !FAILED! equ 0 (
        echo =========================================
        echo Recommendations
        echo =========================================
        echo.
    )
    echo Warnings detected. Consider these actions:
    echo   1. Wait for metrics-server to be ready
    echo   2. Configure hosts file for Ingress access
    echo   3. Check for pod restarts and investigate causes
    echo.
)

REM Exit code
if !FAILED! equ 0 (
    if !WARNINGS! equ 0 (
        echo [32m✓ All health checks passed![0m
        echo.
        echo Your Todo App is healthy and ready to use.
        echo Access at: http://todo.local
        exit /b 0
    ) else (
        echo [33m⚠ Health checks passed with warnings[0m
        echo.
        echo The application is functional but some optional features may have issues.
        exit /b 0
    )
) else (
    echo [31m✗ Health checks failed[0m
    echo.
    echo Please address the issues above before using the application.
    exit /b 1
)

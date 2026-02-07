@echo off
REM Phase IV - Status Check Script (Windows)
REM Displays the current status of the Todo App deployment

setlocal enabledelayedexpansion

echo =========================================
echo Phase IV - Todo App Status
echo =========================================
echo.

REM Check if Minikube is running
minikube status >nul 2>&1
if %errorlevel% neq 0 (
    echo [31m✗ Minikube is not running[0m
    exit /b 1
)

echo [32m✓ Minikube is running[0m
echo.

REM Check if namespace exists
kubectl get namespace todo-app >nul 2>&1
if %errorlevel% neq 0 (
    echo [31m✗ Todo App namespace not found[0m
    echo Run scripts\deploy.bat to deploy the application
    exit /b 1
)

echo [32m✓ Todo App namespace exists[0m
echo.

REM Display pods
echo =========================================
echo Pods
echo =========================================
kubectl get pods -n todo-app -o wide

echo.

REM Display services
echo =========================================
echo Services
echo =========================================
kubectl get services -n todo-app

echo.

REM Display deployments
echo =========================================
echo Deployments
echo =========================================
kubectl get deployments -n todo-app

echo.

REM Display ingress
echo =========================================
echo Ingress
echo =========================================
kubectl get ingress -n todo-app

echo.

REM Display PVC
echo =========================================
echo Persistent Volume Claims
echo =========================================
kubectl get pvc -n todo-app

echo.

REM Check pod health
echo =========================================
echo Pod Health Status
echo =========================================

for /f "tokens=*" %%i in ('kubectl get pods -n todo-app --no-headers 2^>nul ^| find /c /v ""') do set TOTAL_PODS=%%i
for /f "tokens=*" %%i in ('kubectl get pods -n todo-app --no-headers 2^>nul ^| findstr "Running" ^| find /c "/"') do set READY_PODS=%%i

echo Total Pods: [34m%TOTAL_PODS%[0m
echo Ready Pods: [32m%READY_PODS%[0m

if %READY_PODS% equ %TOTAL_PODS% (
    if %TOTAL_PODS% gtr 0 (
        echo [32m✓ All pods are healthy[0m
    )
) else (
    echo [33m⚠ Some pods are not ready[0m
)

echo.

REM Display access information
echo =========================================
echo Access Information
echo =========================================

for /f "tokens=*" %%i in ('minikube ip') do set MINIKUBE_IP=%%i
echo [34mApplication URL:[0m http://todo.local
echo [34mMinikube IP:[0m %MINIKUBE_IP%
echo.
echo Add to hosts file:
echo [33m%MINIKUBE_IP% todo.local[0m

echo.

REM Display resource usage
echo =========================================
echo Resource Usage
echo =========================================
kubectl top pods -n todo-app 2>nul || echo Metrics not available (metrics-server may not be ready)

echo.
echo Useful commands:
echo   - View logs: kubectl logs -f deployment/backend -n todo-app
echo   - Describe pod: kubectl describe pod ^<pod-name^> -n todo-app
echo   - Scale deployment: kubectl scale deployment/backend --replicas=3 -n todo-app
echo   - Port forward: kubectl port-forward service/frontend 3000:3000 -n todo-app

@echo off
REM Phase IV - Deployment Verification Script (Windows)
REM Verifies deployment consistency and reproducibility

setlocal enabledelayedexpansion

set PASSED=0
set FAILED=0
set WARNINGS=0

echo =========================================
echo Phase IV - Deployment Verification
echo =========================================
echo.

REM 1. Environment Verification
echo =========================================
echo 1. Environment Verification
echo =========================================
echo.

echo [34mOperating System:[0m Windows
echo.

REM Check prerequisites
echo Checking Docker installed...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Docker installed
    set /a PASSED+=1
) else (
    echo [31m✗[0m Docker not installed
    set /a FAILED+=1
)

echo Checking Minikube installed...
minikube version >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Minikube installed
    set /a PASSED+=1
) else (
    echo [31m✗[0m Minikube not installed
    set /a FAILED+=1
)

echo Checking kubectl installed...
kubectl version --client >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m kubectl installed
    set /a PASSED+=1
) else (
    echo [31m✗[0m kubectl not installed
    set /a FAILED+=1
)

echo Checking Helm installed...
helm version >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Helm installed
    set /a PASSED+=1
) else (
    echo [31m✗[0m Helm not installed
    set /a FAILED+=1
)

echo.

REM 2. Cluster Verification
echo =========================================
echo 2. Cluster Verification
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

echo.
echo [34mCluster Information:[0m
for /f "tokens=*" %%i in ('minikube version --short 2^>nul') do echo   Minikube: %%i
for /f "tokens=*" %%i in ('kubectl version --client --short 2^>nul ^| findstr /C:"Client"') do echo   kubectl: %%i
for /f "tokens=*" %%i in ('helm version --short 2^>nul') do echo   Helm: %%i
echo.

REM 3. Image Verification
echo =========================================
echo 3. Image Verification
echo =========================================
echo.

REM Configure Docker to use Minikube's daemon
for /f "tokens=*" %%i in ('minikube docker-env --shell cmd') do %%i

echo Checking Frontend images...
docker images todo-frontend >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('docker images todo-frontend --format "{{.Tag}}"') do (
        echo [32m✓[0m Frontend images found: %%i
        set /a PASSED+=1
        goto :backend_check
    )
) else (
    echo [31m✗[0m Frontend images not found
    set /a FAILED+=1
)

:backend_check
echo Checking Backend images...
docker images todo-backend >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('docker images todo-backend --format "{{.Tag}}"') do (
        echo [32m✓[0m Backend images found: %%i
        set /a PASSED+=1
        goto :deployment_check
    )
) else (
    echo [31m✗[0m Backend images not found
    set /a FAILED+=1
)

:deployment_check
echo.

REM 4. Deployment Verification
echo =========================================
echo 4. Deployment Verification
echo =========================================
echo.

kubectl get namespace todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Namespace exists
    set /a PASSED+=1

    REM Check deployments
    for /f "tokens=*" %%i in ('kubectl get deployment frontend -n todo-app -o jsonpath^="{.status.replicas}" 2^>nul') do set FRONTEND_REPLICAS=%%i
    for /f "tokens=*" %%i in ('kubectl get deployment frontend -n todo-app -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set FRONTEND_READY=%%i
    for /f "tokens=*" %%i in ('kubectl get deployment backend -n todo-app -o jsonpath^="{.status.replicas}" 2^>nul') do set BACKEND_REPLICAS=%%i
    for /f "tokens=*" %%i in ('kubectl get deployment backend -n todo-app -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set BACKEND_READY=%%i
    for /f "tokens=*" %%i in ('kubectl get deployment database -n todo-app -o jsonpath^="{.status.replicas}" 2^>nul') do set DATABASE_REPLICAS=%%i
    for /f "tokens=*" %%i in ('kubectl get deployment database -n todo-app -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set DATABASE_READY=%%i

    echo.
    echo [34mDeployment Status:[0m
    echo   Frontend: !FRONTEND_READY!/!FRONTEND_REPLICAS! ready
    echo   Backend: !BACKEND_READY!/!BACKEND_REPLICAS! ready
    echo   Database: !DATABASE_READY!/!DATABASE_REPLICAS! ready
    echo.

    if "!FRONTEND_READY!"=="!FRONTEND_REPLICAS!" (
        if not "!FRONTEND_REPLICAS!"=="0" (
            echo [32m✓[0m Frontend deployment healthy
            set /a PASSED+=1
        )
    ) else (
        echo [31m✗[0m Frontend deployment not healthy
        set /a FAILED+=1
    )

    if "!BACKEND_READY!"=="!BACKEND_REPLICAS!" (
        if not "!BACKEND_REPLICAS!"=="0" (
            echo [32m✓[0m Backend deployment healthy
            set /a PASSED+=1
        )
    ) else (
        echo [31m✗[0m Backend deployment not healthy
        set /a FAILED+=1
    )

    if "!DATABASE_READY!"=="!DATABASE_REPLICAS!" (
        if not "!DATABASE_REPLICAS!"=="0" (
            echo [32m✓[0m Database deployment healthy
            set /a PASSED+=1
        )
    ) else (
        echo [31m✗[0m Database deployment not healthy
        set /a FAILED+=1
    )
) else (
    echo [33m⚠[0m Namespace not found ^(deployment not yet done^)
    set /a WARNINGS+=1
)

echo.

REM 5. Configuration Verification
echo =========================================
echo 5. Configuration Verification
echo =========================================
echo.

kubectl get namespace todo-app >nul 2>&1
if %errorlevel% equ 0 (
    echo Checking ConfigMap exists...
    kubectl get configmap todo-app-config -n todo-app >nul 2>&1
    if %errorlevel% equ 0 (
        echo [32m✓[0m ConfigMap exists
        set /a PASSED+=1
    ) else (
        echo [31m✗[0m ConfigMap not found
        set /a FAILED+=1
    )

    echo Checking Secret exists...
    kubectl get secret todo-app-secrets -n todo-app >nul 2>&1
    if %errorlevel% equ 0 (
        echo [32m✓[0m Secret exists
        set /a PASSED+=1
    ) else (
        echo [31m✗[0m Secret not found
        set /a FAILED+=1
    )

    echo Checking PVC exists...
    kubectl get pvc postgres-pvc -n todo-app >nul 2>&1
    if %errorlevel% equ 0 (
        echo [32m✓[0m PVC exists
        set /a PASSED+=1
    ) else (
        echo [31m✗[0m PVC not found
        set /a FAILED+=1
    )
)

echo.

REM 6. Version Consistency
echo =========================================
echo 6. Version Consistency
echo =========================================
echo.

kubectl get namespace todo-app >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('kubectl get deployment frontend -n todo-app -o jsonpath^="{.spec.template.spec.containers[0].image}" 2^>nul') do set FRONTEND_IMAGE=%%i
    for /f "tokens=*" %%i in ('kubectl get deployment backend -n todo-app -o jsonpath^="{.spec.template.spec.containers[0].image}" 2^>nul') do set BACKEND_IMAGE=%%i

    echo [34mDeployed Images:[0m
    echo   Frontend: !FRONTEND_IMAGE!
    echo   Backend: !BACKEND_IMAGE!
    echo.
)

echo.

REM 7. Helm Release Verification
echo =========================================
echo 7. Helm Release Verification
echo =========================================
echo.

helm list -n todo-app 2>nul | findstr "todo-app" >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Helm release found
    set /a PASSED+=1
) else (
    echo [33m⚠[0m No Helm release found ^(using direct kubectl deployment^)
    set /a WARNINGS+=1
)

echo.

REM Summary
echo =========================================
echo Verification Summary
echo =========================================
echo.
echo [32mPassed:[0m !PASSED!
echo [31mFailed:[0m !FAILED!
echo [33mWarnings:[0m !WARNINGS!
echo.

REM Final verdict
if !FAILED! equ 0 (
    if !WARNINGS! equ 0 (
        echo [32m✓ Deployment is fully verified and reproducible![0m
        echo.
        echo Environment is consistent and ready for use.
        exit /b 0
    ) else (
        echo [33m⚠ Deployment verified with minor warnings[0m
        echo.
        echo Deployment is functional but some optional checks failed.
        echo Review warnings above for details.
        exit /b 0
    )
) else (
    echo [31m✗ Deployment verification failed[0m
    echo.
    echo Please address the failed checks above.
    echo Run scripts\status.bat for more details.
    exit /b 1
)

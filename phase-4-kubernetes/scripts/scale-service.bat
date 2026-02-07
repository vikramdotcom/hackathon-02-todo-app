@echo off
REM Phase IV - Service Scaling Script (Windows)
REM Helper script for scaling services

setlocal enabledelayedexpansion

REM Default values
set NAMESPACE=todo-app
set SERVICE=%1
set REPLICAS=%2

REM Usage function
if "%SERVICE%"=="" goto usage
if "%REPLICAS%"=="" goto usage
goto main

:usage
echo Usage: %0 ^<service^> ^<replicas^>
echo.
echo Services:
echo   frontend   - Scale frontend deployment
echo   backend    - Scale backend deployment
echo   all        - Scale both frontend and backend
echo.
echo Examples:
echo   %0 frontend 3      # Scale frontend to 3 replicas
echo   %0 backend 5       # Scale backend to 5 replicas
echo   %0 all 3           # Scale both to 3 replicas
echo.
exit /b 1

:main

REM Validate replicas is a number
echo %REPLICAS%| findstr /r "^[0-9][0-9]*$" >nul
if %errorlevel% neq 0 (
    echo [31mError: Replicas must be a positive number[0m
    exit /b 1
)

REM Check if namespace exists
kubectl get namespace %NAMESPACE% >nul 2>&1
if %errorlevel% neq 0 (
    echo [31mError: Namespace '%NAMESPACE%' not found[0m
    echo Please deploy the application first
    exit /b 1
)

echo =========================================
echo Service Scaling
echo =========================================
echo.

REM Scale services
if "%SERVICE%"=="frontend" (
    call :scale_service frontend %REPLICAS%
) else if "%SERVICE%"=="backend" (
    call :scale_service backend %REPLICAS%
) else if "%SERVICE%"=="all" (
    call :scale_service frontend %REPLICAS%
    call :scale_service backend %REPLICAS%
) else (
    echo [31mError: Unknown service '%SERVICE%'[0m
    goto usage
)

REM Show current status
echo.
echo =========================================
echo Current Deployment Status
echo =========================================
echo.

kubectl get deployments -n %NAMESPACE%

echo.
echo =========================================
echo Pod Status
echo =========================================
echo.

kubectl get pods -n %NAMESPACE% -o wide

echo.
echo [32m✓ Scaling complete![0m
echo.
echo Monitor resource usage:
echo   kubectl top pods -n %NAMESPACE%
echo   kubectl top nodes

exit /b 0

:scale_service
set SVC=%1
set REP=%2

echo Scaling %SVC% to %REP% replicas...

kubectl scale deployment/%SVC% --replicas=%REP% -n %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓[0m Scaled %SVC%

    REM Wait for rollout
    echo Waiting for rollout to complete...
    kubectl rollout status deployment/%SVC% -n %NAMESPACE% --timeout=120s >nul 2>&1
    if %errorlevel% equ 0 (
        echo [32m✓[0m Rollout complete

        REM Get current status
        for /f "tokens=*" %%i in ('kubectl get deployment %SVC% -n %NAMESPACE% -o jsonpath^="{.status.readyReplicas}" 2^>nul') do set READY=%%i
        for /f "tokens=*" %%i in ('kubectl get deployment %SVC% -n %NAMESPACE% -o jsonpath^="{.spec.replicas}" 2^>nul') do set DESIRED=%%i

        echo [34mStatus:[0m !READY!/!DESIRED! ready
    ) else (
        echo [33m⚠[0m Rollout is taking longer than expected
    )
) else (
    echo [31m✗[0m Failed to scale %SVC%
)

echo.
goto :eof

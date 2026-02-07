@echo off
REM Phase IV - Log Viewing Helper Script (Windows)
REM Simplified log viewing for troubleshooting

setlocal enabledelayedexpansion

set NAMESPACE=todo-app
set COMPONENT=%1
set FOLLOW=false
set TAIL_LINES=100
set PREVIOUS=false

REM Parse arguments
:parse_args
if "%1"=="" goto check_component
if "%1"=="-f" (
    set FOLLOW=true
    shift
    goto parse_args
)
if "%1"=="--follow" (
    set FOLLOW=true
    shift
    goto parse_args
)
if "%1"=="-n" (
    set TAIL_LINES=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--lines" (
    set TAIL_LINES=%2
    shift
    shift
    goto parse_args
)
if "%1"=="-p" (
    set PREVIOUS=true
    shift
    goto parse_args
)
if "%1"=="--previous" (
    set PREVIOUS=true
    shift
    goto parse_args
)
if "%1"=="-h" goto usage
if "%1"=="--help" goto usage

set COMPONENT=%1
shift
goto parse_args

:check_component
if "%COMPONENT%"=="" goto usage
goto main

:usage
echo Usage: %0 [options] ^<component^>
echo.
echo Components:
echo   frontend   - View frontend logs
echo   backend    - View backend logs
echo   database   - View database logs
echo   all        - View logs from all components
echo.
echo Options:
echo   -f, --follow       Follow log output (like tail -f)
echo   -n, --lines NUM    Number of lines to show (default: 100)
echo   -p, --previous     Show logs from previous container (if crashed)
echo   -h, --help         Show this help message
echo.
echo Examples:
echo   %0 backend                    # Show last 100 lines of backend logs
echo   %0 -f frontend                # Follow frontend logs
echo   %0 -n 500 backend             # Show last 500 lines
echo   %0 -p backend                 # Show logs from crashed container
echo   %0 all                        # Show logs from all components
echo.
exit /b 1

:main

REM Check if namespace exists
kubectl get namespace %NAMESPACE% >nul 2>&1
if %errorlevel% neq 0 (
    echo [31mError: Namespace '%NAMESPACE%' not found[0m
    echo Please deploy the application first
    exit /b 1
)

echo =========================================
echo Log Viewer - Todo App
echo =========================================
echo.

REM View logs based on component
if "%COMPONENT%"=="frontend" goto view_single
if "%COMPONENT%"=="backend" goto view_single
if "%COMPONENT%"=="database" goto view_single
if "%COMPONENT%"=="all" goto view_all
goto unknown_component

:view_single
echo [34mComponent:[0m %COMPONENT%
echo [34mNamespace:[0m %NAMESPACE%
echo.

REM Check if deployment exists
kubectl get deployment %COMPONENT% -n %NAMESPACE% >nul 2>&1
if %errorlevel% neq 0 (
    echo [31mError: Deployment '%COMPONENT%' not found[0m
    exit /b 1
)

REM Get pod count
for /f "tokens=*" %%i in ('kubectl get pods -n %NAMESPACE% -l component^=%COMPONENT% --no-headers 2^>nul ^| find /c /v ""') do set POD_COUNT=%%i

if "%POD_COUNT%"=="0" (
    echo [31mError: No pods found for component '%COMPONENT%'[0m
    exit /b 1
)

echo [34mPods found:[0m %POD_COUNT%
echo.

REM Build kubectl logs command
set CMD=kubectl logs

if "%FOLLOW%"=="true" set CMD=!CMD! -f
if "%PREVIOUS%"=="true" set CMD=!CMD! --previous

set CMD=!CMD! --tail=%TAIL_LINES%
set CMD=!CMD! -l component=%COMPONENT%
set CMD=!CMD! -n %NAMESPACE%
set CMD=!CMD! --all-containers=true
set CMD=!CMD! --prefix=true

echo [32mViewing logs...[0m
echo.
echo ---
echo.

REM Execute command
!CMD!

goto end

:view_all
echo [34mViewing logs from all components[0m
echo.

for %%c in (frontend backend database) do (
    echo =========================================
    echo Component: %%c
    echo =========================================
    echo.

    kubectl logs --tail=50 -l component=%%c -n %NAMESPACE% --all-containers=true --prefix=true 2>nul || echo No logs available for %%c

    echo.
    echo.
)

goto end

:unknown_component
echo [31mError: Unknown component '%COMPONENT%'[0m
goto usage

:end
echo.
echo [32m✓ Log viewing complete[0m
echo.
echo Useful commands:
echo   - Follow logs: %0 -f %COMPONENT%
echo   - More lines: %0 -n 500 %COMPONENT%
echo   - Previous container: %0 -p %COMPONENT%
echo   - All components: %0 all

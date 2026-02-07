@echo off
REM Phase IV - Cleanup Script (Windows)
REM Removes all Kubernetes resources and optionally Minikube cluster

setlocal enabledelayedexpansion

REM Function to display usage
if "%1"=="-h" goto usage
if "%1"=="--help" goto usage
if "%1"=="/?" goto usage
if "%1"=="" goto usage

REM Configuration
set RELEASE_NAME=todo-app
set NAMESPACE=todo-app
set REMOVE_HELM=false
set REMOVE_NAMESPACE=false
set REMOVE_MINIKUBE=false
set REMOVE_IMAGES=false
set REMOVE_ALL=false

REM Parse command-line arguments
:parse_args
if "%1"=="" goto after_parse

if "%1"=="--all" (
    set REMOVE_ALL=true
    set REMOVE_HELM=true
    set REMOVE_NAMESPACE=true
    set REMOVE_MINIKUBE=true
    set REMOVE_IMAGES=true
    shift
    goto parse_args
)
if "%1"=="--helm" (
    set REMOVE_HELM=true
    shift
    goto parse_args
)
if "%1"=="--namespace" (
    set REMOVE_NAMESPACE=true
    shift
    goto parse_args
)
if "%1"=="--minikube" (
    set REMOVE_MINIKUBE=true
    shift
    goto parse_args
)
if "%1"=="--images" (
    set REMOVE_IMAGES=true
    shift
    goto parse_args
)
if "%1"=="--keep-minikube" (
    set REMOVE_HELM=true
    set REMOVE_NAMESPACE=true
    shift
    goto parse_args
)

echo [31mError: Unknown option: %1[0m
goto usage

:after_parse

echo =========================================
echo Phase IV - Cleanup
echo =========================================
echo.

REM Confirmation prompt
echo [33m⚠️  WARNING: This will remove the following:[0m
echo.
if "!REMOVE_HELM!"=="true" (
    echo   - Helm release: %RELEASE_NAME%
)
if "!REMOVE_NAMESPACE!"=="true" (
    echo   - Namespace: %NAMESPACE% (all resources)
)
if "!REMOVE_MINIKUBE!"=="true" (
    echo   - Minikube cluster (complete deletion)
)
if "!REMOVE_IMAGES!"=="true" (
    echo   - Docker images (todo-frontend, todo-backend)
)
echo.
set /p "response=Are you sure you want to continue? (y/N): "

if /i not "!response!"=="y" (
    echo Cleanup cancelled
    exit /b 0
)

echo.

REM Remove Helm release
if "!REMOVE_HELM!"=="true" (
    echo =========================================
    echo Removing Helm Release
    echo =========================================
    echo.

    helm list -n %NAMESPACE% 2>nul | findstr "%RELEASE_NAME%" >nul 2>&1
    if %errorlevel% equ 0 (
        echo Uninstalling Helm release: %RELEASE_NAME%
        helm uninstall %RELEASE_NAME% -n %NAMESPACE%

        if %errorlevel% equ 0 (
            echo [32m✓ Helm release removed[0m
        ) else (
            echo [31m✗ Failed to remove Helm release[0m
        )
    ) else (
        echo [33m⚠ Helm release not found: %RELEASE_NAME%[0m
    )

    echo.
)

REM Remove namespace
if "!REMOVE_NAMESPACE!"=="true" (
    echo =========================================
    echo Removing Namespace
    echo =========================================
    echo.

    kubectl get namespace %NAMESPACE% >nul 2>&1
    if %errorlevel% equ 0 (
        echo Deleting namespace: %NAMESPACE%
        kubectl delete namespace %NAMESPACE%

        if %errorlevel% equ 0 (
            echo [32m✓ Namespace removed[0m
        ) else (
            echo [31m✗ Failed to remove namespace[0m
        )
    ) else (
        echo [33m⚠ Namespace not found: %NAMESPACE%[0m
    )

    echo.
)

REM Remove Docker images
if "!REMOVE_IMAGES!"=="true" (
    echo =========================================
    echo Removing Docker Images
    echo =========================================
    echo.

    REM Remove frontend images
    docker images | findstr "todo-frontend" >nul 2>&1
    if %errorlevel% equ 0 (
        echo Removing frontend images...
        for /f "tokens=3" %%i in ('docker images ^| findstr "todo-frontend"') do docker rmi %%i -f 2>nul
        echo [32m✓ Frontend images removed[0m
    ) else (
        echo [33m⚠ No frontend images found[0m
    )

    REM Remove backend images
    docker images | findstr "todo-backend" >nul 2>&1
    if %errorlevel% equ 0 (
        echo Removing backend images...
        for /f "tokens=3" %%i in ('docker images ^| findstr "todo-backend"') do docker rmi %%i -f 2>nul
        echo [32m✓ Backend images removed[0m
    ) else (
        echo [33m⚠ No backend images found[0m
    )

    echo.
)

REM Stop and delete Minikube
if "!REMOVE_MINIKUBE!"=="true" (
    echo =========================================
    echo Removing Minikube Cluster
    echo =========================================
    echo.

    minikube status >nul 2>&1
    if %errorlevel% equ 0 (
        echo Stopping Minikube...
        minikube stop

        echo Deleting Minikube cluster...
        minikube delete

        if %errorlevel% equ 0 (
            echo [32m✓ Minikube cluster removed[0m
        ) else (
            echo [31m✗ Failed to remove Minikube cluster[0m
        )
    ) else (
        echo [33m⚠ Minikube not running[0m
    )

    echo.
)

REM Summary
echo =========================================
echo Cleanup Summary
echo =========================================
echo.

if "!REMOVE_ALL!"=="true" (
    echo [32m✓ Complete cleanup finished[0m
    echo.
    echo All resources have been removed:
    echo   - Helm release
    echo   - Namespace and all resources
    echo   - Docker images
    echo   - Minikube cluster
) else (
    echo [32m✓ Cleanup finished[0m
    echo.
    echo Removed:
    if "!REMOVE_HELM!"=="true" (
        echo   - Helm release
    )
    if "!REMOVE_NAMESPACE!"=="true" (
        echo   - Namespace and all resources
    )
    if "!REMOVE_IMAGES!"=="true" (
        echo   - Docker images
    )
    if "!REMOVE_MINIKUBE!"=="true" (
        echo   - Minikube cluster
    )
)

echo.

REM Next steps
if "!REMOVE_MINIKUBE!"=="false" (
    echo Next steps:
    echo   - To redeploy: scripts\deploy.bat
    echo   - To remove Minikube: %0 --minikube
) else (
    echo Next steps:
    echo   - To start fresh: scripts\setup-minikube.bat
    echo   - Then deploy: scripts\deploy.bat
)

echo.
echo [32m✓ Cleanup complete![0m
goto :eof

:usage
echo Usage: %0 [options]
echo.
echo Options:
echo   --all                 Remove everything (Helm release, namespace, Minikube)
echo   --helm                Remove Helm release only
echo   --namespace           Remove namespace (includes all resources)
echo   --minikube            Stop and delete Minikube cluster
echo   --images              Remove Docker images
echo   --keep-minikube       Remove resources but keep Minikube running
echo   -h, --help, /?        Show this help message
echo.
echo Examples:
echo   %0 --all                      # Remove everything
echo   %0 --helm                     # Remove Helm release only
echo   %0 --namespace                # Remove namespace and all resources
echo   %0 --keep-minikube            # Remove resources but keep Minikube
echo   %0 --helm --images            # Remove Helm release and images
echo.
exit /b 0

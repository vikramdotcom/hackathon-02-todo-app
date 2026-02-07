@echo off
REM Phase IV - Helm Deployment Script (Windows)
REM Deploys the Todo App using Helm chart with configuration profile support

setlocal enabledelayedexpansion

REM Function to display usage
if "%1"=="-h" goto usage
if "%1"=="--help" goto usage
if "%1"=="/?" goto usage

REM Parse command-line arguments
set VALUES_FILE=
set PROFILE=
set RELEASE_NAME=todo-app
set NAMESPACE=todo-app
set CHART_PATH=helm\todo-app

:parse_args
if "%1"=="" goto after_parse

if "%1"=="-f" (
    set VALUES_FILE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--values-file" (
    set VALUES_FILE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="-p" (
    set PROFILE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--profile" (
    set PROFILE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="-n" (
    set NAMESPACE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--namespace" (
    set NAMESPACE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="-r" (
    set RELEASE_NAME=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--release" (
    set RELEASE_NAME=%2
    shift
    shift
    goto parse_args
)

echo [31mError: Unknown option: %1[0m
goto usage

:after_parse

REM Resolve profile to values file
if not "!PROFILE!"=="" (
    if /i "!PROFILE!"=="dev" (
        set VALUES_FILE=!CHART_PATH!\values-dev.yaml
    ) else if /i "!PROFILE!"=="test" (
        set VALUES_FILE=!CHART_PATH!\values-test.yaml
    ) else if /i "!PROFILE!"=="prod" (
        echo [31mError: Production profile not yet implemented[0m
        echo Use a custom values file with -f option
        exit /b 1
    ) else (
        echo [31mError: Unknown profile: !PROFILE![0m
        echo Available profiles: dev, test
        exit /b 1
    )
)

REM Validate values file if specified
if not "!VALUES_FILE!"=="" (
    if not exist "!VALUES_FILE!" (
        echo [31mError: Values file not found: !VALUES_FILE![0m
        exit /b 1
    )
)

echo =========================================
echo Phase IV - Helm Deployment
echo =========================================
echo.
echo [34mRelease Name:[0m %RELEASE_NAME%
echo [34mNamespace:[0m %NAMESPACE%
if not "!VALUES_FILE!"=="" (
    echo [34mValues File:[0m !VALUES_FILE!
    if not "!PROFILE!"=="" (
        echo [34mProfile:[0m !PROFILE!
    )
) else (
    echo [34mValues File:[0m default (values.yaml)
)
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

REM Check if images exist
echo Checking Docker images...
docker images | findstr "todo-frontend" >nul 2>&1
if %errorlevel% neq 0 (
    echo [31m✗ Frontend image not found[0m
    echo Please build images first: scripts\build-images.bat
    exit /b 1
)

docker images | findstr "todo-backend" >nul 2>&1
if %errorlevel% neq 0 (
    echo [31m✗ Backend image not found[0m
    echo Please build images first: scripts\build-images.bat
    exit /b 1
)

echo [32m✓ Docker images found[0m
echo.

REM Check if Helm is installed
helm version >nul 2>&1
if %errorlevel% neq 0 (
    echo [31m✗ Helm is not installed[0m
    echo Please install Helm: https://helm.sh/docs/intro/install/
    exit /b 1
)

echo [32m✓ Helm is installed[0m
echo.

REM Lint the chart
echo Linting Helm chart...
helm lint %CHART_PATH%
if %errorlevel% equ 0 (
    echo [32m✓ Chart lint passed[0m
) else (
    echo [31m✗ Chart lint failed[0m
    exit /b 1
)
echo.

REM Check if release already exists
helm list -n %NAMESPACE% | findstr "%RELEASE_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [33m⚠ Release '%RELEASE_NAME%' already exists[0m
    echo.
    set /p UPGRADE="Do you want to upgrade the existing release? (y/N): "

    if /i "!UPGRADE!"=="y" (
        echo Upgrading release...

        if not "!VALUES_FILE!"=="" (
            helm upgrade %RELEASE_NAME% %CHART_PATH% --namespace %NAMESPACE% --values !VALUES_FILE! --wait --timeout 5m
        ) else (
            helm upgrade %RELEASE_NAME% %CHART_PATH% --namespace %NAMESPACE% --wait --timeout 5m
        )

        echo.
        echo [32m✓ Release upgraded successfully[0m
    ) else (
        echo Upgrade cancelled
        exit /b 0
    )
) else (
    echo Installing release...

    if not "!VALUES_FILE!"=="" (
        helm install %RELEASE_NAME% %CHART_PATH% --namespace %NAMESPACE% --create-namespace --values !VALUES_FILE! --wait --timeout 5m
    ) else (
        helm install %RELEASE_NAME% %CHART_PATH% --namespace %NAMESPACE% --create-namespace --wait --timeout 5m
    )

    echo.
    echo [32m✓ Release installed successfully[0m
)

echo.

REM Get deployment status
echo =========================================
echo Deployment Status
echo =========================================
echo.

helm status %RELEASE_NAME% -n %NAMESPACE%

echo.
echo =========================================
echo Resources
echo =========================================
echo.

kubectl get all -n %NAMESPACE%

echo.
echo =========================================
echo Access Information
echo =========================================
echo.

for /f "tokens=*" %%i in ('minikube ip') do set MINIKUBE_IP=%%i
echo [34mApplication URL:[0m http://todo.local
echo [34mMinikube IP:[0m %MINIKUBE_IP%
echo.
echo Make sure you have added the following to your hosts file:
echo [33m%MINIKUBE_IP% todo.local[0m
echo.
echo On Windows (Run as Administrator):
echo   notepad C:\Windows\System32\drivers\etc\hosts
echo.
echo [32m✓ Deployment complete![0m
echo.
echo Useful commands:
echo   - View release: helm list -n %NAMESPACE%
echo   - View values: helm get values %RELEASE_NAME% -n %NAMESPACE%
echo   - Upgrade: helm upgrade %RELEASE_NAME% %CHART_PATH% -n %NAMESPACE%
echo   - Uninstall: helm uninstall %RELEASE_NAME% -n %NAMESPACE%
goto :eof

:usage
echo Usage: %0 [options]
echo.
echo Options:
echo   -f, --values-file FILE    Path to custom values file
echo   -p, --profile PROFILE     Use predefined profile (dev, test, prod)
echo   -n, --namespace NAME      Kubernetes namespace (default: todo-app)
echo   -r, --release NAME        Helm release name (default: todo-app)
echo   -h, --help, /?            Show this help message
echo.
echo Examples:
echo   %0                                    # Deploy with default values
echo   %0 -p dev                             # Deploy with development profile
echo   %0 -p test                            # Deploy with testing profile
echo   %0 -f custom-values.yaml              # Deploy with custom values file
echo   %0 -p dev -n todo-dev                 # Deploy dev profile to custom namespace
echo.
echo Available profiles:
echo   dev   - Development profile (minimal resources, single replica)
echo   test  - Testing profile (production-like, multiple replicas)
echo.
exit /b 0

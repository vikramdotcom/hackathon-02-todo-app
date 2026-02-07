@echo off
REM Phase IV - Deployment Script (Windows)
REM Deploys the Todo App to Kubernetes cluster

setlocal enabledelayedexpansion

echo =========================================
echo Phase IV - Deploying Todo App
echo =========================================
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

REM Create namespace
echo Creating namespace...
kubectl apply -f k8s\namespace.yaml
echo [32m✓ Namespace created[0m
echo.

REM Check if secrets exist
echo Checking secrets...
kubectl get secret todo-app-secrets -n todo-app >nul 2>&1
if %errorlevel% neq 0 (
    echo [33m⚠ Secrets not found[0m
    echo.
    echo Creating secrets from example file...

    if not exist k8s\secret.yaml (
        echo Copying secret.yaml.example to secret.yaml...
        copy k8s\secret.yaml.example k8s\secret.yaml
        echo.
        echo [33m⚠ Using default secrets[0m
        echo Please update k8s\secret.yaml with your actual secrets before production use
        echo.
    )

    kubectl apply -f k8s\secret.yaml
    echo [32m✓ Secrets created[0m
) else (
    echo [32m✓ Secrets already exist[0m
)
echo.

REM Apply ConfigMap
echo Applying ConfigMap...
kubectl apply -f k8s\configmap.yaml
echo [32m✓ ConfigMap applied[0m
echo.

REM Apply PersistentVolumeClaim
echo Creating PersistentVolumeClaim...
kubectl apply -f k8s\postgres-pvc.yaml
echo [32m✓ PVC created[0m
echo.

REM Deploy database
echo Deploying database...
kubectl apply -f k8s\database-deployment.yaml
kubectl apply -f k8s\database-service.yaml
echo [32m✓ Database deployed[0m
echo.

REM Wait for database to be ready
echo Waiting for database to be ready...
kubectl wait --for=condition=ready pod -l component=database -n todo-app --timeout=120s
echo [32m✓ Database is ready[0m
echo.

REM Deploy backend
echo Deploying backend...
kubectl apply -f k8s\backend-deployment.yaml
kubectl apply -f k8s\backend-service.yaml
echo [32m✓ Backend deployed[0m
echo.

REM Wait for backend to be ready
echo Waiting for backend to be ready...
kubectl wait --for=condition=ready pod -l component=backend -n todo-app --timeout=120s
echo [32m✓ Backend is ready[0m
echo.

REM Deploy frontend
echo Deploying frontend...
kubectl apply -f k8s\frontend-deployment.yaml
kubectl apply -f k8s\frontend-service.yaml
echo [32m✓ Frontend deployed[0m
echo.

REM Wait for frontend to be ready
echo Waiting for frontend to be ready...
kubectl wait --for=condition=ready pod -l component=frontend -n todo-app --timeout=120s
echo [32m✓ Frontend is ready[0m
echo.

REM Apply Ingress
echo Applying Ingress...
kubectl apply -f k8s\ingress.yaml
echo [32m✓ Ingress applied[0m
echo.

REM Get deployment status
echo =========================================
echo Deployment Status
echo =========================================
echo.

kubectl get all -n todo-app

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
echo   - View logs: kubectl logs -f deployment/backend -n todo-app
echo   - Check status: kubectl get pods -n todo-app
echo   - Scale replicas: kubectl scale deployment/backend --replicas=3 -n todo-app

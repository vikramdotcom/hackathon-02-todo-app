# Phase IV - Setup Guide

Complete setup guide for deploying the Todo App to a local Kubernetes cluster.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Platform-Specific Setup](#platform-specific-setup)
3. [Environment Configuration](#environment-configuration)
4. [Minikube Setup](#minikube-setup)
5. [Docker Configuration](#docker-configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Docker | 24.0+ | Container runtime |
| Minikube | 1.30+ | Local Kubernetes cluster |
| kubectl | 1.28+ | Kubernetes CLI |
| Helm | 3.12+ | Package manager |
| Git | 2.30+ | Version control |

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 8GB | 16GB |
| CPU | 4 cores | 6+ cores |
| Disk Space | 20GB free | 30GB+ free |
| OS | Windows 10+, macOS 11+, Ubuntu 20.04+ | Latest stable |

---

## Platform-Specific Setup

### Windows 10/11

#### 1. Install Docker Desktop

1. Download from: https://www.docker.com/products/docker-desktop
2. Run installer
3. Enable WSL 2 backend (recommended)
4. Start Docker Desktop
5. Verify: `docker --version`

#### 2. Install Minikube

**Option A: Using Chocolatey**
```powershell
choco install minikube
```

**Option B: Manual Installation**
```powershell
# Download installer
Invoke-WebRequest -Uri https://github.com/kubernetes/minikube/releases/latest/download/minikube-installer.exe -OutFile minikube-installer.exe

# Run installer
.\minikube-installer.exe

# Verify
minikube version
```

#### 3. Install kubectl

**Option A: Using Chocolatey**
```powershell
choco install kubernetes-cli
```

**Option B: Manual Installation**
```powershell
# Download kubectl
curl.exe -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"

# Add to PATH
# Move kubectl.exe to C:\Program Files\kubectl\
# Add C:\Program Files\kubectl\ to PATH

# Verify
kubectl version --client
```

#### 4. Install Helm

**Option A: Using Chocolatey**
```powershell
choco install kubernetes-helm
```

**Option B: Manual Installation**
```powershell
# Download from: https://github.com/helm/helm/releases
# Extract and add to PATH

# Verify
helm version
```

#### 5. Configure Hosts File

Run as Administrator:
```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

Add (replace with your Minikube IP):
```
192.168.49.2 todo.local
```

---

### macOS

#### 1. Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Docker Desktop

```bash
brew install --cask docker
```

Or download from: https://www.docker.com/products/docker-desktop

Start Docker Desktop and verify:
```bash
docker --version
```

#### 3. Install Minikube

```bash
brew install minikube
minikube version
```

#### 4. Install kubectl

```bash
brew install kubectl
kubectl version --client
```

#### 5. Install Helm

```bash
brew install helm
helm version
```

#### 6. Configure Hosts File

```bash
sudo nano /etc/hosts
```

Add (replace with your Minikube IP):
```
192.168.49.2 todo.local
```

---

### Linux (Ubuntu/Debian)

#### 1. Install Docker

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
```

#### 2. Install Minikube

```bash
# Download Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify
minikube version
```

#### 3. Install kubectl

```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify
kubectl version --client
```

#### 4. Install Helm

```bash
# Download Helm install script
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
helm version
```

#### 5. Configure Hosts File

```bash
sudo nano /etc/hosts
```

Add (replace with your Minikube IP):
```
192.168.49.2 todo.local
```

---

## Environment Configuration

### 1. Clone Repository

```bash
git clone <repository-url>
cd hackathon-02-todo-app/phase-4-kubernetes
```

### 2. Configure Environment Variables

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```bash
# Backend Configuration
DATABASE_URL=postgresql://postgres:postgres@database:5432/todo_db
SECRET_KEY=your-secret-key-here-change-in-production
OPENAI_API_KEY=sk-your-openai-api-key  # Optional

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://todo.local/api

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=todo_db

# Kubernetes Configuration
NAMESPACE=todo-app
IMAGE_TAG=latest
FRONTEND_REPLICAS=2
BACKEND_REPLICAS=2
```

### 3. Generate Secrets

For production, generate secure secrets:

```bash
# Generate SECRET_KEY
openssl rand -base64 32

# Generate POSTGRES_PASSWORD
openssl rand -base64 32
```

Update `k8s/secret.yaml` or use Helm values:
```bash
helm install todo-app ./helm/todo-app -n todo-app \
  --set secrets.postgresPassword="$(openssl rand -base64 32)" \
  --set secrets.secretKey="$(openssl rand -base64 32)"
```

---

## Minikube Setup

### 1. Start Minikube

**Linux/macOS:**
```bash
./scripts/setup-minikube.sh
```

**Windows:**
```cmd
scripts\setup-minikube.bat
```

**Manual Start:**
```bash
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker
```

### 2. Enable Required Addons

```bash
# Ingress controller
minikube addons enable ingress

# Metrics server
minikube addons enable metrics-server
```

### 3. Verify Cluster

```bash
# Check status
minikube status

# Get cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes

# Get Minikube IP
minikube ip
```

### 4. Update Hosts File

Add Minikube IP to hosts file:

**Linux/macOS:**
```bash
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
```

**Windows (Run as Administrator):**
```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "$(minikube ip) todo.local"
```

---

## Docker Configuration

### 1. Configure Docker to Use Minikube

This ensures images are built directly in Minikube's Docker daemon:

**Linux/macOS:**
```bash
eval $(minikube docker-env)
```

**Windows (PowerShell):**
```powershell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

**Windows (CMD):**
```cmd
@FOR /f "tokens=*" %i IN ('minikube -p minikube docker-env --shell cmd') DO @%i
```

### 2. Verify Docker Configuration

```bash
# Should show Minikube's Docker daemon
docker info | grep -i "Name:"

# Should show Minikube images
docker images | grep k8s
```

### 3. Build Images

**Linux/macOS:**
```bash
./scripts/build-images.sh
```

**Windows:**
```cmd
scripts\build-images.bat
```

**With Version Tag:**
```bash
./scripts/build-images.sh v1.0.0
```

---

## Verification

### 1. Validate Prerequisites

**Linux/macOS:**
```bash
./scripts/validate-prerequisites.sh
```

**Windows:**
```cmd
scripts\validate-prerequisites.bat
```

### 2. Verify Minikube

```bash
# Check Minikube status
minikube status

# Check addons
minikube addons list

# Check cluster
kubectl cluster-info
kubectl get nodes
```

### 3. Verify Docker Images

```bash
# List images
docker images | grep todo-

# Should see:
# todo-frontend   latest
# todo-backend    latest
```

### 4. Verify Hosts File

**Linux/macOS:**
```bash
cat /etc/hosts | grep todo.local
```

**Windows:**
```cmd
type C:\Windows\System32\drivers\etc\hosts | findstr todo.local
```

Should show:
```
<MINIKUBE_IP> todo.local
```

---

## Troubleshooting

### Minikube Won't Start

**Issue**: Minikube fails to start

**Solutions**:
1. Check Docker is running:
   ```bash
   docker info
   ```

2. Delete and recreate cluster:
   ```bash
   minikube delete
   minikube start
   ```

3. Try different driver:
   ```bash
   minikube start --driver=virtualbox
   ```

4. Check logs:
   ```bash
   minikube logs
   ```

### Docker Daemon Not Accessible

**Issue**: Cannot connect to Docker daemon

**Solutions**:
1. Start Docker Desktop

2. Check Docker service (Linux):
   ```bash
   sudo systemctl status docker
   sudo systemctl start docker
   ```

3. Add user to docker group (Linux):
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

### Insufficient Resources

**Issue**: Minikube fails due to resource constraints

**Solutions**:
1. Close unnecessary applications

2. Reduce Minikube resources:
   ```bash
   minikube start --cpus=2 --memory=4096
   ```

3. Increase system resources (VM settings)

### Hosts File Not Updating

**Issue**: Cannot access todo.local

**Solutions**:
1. Verify hosts file entry:
   ```bash
   cat /etc/hosts | grep todo.local  # Linux/macOS
   type C:\Windows\System32\drivers\etc\hosts | findstr todo.local  # Windows
   ```

2. Ensure correct IP:
   ```bash
   minikube ip
   ```

3. Flush DNS cache:
   ```bash
   # macOS
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

   # Windows
   ipconfig /flushdns

   # Linux
   sudo systemd-resolve --flush-caches
   ```

4. Use port forwarding as alternative:
   ```bash
   kubectl port-forward service/frontend 3000:3000 -n todo-app
   # Access: http://localhost:3000
   ```

### Images Not Found

**Issue**: ImagePullBackOff or ErrImagePull

**Solutions**:
1. Ensure using Minikube's Docker daemon:
   ```bash
   eval $(minikube docker-env)
   ```

2. Rebuild images:
   ```bash
   ./scripts/build-images.sh
   ```

3. Verify images exist:
   ```bash
   docker images | grep todo-
   ```

4. Check image pull policy in deployment:
   ```yaml
   imagePullPolicy: Never  # For local images
   ```

---

## Next Steps

After completing setup:

1. **Deploy Application**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
2. **Verify Deployment**: Run verification scripts
3. **Access Application**: Visit http://todo.local
4. **Monitor Resources**: Use kubectl top commands

---

## Environment Profiles

### Development Profile

Use `values-dev.yaml` for local development:
```bash
helm install todo-app ./helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml
```

Features:
- Single replica for each service
- Reduced resource limits
- Debug logging enabled
- Smaller database storage

### Testing Profile

Use `values-test.yaml` for testing:
```bash
helm install todo-app ./helm/todo-app -n todo-app -f helm/todo-app/values-test.yaml
```

Features:
- Multiple replicas for HA testing
- Standard resource limits
- Info logging
- Pod disruption budgets enabled

---

## Additional Resources

- **Quick Reference**: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Helm Chart**: [helm/todo-app/README.md](./helm/todo-app/README.md)

---

**Last Updated**: February 7, 2026

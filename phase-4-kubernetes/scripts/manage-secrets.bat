@echo off
REM Phase IV - Secret Management Helper Script (Windows)
REM Simplifies secret creation, viewing, updating, and deletion

setlocal enabledelayedexpansion

set NAMESPACE=todo-app
set SECRET_NAME=todo-app-secrets

REM Parse command
set COMMAND=%1

if "%COMMAND%"=="" goto usage
if "%COMMAND%"=="-h" goto usage
if "%COMMAND%"=="--help" goto usage

REM Execute command
if "%COMMAND%"=="create" goto cmd_create
if "%COMMAND%"=="update" goto cmd_update
if "%COMMAND%"=="view" goto cmd_view
if "%COMMAND%"=="delete" goto cmd_delete
if "%COMMAND%"=="backup" goto cmd_backup
if "%COMMAND%"=="restore" goto cmd_restore
if "%COMMAND%"=="rotate" goto cmd_rotate

echo [31mError: Unknown command: %COMMAND%[0m
goto usage

:usage
echo Usage: %0 ^<command^>
echo.
echo Commands:
echo   create    - Create new secrets (interactive)
echo   update    - Update existing secrets (interactive)
echo   view      - View current secrets (decoded)
echo   delete    - Delete secrets
echo   backup    - Backup secrets to file
echo   restore   - Restore secrets from backup file
echo   rotate    - Rotate specific secret
echo.
echo Examples:
echo   %0 create                    # Create new secrets
echo   %0 update                    # Update existing secrets
echo   %0 view                      # View current secrets
echo   %0 backup secrets.backup     # Backup to file
echo   %0 restore secrets.backup    # Restore from file
echo   %0 rotate SECRET_KEY         # Rotate specific secret
echo.
exit /b 1

:check_namespace
kubectl get namespace %NAMESPACE% >nul 2>&1
if %errorlevel% neq 0 (
    echo [31mError: Namespace '%NAMESPACE%' not found[0m
    echo Please deploy the application first
    exit /b 1
)
exit /b 0

:secret_exists
kubectl get secret %SECRET_NAME% -n %NAMESPACE% >nul 2>&1
exit /b %errorlevel%

:generate_secret_key
REM Generate random 32-byte hex string
for /f %%i in ('powershell -Command "[System.BitConverter]::ToString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32)).Replace('-','')"') do set SECRET_KEY_GEN=%%i
exit /b 0

:cmd_create
call :check_namespace
if %errorlevel% neq 0 exit /b 1

call :secret_exists
if %errorlevel% equ 0 (
    echo [33mWarning: Secret '%SECRET_NAME%' already exists[0m
    set /p "response=Do you want to replace it? (y/N): "
    if /i not "!response!"=="y" (
        echo Aborted
        exit /b 0
    )
)

echo =========================================
echo Create Secrets - Todo App
echo =========================================
echo.
echo This will create secrets for the Todo App.
echo Press Ctrl+C to cancel at any time.
echo.

REM Prompt for DATABASE_URL
echo [34mDATABASE_URL[0m
echo   Description: PostgreSQL connection string
set /p "DATABASE_URL=  Value (or press Enter for default): "
if "!DATABASE_URL!"=="" (
    set DATABASE_URL=postgresql://postgres:password@database:5432/todo_db
    echo [33mUsing default: !DATABASE_URL![0m
)

REM Prompt for SECRET_KEY
echo.
echo [34mSECRET_KEY[0m
echo   Description: Application secret key for JWT/sessions
set /p "SECRET_KEY=  Value (or press Enter to generate): "
if "!SECRET_KEY!"=="" (
    call :generate_secret_key
    set SECRET_KEY=!SECRET_KEY_GEN!
    echo [33mGenerated random secret key[0m
)

REM Prompt for OPENAI_API_KEY
echo.
echo [34mOPENAI_API_KEY[0m
echo   Description: OpenAI API key for chatbot (optional)
set /p "OPENAI_API_KEY=  Value (or press Enter to skip): "

REM Create secret
echo.
echo Creating secret...

kubectl create secret generic %SECRET_NAME% -n %NAMESPACE% --from-literal=DATABASE_URL="!DATABASE_URL!" --from-literal=SECRET_KEY="!SECRET_KEY!" --from-literal=OPENAI_API_KEY="!OPENAI_API_KEY!" --dry-run=client -o yaml | kubectl apply -f -

if %errorlevel% equ 0 (
    echo [32m✓ Secret created successfully[0m
    echo.
    echo Next steps:
    echo   1. Restart pods to pick up new secrets:
    echo      kubectl rollout restart deployment/backend -n %NAMESPACE%
    echo   2. Verify application functionality
) else (
    echo [31m✗ Failed to create secret[0m
    exit /b 1
)
exit /b 0

:cmd_update
call :check_namespace
if %errorlevel% neq 0 exit /b 1

call :secret_exists
if %errorlevel% neq 0 (
    echo [31mError: Secret '%SECRET_NAME%' not found[0m
    echo Use '%0 create' to create secrets first
    exit /b 1
)

echo =========================================
echo Update Secrets - Todo App
echo =========================================
echo.
echo This will update existing secrets.
echo Press Enter to keep current value.
echo Press Ctrl+C to cancel at any time.
echo.

REM Get current values
for /f "delims=" %%i in ('kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o jsonpath^="{.data.DATABASE_URL}" 2^>nul') do set CURRENT_DATABASE_URL_B64=%%i
for /f "delims=" %%i in ('powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%CURRENT_DATABASE_URL_B64%'))"') do set CURRENT_DATABASE_URL=%%i

for /f "delims=" %%i in ('kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o jsonpath^="{.data.SECRET_KEY}" 2^>nul') do set CURRENT_SECRET_KEY_B64=%%i
for /f "delims=" %%i in ('powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%CURRENT_SECRET_KEY_B64%'))"') do set CURRENT_SECRET_KEY=%%i

for /f "delims=" %%i in ('kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o jsonpath^="{.data.OPENAI_API_KEY}" 2^>nul') do set CURRENT_OPENAI_API_KEY_B64=%%i
for /f "delims=" %%i in ('powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%CURRENT_OPENAI_API_KEY_B64%'))"') do set CURRENT_OPENAI_API_KEY=%%i

REM Prompt for DATABASE_URL
echo [34mDATABASE_URL[0m
echo   Description: PostgreSQL connection string
echo   Current value: !CURRENT_DATABASE_URL:~0,20!... (hidden)
set /p "NEW_DATABASE_URL=  New value (or press Enter to keep current): "
if "!NEW_DATABASE_URL!"=="" (
    set DATABASE_URL=!CURRENT_DATABASE_URL!
) else (
    set DATABASE_URL=!NEW_DATABASE_URL!
)

REM Prompt for SECRET_KEY
echo.
echo [34mSECRET_KEY[0m
echo   Description: Application secret key for JWT/sessions
echo   Current value: !CURRENT_SECRET_KEY:~0,20!... (hidden)
set /p "NEW_SECRET_KEY=  New value (or press Enter to keep current): "
if "!NEW_SECRET_KEY!"=="" (
    set SECRET_KEY=!CURRENT_SECRET_KEY!
) else (
    set SECRET_KEY=!NEW_SECRET_KEY!
)

REM Prompt for OPENAI_API_KEY
echo.
echo [34mOPENAI_API_KEY[0m
echo   Description: OpenAI API key for chatbot (optional)
if not "!CURRENT_OPENAI_API_KEY!"=="" (
    echo   Current value: !CURRENT_OPENAI_API_KEY:~0,20!... (hidden)
)
set /p "NEW_OPENAI_API_KEY=  New value (or press Enter to keep current): "
if "!NEW_OPENAI_API_KEY!"=="" (
    set OPENAI_API_KEY=!CURRENT_OPENAI_API_KEY!
) else (
    set OPENAI_API_KEY=!NEW_OPENAI_API_KEY!
)

REM Update secret
echo.
echo Updating secret...

kubectl create secret generic %SECRET_NAME% -n %NAMESPACE% --from-literal=DATABASE_URL="!DATABASE_URL!" --from-literal=SECRET_KEY="!SECRET_KEY!" --from-literal=OPENAI_API_KEY="!OPENAI_API_KEY!" --dry-run=client -o yaml | kubectl apply -f -

if %errorlevel% equ 0 (
    echo [32m✓ Secret updated successfully[0m
    echo.
    echo [33m⚠️  IMPORTANT: Restart pods to pick up changes:[0m
    echo    kubectl rollout restart deployment/backend -n %NAMESPACE%
    echo    kubectl rollout restart deployment/frontend -n %NAMESPACE%
) else (
    echo [31m✗ Failed to update secret[0m
    exit /b 1
)
exit /b 0

:cmd_view
call :check_namespace
if %errorlevel% neq 0 exit /b 1

call :secret_exists
if %errorlevel% neq 0 (
    echo [31mError: Secret '%SECRET_NAME%' not found[0m
    exit /b 1
)

echo =========================================
echo View Secrets - Todo App
echo =========================================
echo.

echo [34mDATABASE_URL:[0m
for /f "delims=" %%i in ('kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o jsonpath^="{.data.DATABASE_URL}" 2^>nul') do set DATABASE_URL_B64=%%i
for /f "delims=" %%i in ('powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%DATABASE_URL_B64%'))"') do echo %%i
echo.

echo [34mSECRET_KEY:[0m
for /f "delims=" %%i in ('kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o jsonpath^="{.data.SECRET_KEY}" 2^>nul') do set SECRET_KEY_B64=%%i
for /f "delims=" %%i in ('powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%SECRET_KEY_B64%'))"') do echo %%i
echo.

echo [34mOPENAI_API_KEY:[0m
for /f "delims=" %%i in ('kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o jsonpath^="{.data.OPENAI_API_KEY}" 2^>nul') do set OPENAI_API_KEY_B64=%%i
if not "!OPENAI_API_KEY_B64!"=="" (
    for /f "delims=" %%i in ('powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%OPENAI_API_KEY_B64%'))"') do echo %%i
) else (
    echo (not set)
)
echo.

echo [33m⚠️  WARNING: These are sensitive values. Do not share![0m
exit /b 0

:cmd_delete
call :check_namespace
if %errorlevel% neq 0 exit /b 1

call :secret_exists
if %errorlevel% neq 0 (
    echo [33mSecret '%SECRET_NAME%' not found[0m
    exit /b 0
)

echo [33mWarning: This will delete all secrets for the Todo App[0m
set /p "response=Are you sure? (y/N): "
if /i not "!response!"=="y" (
    echo Aborted
    exit /b 0
)

kubectl delete secret %SECRET_NAME% -n %NAMESPACE%

if %errorlevel% equ 0 (
    echo [32m✓ Secret deleted successfully[0m
) else (
    echo [31m✗ Failed to delete secret[0m
    exit /b 1
)
exit /b 0

:cmd_backup
call :check_namespace
if %errorlevel% neq 0 exit /b 1

call :secret_exists
if %errorlevel% neq 0 (
    echo [31mError: Secret '%SECRET_NAME%' not found[0m
    exit /b 1
)

set BACKUP_FILE=%2
if "!BACKUP_FILE!"=="" (
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATE=%%c%%a%%b
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME=%%a%%b
    set BACKUP_FILE=secrets-backup-!DATE!-!TIME!.yaml
)

echo Backing up secrets to: !BACKUP_FILE!

kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o yaml > "!BACKUP_FILE!"

if %errorlevel% equ 0 (
    echo [32m✓ Secrets backed up successfully[0m
    echo.
    echo [33m⚠️  WARNING: This file contains sensitive data![0m
    echo    - Store it securely
    echo    - Do not commit to version control
    echo    - Delete after use
) else (
    echo [31m✗ Failed to backup secrets[0m
    exit /b 1
)
exit /b 0

:cmd_restore
call :check_namespace
if %errorlevel% neq 0 exit /b 1

set BACKUP_FILE=%2

if "!BACKUP_FILE!"=="" (
    echo [31mError: Backup file not specified[0m
    echo Usage: %0 restore ^<backup-file^>
    exit /b 1
)

if not exist "!BACKUP_FILE!" (
    echo [31mError: Backup file not found: !BACKUP_FILE![0m
    exit /b 1
)

echo Restoring secrets from: !BACKUP_FILE!

call :secret_exists
if %errorlevel% equ 0 (
    echo [33mWarning: This will replace existing secrets[0m
    set /p "response=Continue? (y/N): "
    if /i not "!response!"=="y" (
        echo Aborted
        exit /b 0
    )
)

kubectl apply -f "!BACKUP_FILE!"

if %errorlevel% equ 0 (
    echo [32m✓ Secrets restored successfully[0m
    echo.
    echo Restart pods to pick up restored secrets:
    echo   kubectl rollout restart deployment/backend -n %NAMESPACE%
) else (
    echo [31m✗ Failed to restore secrets[0m
    exit /b 1
)
exit /b 0

:cmd_rotate
call :check_namespace
if %errorlevel% neq 0 exit /b 1

call :secret_exists
if %errorlevel% neq 0 (
    echo [31mError: Secret '%SECRET_NAME%' not found[0m
    exit /b 1
)

set KEY_NAME=%2

if "!KEY_NAME!"=="" (
    echo [31mError: Secret key not specified[0m
    echo Usage: %0 rotate ^<key-name^>
    echo.
    echo Available keys:
    echo   - DATABASE_URL
    echo   - SECRET_KEY
    echo   - OPENAI_API_KEY
    exit /b 1
)

echo =========================================
echo Rotate Secret - !KEY_NAME!
echo =========================================
echo.

REM Get current values
for /f "delims=" %%i in ('kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o jsonpath^="{.data.DATABASE_URL}" 2^>nul') do set CURRENT_DATABASE_URL_B64=%%i
for /f "delims=" %%i in ('powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%CURRENT_DATABASE_URL_B64%'))"') do set CURRENT_DATABASE_URL=%%i

for /f "delims=" %%i in ('kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o jsonpath^="{.data.SECRET_KEY}" 2^>nul') do set CURRENT_SECRET_KEY_B64=%%i
for /f "delims=" %%i in ('powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%CURRENT_SECRET_KEY_B64%'))"') do set CURRENT_SECRET_KEY=%%i

for /f "delims=" %%i in ('kubectl get secret %SECRET_NAME% -n %NAMESPACE% -o jsonpath^="{.data.OPENAI_API_KEY}" 2^>nul') do set CURRENT_OPENAI_API_KEY_B64=%%i
for /f "delims=" %%i in ('powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%CURRENT_OPENAI_API_KEY_B64%'))"') do set CURRENT_OPENAI_API_KEY=%%i

if /i "!KEY_NAME!"=="DATABASE_URL" (
    echo [34mDATABASE_URL[0m
    echo   Description: New PostgreSQL connection string
    set /p "NEW_VALUE=  New value: "
    set DATABASE_URL=!NEW_VALUE!
    set SECRET_KEY=!CURRENT_SECRET_KEY!
    set OPENAI_API_KEY=!CURRENT_OPENAI_API_KEY!
) else if /i "!KEY_NAME!"=="SECRET_KEY" (
    echo Generating new secret key...
    call :generate_secret_key
    set DATABASE_URL=!CURRENT_DATABASE_URL!
    set SECRET_KEY=!SECRET_KEY_GEN!
    set OPENAI_API_KEY=!CURRENT_OPENAI_API_KEY!
    echo [32mGenerated: !SECRET_KEY:~0,20!...[0m
) else if /i "!KEY_NAME!"=="OPENAI_API_KEY" (
    echo [34mOPENAI_API_KEY[0m
    echo   Description: New OpenAI API key
    set /p "NEW_VALUE=  New value: "
    set DATABASE_URL=!CURRENT_DATABASE_URL!
    set SECRET_KEY=!CURRENT_SECRET_KEY!
    set OPENAI_API_KEY=!NEW_VALUE!
) else (
    echo [31mError: Unknown secret key: !KEY_NAME![0m
    exit /b 1
)

REM Update secret
echo.
echo Rotating secret...

kubectl create secret generic %SECRET_NAME% -n %NAMESPACE% --from-literal=DATABASE_URL="!DATABASE_URL!" --from-literal=SECRET_KEY="!SECRET_KEY!" --from-literal=OPENAI_API_KEY="!OPENAI_API_KEY!" --dry-run=client -o yaml | kubectl apply -f -

if %errorlevel% equ 0 (
    echo [32m✓ Secret rotated successfully[0m
    echo.
    echo [33m⚠️  IMPORTANT: Restart pods to pick up changes:[0m
    echo    kubectl rollout restart deployment/backend -n %NAMESPACE%

    if /i "!KEY_NAME!"=="SECRET_KEY" (
        echo.
        echo [33m⚠️  NOTE: Rotating SECRET_KEY will invalidate existing sessions[0m
    )
) else (
    echo [31m✗ Failed to rotate secret[0m
    exit /b 1
)
exit /b 0

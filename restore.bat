@echo off
REM LookHub Restore Script for Windows
setlocal enabledelayedexpansion

echo 🔄 Starting LookHub restore process...

REM Configuration
set BACKUP_DIR=.\backups

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker first.
    exit /b 1
)

REM List available backups
echo [INFO] Available backups:
if not exist "%BACKUP_DIR%" (
    echo [ERROR] Backup directory does not exist: %BACKUP_DIR%
    exit /b 1
)

dir /B "%BACKUP_DIR%\*.zip" 2>nul
if errorlevel 1 (
    echo [ERROR] No backup files found in %BACKUP_DIR%
    exit /b 1
)

echo.
set /p BACKUP_FILE="Enter backup filename (without .zip): "
if "%BACKUP_FILE%"=="" (
    echo [ERROR] No backup file specified
    exit /b 1
)

set "BACKUP_PATH=%BACKUP_DIR%\%BACKUP_FILE%.zip"
if not exist "%BACKUP_PATH%" (
    echo [ERROR] Backup file not found: %BACKUP_PATH%
    exit /b 1
)

echo [WARN] This will restore data from: %BACKUP_FILE%.zip
echo [WARN] Current data will be REPLACED!
set /p CONFIRM="Are you sure? (yes/no): "
if /i not "%CONFIRM%"=="yes" (
    echo [INFO] Restore cancelled
    exit /b 0
)

REM Stop application
echo [INFO] Stopping application...
docker-compose -f docker-compose.prod.yaml down
if errorlevel 1 (
    echo [WARN] Failed to stop application with docker-compose, trying direct docker commands
    docker stop lookhub-web lookhub-worker socialmediaposter-worker flower lookhub-nginx 2>nul
)

REM Extract backup
echo [INFO] Extracting backup...
set "EXTRACT_DIR=%BACKUP_DIR%\temp_restore"
if exist "%EXTRACT_DIR%" rmdir /S /Q "%EXTRACT_DIR%"
mkdir "%EXTRACT_DIR%"

powershell -Command "Expand-Archive -Path '%BACKUP_PATH%' -DestinationPath '%EXTRACT_DIR%' -Force"
if errorlevel 1 (
    echo [ERROR] Failed to extract backup
    exit /b 1
)

REM Start database container only
echo [INFO] Starting database container...
docker-compose -f docker-compose.prod.yaml up -d db redis
if errorlevel 1 (
    echo [ERROR] Failed to start database and redis containers
    exit /b 1
)

REM Wait for database to be ready
echo [INFO] Waiting for database to be ready...
timeout /t 30 /nobreak >nul

REM Restore database
echo [INFO] Restoring database...
if exist "%EXTRACT_DIR%\database.sql" (
    docker exec -i lookhub-db psql -U lookhubweb -d lookhub < "%EXTRACT_DIR%\database.sql"
    if errorlevel 1 (
        echo [ERROR] Database restore failed
        exit /b 1
    )
    echo [INFO] ✅ Database restored successfully
) else (
    echo [WARN] No database backup found in archive
)

REM Restore Redis
echo [INFO] Restoring Redis data...
if exist "%EXTRACT_DIR%\redis_dump.rdb" (
    docker cp "%EXTRACT_DIR%\redis_dump.rdb" lookhub-redis:/data/dump.rdb
    if errorlevel 1 (
        echo [WARN] Redis restore failed
    ) else (
        echo [INFO] ✅ Redis data restored successfully
    )
) else (
    echo [WARN] No Redis backup found in archive
)

REM Restore files
echo [INFO] Restoring application files...

REM Restore images
if exist "%EXTRACT_DIR%\images" (
    if exist ".\images" rmdir /S /Q ".\images"
    xcopy /E /I /Y "%EXTRACT_DIR%\images" ".\images"
    if errorlevel 1 (
        echo [WARN] Images restore failed
    ) else (
        echo [INFO] ✅ Images restored successfully
    )
)

REM Restore logs
if exist "%EXTRACT_DIR%\logs" (
    if exist ".\logs" rmdir /S /Q ".\logs"
    xcopy /E /I /Y "%EXTRACT_DIR%\logs" ".\logs"
    if errorlevel 1 (
        echo [WARN] Logs restore failed
    ) else (
        echo [INFO] ✅ Logs restored successfully
    )
)

REM Restore configuration files (optional)
echo [INFO] Configuration files found in backup:"
if exist "%EXTRACT_DIR%\docker-compose.prod.yaml" echo - docker-compose.prod.yaml
if exist "%EXTRACT_DIR%\nginx.prod.conf" echo - nginx.prod.conf
if exist "%EXTRACT_DIR%\LookHubWeb.env" echo - LookHubWeb.env
if exist "%EXTRACT_DIR%\SocialMediaPoster.env" echo - SocialMediaPoster.env

echo [WARN] Configuration files were found in backup.
echo [WARN] Please review them manually before using in production.
set /p RESTORE_CONFIG="Restore configuration files? (yes/no): "
if /i "%RESTORE_CONFIG%"=="yes" (
    if exist "%EXTRACT_DIR%\docker-compose.prod.yaml" copy "%EXTRACT_DIR%\docker-compose.prod.yaml" ".\docker-compose.prod.yaml.backup" >nul 2>&1
    if exist "%EXTRACT_DIR%\nginx.prod.conf" copy "%EXTRACT_DIR%\nginx.prod.conf" ".\nginx.prod.conf.backup" >nul 2>&1
    if exist "%EXTRACT_DIR%\LookHubWeb.env" copy "%EXTRACT_DIR%\LookHubWeb.env" ".\LookHubWeb\.env.backup" >nul 2>&1
    if exist "%EXTRACT_DIR%\SocialMediaPoster.env" copy "%EXTRACT_DIR%\SocialMediaPoster.env" ".\SocialMediaPoster\.env.backup" >nul 2>&1
    echo [INFO] Configuration files backed up with .backup extension
)

REM Cleanup
echo [INFO] Cleaning up temporary files...
rmdir /S /Q "%EXTRACT_DIR%"

REM Start application
echo [INFO] Starting application...
docker-compose -f docker-compose.prod.yaml up -d
if errorlevel 1 (
    echo [ERROR] Failed to start application
    exit /b 1
)

REM Wait for services
echo [INFO] Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check health
echo [INFO] Checking service health...
curl -f http://localhost/health >nul 2>&1
if errorlevel 1 (
    echo [WARN] Health check failed, but services may still be starting
) else (
    echo [INFO] ✅ Application health check passed
)

echo [INFO] 🎉 Restore completed successfully!
echo [INFO] Application should be available at: http://localhost
echo [INFO] Please verify all data was restored correctly

pause


@echo off
REM LookHub Backup Script for Windows
setlocal enabledelayedexpansion

echo 🔄 Starting LookHub backup process...

REM Configuration
set PROJECT_NAME=lookhub
set BACKUP_DIR=.\backups
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "DATE=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"
set "BACKUP_NAME=%PROJECT_NAME%_backup_%DATE%"

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker first.
    exit /b 1
)

REM Check if containers are running
docker ps -q -f name=lookhub-db | findstr . >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Database container is not running. Please start the application first.
    exit /b 1
)

REM Create backup directory
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Create timestamped backup directory
set "FULL_BACKUP_DIR=%BACKUP_DIR%\%BACKUP_NAME%"
mkdir "%FULL_BACKUP_DIR%"

echo [INFO] Creating backup: %BACKUP_NAME%

REM 1. Database backup
echo [INFO] Backing up database...
docker exec lookhub-db pg_dump -U lookhubweb -d lookhub --clean --if-exists --create > "%FULL_BACKUP_DIR%\database.sql"
if errorlevel 1 (
    echo [ERROR] Database backup failed
    exit /b 1
)
echo [INFO] ✅ Database backup completed

REM 2. Redis backup (if needed)
echo [INFO] Backing up Redis data...
docker exec lookhub-redis redis-cli BGSAVE >nul 2>&1
timeout /t 5 /nobreak >nul
docker cp lookhub-redis:/data/dump.rdb "%FULL_BACKUP_DIR%\redis_dump.rdb"
if errorlevel 1 (
    echo [WARN] Redis backup failed or not available
) else (
    echo [INFO] ✅ Redis backup completed
)

REM 3. Application files backup
echo [INFO] Backing up application files...
xcopy /E /I /Y ".\images" "%FULL_BACKUP_DIR%\images"
if errorlevel 1 (
    echo [WARN] Images backup failed
) else (
    echo [INFO] ✅ Images backup completed
)

REM 4. Configuration files backup
echo [INFO] Backing up configuration files...
copy ".\docker-compose.prod.yaml" "%FULL_BACKUP_DIR%\" >nul 2>&1
copy ".\nginx.prod.conf" "%FULL_BACKUP_DIR%\" >nul 2>&1
if exist ".\LookHubWeb\.env" copy ".\LookHubWeb\.env" "%FULL_BACKUP_DIR%\LookHubWeb.env" >nul 2>&1
if exist ".\SocialMediaPoster\.env" copy ".\SocialMediaPoster\.env" "%FULL_BACKUP_DIR%\SocialMediaPoster.env" >nul 2>&1
echo [INFO] ✅ Configuration backup completed

REM 5. Logs backup (if they exist)
if exist ".\logs" (
    echo [INFO] Backing up logs...
    xcopy /E /I /Y ".\logs" "%FULL_BACKUP_DIR%\logs"
    if errorlevel 1 (
        echo [WARN] Logs backup failed
    ) else (
        echo [INFO] ✅ Logs backup completed
    )
)

REM 6. Create backup manifest
echo [INFO] Creating backup manifest...
(
echo Backup created: %DATE%
echo Project: %PROJECT_NAME%
echo.
echo Contents:
echo - database.sql - PostgreSQL database dump
echo - redis_dump.rdb - Redis data dump
echo - images/ - Application images
echo - logs/ - Application logs
echo - Configuration files
echo.
echo To restore this backup:
echo 1. Stop the application: docker-compose -f docker-compose.prod.yaml down
echo 2. Restore database: docker exec -i lookhub-db psql -U lookhubweb -d lookhub ^< database.sql
echo 3. Restore Redis: docker cp redis_dump.rdb lookhub-redis:/data/dump.rdb
echo 4. Restore files: copy images/ to ./images/, copy logs/ to ./logs/
echo 5. Start application: docker-compose -f docker-compose.prod.yaml up -d
) > "%FULL_BACKUP_DIR%\README.txt"

REM 7. Create compressed archive
echo [INFO] Creating compressed archive...
cd "%BACKUP_DIR%"
powershell -Command "Compress-Archive -Path '%BACKUP_NAME%' -DestinationPath '%BACKUP_NAME%.zip' -Force"
if errorlevel 1 (
    echo [WARN] Archive creation failed, backup files are in: %FULL_BACKUP_DIR%
) else (
    echo [INFO] ✅ Compressed archive created: %BACKUP_NAME%.zip
    REM Remove uncompressed directory to save space
    rmdir /S /Q "%BACKUP_NAME%"
)
cd ..

REM 8. Cleanup old backups (keep last 7 days)
echo [INFO] Cleaning up old backups...
forfiles /p "%BACKUP_DIR%" /m "*.zip" /d -7 /c "cmd /c del @path" 2>nul

echo [INFO] 🎉 Backup completed successfully!
echo [INFO] Backup location: %BACKUP_DIR%\%BACKUP_NAME%.zip
echo [INFO] Backup size:
for %%A in ("%BACKUP_DIR%\%BACKUP_NAME%.zip") do echo [INFO] %%~zA bytes

pause


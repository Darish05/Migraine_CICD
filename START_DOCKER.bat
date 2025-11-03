@echo off
cls
echo.
echo ========================================
echo   MIGRAINE ML - DOCKER BUILD
echo ========================================
echo.

cd /d D:\Mlops\migraine-ml

echo Step 1: Build Docker Image
echo.
echo This will take 5-10 minutes...
echo.
docker build -t migraine-ml-api:latest .

if %errorlevel% neq 0 (
    echo.
    echo BUILD FAILED!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD SUCCESSFUL!
echo ========================================
echo.
echo Starting containers...
echo.

docker-compose up -d

if %errorlevel% neq 0 (
    echo.
    echo FAILED TO START!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS! API IS RUNNING
echo ========================================
echo.
echo Your API: http://localhost:8000
echo.
echo Test: curl http://localhost:8000/health
echo Logs: docker-compose logs -f
echo Stop: docker-compose down
echo.
pause

@echo off
echo.
echo ====================================
echo   DOCKER BUILD - MIGRAINE ML API
echo ====================================
echo.

cd /d D:\Mlops\migraine-ml

echo [1/5] Checking Docker...
docker --version
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo.
echo [2/5] Checking required files...
if not exist Dockerfile (
    echo ERROR: Dockerfile not found!
    pause
    exit /b 1
)
if not exist docker-compose.yml (
    echo ERROR: docker-compose.yml not found!
    pause
    exit /b 1
)
if not exist models\classification_model_top1.pkl (
    echo ERROR: Models not found! Run training first.
    pause
    exit /b 1
)

echo All files present!

echo.
echo [3/5] Cleaning old containers...
docker-compose down 2>nul

echo.
echo [4/5] Building Docker image...
echo This will take 5-10 minutes. Please wait...
echo.
docker build -t migraine-ml-api:latest .

if errorlevel 1 (
    echo.
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)

echo.
echo [5/5] Starting containers...
docker-compose up -d

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start containers!
    pause
    exit /b 1
)

echo.
echo ====================================
echo   SUCCESS! 
echo ====================================
echo.
echo Your API is now running at:
echo   http://localhost:8000
echo.
echo Test it with:
echo   curl http://localhost:8000/health
echo.
echo View logs with:
echo   docker-compose logs -f
echo.
echo Stop containers with:
echo   docker-compose down
echo.
pause

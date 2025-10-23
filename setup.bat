@echo off
echo ========================================
echo Pathway RAG System - Windows Setup
echo ========================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop for Windows
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [OK] Docker found
echo.

REM Check if Docker daemon is running
docker info >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker daemon is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [OK] Docker daemon is running
echo.

REM Check if .env exists
if not exist .env (
    echo [SETUP] Creating .env file...
    echo GEMINI_API_KEY=your_gemini_api_key_here > .env
    echo [WARNING] Please edit .env and add your Gemini API key
    echo.
    notepad .env
    echo.
    echo Press any key after saving your API key...
    pause >nul
)

REM Create data directory if it doesn't exist
if not exist data mkdir data

REM Check if sample data exists
if not exist data\balances.csv (
    echo [SETUP] Creating sample data file...
    (
        echo id,description
        echo 1,"Q1 2024 revenue increased by 15%% reaching $2.5M with strong customer acquisition"
        echo 2,"Operating expenses decreased by 8%% due to cost optimization initiatives"
        echo 3,"Cash reserves stand at $1.2M as of March 2024 showing healthy liquidity"
        echo 4,"Q2 2024 shows promising growth trajectory with 20%% increase in recurring revenue"
        echo 5,"Customer churn rate dropped to 3%% indicating improved retention strategies"
        echo 6,"R&D investment increased to 18%% of revenue to support product innovation"
        echo 7,"Gross margin improved to 68%% from 62%% in previous quarter"
        echo 8,"Marketing spend efficiency improved with 25%% lower customer acquisition cost"
        echo 9,"Accounts receivable days reduced from 45 to 35 days showing better collections"
        echo 10,"Net profit margin reached 15%% exceeding industry average of 12%%"
    ) > data\balances.csv
    echo [OK] Sample data created
    echo.
)

echo ========================================
echo Building Docker Image...
echo ========================================
docker-compose build

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Container...
echo ========================================
docker-compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start container
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Pathway RAG Server is running!
echo ========================================
echo.
echo Server URL: http://localhost:8080
echo.
echo Endpoints:
echo   - POST http://localhost:8080/v1/retrieve
echo   - POST http://localhost:8080/v1/statistics
echo.
echo Commands:
echo   View logs:    docker-compose logs -f
echo   Stop server:  docker-compose down
echo   Restart:      docker-compose restart
echo.
echo Testing connection in 10 seconds...
timeout /t 10 /nobreak >nul

curl -X POST http://localhost:8080/v1/statistics 2>nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Server is responding!
) else (
    echo.
    echo [INFO] Server is still starting up...
    echo Run: docker-compose logs -f
    echo to monitor startup progress
)
echo.
pause
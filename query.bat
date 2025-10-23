@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Pathway RAG Query Interface
echo ========================================
echo.

REM Check if server is running
curl -s -X POST http://localhost:8080/v1/statistics >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Server is not responding
    echo Please run setup.bat first to start the server
    pause
    exit /b 1
)

echo [OK] Server is running
echo.

:menu
echo ========================================
echo Select a query or enter custom:
echo ========================================
echo 1. Summarize financial balance trends
echo 2. What is the cash reserve position?
echo 3. How has customer retention improved?
echo 4. What are revenue growth indicators?
echo 5. Custom query
echo 6. Exit
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" set "query=Summarize the latest financial balance trends"
if "%choice%"=="2" set "query=What is the current cash reserve position?"
if "%choice%"=="3" set "query=How has customer retention improved?"
if "%choice%"=="4" set "query=What are the key revenue growth indicators?"
if "%choice%"=="5" (
    set /p "query=Enter your query: "
)
if "%choice%"=="6" exit /b 0

if not defined query goto menu

echo.
echo Query: !query!
echo.
echo Searching...
echo.

REM Create temporary JSON file for the request
echo {"query": "!query!", "k": 3} > temp_query.json

REM Make the request
curl -X POST http://localhost:8080/v1/retrieve ^
     -H "Content-Type: application/json" ^
     -d @temp_query.json

echo.
echo.
del temp_query.json

REM Ask if user wants to continue
echo.
set /p continue="Query again? (Y/N): "
if /i "%continue%"=="Y" (
    cls
    goto menu
)

echo.
echo Goodbye!
pause
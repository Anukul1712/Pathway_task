# Fix project structure for Windows
Write-Host "Fixing project structure..." -ForegroundColor Yellow

# Create requirements.txt in the root directory
$requirementsContent = @"
# Core Pathway with ALL LLM xpack dependencies
pathway[xpack-llm-docs]>=0.8.0

# Embedders
sentence-transformers>=2.2.0
torch>=2.0.0

# LLM providers - Ollama
langchain>=0.2.0
langchain-community>=0.2.0
ollama>=0.1.0

# Utilities
python-dotenv>=1.0.0
pandas>=2.0.0
requests>=2.31.0
colorlog>=6.7.0

# Additional system utilities for Windows compatibility
python-magic-bin>=0.4.14; sys_platform == 'win32'
"@

Write-Host "Creating requirements.txt in root..." -ForegroundColor Yellow
$requirementsContent | Out-File -FilePath "requirements.txt" -Encoding UTF8 -NoNewline

# Create .env.example if it doesn't exist
$envContent = @"
# Ollama Configuration
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2:3b

# Available models you can use:
# - llama3.2:1b (fastest, smallest)
# - llama3.2:3b (balanced)
# - llama3.1:8b (more capable)
# - mistral:7b
# - phi3:mini

# Pathway Configuration
PATHWAY_HOST=0.0.0.0
PATHWAY_PORT=8080

# Logging
LOG_LEVEL=INFO
"@

if (-not (Test-Path ".env.example")) {
    Write-Host "Creating .env.example..." -ForegroundColor Yellow
    $envContent | Out-File -FilePath ".env.example" -Encoding UTF8 -NoNewline
}

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env..." -ForegroundColor Yellow
    $envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline
}

# Ensure app directory exists with the correct files
Write-Host "Setting up app directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "app" | Out-Null

# Check if main.py exists in app
if (-not (Test-Path "app\main.py")) {
    Write-Host "[WARNING] app\main.py is missing!" -ForegroundColor Red
    Write-Host "Please ensure you have main.py in the app folder" -ForegroundColor Yellow
}

# Check if langchain_agent.py exists in app
if (-not (Test-Path "app\langchain_agent.py")) {
    Write-Host "[WARNING] app\langchain_agent.py is missing!" -ForegroundColor Red
    Write-Host "Please ensure you have langchain_agent.py in the app folder" -ForegroundColor Yellow
}

# Create data directory with sample CSV
Write-Host "Setting up data directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data" | Out-Null

if (-not (Test-Path "data\balances.csv")) {
    Write-Host "Creating sample balances.csv..." -ForegroundColor Yellow
    $csvContent = @"
id,description
1,"Company ABC has a balance of `$50,000 in Q1 2024"
2,"Company XYZ reported `$120,000 balance in January 2024"
3,"Recent update: Company ABC balance increased to `$65,000 in Q2 2024"
4,"Company XYZ maintained stable balance of `$118,000 in February 2024"
5,"New entry: Company DEF started with `$200,000 initial balance"
6,"Company ABC reached `$80,000 balance in Q3 2024 showing strong growth"
7,"Company GHI launched with `$150,000 funding in March 2024"
"@
    $csvContent | Out-File -FilePath "data\balances.csv" -Encoding UTF8 -NoNewline
}

Write-Host "`n[OK] Project structure fixed!" -ForegroundColor Green
Write-Host "`nYour project should now have:" -ForegroundColor Yellow
Write-Host "  - requirements.txt (root)" -ForegroundColor White
Write-Host "  - .env and .env.example" -ForegroundColor White
Write-Host "  - app/main.py" -ForegroundColor White
Write-Host "  - app/langchain_agent.py" -ForegroundColor White
Write-Host "  - data/balances.csv" -ForegroundColor White
Write-Host "  - Dockerfile" -ForegroundColor White
Write-Host "  - docker-compose.yml" -ForegroundColor White

# Verify structure
Write-Host "`nVerifying structure..." -ForegroundColor Yellow
$files = @(
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    ".env",
    "app\main.py",
    "app\langchain_agent.py",
    "data\balances.csv"
)

$allGood = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $allGood = $false
    }
}

if ($allGood) {
    Write-Host "`n[SUCCESS] All required files are in place!" -ForegroundColor Green
    Write-Host "You can now run: docker-compose build" -ForegroundColor Yellow
} else {
    Write-Host "`n[WARNING] Some files are missing. Please add them before building." -ForegroundColor Red
}
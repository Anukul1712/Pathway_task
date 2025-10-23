# Pathway + LangChain RAG System (Windows + Docker)

Real-time Retrieval-Augmented Generation system using Pathway in Docker for Windows users.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop for Windows
- Python 3.10+ (for client only)
- Gemini API Key

### Setup Steps

1. **Get Gemini API Key**: https://makersuite.google.com/app/apikey

2. **Run Setup**:
```cmd
   setup.bat
```

3. **Query the System**:
```cmd
   query.bat
```
   Or:
```cmd
   python test_client.py
```

## 📊 Architecture
## 🐳 Docker Commands
```cmd
# Start server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop server
docker-compose down

# Restart
docker-compose restart
```

## 📡 API Endpoints

- `POST http://localhost:8080/v1/retrieve` - Retrieve documents
- `POST http://localhost:8080/v1/statistics` - Get statistics

## 🔄 Real-time Updates

Add data to `data/balances.csv` and it's automatically indexed:
```cmd
echo 11,"New financial metric..." >> data\balances.csv
```

## 🐛 Troubleshooting

### Server Not Responding
```cmd
docker-compose restart
docker-compose logs
```

### Port Already in Use
```cmd
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

## 📚 Resources

- [Pathway Docs](https://pathway.com/developers/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Gemini API](https://ai.google.dev/docs)

## 📝 License

MIT License
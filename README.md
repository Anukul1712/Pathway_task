# Pathway Vector Store with LangChain Agent

A real-time RAG (Retrieval-Augmented Generation) system that combines Pathway's streaming vector store with a LangChain agent powered by Ollama for intelligent document retrieval and question answering.

## Overview

This project demonstrates:
- **Pathway Vector Store**: Real-time document indexing and semantic search from streaming CSV data
- **LangChain ReAct Agent**: Intelligent agent that retrieves and reasons over financial data
- **Ollama Integration**: Local LLM (Llama 3.1) for private, cost-effective AI responses
- **Docker Containerization**: Easy deployment with Docker Compose

## Architecture

```
┌─────────────────┐         ┌──────────────────────┐         ┌─────────────┐
│   CSV Data      │────────▶│  Pathway Vector      │◀────────│  LangChain  │
│  (Streaming)    │         │  Store Server        │         │   Agent     │
│                 │         │  (Docker: 8080)      │         │             │
└─────────────────┘         └──────────────────────┘         └─────────────┘
                                                                     │
                                                                     ▼
                                                              ┌─────────────┐
                                                              │   Ollama    │
                                                              │  (11434)    │
                                                              └─────────────┘
```

## Prerequisites

Ensure you have the following installed:

- **Docker** (version 20.10+) and **Docker Compose**
- **Python 3.10+**
- **Ollama** - [Install Ollama](https://ollama.ai/download)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Anukul1712/Pathway_task.git
cd Pathway_task
```

### 2. Project Structure

```
Pathway_task/
├── app/
│   └── main.py                 # Pathway vector store server
│   └── langchain.py            # LangChain agent with Ollama
│   └── requirements.txt
├── data/                       # CSV files directory (streaming input)
│   └── balances.csv
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Pathway server container
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### 3. Install Ollama and Pull Model

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull the qwen 2.5 model
ollama pull qwen2.5:1.5b

# Start Ollama server (if not running)
ollama serve
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
```txt
pathway-ai
langchain
langchain-community
requests
sentence-transformers
```

### 5. Prepare Your Data

Place your CSV files in the `data/` directory. Expected schema:

```csv
id,description
1,"Company ABC has a balance of $50000"
2,"Company XYZ reported balance of $75000"
```

The system will automatically monitor this directory for new/updated CSV files.

## Running the Project

### **IMPORTANT: Follow this execution order!**

### Step 1: Start Pathway Vector Store (Docker)

First, start the Pathway server using Docker Compose:

```bash
docker-compose up -d
```

**What this does:**
- Builds the Pathway Docker container
- Starts the vector store server on `localhost:8080`
- Monitors `./data/` directory for CSV files
- Creates embeddings using `sentence-transformers/all-MiniLM-L6-v2`

**Verify it's running:**

```bash
# Check container status
docker ps

# View logs
docker logs pathway_vectorstore

# Test the statistics endpoint
curl http://localhost:8080/v1/statistics
```

### Step 2: Run the LangChain Agent

Once Pathway is running, start the interactive agent:

```bash
python lanchain_agent.py
```

**What this does:**
- Waits for Pathway server to be ready
- Connects to your local Ollama instance
- Creates a ReAct agent with the `pathway_retrieve` tool
- Starts an interactive query interface

## Interactive Query Examples

Once the agent is running, you can ask questions like:

```
 Your question: What is the balance of Company ABC?
 Your question: Which company has the highest balance?
 Your question: List all companies and their balances
 Your question: Summarize the financial data
```

Type `exit`, `quit`, or `q` to stop the agent.

## How It Works

### Pathway Vector Store (main.py)

1. **Reads CSV files** from `/app/data/` in streaming mode
2. **Generates embeddings** using sentence-transformers
3. **Exposes REST API** endpoints:
   - `POST /v1/retrieve` - Semantic search
   - `GET /v1/statistics` - Server stats

### LangChain Agent (lanchain_agent.py)

1. **pathway_retrieve tool**: Queries the vector store with semantic search
2. **ReAct agent**: Uses thought-action-observation loop to reason
3. **Ollama LLM**: Processes queries using Llama 3.1 (8B parameters)
4. **Interactive mode**: Allows continuous querying

## Configuration

### Environment Variables

You can customize settings via environment variables:

```bash
# Pathway server URL
export PATHWAY_RETRIEVE_URL="http://localhost:8080/v1/retrieve"

# Ollama configuration
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.1:8b"
```

### Docker Configuration

Edit `docker-compose.yml` to change:
- Port mappings (default: 8080)
- Volume mounts
- Environment variables

### Agent Configuration

In `lanchain_agent.py`, you can modify:
- `max_iterations`: Agent reasoning steps (default: 4)
- `temperature`: LLM randomness (default: 0)
- `k`: Number of documents to retrieve (default: 5)

## Troubleshooting

### Pathway Container Won't Start

```bash
# Check logs
docker logs pathway_vectorstore

# Restart container
docker-compose restart

# Rebuild if needed
docker-compose up --build -d
```

### Ollama Connection Failed

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Verify model is available
ollama list
```

### Agent Doesn't Find Data

- Ensure CSV files are in the `data/` directory
- Check Pathway logs: `docker logs pathway_vectorstore`
- Verify the CSV schema matches expected format
- Wait a few seconds for indexing after adding new files

### Port Already in Use

```bash
# Check what's using port 8080
lsof -i :8080

# Change port in docker-compose.yml
ports:
  - "8081:8080"  # Use 8081 instead

# Update PATHWAY_RETRIEVE_URL
export PATHWAY_RETRIEVE_URL="http://localhost:8081/v1/retrieve"
```

## API Endpoints

### Pathway Vector Store

**Retrieve Documents (Semantic Search)**
```bash
curl -X POST http://localhost:8080/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "company balance", "k": 5}'
```

**Server Statistics**
```bash
curl http://localhost:8080/v1/statistics
```

## Testing

### 1. Test Pathway Vector Store

```bash
# Add a test CSV file
echo "id,description" > data/test.csv
echo "1,Test Company has balance of \$10000" >> data/test.csv

# Wait 2-3 seconds for indexing, then query
curl -X POST http://localhost:8080/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "Test Company balance", "k": 3}'
```

### 2. Test Agent

```bash
python lanchain_agent.py
# Then ask: "What is the balance of Test Company?"
```

## Stopping the Services

```bash
# Stop the agent (Ctrl+C or type 'exit')

# Stop Pathway Docker container
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Performance Tips

1. **Adjust autocommit duration** in `main.py` for faster/slower indexing:
   ```python
   autocommit_duration_ms=2000  # 2 seconds (default)
   ```

2. **Use GPU acceleration** for Ollama (if available):
   ```bash
   ollama pull llama3.1:8b  # Will use GPU automatically
   ```

3. **Increase retrieval results** for more context:
   ```python
   payload = {"query": clean_query, "k": 10}  # Get 10 docs instead of 5
   ```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Resources

- [Pathway Documentation](https://pathway.com/developers/documentation/)
- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://ollama.ai/)
- [Sentence Transformers](https://www.sbert.net/)

## Author

**Anukul**
- GitHub: [@Anukul1712](https://github.com/Anukul1712)

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/Anukul1712/Pathway_task/issues)
- Check existing documentation
- Review logs: `docker logs pathway_vectorstore`

---

**Quick Start Reminder:**
1. `docker-compose up -d` (Start Pathway)
2. `python lanchain_agent.py` (Run Agent)
3. Ask questions about your data!

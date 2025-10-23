import os
import pathway as pw
from pathway.xpacks.llm.vector_store import VectorStoreServer
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

logger.info("Gemini API key loaded")

# Define schema
class BalanceSchema(pw.Schema):
    id: str
    description: str

# Step 1: Read streaming data
logger.info("Setting up data source from /app/data/...")
data_source = pw.io.csv.read(
    "/app/data/",
    schema=BalanceSchema,
    mode="streaming",
    autocommit_duration_ms=2000,
)

# Step 2: Prepare documents with correct schema for VectorStoreServer
# VectorStoreServer expects 'data' column, not 'text'
documents = data_source.select(
    data=pw.this.description,  # Changed from 'text' to 'data'
)

logger.info(f"Documents configured: {documents}")

# Step 3: Configure embeddings
logger.info("Loading sentence-transformers embedding model...")
from pathway.xpacks.llm.embedders import SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2",
)

logger.info("Embedder loaded successfully")

# Step 4: Create vector store with REST API
logger.info("Building vector store server...")
vector_store = VectorStoreServer(
    documents,
    embedder=embedder,
)

# Step 5: Setup REST API endpoint
host = "0.0.0.0"
port = 8080

logger.info(f"Starting REST API server on {host}:{port}")
logger.info(f"Retrieve endpoint: http://localhost:{port}/v1/retrieve")
logger.info(f"Statistics endpoint: http://localhost:{port}/v1/statistics")
logger.info("Monitoring /app/data/ for real-time updates...")
logger.info("Server is ready to accept requests!")

# Run the server
vector_store.run_server(
    host=host, 
    port=port, 
    with_cache=False,  # Disabled cache for simplicity
    cache_backend=None
)

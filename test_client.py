"""
Windows-compatible client to query Pathway RAG system running in Docker
No need to install Pathway locally - just requests and langchain-google-genai
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
API_URL = "http://localhost:8080/v1/retrieve"
STATS_URL = "http://localhost:8080/v1/statistics"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def check_server():
    """Check if Pathway server is running"""
    try:
        response = requests.post(STATS_URL, timeout=5)
        response.raise_for_status()
        print("✅ Server is running and responding")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:8080")
        print("   Please run: docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def retrieve_documents(question: str, top_k: int = 3):
    """Retrieve relevant documents from Pathway vector store"""
    payload = {"query": question, "k": top_k}
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        results = response.json()
        return results
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        return None

def generate_answer_with_gemini(question: str, documents: list):
    """Generate answer using Gemini API"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("⚠️  GEMINI_API_KEY not set. Showing retrieved documents only.")
        return None
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Build context
        context = "\n\n".join([
            f"Document {i+1}: {doc['text']}" 
            for i, doc in enumerate(documents)
        ])
        
        # Create LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.5
        )
        
        # Generate answer
        prompt = f"""Based on the following financial data, answer the question concisely.

Context:
{context}

Question: {question}

Provide a clear, concise answer:"""
        
        answer = llm.invoke(prompt)
        return answer.content
        
    except ImportError:
        print("⚠️  langchain-google-genai not installed. Install with:")
        print("   pip install langchain-google-genai")
        return None
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return None

def query_rag(question: str, top_k: int = 3):
    """Complete RAG query pipeline"""
    print(f"\n{'='*60}")
    print(f"❓ Query: {question}")
    print(f"{'='*60}\n")
    
    # Step 1: Retrieve documents
    print("🔍 Retrieving relevant documents from Pathway...")
    documents = retrieve_documents(question, top_k)
    
    if not documents:
        return
    
    print(f"✅ Found {len(documents)} relevant documents\n")
    
    # Display retrieved documents
    print("📄 Retrieved Documents:")
    print("-" * 60)
    for i, doc in enumerate(documents):
        print(f"\n[{i+1}] {doc.get('text', 'N/A')}")
    print("\n" + "-" * 60)
    
    # Step 2: Generate answer with Gemini
    print("\n🤖 Generating answer with Gemini...\n")
    answer = generate_answer_with_gemini(question, documents)
    
    if answer:
        print("💡 Answer:")
        print("=" * 60)
        print(answer)
        print("=" * 60)
    
    return {
        "question": question,
        "documents": documents,
        "answer": answer
    }

def interactive_mode():
    """Interactive query interface"""
    print("\n" + "="*60)
    print("🚀 Pathway RAG Interactive Query Client")
    print("="*60)
    
    if not check_server():
        return
    
    print("\nType 'quit' or 'exit' to stop\n")
    
    sample_queries = [
        "Summarize the latest financial balance trends",
        "What is the current cash reserve position?",
        "How has customer retention improved?",
        "What are the key revenue growth indicators?",
    ]
    
    while True:
        print("\n" + "-"*60)
        print("Sample queries:")
        for i, q in enumerate(sample_queries, 1):
            print(f"  {i}. {q}")
        print("\nOr enter your custom query:")
        
        user_input = input("\n> ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        # Check if user selected a number
        if user_input.isdigit() and 1 <= int(user_input) <= len(sample_queries):
            query = sample_queries[int(user_input) - 1]
        elif user_input:
            query = user_input
        else:
            continue
        
        query_rag(query)

if __name__ == "__main__":
    # Check if running in interactive mode
    import sys
    
    if len(sys.argv) > 1:
        # Command line query
        question = " ".join(sys.argv[1:])
        if check_server():
            query_rag(question)
    else:
        # Interactive mode
        interactive_mode()
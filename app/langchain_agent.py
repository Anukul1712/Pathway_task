import os
import time
import requests
from langchain_community.llms import Ollama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

# ==========================
# CONFIGURATION
# ==========================
PATHWAY_RETRIEVE_URL = os.getenv("PATHWAY_RETRIEVE_URL", "http://localhost:8080/v1/retrieve")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")  # You can use "llama3.1:8b"

print(f" Configuration:")
print(f"   Pathway URL: {PATHWAY_RETRIEVE_URL}")
print(f"   Ollama URL:  {OLLAMA_BASE_URL}")
print(f"   Ollama Model:{OLLAMA_MODEL}")


# ==========================
# WAIT FUNCTIONS
# ==========================
def wait_for_pathway(max_retries=30, delay=2):
    """Wait for Pathway server to be ready"""
    print(" Waiting for Pathway server to be ready...")
    for i in range(max_retries):
        try:
            response = requests.get(PATHWAY_RETRIEVE_URL.replace("/v1/retrieve", "/v1/statistics"))
            if response.status_code == 200:
                print(" Pathway server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"   Attempt {i+1}/{max_retries}...")
        time.sleep(delay)
    print(" Pathway server failed to start.")
    return False


def wait_for_ollama(max_retries=10, delay=2):
    """Wait for Ollama to be ready"""
    print(" Checking Ollama connection...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                print(f" Ollama is ready! Available models: {model_names}")

                if any(OLLAMA_MODEL in name for name in model_names):
                    print(f" Model {OLLAMA_MODEL} is available!")
                else:
                    print(f" Model {OLLAMA_MODEL} not found. Please pull it:")
                    print(f"   ollama pull {OLLAMA_MODEL}")
                return True
        except requests.exceptions.RequestException as e:
            print(f"   Connection failed: {e}")
        print(f"   Attempt {i+1}/{max_retries}...")
        time.sleep(delay)
    print(" Cannot connect to Ollama. Make sure it's running on your host machine.")
    print("   Start Ollama: ollama serve")
    return False


# ==========================
# PATHWAY RETRIEVAL TOOL
# ==========================
@tool
def pathway_retrieve(query: str) -> str:
    """
    Retrieves semantically similar documents from the Pathway vector store.
    Use this tool to search for information about company balances, financial data, and CSV records.
    """
    try:
        clean_query = query.strip().strip('"').strip("'").strip()
        if " or " in clean_query.lower():
            clean_query = clean_query.split(" or ")[0].strip()
        if " and " in clean_query.lower():
            clean_query = clean_query.split(" and ")[0].strip()

        print(f"\n Searching Pathway for: '{clean_query}'")
        payload = {"query": clean_query, "k": 5}
        print(f" Request payload: {payload}")

        response = requests.post(PATHWAY_RETRIEVE_URL, json=payload)
        print(f" Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            docs = [d.get("text", "") for d in data]
            result = "\n\n".join(docs)
            print(f" Found {len(docs)} documents")
            return result if result else "No relevant documents found."
        else:
            return f"Error retrieving from Pathway: {response.text}"

    except Exception as e:
        return f"Error calling Pathway: {str(e)}"


# ==========================
# REACT PROMPT TEMPLATE
# ==========================
REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format EXACTLY:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (use simple phrases like "Company ABC balance")
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

CRITICAL RULES:
1. ALWAYS answer the ORIGINAL question, not a different question
2. After getting relevant information from pathway_retrieve, provide a Final Answer
3. Use simple search phrases for Action Input (e.g., "Company ABC balance")
4. If you have information to answer the question, say "I now know the final answer" and provide it
5. Do not ask different questions - stick to the original question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


# ==========================
# MAIN EXECUTION
# ==========================
if __name__ == "__main__":
    if not wait_for_pathway():
        exit(1)
    if not wait_for_ollama():
        exit(1)

    print("\n Initializing Ollama LLM...")
    try:
        llm = Ollama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,
            system="You are a helpful financial data assistant. You analyze company balance information from a database. This is business data analysis, not personal information."
        )
        print(" Ollama LLM initialized")
    except Exception as e:
        print(f" Failed to initialize Ollama: {e}")
        exit(1)

    print("\n🔧 Creating agent with Pathway retrieval tool...")
    try:
        prompt = PromptTemplate.from_template(REACT_PROMPT)
        tools = [pathway_retrieve]
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=4,
            return_intermediate_steps=True
        )
        print(" Agent created successfully")
    except Exception as e:
        print(f" Failed to create agent: {e}")
        exit(1)

    # ==========================
    # INTERACTIVE QUERY MODE
    # ==========================
    print("\n" + "=" * 80)
    print(" INTERACTIVE QUERY MODE")
    print("=" * 80)
    print("\n You can now ask questions about your data!")
    print("Examples:")
    print("  - What is the balance of Company ABC?")
    print("  - Which company has the highest balance?")
    print("  - List all companies and their balances")
    print("  - Summarize the recent updates")
    print("\nType 'exit', 'quit', or 'q' to stop.\n")

    while True:
        try:
            query = input(" Your question: ").strip()
            if query.lower() in ["exit", "quit", "q", ""]:
                print("\n Goodbye! Thanks for using the agent.")
                break

            print(f"\n{'='*80}")
            print(f" Query: {query}")
            print(f"{'='*80}")

            try:
                result = agent_executor.invoke({"input": query})
                output = result.get("output", "No output")

                if output == "Agent stopped due to iteration limit or time limit.":
                    print("\n Agent reached iteration limit. Extracting last retrieved info...")
                    steps = result.get("intermediate_steps", [])
                    if steps:
                        last_observation = steps[-1][1] if len(steps) > 0 else ""
                        if last_observation:
                            print(f"\n📄 Retrieved Information:\n{last_observation[:500]}...")
                            print("\n💡 Suggested Answer: Based on the retrieved data above.")
                else:
                    print(f"\n Answer: {output}")

            except Exception as e:
                print(f"\n Error processing query: {e}")

            print(f"{'='*80}\n")

        except KeyboardInterrupt:
            print("\n Interrupted by user. Exiting...")
            break

    print("\n✅ All queries completed!")


import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directories Configuration
BASE_DIR        = Path(__file__).parent
DATA_DIR        = BASE_DIR / "data"
IS875_DIR       = DATA_DIR / "is875"         
VECTORDB_DIR    = DATA_DIR / "vectordb"       
QA_DIR          = DATA_DIR / "qa_pairs"       
LOGS_DIR        = BASE_DIR / "logs" 


for d in [IS875_DIR, VECTORDB_DIR, QA_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


IS875_FILES = {
    "part1": IS875_DIR / "IS_875_Part1_Dead_Loads.pdf",
    "part2": IS875_DIR / "IS_875_Part2_Imposed_Loads.pdf",
    "part3": IS875_DIR / "IS_875_Part3_Wind_Loads.pdf",
}

# Embedding model Configuration
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5" 
EMBEDDING_DEVICE = "cpu"


CHROMA_COLLECTION_NAME = "is875_clauses"

# Chunking Configuration
CHUNK_MAX_TOKENS   = 400    
CHUNK_OVERLAP      = 75     

# Retrieval Configuration
TOP_K_SEMANTIC     = 10    
TOP_K_BM25         = 10     
TOP_K_FINAL        = 7     
SEMANTIC_WEIGHT    = 0.6   
BM25_WEIGHT        = 0.4   

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash-lite"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"
OLLAMA_MODEL       = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL    = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MAX_TOKENS     = 1024
LLM_TEMPERATURE    = 0.1   

# Logging Configuration
LOG_LEVEL = "INFO"

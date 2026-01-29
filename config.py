# Configuration file for API settings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAnalyst API (for data analysis)
API_KEY = os.environ.get("OPENANALYST_API_KEY", "")
API_BASE_URL = "https://api.openanalyst.com/api/ai/chat"
MODEL = "anthropic/claude-sonnet-4"
MAX_TOKENS = 4096

# Perplexity API (for web search)
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "llama-3.1-sonar-small-128k-online"  # Online model with web search

"""
Web Search Script using Perplexity API
Usage: python scripts/web_search.py <query>
Performs web search and returns AI-summarized results
"""
import sys
import os
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PERPLEXITY_API_KEY, PERPLEXITY_API_URL, PERPLEXITY_MODEL


def web_search(query):
    """Perform web search using Perplexity API"""

    if not PERPLEXITY_API_KEY:
        return {
            "success": False,
            "error": "Perplexity API key not configured. Please set PERPLEXITY_API_KEY in your .env file"
        }

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful research assistant. Provide accurate, well-sourced information from the web. Include relevant facts, statistics, and cite sources when possible. Format your response clearly with sections and bullet points."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "max_tokens": 2048,
        "temperature": 0.2,
        "return_citations": True,
        "return_related_questions": True
    }

    try:
        response = requests.post(
            PERPLEXITY_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()

        # Extract the response
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "No response")

        # Extract citations if available
        citations = result.get("citations", [])

        # Format output
        output = content

        if citations:
            output += "\n\n**Sources:**\n"
            for i, citation in enumerate(citations, 1):
                output += f"{i}. {citation}\n"

        return {
            "success": True,
            "title": "Web Search Results",
            "result": output
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Perplexity API Error: {str(e)}"
        }


def format_output(data):
    """Format output as JSON"""
    return json.dumps(data, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(format_output({"success": False, "error": "Please provide a search query"}))
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    result = web_search(query)
    print(format_output(result))

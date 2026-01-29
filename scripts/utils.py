"""
Utility functions for all analysis scripts
"""
import pandas as pd
import requests
import json
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_KEY, API_BASE_URL, MODEL, MAX_TOKENS


def load_data(file_paths):
    """Load and combine data from multiple files"""
    dataframes = []
    for file_path in file_paths:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            continue
        dataframes.append(df)

    if not dataframes:
        return None

    # Combine all dataframes
    combined = pd.concat(dataframes, ignore_index=True) if len(dataframes) > 1 else dataframes[0]
    return combined


def get_data_context(df, max_rows=50):
    """Generate a context string describing the data"""
    context = f"Dataset has {len(df)} rows and {len(df.columns)} columns.\n\n"
    context += f"Columns: {', '.join(df.columns.tolist())}\n\n"
    context += f"Data types:\n{df.dtypes.to_string()}\n\n"
    context += f"Sample data (first {min(max_rows, len(df))} rows):\n"
    context += df.head(max_rows).to_string()

    # Add basic statistics for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        context += f"\n\nNumeric column statistics:\n{df[numeric_cols].describe().to_string()}"

    return context


def call_ai(prompt, system_message=None):
    """Make API call to get AI response"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": messages
    }

    try:
        response = requests.post(
            API_BASE_URL,
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        # OpenAI format response
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0].get("message", {}).get("content", "No response generated")
        # Anthropic format response
        if "content" in result and len(result["content"]) > 0:
            return result["content"][0].get("text", "No response generated")
        return "No response generated"

    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"


def format_output(result, title="Analysis Result"):
    """Format output as JSON for the UI"""
    output = {
        "success": True,
        "title": title,
        "result": result
    }
    return json.dumps(output, indent=2)


def error_output(message):
    """Format error output as JSON"""
    output = {
        "success": False,
        "error": message
    }
    return json.dumps(output, indent=2)

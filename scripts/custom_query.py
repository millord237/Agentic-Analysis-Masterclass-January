"""
Custom Query Analysis Script
Usage: python scripts/custom_query.py <query> <file1> [file2] ...
Handles any custom AI-powered query about the data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import load_data, get_data_context, call_ai, format_output, error_output


def run_custom_query(query, file_paths):
    """Handle custom query using AI"""
    df = load_data(file_paths)
    if df is None:
        return error_output("Could not load data files")

    context = get_data_context(df)

    prompt = f"""Based on this dataset, answer the user's question:

USER QUERY: {query}

DATASET:
{context}

Please provide a comprehensive answer to the user's question. Include:
- Direct answer to the question
- Supporting data and numbers from the dataset
- Any relevant calculations
- Additional insights that might be helpful
- Recommendations if applicable

Format your response clearly with markdown. Use tables for data comparisons."""

    system_message = "You are a data analyst expert. Answer questions about data accurately using the actual numbers from the dataset. Provide clear, actionable insights."

    result = call_ai(prompt, system_message)
    return format_output(result, "Analysis Result")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(error_output("Usage: python custom_query.py <query> <file1> [file2] ..."))
        sys.exit(1)

    query = sys.argv[1]
    file_paths = sys.argv[2:]
    print(run_custom_query(query, file_paths))
